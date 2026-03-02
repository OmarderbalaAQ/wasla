# Database Backups

This folder contains database backup files that are automatically created and restored by the system.

## Purpose

- Provides automatic database recovery in production environments
- Ensures data persistence across deployments
- Allows rollback to previous database states

## How It Works

1. **Automatic Restore on Startup**: When the application starts, it checks if the database is empty or missing
2. **Restore from Latest Backup**: If no data exists, it automatically restores from the most recent backup in this folder
3. **Fallback to Seeding**: If no backups exist, it creates a new database with default admin user and bundles

## Backup Files

Backup files follow the naming pattern: `backup_YYYYMMDD_HHMMSS.db`

Example: `backup_20260217_173152.db` (created on Feb 17, 2026 at 17:31:52)

## Important Notes

- These backup files ARE committed to Git (exception to the .gitignore rule)
- This ensures production deployments have a baseline database to restore from
- The system keeps the 10 most recent backups by default
- Manual backups can be created using `backup_database.py`

## Manual Operations

### Create a backup:
```bash
python backup_database.py
```

### Restore from a specific backup:
```bash
python restore_database.py
```

### List available backups:
```python
from utils.backup import BackupManager
manager = BackupManager()
backups = manager.list_backups()
for backup in backups:
    print(f"{backup['filename']} - {backup['date']}")
```

## Production Deployment

When deploying to production (Railway, Render, etc.):
1. The backup files in this folder are deployed with your code
2. On first startup, if no database exists, the system restores from the latest backup
3. This ensures your production environment has the necessary admin users and data

## Security Note

⚠️ Backup files may contain sensitive data (user passwords are hashed, but emails and other data are present)
- Only commit backups that are safe for your repository visibility
- For public repositories, consider using environment-based seeding instead
- For private repositories, this approach provides excellent data persistence
