# Implementation Steps - Backup Upload & CSV Import

## Overview
This document provides the exact step-by-step implementation order for both features.

---

## PHASE 1: Database Backup Upload System

### Step 1: Create Backup Validator Utility
**File:** `utils/backup_validator.py`

**Purpose:** Validate uploaded backup files for compatibility

**Functions to implement:**
1. `validate_file_format(file_path)` - Check if file is SQLite database
2. `get_backup_tables(file_path)` - List all tables in backup
3. `validate_schema(file_path)` - Check if required tables exist
4. `check_table_structure(file_path, table_name)` - Verify column structure
5. `get_backup_info(file_path)` - Get metadata (size, tables, row counts)

**Required tables to check:**
- users
- bundles
- contact_requests
- lead_assignments
- payments
- subscriptions

**Validation checks:**
- File is valid SQLite database
- All required tables exist
- Table structures match current schema
- No corrupted data

---

### Step 2: Add Backup Upload Endpoint
**File:** `routers/admin.py`

**Endpoint:** `POST /admin/backups/upload`

**Requirements:**
- Accept multipart/form-data file upload
- Validate file type (.db only)
- Check file size (max 50MB)
- Validate backup using BackupValidator
- Save to backups/ folder with custom name
- Return validation results

**Authorization:**
- Admin role only
- Rate limit: 5 uploads per hour

---

### Step 3: Add Backup List Endpoint
**File:** `routers/admin.py`

**Endpoint:** `GET /admin/backups/list`

**Requirements:**
- List all backups (automatic + uploaded)
- Include metadata for each backup
- Mark uploaded backups differently
- Show validation status

---

### Step 4: Add Backup Restore Endpoint
**File:** `routers/admin.py`

**Endpoint:** `POST /admin/backups/restore/{backup_name}`

**Requirements:**
- Validate backup before restore
- Create safety backup of current database
- Restore from specified backup
- Return success/failure status

**Safety measures:**
- Confirm backup is valid
- Create pre-restore backup
- Use transaction for restore
- Rollback on error

---

### Step 5: Frontend - Backup Management UI
**File:** `static/admin.html`

**Add new section:** "Backup Management"

**Components:**
1. **Upload Section**
   - File input (accept=".db")
   - Custom name input
   - Upload button
   - Progress indicator

2. **Backup List**
   - Table showing all backups
   - Columns: Name, Type, Size, Date, Status, Actions
   - Actions: Validate, Restore, Delete

3. **Validation Modal**
   - Show validation results
   - Display warnings/errors
   - Compatibility status

4. **Restore Confirmation Modal**
   - Warning message
   - Backup details
   - Confirm/Cancel buttons

**JavaScript functions:**
- `uploadBackup()`
- `listBackups()`
- `validateBackup(backupName)`
- `restoreBackup(backupName)`
- `deleteBackup(backupName)`

---

## PHASE 2: CSV Lead Import System

### Step 6: Create CSV Importer Utility
**File:** `utils/csv_importer.py`

**Purpose:** Handle CSV parsing, validation, and import

**Classes:**
```python
class CSVImporter:
    def __init__(self, db_session):
        self.db = db_session
    
    def validate_csv_format(file) -> dict
    def parse_csv(file) -> list[dict]
    def detect_duplicates(leads) -> dict
    def import_leads(leads, duplicate_action) -> dict
    def generate_report(results) -> dict
```

**CSV Format:**
```csv
first_name,last_name,email,phone,country_code,country,business_name,num_locations,referral_source,status
```

**Required columns:**
- first_name
- last_name
- email
- phone
- country_code

**Optional columns:**
- country (default: "Unknown")
- business_name (default: "")
- num_locations (default: "1")
- referral_source (default: "CSV Import")
- status (default: "new")
- marketing_consent (default: false)
- language_preference (default: "en")

**Duplicate detection:**
- By email (exact match, case-insensitive)
- By phone + country_code (exact match)
- Return list of duplicates with existing record info

---

### Step 7: Add Import Validation Endpoint
**File:** `routers/admin.py`

**Endpoint:** `POST /admin/leads/import/validate`

**Requirements:**
- Accept CSV file upload
- Parse and validate CSV
- Detect duplicates
- Return preview with duplicate info
- Store temp file for later import

**Response includes:**
- Total rows
- Valid rows
- Invalid rows (with errors)
- Duplicate count and details
- Preview of first 10 rows

---

### Step 8: Add Import Execution Endpoint
**File:** `routers/admin.py`

**Endpoint:** `POST /admin/leads/import/execute`

**Requirements:**
- Accept duplicate action choice
- Import leads based on action
- Handle errors gracefully
- Return detailed results

**Duplicate actions:**
- `skip` - Skip duplicate rows
- `overwrite` - Update existing records
- `import_all` - Import as new (allow duplicates)

**Transaction safety:**
- Use database transaction
- Rollback on critical errors
- Continue on row-level errors

---

### Step 9: Add CSV Template Endpoint
**File:** `routers/admin.py`

