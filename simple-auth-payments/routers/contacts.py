from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from schemas import ContactRequestCreate, ContactRequestResponse, ContactStatusUpdate, ContactNoteCreate, ContactNoteResponse
from routers.auth import get_current_user, require_lead_access, require_admin_or_accountant
import models
from datetime import datetime
from typing import List, Optional
import time
import csv
import io

# Email notification system (currently disabled)
# Uncomment the import below to enable email notifications
# from utils.email import send_contact_notification

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def require_admin(current_user: models.User = Depends(get_current_user)):
    """Dependency to check if user is admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/submit", status_code=status.HTTP_201_CREATED)
def submit_contact_form(
    request: Request,
    contact_data: ContactRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to submit contact form data.
    Rate limited to 5 requests per minute per IP (handled by middleware).
    """
    # Create ContactRequest in database
    try:
        new_contact = models.ContactRequest(
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            email=contact_data.email,
            phone=contact_data.phone,
            country_code=contact_data.country_code,
            country=contact_data.country,
            business_name=contact_data.business_name,
            num_locations=contact_data.num_locations,
            referral_source=contact_data.referral_source,
            marketing_consent=contact_data.marketing_consent,
            language_preference=contact_data.language_preference,
            status="new",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        # ========================================================================
        # EMAIL NOTIFICATION (Currently Disabled)
        # ========================================================================
        # Uncomment the code below to enable email notifications for new contacts
        # Make sure to:
        # 1. Configure SMTP settings in .env file
        # 2. Set ENABLE_EMAIL_NOTIFICATIONS=true in .env
        # 3. Uncomment the import at the top of this file
        # ========================================================================
        
        # try:
        #     # Send email notification to admins
        #     send_contact_notification(
        #         contact_data={
        #             'first_name': new_contact.first_name,
        #             'last_name': new_contact.last_name,
        #             'email': new_contact.email,
        #             'phone': new_contact.phone,
        #             'country_code': new_contact.country_code,
        #             'country': new_contact.country,
        #             'business_name': new_contact.business_name,
        #             'num_locations': new_contact.num_locations,
        #             'referral_source': new_contact.referral_source,
        #             'marketing_consent': new_contact.marketing_consent,
        #             'language_preference': new_contact.language_preference,
        #             'created_at': new_contact.created_at
        #         },
        #         contact_id=new_contact.id
        #     )
        # except Exception as email_error:
        #     # Log email error but don't fail the request
        #     # The contact is already saved in the database
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.error(f"Failed to send email notification for contact {new_contact.id}: {str(email_error)}")
        
        # ========================================================================
        
        return {
            "id": new_contact.id,
            "message": "Contact request submitted successfully",
            "created_at": new_contact.created_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit contact request"
        )


# Admin Endpoints

@router.get("/admin/contacts/export")
def export_contacts(
    status: Optional[str] = None,
    country: Optional[str] = None,
    referral_source: Optional[str] = None,
    language_preference: Optional[str] = None,
    marketing_consent: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_or_accountant)
):
    """
    Export contact requests as CSV file with multiple filters.
    Admin and accountant only endpoint.
    
    Filters:
    - status: Filter by contact status
    - country: Filter by country
    - referral_source: Filter by referral source
    - language_preference: Filter by language (en/ar)
    - marketing_consent: Filter by marketing consent (true/false)
    - start_date: Filter by created date (YYYY-MM-DD) - from this date
    - end_date: Filter by created date (YYYY-MM-DD) - to this date
    """
    # Build query
    query = db.query(models.ContactRequest)
    
    # Apply filters
    if status:
        query = query.filter(models.ContactRequest.status == status)
    
    if country:
        query = query.filter(models.ContactRequest.country == country)
    
    if referral_source:
        query = query.filter(models.ContactRequest.referral_source == referral_source)
    
    if language_preference:
        query = query.filter(models.ContactRequest.language_preference == language_preference)
    
    if marketing_consent is not None:
        query = query.filter(models.ContactRequest.marketing_consent == marketing_consent)
    
    # Date range filters
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(models.ContactRequest.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )
    
    if end_date:
        try:
            # Add one day to include the entire end date
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(models.ContactRequest.created_at <= end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )
    
    # Order by created_at descending (newest first)
    query = query.order_by(models.ContactRequest.created_at.desc())
    
    # Get all contacts
    contacts = query.all()
    
    # Create CSV in memory with UTF-8 BOM for Excel compatibility
    output = io.StringIO()
    
    # Write UTF-8 BOM (Byte Order Mark) for Excel to recognize UTF-8 encoding
    # This fixes Arabic text corruption in Excel
    output.write('\ufeff')
    
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID',
        'First Name',
        'Last Name',
        'Email',
        'Phone',
        'Country',
        'Business Name',
        'Locations',
        'Referral Source',
        'Marketing Consent',
        'Language',
        'Status',
        'Created At',
        'Updated At'
    ])
    
    # Write data rows
    for contact in contacts:
        # Format dates in readable format (YYYY-MM-DD HH:MM:SS)
        created_at_formatted = contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        updated_at_formatted = contact.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Phone number is stored separately from country code
        phone_formatted = f"{contact.country_code} {contact.phone}"
        
        # Format marketing consent as Yes/No
        marketing_consent_formatted = "Yes" if contact.marketing_consent else "No"
        
        writer.writerow([
            contact.id,
            contact.first_name,
            contact.last_name,
            contact.email,
            phone_formatted,
            contact.country,
            contact.business_name,
            contact.num_locations,
            contact.referral_source,
            marketing_consent_formatted,
            contact.language_preference,
            contact.status,
            created_at_formatted,
            updated_at_formatted
        ])
    
    # Prepare CSV for download
    output.seek(0)
    
    # Generate filename with timestamp and filter info
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filter_suffix = ""
    if status:
        filter_suffix += f"_{status}"
    if start_date or end_date:
        filter_suffix += "_filtered"
    
    filename = f"contact_requests{filter_suffix}_{timestamp}.csv"
    
    # Return as streaming response with proper headers
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/admin/contacts", response_model=List[ContactRequestResponse])
def get_all_contacts(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_lead_access)
):
    """
    Get contact requests with pagination and filtering.
    Role-based access:
    - Admin/Accountant: See all leads
    - Salesman: See only assigned leads
    - Technical: 403 Forbidden
    """
    # Technical users should not access this endpoint
    if current_user.role == "technical":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Technical users cannot access leads"
        )
    
    query = db.query(models.ContactRequest)
    
    # Filter based on role
    if current_user.role == "salesman":
        # Salesman: only see assigned leads
        assigned_lead_ids = db.query(models.LeadAssignment.contact_request_id).filter(
            models.LeadAssignment.salesman_id == current_user.id
        ).subquery()
        query = query.filter(models.ContactRequest.id.in_(assigned_lead_ids))
    # Admin and accountant see all leads (no additional filter)
    
    # Apply status filter if provided
    if status:
        query = query.filter(models.ContactRequest.status == status)
    
    # Order by created_at descending (newest first)
    query = query.order_by(models.ContactRequest.created_at.desc())
    
    # Apply pagination
    contacts = query.offset(offset).limit(limit).all()
    
    # Build response with notes count and assignment info
    result = []
    for contact in contacts:
        # Get assignment info
        assignment = db.query(models.LeadAssignment).filter(
            models.LeadAssignment.contact_request_id == contact.id
        ).first()
        
        contact_dict = {
            "id": contact.id,
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "country_code": contact.country_code,
            "country": contact.country,
            "business_name": contact.business_name,
            "num_locations": contact.num_locations,
            "referral_source": contact.referral_source,
            "marketing_consent": contact.marketing_consent,
            "language_preference": contact.language_preference,
            "status": contact.status,
            "created_at": contact.created_at,
            "updated_at": contact.updated_at,
            "notes_count": len(contact.notes)
        }
        
        # Add assignment info if exists
        if assignment:
            contact_dict["assigned_to"] = {
                "id": assignment.salesman_id,
                "email": assignment.salesman.email,
                "full_name": assignment.salesman.full_name
            }
        else:
            contact_dict["assigned_to"] = None
        
        result.append(contact_dict)
    
    return result


