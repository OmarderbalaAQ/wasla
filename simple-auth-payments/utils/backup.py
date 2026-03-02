"""
Database Backup and Restore Utilities
"""
import shutil
import os
from datetime import datetime
from typing import Optional, List, Dict
import glob


class BackupManager:
    """Manages database backups and restores"""
    
    def __init__(self, db_path: str = "dev.db", backup_dir: str = "backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self) -> Dict:
        """Create a timestamped backup of the database"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found")
        
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        # Get file size
        size_bytes = os.path.getsize(backup_path)
        
        return {
            "success": True,
            "filename": backup_filename,
            "path": backup_path,
            "size_bytes": size_bytes,
            "timestamp": datetime.now().isoformat()
        }
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        backup_files = sorted(
            glob.glob(os.path.join(self.backup_dir, "backup_*.db")),
            reverse=True
        )
        
        for backup_path in backup_files:
            filename = os.path.basename(backup_path)
            size_bytes = os.path.getsize(backup_path)
            
            # Extract timestamp from filename
            timestamp_str = filename.replace("backup_", "").replace(".db", "")
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except:
                date_str = timestamp_str
            
            backups.append({
                "filename": filename,
                "path": backup_path,
                "size_bytes": size_bytes,
                "date": date_str,
                "timestamp": timestamp_str
            })
        
        return backups
    
    def get_latest_backup(self) -> Optional[Dict]:
        """Get the most recent backup"""
        backups = self.list_backups()
        return backups[0] if backups else None
    
    def restore_backup(self, backup_filename: str) -> Dict:
        """Restore database from a specific backup"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file {backup_filename} not found")
        
        # Backup current database before restoring
        if os.path.exists(self.db_path):
            safety_backup = f"{self.db_path}.before_restore"
            try:
                shutil.copy2(self.db_path, safety_backup)
            except PermissionError:
                # On Windows, if file is locked, wait a moment and retry
                import time
                time.sleep(0.5)
                shutil.copy2(self.db_path, safety_backup)
        
        # Restore from backup
        # On Windows, if the file is locked, this will fail
        # The calling code should ensure all DB connections are closed first
        try:
            shutil.copy2(backup_path, self.db_path)
        except PermissionError as e:
            raise PermissionError(
                "Cannot restore: database file is locked. "
                "Please ensure all database connections are closed. "
                f"Original error: {str(e)}"
            )
        
        return {
            "success": True,
            "restored_from": backup_filename,
            "timestamp": datetime.now().isoformat()
        }
    
    def restore_latest(self) -> Dict:
        """Restore the most recent backup"""
        latest = self.get_latest_backup()
        if not latest:
            raise FileNotFoundError("No backups available")
        
        return self.restore_backup(latest["filename"])
    
    def check_and_restore_if_empty(self) -> Dict:
        """
        Check if database has essential data.
        If empty or missing, restore from latest backup.
        Returns status information.
        """
        from database import SessionLocal
        import models
        
        # Check if database file exists
        if not os.path.exists(self.db_path):
            # Try to restore from latest backup
            latest = self.get_latest_backup()
            if latest:
                try:
                    result = self.restore_latest()
                    return {
                        "action": "restored",
                        "reason": "database_missing",
                        "details": f"Restored from {latest['filename']}",
                        "backup_used": latest['filename']
                    }
                except Exception as e:
                    return {
                        "action": "failed",
                        "reason": "restore_failed",
                        "details": f"Failed to restore: {str(e)}",
                        "will_create_new": True
                    }
            else:
                return {
                    "action": "none",
                    "reason": "no_backups_available",
                    "details": "Database missing and no backups found. Will create new database.",
                    "will_create_new": True
                }
        
        # Check if database has essential data
        db = SessionLocal()
        try:
            # Check for users (at least one admin should exist)
            user_count = db.query(models.User).count()
            bundle_count = db.query(models.Bundle).count()
            
            if user_count == 0:
                # Database is empty, try to restore
                latest = self.get_latest_backup()
                if latest:
                    try:
                        result = self.restore_latest()
                        return {
                            "action": "restored",
                            "reason": "database_empty_no_users",
                            "details": f"Restored from {latest['filename']}",
                            "backup_used": latest['filename']
                        }
                    except Exception as e:
                        return {
                            "action": "failed",
                            "reason": "restore_failed",
                            "details": f"Failed to restore: {str(e)}",
                            "will_seed_new": True
                        }
                else:
                    return {
                        "action": "none",
                        "reason": "no_backups_available",
                        "details": "Database empty (no users) and no backups found. Will seed new data.",
                        "will_seed_new": True
                    }
            
            return {
                "action": "none",
                "reason": "database_ok",
                "details": f"Database has {user_count} users and {bundle_count} bundles"
            }
        
        finally:
            db.close()
    
    def delete_old_backups(self, keep_count: int = 10) -> Dict:
        """Delete old backups, keeping only the most recent ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return {
                "deleted": 0,
                "kept": len(backups),
                "message": "No backups deleted"
            }
        
        # Delete older backups
        to_delete = backups[keep_count:]
        deleted_count = 0
        
        for backup in to_delete:
            try:
                os.remove(backup["path"])
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {backup['filename']}: {e}")
        
        return {
            "deleted": deleted_count,
            "kept": keep_count,
            "message": f"Deleted {deleted_count} old backups"
        }
