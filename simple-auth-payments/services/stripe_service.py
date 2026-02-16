import stripe
from config import settings
from typing import Dict

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(amount: int, currency: str, metadata: Dict[str, str]):
    """
    Create a Stripe PaymentIntent
    
    Args:
        amount: Amount in cents
        currency: Currency code (e.g., 'usd')
        metadata: Additional metadata to attach to the payment intent
    
    Returns:
        Stripe PaymentIntent object
    """
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        metadata=metadata,
        automatic_payment_methods={"enabled": True}
    )
    return payment_intent


def verify_webhook_signature(payload: bytes, sig_header: str):
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Raw request body
        sig_header: Stripe signature header
    
    Returns:
        Verified event object
    
    Raises:
        ValueError: Invalid payload
        stripe.error.SignatureVerificationError: Invalid signature
    """
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    return event
