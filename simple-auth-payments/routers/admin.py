from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from routers.auth import get_current_user, require_admin, require_admin_or_accountant, require_admin_or_technical
import models
from datetime import datetime
from utils.bundle_helpers import get_logo_options, get_description_options, get_svg_html, get_predefined_description
from schemas import LeadAssignmentCreate, LeadAssignmentResponse
from utils.backup import BackupManager

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Get all users (admin or technical)"""
    users = db.query(models.User).all()
    return [{
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "role": user.role,
        "allow_access_without_subscription": user.allow_access_without_subscription
    } for user in users]


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Update user role (admin or technical)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Technical users cannot remove admin role from anyone
    if current_user.role == "technical" and user.role == "admin" and role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Technical users cannot remove admin role"
        )
    
    user.role = role
    db.commit()
    return {"message": "User role updated", "user_id": user_id, "new_role": role}


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Update user active status (admin only)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    return {"message": "User status updated", "user_id": user_id, "is_active": is_active}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Delete user (admin or technical)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted", "user_id": user_id}


@router.get("/payments")
def get_all_payments(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Get all payments (admin only)"""
    payments = db.query(models.Payment).all()
    return [{
        "id": payment.id,
        "user_id": payment.user_id,
        "user_email": payment.user.email,
        "bundle_id": payment.bundle_id,
        "bundle_name": payment.bundle.name,
        "amount_cents": payment.amount_cents,
        "currency": payment.currency,
        "status": payment.status,
        "stripe_pi_id": payment.stripe_pi_id,
        "months_purchased": payment.months_purchased,
        "discount_percentage": payment.discount_percentage,
        "created_at": payment.created_at.isoformat()
    } for payment in payments]


