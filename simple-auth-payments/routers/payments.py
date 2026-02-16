from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import BundleResponse, PaymentCreate
from routers.auth import get_current_user_from_cookie
import models
from services.stripe_service import create_payment_intent, verify_webhook_signature
import stripe

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/discount-options")
def get_discount_options(db: Session = Depends(get_db)):
    """Get available discount options for frontend display"""
    rules = db.query(models.DiscountRule).filter(
        models.DiscountRule.is_active == True
    ).order_by(models.DiscountRule.min_months).all()
    
    options = []
    for rule in rules:
        # Create user-friendly display
        if rule.max_months:
            if rule.min_months == rule.max_months:
                months_display = f"{rule.min_months} months"
            else:
                months_display = f"{rule.min_months}-{rule.max_months} months"
        else:
            months_display = f"{rule.min_months}+ months"
        
        options.append({
            "min_months": rule.min_months,
            "max_months": rule.max_months,
            "discount_percentage": rule.discount_percentage,
            "display_text": f"{months_display}: {rule.discount_percentage}% OFF",
            "banner_message": f"Save {rule.discount_percentage}% on {months_display}!"
        })
    
    return options


@router.get("/bundles", response_model=List[BundleResponse])
def get_bundles(db: Session = Depends(get_db)):
    bundles = db.query(models.Bundle).filter(models.Bundle.is_active == True).all()
    return bundles


@router.get("/bundle-content/{bundle_id}")
def get_bundle_content(bundle_id: int, db: Session = Depends(get_db)):
    """Get SVG and description content for a specific bundle"""
    from utils.bundle_helpers import get_svg_html, get_predefined_description
    
    bundle = db.query(models.Bundle).filter(
        models.Bundle.id == bundle_id,
        models.Bundle.is_active == True
    ).first()
    
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bundle not found"
        )
    
    # Get SVG HTML
    svg_html = get_svg_html(bundle.logo_type or "silver")
    
    # Get description HTML
    description_html = ""
    if bundle.description:
        # Check if it's a predefined description
        if bundle.description in ["basic-silver", "upper-gold", "advanced-diamond"]:
            description_html = get_predefined_description(bundle.description)
        else:
            # Custom description - wrap in basic HTML
            description_html = f"<ul><li>{bundle.description}</li></ul>"
    
    return {
        "bundle_id": bundle.id,
        "name": bundle.name,
        "price_cents": bundle.price_cents,
        "currency": bundle.currency,
        "tier_level": bundle.tier_level,
        "logo_type": bundle.logo_type,
        "main_description": bundle.main_description,
        "svg_html": svg_html,
        "description_html": description_html
    }