@router.get("/admin/contacts/{contact_id}")
def get_contact_detail(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_lead_access)
):
    """
    Get detailed contact request with notes.
    Role-based access:
    - Admin/Accountant: Can access any lead
    - Salesman: Can only access assigned leads
    """
    contact = db.query(models.ContactRequest).filter(
        models.ContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found"
        )
    
    # Check if salesman is trying to access unassigned lead
    if current_user.role == "salesman":
        assignment = db.query(models.LeadAssignment).filter(
            models.LeadAssignment.contact_request_id == contact_id,
            models.LeadAssignment.salesman_id == current_user.id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access leads assigned to you"
            )
    
    # Build notes list
    notes = []
    for note in contact.notes:
        notes.append({
            "id": note.id,
            "note_text": note.note_text,
            "admin_email": note.admin.email,
            "created_at": note.created_at.isoformat()
        })
    
    # Sort notes chronologically (oldest first)
    notes.sort(key=lambda x: x["created_at"])
    
    return {
        "id": contact.id,
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "email": contact.email,
        "phone": contact.phone,
        "country_code": contact.country_code,
        "country": contact.country,
        "business_name": contact.business_name,
        "num_locations": contact.num_locations,
        "referral_source": contact.referral_source,
        "marketing_consent": contact.marketing_consent,
        "language_preference": contact.language_preference,
        "status": contact.status,
        "created_at": contact.created_at.isoformat(),
        "updated_at": contact.updated_at.isoformat(),
        "notes": notes
    }


