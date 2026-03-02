# Backup & CSV Import Implementation Plan

## Overview

This document outlines the implementation plan for two major features:
1. **Backup Upload System** - Upload and validate database backups from local machine
2. **CSV Lead Import** - Import leads from CSV with duplicate detection and resolution

---

## Feature 1: Backup Upload System

### Requirements

#### User Story
As an admin, I want to upload a database backup from my local machine to the production server, so that I can restore data without direct server access.

#### Acceptance Criteria
1. Admin can upload a .db file through the admin panel
2. System validates the backup file structure and tables
3. System checks if backup is compatible with current schema
4. Admin can name/rename the uploaded backup
5. Uploaded backup appears in the backup list
6. Admin can restore from uploaded backup
7. System provides clear error messages for invalid backups

### Technical Design

#### Backend Components

**1. Backup Validation Utility (`utils/backup_validator.py`)**
```python
class BackupValidator:
    - validate_file_format(file) -> bool
    - validate_schema(backup_path) -> dict
    - check_table_compatibility(backup_path) -> dict
    - get_backup_info(backup_path) -> dict
```

**2. Admin API Endpoints (`routers/admin.py`)**
```python
POST /admin/backups/upload
    - Accept file upload
    - Validate file
    - Save with custom name
    - Return validation results

GET /admin/backups/list
    - List all backups (existing + uploaded)
    - Show backup metadata

POST /admin/backups/restore/{backup_name}
    - Restore from specific backup
    - Create safety backup first

GET /admin/backups/validate/{backup_name}
    - Validate specific backup
    - Return compatibility report
```

**3. Schema Validation**
- Check for required tables: users, bundles, contacts, lead_assignments
- Verify column structure matches current models
- Check for foreign key relationships
- Validate data types

#### Frontend Components

**Admin Panel UI (`static/admin.html`)**
- New "Backup Management" section
- File upload interface
- Backup list with actions (validate, restore, delete)
- Validation results display
- Restore confirmation modal

#### Security Considerations
- Only admin role can upload/restore backups
- File size limit (e.g., 50MB)
- File type validation (.db only)
- SQL injection prevention
- Rate limiting on upload endpoint

---

## Feature 2: CSV Lead Import

### Requirements

#### User Story
As an admin, I want to import leads from a CSV file, so that I can bulk-add contacts from external sources.

#### Acceptance Criteria
1. Admin can upload CSV file with lead data
2. System validates CSV format and required columns
3. System detects duplicate leads (by email or phone)
4. Admin sees preview of duplicates before import
5. Admin can choose to skip or overwrite duplicates
6. System imports valid leads and reports results
7. System provides detailed import summary

### Technical Design

#### CSV Format

**Required Columns:**
- name (or first_name + last_name)
- email
- phone
- country_code

**Optional Columns:**
- company
- message
- status
- assigned_to (user email or ID)

**Example CSV:**
```csv
name,email,phone,country_code,company,message
John Doe,john@example.com,1234567890,+1,Acme Corp,Interested in Pro Bundle
Jane Smith,jane@example.com,9876543210,+1,Tech Inc,Need pricing info
```

#### Backend Components

**1. CSV Import Utility (`utils/csv_importer.py`)**
```python
class CSVImporter:
    - validate_csv_format(file) -> dict
    - parse_csv(file) -> list[dict]
    - detect_duplicates(leads, strategy) -> dict
    - import_leads(leads, duplicate_action) -> dict
    - generate_import_report(results) -> dict
```

**2. Duplicate Detection Strategies**
- By email (exact match)
- By phone + country_code (exact match)
- By email OR phone (either matches)

**3. Duplicate Resolution Options**
- Skip duplicates (keep existing)
- Overwrite duplicates (update existing)
- Import as new (allow duplicates)
- Review individually (show modal for each)

**4. Admin API Endpoints (`routers/admin.py`)**
```python
POST /admin/leads/import/validate
    - Upload CSV
    - Validate format
    - Detect duplicates
    - Return preview with duplicate info

POST /admin/leads/import/execute
    - Import leads with chosen duplicate action
    - Return detailed results

GET /admin/leads/import/template
    - Download CSV template
```