@router.post("/create-payment-intent")
def create_payment(
    request: Request,
    payment_data: PaymentCreate,
    current_user: models.User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    
    # Find the bundle
    bundle = db.query(models.Bundle).filter(
        models.Bundle.id == payment_data.bundle_id,
        models.Bundle.is_active == True
    ).first()
    
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bundle not found"
        )
    
    # Validate months
    if payment_data.months not in [1, 6, 12]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Months must be 1, 6, or 12"
        )
    
    # Check for existing active subscription with higher tier
    active_sub = db.query(models.Subscription).filter(
        models.Subscription.user_id == current_user.id,
        models.Subscription.is_active == True,
        models.Subscription.end_date > datetime.utcnow()
    ).first()
    
    if active_sub:
        active_bundle = db.query(models.Bundle).filter(models.Bundle.id == active_sub.bundle_id).first()
        if active_bundle and active_bundle.tier_level > bundle.tier_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have an active {active_bundle.name} subscription until {active_sub.end_date.strftime('%Y-%m-%d')}. Lower tier subscriptions will start after your current subscription ends."
            )
    
    # Calculate discount using dynamic rules
    discount_percentage = 0
    discount_rules = db.query(models.DiscountRule).filter(
        models.DiscountRule.is_active == True,
        models.DiscountRule.min_months <= payment_data.months
    ).all()
    
    # Find the best matching discount rule
    best_discount = 0
    for rule in discount_rules:
        if rule.max_months is None or payment_data.months <= rule.max_months:
            if rule.discount_percentage > best_discount:
                best_discount = rule.discount_percentage
    
    discount_percentage = best_discount
    
    # Calculate price
    original_amount = bundle.price_cents * payment_data.months
    discount_amount = int(original_amount * discount_percentage / 100)
    final_amount = original_amount - discount_amount
    
    # Create Stripe PaymentIntent
    try:
        payment_intent = create_payment_intent(
            amount=final_amount,
            currency=bundle.currency,
            metadata={
                "user_id": str(current_user.id),
                "bundle_id": str(bundle.id),
                "user_email": current_user.email,
                "months": str(payment_data.months),
                "discount_percentage": str(discount_percentage)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )
    
    # Create Payment record in DB
    new_payment = models.Payment(
        user_id=current_user.id,
        bundle_id=bundle.id,
        stripe_pi_id=payment_intent.id,
        amount_cents=final_amount,
        currency=bundle.currency,
        status="pending",
        months_purchased=payment_data.months,
        discount_percentage=discount_percentage
    )
    
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return {
        "client_secret": payment_intent.client_secret,
        "payment_id": new_payment.id,
        "amount_cents": final_amount,
        "original_amount_cents": original_amount,
        "discount_percentage": discount_percentage,
        "months": payment_data.months
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header"
        )
    
    try:
        event = verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Handle payment_intent.succeeded event
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        stripe_pi_id = payment_intent["id"]
        metadata = payment_intent.get("metadata", {})
        
        # Find and update payment record
        payment = db.query(models.Payment).filter(
            models.Payment.stripe_pi_id == stripe_pi_id
        ).first()
        
        if payment:
            from datetime import datetime, timedelta
            
            payment.status = "succeeded"
            
            # Get months from payment record
            months = payment.months_purchased or 1
            days = months * 30
            
            # Check for existing active subscription with higher tier
            active_sub = db.query(models.Subscription).filter(
                models.Subscription.user_id == payment.user_id,
                models.Subscription.is_active == True,
                models.Subscription.end_date > datetime.utcnow()
            ).first()
            
            start_date = datetime.utcnow()
            
            if active_sub:
                # Check tier levels
                current_bundle = db.query(models.Bundle).filter(models.Bundle.id == active_sub.bundle_id).first()
                new_bundle = db.query(models.Bundle).filter(models.Bundle.id == payment.bundle_id).first()
                
                if current_bundle and new_bundle and current_bundle.tier_level > new_bundle.tier_level:
                    # Lower tier - start after current subscription ends
                    start_date = active_sub.end_date
                else:
                    # Same or higher tier - deactivate old subscription
                    active_sub.is_active = False
            
            end_date = start_date + timedelta(days=days)
            
            # Create or update subscription
            subscription = models.Subscription(
                user_id=payment.user_id,
                bundle_id=payment.bundle_id,
                start_date=start_date,
                end_date=end_date,
                is_active=True
            )
            db.add(subscription)
            
            # Create or update dashboard
            dashboard = db.query(models.Dashboard).filter(
                models.Dashboard.user_id == payment.user_id
            ).first()
            
            if not dashboard:
                dashboard = models.Dashboard(
                    user_id=payment.user_id,
                    looker_studio_url=f"https://lookerstudio.google.com/reporting/user-{payment.user_id}-bundle-{payment.bundle_id}"
                )
                db.add(dashboard)
            
            db.commit()
            
            return {
                "status": "success",
                "payment_id": payment.id,
                "subscription_start": start_date.isoformat(),
                "subscription_end": end_date.isoformat(),
                "dashboard_url": dashboard.looker_studio_url
            }
    
    return {"status": "received"}
