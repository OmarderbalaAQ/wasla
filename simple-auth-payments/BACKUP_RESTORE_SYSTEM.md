# Backup and Restore System - Complete Guide

## Overview

The system now has a fully synchronized backup and restore mechanism that ensures data persistence across deployments and prevents data loss.

## How It Works

### Startup Flow

```
Application Starts
    ↓
Check Database Status
    ↓
┌─────────────────────────────────────┐
│ Is database file missing or empty? │
└─────────────────────────────────────┘
    ↓                           ↓
   YES                         NO
    ↓                           ↓
Check for backups          Database OK
    ↓                      (Skip seeding)
┌──────────────┐
│ Backups exist?│
└──────────────┘
    ↓         ↓
   YES       NO
    ↓         ↓
Restore    Seed new data
from       (admin + bundles)
latest          ↓
backup     Create initial
           backup
```

## Key Features

### 1. Automatic Restore on Startup

When the application starts, it automatically:
- Checks if the database exists and has data
- If empty or missing, restores from the latest backup
- If no backups exist, creates new database with default data

### 2. Backup Files in Git

The `.gitignore` has been updated to:
- Exclude regular database files (`*.db`)
- Include backup files in the `backups/` folder (`!backups/*.db`)

This ensures:
- Production deployments have backup files available
- Fresh deployments can restore from a known good state
- No need to manually create admin users in production

### 3. Synchronized Seeding

The system intelligently handles data seeding:
- If restore succeeds → Skip seeding (data already exists)
- If restore fails → Seed new data
- If no backups → Seed new data and create initial backup

## Configuration

### Backup Settings

Located in `utils/backup.py`:

```python
BackupManager(
    db_path="dev.db",        # Database file to backup
    backup_dir="backups"     # Backup directory
)
```

### Default Data

When seeding new database:
- **Admin User**: admin@admin.com / admin123
- **Bundles**: Basic Bundle ($10), Pro Bundle ($50)

## Usage

### Automatic (Recommended)

The system handles everything automatically on startup. No manual intervention needed.

### Manual Backup

Create a backup anytime:

```bash
python backup_database.py
```

Or programmatically:

```python
from utils.backup import BackupManager
manager = BackupManager()
result = manager.create_backup()
print(f"Backup created: {result['filename']}")
```

### Manual Restore

Restore from latest backup:

```bash
python restore_database.py
```

Or restore specific backup:

```python
from utils.backup import BackupManager
manager = BackupManager()
manager.restore_backup("backup_20260217_173152.db")
```

### List Backups

```python
from utils.backup import BackupManager
manager = BackupManager()
backups = manager.list_backups()
for backup in backups:
    print(f"{backup['filename']} - {backup['date']} - {backup['size_bytes']} bytes")
```

## Production Deployment

### Railway / Render / Other Platforms

1. **First Deployment**:
   - Backup files are deployed with your code
   - System restores from latest backup automatically
   - Your admin users and data are ready to use

2. **Subsequent Deployments**:
   - If database persists (volume mounted), no restore needed
   - If database is lost, automatic restore from backup
   - No manual database setup required

3. **Creating Production Backups**:
   - Before major changes, create a backup
   - Commit the backup to git
   - Push to repository
   - Your backup is now safe and deployable

### Example Workflow

```bash
# Before making major changes
python backup_database.py

# Add the new backup to git
git add backups/backup_*.db

# Commit and push
git commit -m "Backup before major changes"
git push

# Now deploy - if anything goes wrong, the backup is available
```

## Backup Management

### Automatic Cleanup

The system can automatically delete old backups:

```python
from utils.backup import BackupManager
manager = BackupManager()
result = manager.delete_old_backups(keep_count=10)
print(f"Deleted {result['deleted']} old backups, kept {result['kept']}")
```

### Backup File Naming

Format: `backup_YYYYMMDD_HHMMSS.db`

Example: `backup_20260217_173152.db`
- Created on: February 17, 2026
- Time: 17:31:52

## Troubleshooting

### Issue: No backups available on first deployment

**Solution**: Create and commit an initial backup:
```bash
python backup_database.py
git add backups/backup_*.db
git commit -m "Add initial backup"
git push
```

### Issue: Restore fails with "No backups available"

**Cause**: Backup files not committed to git or `.gitignore` excluding them

**Solution**: 
1. Check `.gitignore` has `!backups/*.db`
2. Verify backup files exist in `backups/` folder
3. Commit backup files to git

### Issue: Database restored but missing recent data

**Cause**: Backup is outdated

**Solution**: Create a fresh backup before deployment:
```bash
python backup_database.py
git add backups/
git commit -m "Update backup with latest data"
git push
```

### Issue: Want to start fresh without backups

**Solution**: 
1. Delete or rename backup files
2. Delete database file
3. Restart application
4. System will seed new data

## Security Considerations

### What's in Backup Files?

- User accounts (passwords are hashed with bcrypt)
- Email addresses
- Bundles and pricing
- Contact form submissions
- All application data

### Best Practices

1. **Private Repositories**: Safe to commit backups
2. **Public Repositories**: 
   - Consider if backup data should be public
   - Alternative: Use environment-based seeding
   - Or: Store backups separately (S3, etc.)

3. **Production Secrets**:
   - Backups don't contain `.env` secrets
   - JWT keys and API keys are safe

## Monitoring

### Startup Logs

The system logs its actions on startup:

```
✓ Database restored from backup
  Reason: database_empty_no_users
  Backup: backup_20260217_173152.db
  Details: Restored from backup_20260217_173152.db
```

Or:

```
✓ Database OK: Database has 5 users and 2 bundles
```

Or:

```
⚠ No backups available: Database missing and no backups found. Will create new database.
✓ Created default admin user: admin@admin.com / admin123
  ⚠ IMPORTANT: Change this password in production!
✓ Seeded initial bundles
✓ Created initial backup: backup_20260225_120000.db
```

## Summary

The backup and restore system provides:
- ✅ Automatic data recovery
- ✅ Zero-downtime deployments
- ✅ No manual database setup
- ✅ Git-based backup distribution
- ✅ Intelligent seeding fallback
- ✅ Production-ready data persistence

Your database is now protected and automatically managed!