#### Frontend Components

**Admin Panel UI (`static/admin.html`)**

**Step 1: Upload CSV**
- File upload interface
- Drag & drop support
- Template download link

**Step 2: Validation & Preview**
- Show total rows found
- Display validation errors
- Show duplicate detection results
- Preview first 10 rows

**Step 3: Duplicate Resolution**
- If duplicates found:
  - Show duplicate count
  - Display duplicate records
  - Radio buttons for action:
    - ○ Skip duplicates (recommended)
    - ○ Overwrite existing data
    - ○ Import as new entries
  - Checkbox: "Review each duplicate individually"

**Step 4: Import Execution**
- Progress indicator
- Real-time import status
- Final results summary

**Step 5: Results Summary**
- Total rows processed
- Successfully imported
- Skipped (duplicates)
- Failed (errors)
- Download detailed report

#### Security Considerations
- Only admin role can import leads
- File size limit (e.g., 10MB, ~50,000 rows)
- CSV injection prevention
- Rate limiting on import endpoint
- Validate all data before import
- Transaction rollback on errors

---

## Implementation Steps

### Phase 1: Backup Upload System

**Step 1: Backend - Validation Utility**
- [ ] Create `utils/backup_validator.py`
- [ ] Implement file format validation
- [ ] Implement schema validation
- [ ] Implement table compatibility check
- [ ] Add unit tests

**Step 2: Backend - API Endpoints**
- [ ] Add backup upload endpoint
- [ ] Add backup list endpoint
- [ ] Add backup restore endpoint
- [ ] Add backup validation endpoint
- [ ] Add authorization checks
- [ ] Add rate limiting

**Step 3: Frontend - UI Components**
- [ ] Add "Backup Management" section to admin panel
- [ ] Create file upload interface
- [ ] Create backup list display
- [ ] Create validation results modal
- [ ] Create restore confirmation modal
- [ ] Add error handling and user feedback

**Step 4: Testing**
- [ ] Test with valid backup files
- [ ] Test with invalid backup files
- [ ] Test with incompatible schema
- [ ] Test restore functionality
- [ ] Test authorization
- [ ] Test file size limits

### Phase 2: CSV Lead Import

**Step 1: Backend - CSV Import Utility**
- [ ] Create `utils/csv_importer.py`
- [ ] Implement CSV format validation
- [ ] Implement CSV parsing
- [ ] Implement duplicate detection
- [ ] Implement import logic
- [ ] Add unit tests

**Step 2: Backend - API Endpoints**
- [ ] Add CSV validation endpoint
- [ ] Add CSV import execution endpoint
- [ ] Add template download endpoint
- [ ] Add authorization checks
- [ ] Add rate limiting

**Step 3: Frontend - Multi-Step UI**
- [ ] Create CSV upload interface
- [ ] Create validation preview display
- [ ] Create duplicate resolution interface
- [ ] Create import progress indicator
- [ ] Create results summary display
- [ ] Add CSV template download

**Step 4: Testing**
- [ ] Test with valid CSV files
- [ ] Test with invalid CSV files
- [ ] Test duplicate detection
- [ ] Test all duplicate resolution options
- [ ] Test large file imports
- [ ] Test error handling

### Phase 3: Integration & Documentation

**Step 1: Integration**
- [ ] Integrate both features into admin panel
- [ ] Add navigation/tabs for features
- [ ] Ensure consistent UI/UX
- [ ] Add i18n support (English/Arabic)

**Step 2: Documentation**
- [ ] Create user guide for backup upload
- [ ] Create user guide for CSV import
- [ ] Document CSV format requirements
- [ ] Create troubleshooting guide

**Step 3: Final Testing**
- [ ] End-to-end testing
- [ ] Security testing
- [ ] Performance testing
- [ ] User acceptance testing

---

## Database Schema Changes

### New Table: `import_logs`
```sql
CREATE TABLE import_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    import_type VARCHAR(50) NOT NULL,  -- 'csv_leads', 'backup'
    filename VARCHAR(255) NOT NULL,
    total_rows INTEGER,
    successful_rows INTEGER,
    failed_rows INTEGER,
    skipped_rows INTEGER,
    duplicate_action VARCHAR(50),
    status VARCHAR(50) NOT NULL,  -- 'pending', 'completed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id)
);
```