@router.get("/bundles")
def get_all_bundles(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Get all bundles including inactive (admin only)"""
    bundles = db.query(models.Bundle).all()
    return [{
        "id": bundle.id,
        "name": bundle.name,
        "price_cents": bundle.price_cents,
        "currency": bundle.currency,
        "is_active": bundle.is_active,
        "tier_level": bundle.tier_level,
        "logo_type": bundle.logo_type or "silver",
        "description": bundle.description,
        "main_description": bundle.main_description
    } for bundle in bundles]


@router.post("/bundles")
def create_bundle(
    name: str,
    price_cents: int,
    currency: str = "usd",
    tier_level: int = 1,
    logo_type: str = "silver",
    description: str = None,
    main_description: str = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Create new bundle (admin only)"""
    bundle = models.Bundle(
        name=name,
        price_cents=price_cents,
        currency=currency,
        tier_level=tier_level,
        logo_type=logo_type,
        description=description,
        main_description=main_description,
        is_active=True
    )
    db.add(bundle)
    db.commit()
    db.refresh(bundle)
    return bundle


@router.put("/bundles/{bundle_id}")
def update_bundle(
    bundle_id: int,
    name: str = None,
    price_cents: int = None,
    is_active: bool = None,
    tier_level: int = None,
    logo_type: str = None,
    description: str = None,
    main_description: str = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Update bundle (admin only)"""
    bundle = db.query(models.Bundle).filter(models.Bundle.id == bundle_id).first()
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")
    
    if name is not None:
        bundle.name = name
    if price_cents is not None:
        bundle.price_cents = price_cents
    if is_active is not None:
        bundle.is_active = is_active
    if tier_level is not None:
        bundle.tier_level = tier_level
    if logo_type is not None:
        bundle.logo_type = logo_type
    if description is not None:
        bundle.description = description
    if main_description is not None:
        bundle.main_description = main_description
    
    db.commit()
    db.refresh(bundle)
    return bundle


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Get system statistics (admin only)"""
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    total_payments = db.query(models.Payment).count()
    successful_payments = db.query(models.Payment).filter(models.Payment.status == "succeeded").count()
    
    total_revenue = db.query(models.Payment).filter(
        models.Payment.status == "succeeded"
    ).with_entities(models.Payment.amount_cents).all()
    
    revenue_cents = sum([p[0] for p in total_revenue]) if total_revenue else 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_payments": total_payments,
        "successful_payments": successful_payments,
        "total_revenue_cents": revenue_cents,
        "total_revenue_usd": revenue_cents / 100
    }


@router.post("/users/create")
def create_user(
    email: str,
    password: str,
    full_name: str = None,
    role: str = "user",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Create new user (admin or technical)"""
    from utils.security import hash_password
    
    # Validate role
    valid_roles = ["admin", "user", "salesman", "accountant", "technical"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Check if user exists
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create user
    new_user = models.User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=True,
        is_verified=True,
        role=role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "role": new_user.role,
        "is_active": new_user.is_active
    }


@router.put("/users/{user_id}/access-override")
def toggle_access_override(
    user_id: int,
    allow_access: bool,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Toggle admin override for user access without subscription"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.allow_access_without_subscription = allow_access
    db.commit()
    
    return {
        "message": "Access override updated",
        "user_id": user_id,
        "allow_access_without_subscription": allow_access
    }


@router.post("/dashboards")
def create_or_update_dashboard(
    user_id: int,
    looker_studio_url: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Create or update dashboard for a user (admin or technical)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    dashboard = db.query(models.Dashboard).filter(models.Dashboard.user_id == user_id).first()
    
    if dashboard:
        dashboard.looker_studio_url = looker_studio_url
        message = "Dashboard updated"
    else:
        dashboard = models.Dashboard(
            user_id=user_id,
            looker_studio_url=looker_studio_url
        )
        db.add(dashboard)
        message = "Dashboard created"
    
    db.commit()
    db.refresh(dashboard)
    
    return {
        "message": message,
        "dashboard_id": dashboard.id,
        "user_id": user_id,
        "looker_studio_url": dashboard.looker_studio_url
    }


@router.get("/dashboards")
def get_all_dashboards(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_technical)
):
    """Get all dashboards (admin or technical)"""
    dashboards = db.query(models.Dashboard).all()
    return [{
        "id": d.id,
        "user_id": d.user_id,
        "user_email": d.user.email,
        "looker_studio_url": d.looker_studio_url,
        "created_at": d.created_at.isoformat(),
        "updated_at": d.updated_at.isoformat()
    } for d in dashboards]


@router.get("/subscriptions")
def get_all_subscriptions(
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Get all subscriptions"""
    from datetime import datetime
    subscriptions = db.query(models.Subscription).all()
    return [{
        "id": sub.id,
        "user_id": sub.user_id,
        "user_email": sub.user.email,
        "bundle_id": sub.bundle_id,
        "bundle_name": sub.bundle.name,
        "start_date": sub.start_date.isoformat(),
        "end_date": sub.end_date.isoformat(),
        "is_active": sub.is_active and sub.end_date > datetime.utcnow(),
        "auto_renew": sub.auto_renew
    } for sub in subscriptions]


@router.get("/discount-rules")
def get_discount_rules(
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all discount rules (admin only)"""
    try:
        rules = db.query(models.DiscountRule).order_by(models.DiscountRule.min_months).all()
        result = []
        for rule in rules:
            result.append({
                "id": rule.id,
                "name": rule.name,
                "min_months": rule.min_months,
                "max_months": rule.max_months,
                "discount_percentage": rule.discount_percentage,
                "is_active": rule.is_active,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading discount rules: {str(e)}")


@router.post("/discount-rules")
def create_discount_rule(
    name: str,
    min_months: int,
    max_months: int = None,
    discount_percentage: int = 0,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new discount rule (admin only)"""
    # Validate input
    if min_months < 1:
        raise HTTPException(status_code=400, detail="Minimum months must be at least 1")
    if max_months and max_months <= min_months:
        raise HTTPException(status_code=400, detail="Maximum months must be greater than minimum months")
    if discount_percentage < 0 or discount_percentage > 100:
        raise HTTPException(status_code=400, detail="Discount percentage must be between 0 and 100")
    
    # Check for overlapping rules
    existing_rules = db.query(models.DiscountRule).filter(models.DiscountRule.is_active == True).all()
    for rule in existing_rules:
        rule_max = rule.max_months or 999999  # Treat None as infinity
        new_max = max_months or 999999
        
        # Check if ranges overlap
        if not (new_max < rule.min_months or min_months > rule_max):
            raise HTTPException(
                status_code=400, 
                detail=f"Discount rule overlaps with existing rule: {rule.name}"
            )
    
    rule = models.DiscountRule(
        name=name,
        min_months=min_months,
        max_months=max_months,
        discount_percentage=discount_percentage,
        is_active=True
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/discount-rules/{rule_id}")
def update_discount_rule(
    rule_id: int,
    name: str = None,
    min_months: int = None,
    max_months: int = None,
    discount_percentage: int = None,
    is_active: bool = None,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update discount rule (admin only)"""
    rule = db.query(models.DiscountRule).filter(models.DiscountRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Discount rule not found")
    
    if name is not None:
        rule.name = name
    if min_months is not None:
        if min_months < 1:
            raise HTTPException(status_code=400, detail="Minimum months must be at least 1")
        rule.min_months = min_months
    if max_months is not None:
        if max_months <= rule.min_months:
            raise HTTPException(status_code=400, detail="Maximum months must be greater than minimum months")
        rule.max_months = max_months
    if discount_percentage is not None:
        if discount_percentage < 0 or discount_percentage > 100:
            raise HTTPException(status_code=400, detail="Discount percentage must be between 0 and 100")
        rule.discount_percentage = discount_percentage
    if is_active is not None:
        rule.is_active = is_active
    
    from datetime import datetime
    rule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/discount-rules/{rule_id}")
def delete_discount_rule(
    rule_id: int,
    admin: models.User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete discount rule (admin only)"""
    rule = db.query(models.DiscountRule).filter(models.DiscountRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Discount rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Discount rule deleted", "rule_id": rule_id}


@router.get("/bundle-options")
def get_bundle_options(
    admin: models.User = Depends(require_admin)
):
    """Get available options for bundle creation/editing"""
    return {
        "logo_options": get_logo_options(),
        "description_options": get_description_options()
    }


@router.get("/bundle-preview")
def get_bundle_preview(
    logo_type: str = "silver",
    description: str = "basic-silver",
    admin: models.User = Depends(require_admin)
):
    """Preview SVG and description for bundle"""
    svg_html = get_svg_html(logo_type)
    
    # Check if description is predefined or custom
    if description in ["basic-silver", "upper-gold", "advanced-diamond"]:
        desc_html = get_predefined_description(description)
    else:
        desc_html = description  # Custom description
    
    return {
        "svg_html": svg_html,
        "description_html": desc_html
    }


# Lead Assignment Endpoints

@router.post("/leads/{lead_id}/assign", response_model=LeadAssignmentResponse)
def assign_lead_to_salesman(
    lead_id: int,
    assignment_data: LeadAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_accountant)
):
    """
    Assign a lead to a salesman (admin/accountant only).
    Creates or updates the assignment.
    """
    # Verify lead exists
    lead = db.query(models.ContactRequest).filter(models.ContactRequest.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Verify salesman exists and has salesman role
    salesman = db.query(models.User).filter(models.User.id == assignment_data.salesman_id).first()
    if not salesman:
        raise HTTPException(status_code=404, detail="Salesman not found")
    
    if salesman.role != "salesman":
        raise HTTPException(
            status_code=400, 
            detail=f"User {salesman.email} does not have salesman role"
        )
    
    # Check if assignment already exists
    existing_assignment = db.query(models.LeadAssignment).filter(
        models.LeadAssignment.contact_request_id == lead_id
    ).first()
    
    if existing_assignment:
        # Update existing assignment
        existing_assignment.salesman_id = assignment_data.salesman_id
        existing_assignment.assigned_by_id = current_user.id
        existing_assignment.updated_at = datetime.utcnow()
        assignment = existing_assignment
    else:
        # Create new assignment
        assignment = models.LeadAssignment(
            contact_request_id=lead_id,
            salesman_id=assignment_data.salesman_id,
            assigned_by_id=current_user.id,
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(assignment)
    
    try:
        db.commit()
        db.refresh(assignment)
        
        return LeadAssignmentResponse(
            id=assignment.id,
            contact_request_id=assignment.contact_request_id,
            salesman_id=assignment.salesman_id,
            salesman_email=salesman.email,
            salesman_name=salesman.full_name,
            assigned_by_id=assignment.assigned_by_id,
            assigned_at=assignment.assigned_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to assign lead"
        )


@router.delete("/leads/{lead_id}/assign")
def unassign_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_accountant)
):
    """
    Remove lead assignment (admin/accountant only).
    """
    # Verify lead exists
    lead = db.query(models.ContactRequest).filter(models.ContactRequest.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Find assignment
    assignment = db.query(models.LeadAssignment).filter(
        models.LeadAssignment.contact_request_id == lead_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Lead is not assigned")
    
    try:
        db.delete(assignment)
        db.commit()
        return {"message": "Lead unassigned successfully", "lead_id": lead_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to unassign lead"
        )


@router.get("/salesmen")
def get_salesmen(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_accountant)
):
    """
    Get list of all users with salesman role (admin/accountant only).
    Used for populating assignment dropdowns.
    """
    salesmen = db.query(models.User).filter(
        models.User.role == "salesman",
        models.User.is_active == True
    ).all()
    
    return [{
        "id": s.id,
        "email": s.email,
        "full_name": s.full_name
    } for s in salesmen]


# Database Backup Endpoints

@router.post("/backup/create")
def create_database_backup(
    current_user: models.User = Depends(require_admin_or_technical)
):
    """
    Create a new database backup (admin/technical only).
    Returns backup information.
    """
    try:
        backup_manager = BackupManager()
        result = backup_manager.create_backup()
        
        # Clean up old backups (keep last 10)
        cleanup = backup_manager.delete_old_backups(keep_count=10)
        
        return {
            "success": True,
            "backup": result,
            "cleanup": cleanup
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )


@router.get("/backup/list")
def list_database_backups(
    current_user: models.User = Depends(require_admin_or_technical)
):
    """
    List all available database backups (admin/technical only).
    """
    try:
        backup_manager = BackupManager()
        backups = backup_manager.list_backups()
        
        return {
            "success": True,
            "count": len(backups),
            "backups": backups
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list backups: {str(e)}"
        )


@router.post("/backup/restore/{backup_filename}")
def restore_database_backup(
    backup_filename: str,
    current_user: models.User = Depends(require_admin_or_technical)
):
    """
    Restore database from a specific backup (admin/technical only).
    WARNING: This will replace the current database!
    """
    try:
        backup_manager = BackupManager()
        result = backup_manager.restore_backup(backup_filename)
        
        return {
            "success": True,
            "message": "Database restored successfully. Please restart the application.",
            "details": result
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore backup: {str(e)}"
        )
