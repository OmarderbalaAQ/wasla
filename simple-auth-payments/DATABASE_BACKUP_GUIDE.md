# Database Backup & Recovery Guide

## Quick Commands

### Create Backup
```bash
python backup_database.py
```

### Restore Database (Interactive)
```bash
python restore_database.py
```

### Restore Latest Backup
```bash
python restore_database.py --latest
```

## What These Scripts Do

### backup_database.py
- Creates a timestamped backup of `dev.db`
- Saves to `backups/` directory
- Shows backup size and location
- Keeps all backups (you can manually delete old ones)

### restore_database.py
- Lists all available backups
- Lets you choose which backup to restore
- Backs up current database before restoring (as `dev.db.before_restore`)
- Restores selected backup to `dev.db`

## Usage Examples

### Example 1: Regular Backup Before Testing
```bash
# Before running tests
python backup_database.py

# Run your tests
pytest test_contact_security_cors.py

# If something goes wrong, restore
python restore_database.py --latest
```

### Example 2: Manual Backup Before Changes
```bash
# Before making database changes
python backup_database.py

# Make your changes...

# If you need to rollback
python restore_database.py
```

### Example 3: Scheduled Backups
Create a batch file `daily_backup.bat`:
```batch
@echo off
python backup_database.py
echo Backup complete at %date% %time%
```

Run it daily or before important work.

## Backup Storage

Backups are stored in: `backups/`

Filename format: `dev_backup_YYYYMMDD_HHMMSS.db`

Example: `dev_backup_20260206_194850.db`

## Current Backup

✅ **First backup created:**
- File: `backups/dev_backup_20260206_194850.db`
- Size: 120 KB
- Contains: 4 users (admin, client, user, override)
- Date: 2026-02-06 19:48:50

## Safety Features

1. **Before Restore**: Current database is backed up as `dev.db.before_restore`
2. **Confirmation**: Restore requires explicit confirmation
3. **No Overwrite**: Backups are never overwritten (timestamped)
4. **List View**: See all backups before choosing

## Restore Process

When you run `python restore_database.py`:

```
1. Shows list of available backups
2. You choose which one to restore
3. Confirms your choice
4. Backs up current database
5. Restores selected backup
6. Reminds you to restart server
```

## Best Practices

### When to Backup

✅ **Before running tests** that modify database
✅ **Before migrations** or schema changes
✅ **Before major updates** to the application
✅ **Daily** if actively developing
✅ **Before deploying** to production

### Managing Backups

- Keep at least 3-5 recent backups
- Delete very old backups to save space
- Name important backups (rename file with description)
- Store critical backups outside project folder

### Example Backup Naming

You can rename backups for clarity:
```
dev_backup_20260206_194850.db  →  dev_backup_before_contact_tests.db
dev_backup_20260206_120000.db  →  dev_backup_working_state.db
```

## Recovery Scenarios

### Scenario 1: Tests Cleared Database
```bash
# Restore latest backup
python restore_database.py --latest

# Restart server
# (Server auto-reloads, but restart ensures clean state)
```

### Scenario 2: Migration Failed
```bash
# Restore backup from before migration
python restore_database.py
# Choose the backup from before migration
```

### Scenario 3: Accidental Data Deletion
```bash
# Restore most recent backup
python restore_database.py --latest
```

## Integration with Tests

To prevent tests from clearing your database, modify test files:

### Option 1: Use Separate Test Database
```python
# At top of test file
import os
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
```

### Option 2: Comment Out Drop Statement
```python
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Base.metadata.drop_all(bind=engine)  # ← Comment this out
```

### Option 3: Backup Before Tests
```bash
# Create backup script for tests
python backup_database.py && pytest test_file.py
```

## Troubleshooting

### "No backups found"
- Run `python backup_database.py` first
- Check if `backups/` directory exists

### "Database locked"
- Stop the server before restoring
- Close any database browser tools

### "Permission denied"
- Close any programs using dev.db
- Run command prompt as administrator (if needed)

## Files Created

- `backup_database.py` - Creates backups
- `restore_database.py` - Restores backups
- `backups/` - Directory containing all backups
- `dev.db.before_restore` - Safety backup before restore

## Quick Recovery After Test Damage

If tests cleared your database:

```bash
# 1. Restore latest backup
python restore_database.py --latest

# 2. Or recreate from scratch
python setup_complete_system.py

# 3. Verify users are back
python -c "from database import SessionLocal; import models; db = SessionLocal(); print(f'Users: {db.query(models.User).count()}'); db.close()"
```

## Automation Ideas

### Windows Task Scheduler
Create a scheduled task to run `backup_database.py` daily

### Git Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python backup_database.py
```

### Batch File for Development
Create `start_dev.bat`:
```batch
@echo off
echo Creating backup...
python backup_database.py
echo Starting server...
uvicorn main:app --reload
```

## Summary

✅ **Backup**: `python backup_database.py`
✅ **Restore**: `python restore_database.py`
✅ **Quick Restore**: `python restore_database.py --latest`
✅ **Location**: `backups/` directory
✅ **Safety**: Always backs up current DB before restore

**Remember**: Backup before tests, migrations, or major changes!
