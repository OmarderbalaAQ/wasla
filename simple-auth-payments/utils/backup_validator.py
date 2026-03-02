"""Backup file validation utility"""
import sqlite3
import os
from typing import Dict, List


class BackupValidator:
    """Validates database backup files"""
    
    REQUIRED_TABLES = [
        "users", "bundles", "contact_requests", 
        "lead_assignments", "payments", "subscriptions"
    ]
    
    def validate_file_format(self, file_path: str) -> Dict:
        """Check if file is valid SQLite database"""
        if not os.path.exists(file_path):
            return {"valid": False, "error": "File not found"}
        
        if not file_path.endswith('.db'):
            return {"valid": False, "error": "File must be .db format"}
        
        conn = None
        try:
            conn = sqlite3.connect(file_path)
            conn.execute("SELECT 1")
            return {"valid": True}
        except sqlite3.Error as e:
            return {"valid": False, "error": f"Invalid SQLite database: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_backup_tables(self, file_path: str) -> List[str]:
        """List all tables in backup"""
        conn = None
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        finally:
            if conn:
                conn.close()
    
    def validate_schema(self, file_path: str) -> Dict:
        """Check if required tables exist"""
        tables = self.get_backup_tables(file_path)
        missing = [t for t in self.REQUIRED_TABLES if t not in tables]
        
        return {
            "valid": len(missing) == 0,
            "tables_found": tables,
            "missing_tables": missing,
            "compatible": len(missing) == 0
        }
    
    def get_backup_info(self, file_path: str) -> Dict:
        """Get backup metadata"""
        conn = None
        try:
            conn = sqlite3.connect(file_path)
            info = {
                "size_bytes": os.path.getsize(file_path),
                "tables": {}
            }
            
            for table in self.REQUIRED_TABLES:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    info["tables"][table] = count
                except:
                    info["tables"][table] = 0
            
            return info
        finally:
            if conn:
                conn.close()
    
    def validate_backup(self, file_path: str) -> Dict:
        """Complete backup validation - uses single connection for efficiency"""
        if not os.path.exists(file_path):
            return {"valid": False, "error": "File not found"}
        
        if not file_path.endswith('.db'):
            return {"valid": False, "error": "File must be .db format"}
        
        conn = None
        try:
            # Open connection once for all checks
            conn = sqlite3.connect(file_path)
            
            # Check format
            conn.execute("SELECT 1")
            
            # Get tables
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check schema
            missing = [t for t in self.REQUIRED_TABLES if t not in tables]
            
            # Get info
            info = {
                "size_bytes": os.path.getsize(file_path),
                "tables": {}
            }
            
            for table in self.REQUIRED_TABLES:
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    info["tables"][table] = count
                except:
                    info["tables"][table] = 0
            
            return {
                "valid": len(missing) == 0,
                "compatible": len(missing) == 0,
                "tables_found": tables,
                "missing_tables": missing,
                "info": info
            }
            
        except sqlite3.Error as e:
            return {"valid": False, "error": f"Invalid SQLite database: {str(e)}"}
        finally:
            if conn:
                conn.close()