---

## API Specifications

### Backup Upload Endpoints

#### POST /admin/backups/upload
**Request:**
```
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <backup.db>
name: "production_backup_2026"
```

**Response:**
```json
{
  "success": true,
  "backup_name": "production_backup_2026.db",
  "validation": {
    "valid": true,
    "tables_found": ["users", "bundles", "contacts", "lead_assignments"],
    "compatible": true,
    "warnings": []
  },
  "size_bytes": 1048576,
  "uploaded_at": "2026-02-25T10:30:00Z"
}
```

#### GET /admin/backups/list
**Response:**
```json
{
  "backups": [
    {
      "filename": "backup_20260225_103000.db",
      "type": "automatic",
      "size_bytes": 1048576,
      "date": "2026-02-25 10:30:00",
      "validated": true,
      "compatible": true
    },
    {
      "filename": "production_backup_2026.db",
      "type": "uploaded",
      "size_bytes": 2097152,
      "date": "2026-02-25 11:00:00",
      "validated": true,
      "compatible": true
    }
  ]
}
```

### CSV Import Endpoints

#### POST /admin/leads/import/validate
**Request:**
```
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <leads.csv>
```

**Response:**
```json
{
  "success": true,
  "total_rows": 150,
  "valid_rows": 145,
  "invalid_rows": 5,
  "duplicates": {
    "count": 12,
    "by_email": 8,
    "by_phone": 4,
    "records": [
      {
        "row": 5,
        "email": "john@example.com",
        "existing_id": 123,
        "existing_name": "John Doe",
        "new_name": "John D."
      }
    ]
  },
  "errors": [
    {
      "row": 10,
      "field": "email",
      "error": "Invalid email format"
    }
  ],
  "preview": [
    {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "1234567890",
      "country_code": "+1"
    }
  ]
}
```

#### POST /admin/leads/import/execute
**Request:**
```json
{
  "file_hash": "abc123...",
  "duplicate_action": "skip",
  "import_invalid": false
}
```

**Response:**
```json
{
  "success": true,
  "import_id": 456,
  "results": {
    "total_processed": 150,
    "imported": 133,
    "skipped": 12,
    "failed": 5
  },
  "details": {
    "imported_ids": [201, 202, 203, ...],
    "skipped_emails": ["john@example.com", ...],
    "failed_rows": [
      {
        "row": 10,
        "error": "Invalid email format"
      }
    ]
  }
}
```

---

## Security Checklist

- [ ] Admin-only access (role check)
- [ ] File type validation
- [ ] File size limits
- [ ] SQL injection prevention
- [ ] CSV injection prevention
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] Transaction safety
- [ ] Error message sanitization
- [ ] Audit logging

---

## UI/UX Considerations

### Backup Upload
- Clear instructions
- Drag & drop support
- Progress indicator
- Validation feedback
- Confirmation dialogs
- Error messages in plain language

### CSV Import
- Step-by-step wizard
- Template download
- Format examples
- Duplicate preview
- Bulk action options
- Detailed results
- Export error report

---

## Next Steps

1. **Review this plan** - Confirm requirements and approach
2. **Prioritize features** - Which to implement first?
3. **Start implementation** - Begin with Phase 1 or Phase 2?
4. **Iterative development** - Build, test, refine

---

## Questions to Resolve

1. Should backup upload replace existing backup or keep both?
2. Maximum file sizes for backups and CSV?
3. Should we support other formats (Excel, JSON)?
4. Should duplicate detection be case-sensitive?
5. Should we auto-assign imported leads to salesmen?
6. Should we send email notifications after import?
7. Should we keep import history/logs?

---

## Estimated Effort

- **Backup Upload System**: 8-12 hours
- **CSV Lead Import**: 12-16 hours
- **Testing & Documentation**: 4-6 hours
- **Total**: 24-34 hours

---

This plan provides a solid foundation. Ready to proceed with implementation?
