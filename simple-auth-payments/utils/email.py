"""
Email notification system for contact form submissions.

This module provides email notification functionality for new contact requests.
It's designed to be modular and can be easily enabled/disabled via configuration.

To enable email notifications:
1. Add SMTP configuration to .env file
2. Set ENABLE_EMAIL_NOTIFICATIONS=true in .env
3. Uncomment the email notification call in routers/contacts.py

Configuration required in .env:
- SMTP_HOST: SMTP server hostname (e.g., smtp.gmail.com)
- SMTP_PORT: SMTP server port (e.g., 587 for TLS)
- SMTP_USER: Email account username
- SMTP_PASSWORD: Email account password or app-specific password
- SMTP_FROM_EMAIL: Sender email address
- SMTP_FROM_NAME: Sender display name
- ADMIN_EMAILS: Comma-separated list of admin email addresses
- ADMIN_PANEL_URL: Base URL for admin panel (e.g., https://wasla.com/admin.html)
- ENABLE_EMAIL_NOTIFICATIONS: Set to "true" to enable email sending
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration loaded from environment variables."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('SMTP_FROM_NAME', 'Wasla Notifications')
        self.admin_emails = self._parse_admin_emails()
        self.admin_panel_url = os.getenv('ADMIN_PANEL_URL', 'http://localhost:8000/admin.html')
        self.enabled = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
    
    def _parse_admin_emails(self) -> List[str]:
        """Parse comma-separated admin emails from environment."""
        emails_str = os.getenv('ADMIN_EMAILS', '')
        if not emails_str:
            return []
        return [email.strip() for email in emails_str.split(',') if email.strip()]
    
    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return bool(
            self.smtp_host and
            self.smtp_user and
            self.smtp_password and
            self.admin_emails and
            self.enabled
        )


def create_contact_notification_html(contact_data: dict, contact_id: int, admin_panel_url: str) -> str:
    """
    Create HTML email template for contact form notification.
    
    Args:
        contact_data: Dictionary containing contact form data
        contact_id: Database ID of the contact request
        admin_panel_url: Base URL for admin panel
    
    Returns:
        HTML string for email body
    """
    # Format phone number
    phone = f"{contact_data.get('country_code', '')} {contact_data.get('phone', '')}"
    
    # Format submission time
    created_at = contact_data.get('created_at')
    if isinstance(created_at, datetime):
        submission_time = created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        submission_time = str(created_at)
    
    # Marketing consent display
    marketing_consent = "Yes" if contact_data.get('marketing_consent', False) else "No"
    
    # Build admin panel link
    view_link = f"{admin_panel_url}#contact-{contact_id}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 20px;
                border: 1px solid #ddd;
                border-top: none;
            }}
            .field {{
                margin-bottom: 15px;
            }}
            .field-label {{
                font-weight: bold;
                color: #555;
            }}
            .field-value {{
                margin-top: 5px;
                padding: 8px;
                background-color: white;
                border-left: 3px solid #4CAF50;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #777;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔔 New Contact Form Submission</h1>
        </div>
        
        <div class="content">
            <p>A new contact request has been submitted through the Wasla contact form.</p>
            
            <div class="field">
                <div class="field-label">Contact ID:</div>
                <div class="field-value">#{contact_id}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Name:</div>
                <div class="field-value">{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Email:</div>
                <div class="field-value">{contact_data.get('email', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Phone:</div>
                <div class="field-value">{phone}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Business Name:</div>
                <div class="field-value">{contact_data.get('business_name', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Country:</div>
                <div class="field-value">{contact_data.get('country', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Number of Locations:</div>
                <div class="field-value">{contact_data.get('num_locations', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Referral Source:</div>
                <div class="field-value">{contact_data.get('referral_source', '')}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Marketing Consent:</div>
                <div class="field-value">{marketing_consent}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Language Preference:</div>
                <div class="field-value">{contact_data.get('language_preference', 'en').upper()}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Submission Time:</div>
                <div class="field-value">{submission_time}</div>
            </div>
            
            <div style="text-align: center;">
                <a href="{view_link}" class="button">View in Admin Panel</a>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated notification from the Wasla contact form system.</p>
            <p>Please respond to the lead promptly to maintain high customer satisfaction.</p>
        </div>
    </body>
    </html>
    """
    
    return html


def create_contact_notification_text(contact_data: dict, contact_id: int, admin_panel_url: str) -> str:
    """
    Create plain text email template for contact form notification.
    
    Args:
        contact_data: Dictionary containing contact form data
        contact_id: Database ID of the contact request
        admin_panel_url: Base URL for admin panel
    
    Returns:
        Plain text string for email body
    """
    # Format phone number
    phone = f"{contact_data.get('country_code', '')} {contact_data.get('phone', '')}"
    
    # Format submission time
    created_at = contact_data.get('created_at')
    if isinstance(created_at, datetime):
        submission_time = created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
    else:
        submission_time = str(created_at)
    
    # Marketing consent display
    marketing_consent = "Yes" if contact_data.get('marketing_consent', False) else "No"
    
    # Build admin panel link
    view_link = f"{admin_panel_url}#contact-{contact_id}"
    
    text = f"""
NEW CONTACT FORM SUBMISSION
===========================

A new contact request has been submitted through the Wasla contact form.

Contact Details:
----------------
Contact ID: #{contact_id}
Name: {contact_data.get('first_name', '')} {contact_data.get('last_name', '')}
Email: {contact_data.get('email', '')}
Phone: {phone}
Business Name: {contact_data.get('business_name', '')}
Country: {contact_data.get('country', '')}
Number of Locations: {contact_data.get('num_locations', '')}
Referral Source: {contact_data.get('referral_source', '')}
Marketing Consent: {marketing_consent}
Language Preference: {contact_data.get('language_preference', 'en').upper()}
Submission Time: {submission_time}

View in Admin Panel:
{view_link}

---
This is an automated notification from the Wasla contact form system.
Please respond to the lead promptly to maintain high customer satisfaction.
    """
    
    return text.strip()