@router.put("/admin/contacts/{contact_id}/status")
def update_contact_status(
    contact_id: int,
    status_update: ContactStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_lead_access)
):
    """
    Update contact request status.
    Role-based access:
    - Admin/Accountant: Can update any lead
    - Salesman: Can only update assigned leads
    """
    contact = db.query(models.ContactRequest).filter(
        models.ContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found"
        )
    
    # Check if salesman is trying to update unassigned lead
    if current_user.role == "salesman":
        assignment = db.query(models.LeadAssignment).filter(
            models.LeadAssignment.contact_request_id == contact_id,
            models.LeadAssignment.salesman_id == current_user.id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update leads assigned to you"
            )
    
    # Update status
    contact.status = status_update.status
    contact.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(contact)
        
        return {
            "id": contact.id,
            "status": contact.status,
            "updated_at": contact.updated_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact status"
        )


@router.post("/admin/contacts/{contact_id}/notes", response_model=ContactNoteResponse, status_code=status.HTTP_201_CREATED)
def add_contact_note(
    contact_id: int,
    note_data: ContactNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_lead_access)
):
    """
    Add note to contact request.
    Role-based access:
    - Admin/Accountant: Can add notes to any lead
    - Salesman: Can only add notes to assigned leads
    """
    # Check if contact exists
    contact = db.query(models.ContactRequest).filter(
        models.ContactRequest.id == contact_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found"
        )
    
    # Check if salesman is trying to add note to unassigned lead
    if current_user.role == "salesman":
        assignment = db.query(models.LeadAssignment).filter(
            models.LeadAssignment.contact_request_id == contact_id,
            models.LeadAssignment.salesman_id == current_user.id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add notes to leads assigned to you"
            )
    
    # Create note
    new_note = models.ContactNote(
        contact_request_id=contact_id,
        admin_id=current_user.id,
        note_text=note_data.note_text,
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        
        return {
            "id": new_note.id,
            "contact_request_id": new_note.contact_request_id,
            "note_text": new_note.note_text,
            "admin_email": current_user.email,
            "created_at": new_note.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add note"
        )