**Endpoint:** `GET /admin/leads/import/template`

**Requirements:**
- Generate CSV template with headers
- Include example row
- Return as downloadable file

---

### Step 10: Frontend - CSV Import UI
**File:** `static/admin.html`

**Add new section:** "Import Leads"

**Multi-step wizard:**

**Step 1: Upload CSV**
- File input (accept=".csv")
- Drag & drop support
- Template download link
- Upload button

**Step 2: Validation Results**
- Show total rows
- Show validation errors
- Display duplicate count
- Preview first 10 rows
- Continue/Cancel buttons

**Step 3: Duplicate Resolution** (if duplicates found)
- Show duplicate count
- Display duplicate records in table
- Radio buttons for action:
  - ○ Skip duplicates (keep existing)
  - ○ Overwrite existing data
  - ○ Import all as new
- Import button

**Step 4: Import Progress**
- Progress bar
- Status messages
- Cancel button

**Step 5: Results Summary**
- Total processed
- Successfully imported
- Skipped (duplicates)
- Failed (errors)
- Download detailed report button
- Close button

**JavaScript functions:**
- `uploadCSV()`
- `validateCSV(file)`
- `showValidationResults(results)`
- `showDuplicateResolution(duplicates)`
- `executeImport(action)`
- `showImportResults(results)`
- `downloadTemplate()`

---

## PHASE 3: Database Schema Updates

### Step 11: Create Import Logs Table
**File:** `models.py`

**Add new model:**
```python
class ImportLog(Base):
    __tablename__ = "import_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    import_type = Column(String(50), nullable=False)  # 'csv_leads', 'backup'
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer)
    successful_rows = Column(Integer)
    failed_rows = Column(Integer)
    skipped_rows = Column(Integer)
    duplicate_action = Column(String(50))
    status = Column(String(50), nullable=False)  # 'pending', 'completed', 'failed'
    error_message = Column(String(2000))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    admin = relationship("User")
```

**Migration script:** `migrate_import_logs.py`

---

## PHASE 4: Testing

### Step 12: Unit Tests

**Test file:** `test_backup_upload.py`
- Test backup validation
- Test file format validation
- Test schema compatibility
- Test upload endpoint
- Test restore endpoint

**Test file:** `test_csv_import.py`
- Test CSV parsing
- Test duplicate detection
- Test import with skip action
- Test import with overwrite action
- Test import with errors
- Test validation endpoint
- Test execution endpoint

---

### Step 13: Integration Tests

**Test file:** `test_backup_csv_integration.py`
- Test complete backup upload flow
- Test complete CSV import flow
- Test authorization
- Test rate limiting
- Test error handling

---

### Step 14: Frontend Tests

**Test file:** `test_backup_csv_ui.html`
- Test backup upload UI
- Test CSV import wizard
- Test duplicate resolution
- Test error displays
- Test success messages

---

## PHASE 5: Documentation & Deployment

### Step 15: User Documentation

**File:** `BACKUP_UPLOAD_GUIDE.md`
- How to upload backups
- How to validate backups
- How to restore backups
- Troubleshooting

**File:** `CSV_IMPORT_GUIDE.md`
- CSV format requirements
- How to prepare CSV file
- How to import leads
- Duplicate handling
- Troubleshooting

---

### Step 16: I18n Support

**Files:** `static/i18n/en.json`, `static/i18n/ar.json`

**Add translations for:**
- Backup upload UI
- CSV import wizard
- Error messages
- Success messages
- Validation messages

---

### Step 17: Final Integration

**Update:** `static/admin.html`
- Add navigation tabs
- Integrate both features
- Ensure consistent styling
- Add help tooltips

---

## Implementation Order Summary

1. ✅ Create `utils/backup_validator.py`
2. ✅ Add backup upload endpoint
3. ✅ Add backup list endpoint
4. ✅ Add backup restore endpoint
5. ✅ Create backup management UI
6. ✅ Create `utils/csv_importer.py`
7. ✅ Add CSV validation endpoint
8. ✅ Add CSV execution endpoint
9. ✅ Add CSV template endpoint
10. ✅ Create CSV import wizard UI
11. ✅ Add ImportLog model and migration
12. ✅ Write unit tests
13. ✅ Write integration tests
14. ✅ Write frontend tests
15. ✅ Create user documentation
16. ✅ Add i18n translations
17. ✅ Final integration and polish

---

## Estimated Timeline

- **Phase 1** (Backup Upload): 6-8 hours
- **Phase 2** (CSV Import): 8-10 hours
- **Phase 3** (Database): 1-2 hours
- **Phase 4** (Testing): 4-6 hours
- **Phase 5** (Documentation): 2-3 hours

**Total:** 21-29 hours

---

## Ready to Start?

Review this plan and let me know:
1. Should we start with Phase 1 (Backup Upload) or Phase 2 (CSV Import)?
2. Any changes to the requirements?
3. Any additional features needed?

Once confirmed, I'll begin implementation step by step!