def send_contact_notification(contact_data: dict, contact_id: int) -> bool:
    """
    Send email notification for new contact form submission.
    
    This function handles all aspects of sending email notifications:
    - Checks if email is configured and enabled
    - Creates HTML and plain text email content
    - Sends to all configured admin emails
    - Handles failures gracefully (logs errors but doesn't raise exceptions)
    
    Args:
        contact_data: Dictionary containing contact form data with keys:
            - first_name, last_name, email, phone, country_code
            - country, business_name, num_locations, referral_source
            - marketing_consent, language_preference, created_at
        contact_id: Database ID of the contact request
    
    Returns:
        bool: True if email sent successfully, False otherwise
    
    Example usage in routers/contacts.py:
        from utils.email import send_contact_notification
        
        # After creating contact in database:
        send_contact_notification(
            contact_data={
                'first_name': new_contact.first_name,
                'last_name': new_contact.last_name,
                'email': new_contact.email,
                'phone': new_contact.phone,
                'country_code': new_contact.country_code,
                'country': new_contact.country,
                'business_name': new_contact.business_name,
                'num_locations': new_contact.num_locations,
                'referral_source': new_contact.referral_source,
                'marketing_consent': new_contact.marketing_consent,
                'language_preference': new_contact.language_preference,
                'created_at': new_contact.created_at
            },
            contact_id=new_contact.id
        )
    """
    # Load configuration
    config = EmailConfig()
    
    # Check if email is enabled
    if not config.enabled:
        logger.info("Email notifications are disabled. Set ENABLE_EMAIL_NOTIFICATIONS=true to enable.")
        return False
    
    # Check if email is properly configured
    if not config.is_configured():
        logger.warning(
            "Email notifications are enabled but not properly configured. "
            "Please check SMTP settings in .env file."
        )
        return False
    
    try:
        # Create email content
        subject = f"New Contact Form Submission - {contact_data.get('business_name', 'Unknown Business')}"
        html_body = create_contact_notification_html(contact_data, contact_id, config.admin_panel_url)
        text_body = create_contact_notification_text(contact_data, contact_id, config.admin_panel_url)
        
        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{config.from_name} <{config.from_email}>"
        message['To'] = ', '.join(config.admin_emails)
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        message.attach(part1)
        message.attach(part2)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(message)
        
        logger.info(
            f"Contact notification email sent successfully for contact ID {contact_id} "
            f"to {len(config.admin_emails)} recipient(s)"
        )
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {str(e)}")
        logger.error("Please check SMTP_USER and SMTP_PASSWORD in .env file")
        return False
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error while sending contact notification: {str(e)}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error sending contact notification: {str(e)}")
        return False


def test_email_configuration() -> dict:
    """
    Test email configuration without sending actual emails.
    
    Returns:
        dict: Configuration status with details
    """
    config = EmailConfig()
    
    result = {
        'enabled': config.enabled,
        'configured': config.is_configured(),
        'smtp_host': config.smtp_host or 'Not set',
        'smtp_port': config.smtp_port,
        'smtp_user': config.smtp_user or 'Not set',
        'from_email': config.from_email or 'Not set',
        'from_name': config.from_name,
        'admin_emails': config.admin_emails,
        'admin_panel_url': config.admin_panel_url,
        'missing_config': []
    }
    
    # Check for missing configuration
    if not config.smtp_host:
        result['missing_config'].append('SMTP_HOST')
    if not config.smtp_user:
        result['missing_config'].append('SMTP_USER')
    if not config.smtp_password:
        result['missing_config'].append('SMTP_PASSWORD')
    if not config.admin_emails:
        result['missing_config'].append('ADMIN_EMAILS')
    
    return result


# Example usage and testing
if __name__ == "__main__":
    # Test configuration
    print("Email Configuration Test")
    print("=" * 50)
    
    config_status = test_email_configuration()
    print(f"Enabled: {config_status['enabled']}")
    print(f"Configured: {config_status['configured']}")
    print(f"SMTP Host: {config_status['smtp_host']}")
    print(f"SMTP Port: {config_status['smtp_port']}")
    print(f"SMTP User: {config_status['smtp_user']}")
    print(f"From Email: {config_status['from_email']}")
    print(f"From Name: {config_status['from_name']}")
    print(f"Admin Emails: {', '.join(config_status['admin_emails']) if config_status['admin_emails'] else 'None'}")
    print(f"Admin Panel URL: {config_status['admin_panel_url']}")
    
    if config_status['missing_config']:
        print(f"\nMissing Configuration: {', '.join(config_status['missing_config'])}")
    
    print("\n" + "=" * 50)
    
    # Test email template generation
    print("\nGenerating sample email template...")
    sample_contact = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '123456789',
        'country_code': '+966',
        'country': 'Saudi Arabia',
        'business_name': "John's Restaurant",
        'num_locations': '2-5',
        'referral_source': 'social',
        'marketing_consent': True,
        'language_preference': 'en',
        'created_at': datetime.utcnow()
    }
    
    html = create_contact_notification_html(sample_contact, 123, 'http://localhost:8000/admin.html')
    print("HTML template generated successfully")
    
    text = create_contact_notification_text(sample_contact, 123, 'http://localhost:8000/admin.html')
    print("Text template generated successfully")
    print("\nSample text email:")
    print("-" * 50)
    print(text)
