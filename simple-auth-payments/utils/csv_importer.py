"""CSV lead import utility"""
import csv
import io
from typing import Dict, List
from sqlalchemy.orm import Session
import models


class CSVImporter:
    """Handles CSV lead import with duplicate detection"""
    
    REQUIRED_COLUMNS = ['first_name', 'last_name', 'email', 'phone', 'country_code']
    OPTIONAL_COLUMNS = ['country', 'business_name', 'num_locations', 'referral_source', 'status']
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_csv_format(self, file_content: str) -> Dict:
        """Validate CSV format and columns"""
        try:
            reader = csv.DictReader(io.StringIO(file_content))
            headers = reader.fieldnames
            
            if not headers:
                return {"valid": False, "error": "No headers found"}
            
            missing = [col for col in self.REQUIRED_COLUMNS if col not in headers]
            if missing:
                return {
                    "valid": False,
                    "error": f"Missing required columns: {', '.join(missing)}"
                }
            
            return {"valid": True, "headers": headers}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def parse_csv(self, file_content: str) -> List[Dict]:
        """Parse CSV and return list of lead dicts"""
        reader = csv.DictReader(io.StringIO(file_content))
        leads = []
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            # Validate required fields
            missing = [col for col in self.REQUIRED_COLUMNS if not row.get(col, '').strip()]
            if missing:
                errors.append({
                    "row": row_num,
                    "error": f"Missing required fields: {', '.join(missing)}"
                })
                continue
            
            # Build lead dict
            lead = {
                "first_name": row['first_name'].strip(),
                "last_name": row['last_name'].strip(),
                "email": row['email'].strip().lower(),
                "phone": row['phone'].strip(),
                "country_code": row['country_code'].strip(),
                "country": row.get('country', 'Unknown').strip(),
                "business_name": row.get('business_name', '').strip(),
                "num_locations": row.get('num_locations', '1').strip(),
                "referral_source": row.get('referral_source', 'CSV Import').strip(),
                "status": row.get('status', 'new').strip(),
                "marketing_consent": False,
                "language_preference": "en",
                "row_number": row_num
            }
            
            leads.append(lead)
        
        return {"leads": leads, "errors": errors}
    
    def detect_duplicates(self, leads: List[Dict]) -> Dict:
        """Detect duplicate leads by email or phone"""
        duplicates = []
        
        for lead in leads:
            # Check by email
            existing = self.db.query(models.ContactRequest).filter(
                models.ContactRequest.email == lead['email']
            ).first()
            
            if existing:
                duplicates.append({
                    "row": lead['row_number'],
                    "email": lead['email'],
                    "match_type": "email",
                    "existing_id": existing.id,
                    "existing_name": f"{existing.first_name} {existing.last_name}",
                    "new_name": f"{lead['first_name']} {lead['last_name']}"
                })
                continue
            
            # Check by phone + country_code
            existing = self.db.query(models.ContactRequest).filter(
                models.ContactRequest.phone == lead['phone'],
                models.ContactRequest.country_code == lead['country_code']
            ).first()
            
            if existing:
                duplicates.append({
                    "row": lead['row_number'],
                    "phone": f"{lead['country_code']} {lead['phone']}",
                    "match_type": "phone",
                    "existing_id": existing.id,
                    "existing_name": f"{existing.first_name} {existing.last_name}",
                    "new_name": f"{lead['first_name']} {lead['last_name']}"
                })
        
        return {
            "count": len(duplicates),
            "duplicates": duplicates
        }
    
    def import_leads(self, leads: List[Dict], duplicate_action: str = "skip") -> Dict:
        """Import leads with duplicate handling"""
        imported = []
        skipped = []
        failed = []
        
        for lead in leads:
            try:
                # Check for duplicate
                existing = self.db.query(models.ContactRequest).filter(
                    (models.ContactRequest.email == lead['email']) |
                    ((models.ContactRequest.phone == lead['phone']) &
                     (models.ContactRequest.country_code == lead['country_code']))
                ).first()
                
                if existing:
                    if duplicate_action == "skip":
                        skipped.append(lead['row_number'])
                        continue
                    elif duplicate_action == "overwrite":
                        # Update existing
                        existing.first_name = lead['first_name']
                        existing.last_name = lead['last_name']
                        existing.email = lead['email']
                        existing.phone = lead['phone']
                        existing.country_code = lead['country_code']
                        existing.country = lead['country']
                        existing.business_name = lead['business_name']
                        existing.num_locations = lead['num_locations']
                        existing.referral_source = lead['referral_source']
                        existing.status = lead['status']
                        self.db.commit()
                        imported.append(lead['row_number'])
                        continue
                    # else: import_all - create new even if duplicate
                
                # Create new contact
                contact = models.ContactRequest(
                    first_name=lead['first_name'],
                    last_name=lead['last_name'],
                    email=lead['email'],
                    phone=lead['phone'],
                    country_code=lead['country_code'],
                    country=lead['country'],
                    business_name=lead['business_name'],
                    num_locations=lead['num_locations'],
                    referral_source=lead['referral_source'],
                    status=lead['status'],
                    marketing_consent=lead['marketing_consent'],
                    language_preference=lead['language_preference']
                )
                
                self.db.add(contact)
                self.db.commit()
                imported.append(lead['row_number'])
                
            except Exception as e:
                self.db.rollback()
                failed.append({
                    "row": lead['row_number'],
                    "error": str(e)
                })
        
        return {
            "total_processed": len(leads),
            "imported": len(imported),
            "skipped": len(skipped),
            "failed": len(failed),
            "imported_rows": imported,
            "skipped_rows": skipped,
            "failed_rows": failed
        }
