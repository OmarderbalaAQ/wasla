# Restore Login Access After Database Restore

## Problem
After restoring the database from backup, you cannot log in because:
- The restored database has password hashes from the backup
- You may not remember the passwords that were set at backup time

## Solution Options

### Option 1: Try Known Passwords (Recommended First)

Run this script to test if you know any passwords:

```bash
python test_specific_login.py
```

Enter the email and password to test. Common test passwords to try:
- `admin123`
- `Admin123!`
- `password123`
- `Password123!`
- `TempPassword123!`

### Option 2: Reset All Passwords (If Option 1 Fails)

If you don't know any passwords, reset them all:

```bash
python fix_restored_database_passwords.py
```

This will:
1. Reset ALL user passwords to: `TempPassword123!`
2. Show you all user emails and their new password
3. Allow you to log in immediately

After logging in, change your password to something secure.

### Option 3: Reset Specific Admin Password

If you just need admin access:

```bash
python reset_admin_password.py
```

This resets the admin password to a known value.

## Current Users in Database

Based on the diagnosis, you have these users:
- admin@admin.com (admin)
- client@test.com (user)
- user@test.com (user)
- override@test.com (user)
- AHMED@wasla.com (user)
- sales@wasla.com (salesman)
- admin2@wasla.com (admin)
- tech@wasla.com (technical)

All accounts are ACTIVE and hashes are VALID.

## Step-by-Step Fix

1. **First, try to remember the password:**
   ```bash
   python test_specific_login.py
   ```
   Enter: admin@admin.com
   Try common passwords

2. **If that fails, reset all passwords:**
   ```bash
   python fix_restored_database_passwords.py
   ```
   Type "yes" to confirm
   
3. **Log in with the new password:**
   - Email: admin@admin.com
   - Password: TempPassword123!

4. **Change your password immediately** after logging in

## Why This Happened

When you restore a database from backup:
- The password hashes come from the backup
- If passwords were changed after the backup, the old hashes won't work
- The backup might have different passwords than you remember

## Prevention

To avoid this in the future:
1. Document passwords when creating backups
2. Use the same test passwords consistently
3. Keep a secure password manager
4. Create a new admin after restore if needed
