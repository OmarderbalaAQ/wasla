"""
Diagnose why login is failing after database restore
"""
from database import SessionLocal
import models
from utils.security import verify_password, verify_and_update_password
import sys

def diagnose_login():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("LOGIN FAILURE DIAGNOSIS")
        print("=" * 70)
        
        # Get all users
        users = db.query(models.User).all()
        
        if not users:
            print("\n✗ PROBLEM: No users found in database!")
            print("  The database might be empty or corrupted.")
            return False
        
        print(f"\n✓ Found {len(users)} users in database")
        print("\nChecking each user's password hash:")
        print("-" * 70)
        
        issues_found = []
        
        for user in users:
            print(f"\nUser: {user.email}")
            print(f"  Role: {user.role}")
            print(f"  Active: {user.is_active}")
            
            # Check hash format
            hash_str = user.hashed_password
            print(f"  Hash: {hash_str[:50]}...")
            
            try:
                # Check if it's a bcrypt hash
                if not hash_str.startswith('$2b$') and not hash_str.startswith('$2a$'):
                    print(f"  ✗ PROBLEM: Hash doesn't look like bcrypt!")
                    print(f"    Hash starts with: {hash_str[:10]}")
                    issues_found.append(f"{user.email}: Invalid hash format")
                    continue
                
                # Extract rounds
                parts = hash_str.split('$')
                if len(parts) >= 3:
                    rounds = int(parts[2])
                    print(f"  Rounds: {rounds}")
                    
                    if rounds < 4:
                        print(f"  ⚠ WARNING: Very weak hash ({rounds} rounds)")
                    elif rounds < 12:
                        print(f"  ⚠ Weak hash ({rounds} rounds) - will be upgraded")
                    else:
                        print(f"  ✓ Strong hash ({rounds} rounds)")
                else:
                    print(f"  ✗ PROBLEM: Cannot parse hash structure")
                    issues_found.append(f"{user.email}: Cannot parse hash")
                    continue
                
                # Try to verify with a test (this will fail but shows if hash is readable)
                try:
                    # This should return False, but not crash
                    result = verify_password("test_wrong_password_12345", hash_str)
                    print(f"  ✓ Hash is readable by bcrypt")
                except Exception as e:
                    print(f"  ✗ PROBLEM: Hash cannot be verified!")
                    print(f"    Error: {e}")
                    issues_found.append(f"{user.email}: Hash verification error - {e}")
                    
            except Exception as e:
                print(f"  ✗ PROBLEM: Error analyzing hash: {e}")
                issues_found.append(f"{user.email}: Analysis error - {e}")
        
        print("\n" + "=" * 70)
        
        if issues_found:
            print("✗ ISSUES FOUND:")
            print("=" * 70)
            for issue in issues_found:
                print(f"  • {issue}")
            print("\n" + "=" * 70)
            print("SOLUTION: Run fix_restored_database_passwords.py")
            print("=" * 70)
            return False
        else:
            print("✓ All password hashes look valid")
            print("=" * 70)
            print("\nIf login still fails, the issue might be:")
            print("  1. Wrong password being used")
            print("  2. User account is inactive")
            print("  3. Network/CORS issue")
            print("  4. Frontend sending wrong format")
            print("\nTry testing with known credentials:")
            print("  python test_specific_login.py")
            return True
            
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = diagnose_login()
    sys.exit(0 if success else 1)
