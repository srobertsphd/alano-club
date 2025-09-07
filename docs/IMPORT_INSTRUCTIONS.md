# Complete Import Instructions

## Enhanced Logging System
All import commands now include comprehensive file-based logging that captures:
- **Every error** with exact row and file information
- **All successful imports** with details
- **Skipped/duplicate records** with reasons
- **Complete row data** for problematic records

## Step-by-Step Import Process

### 1. Clear Database and Reset Migrations

```bash
# Navigate to project directory
cd /home/sng/alano-club

# Activate virtual environment (if using one)
source .venv/bin/activate  # or however you activate your venv

# Drop all Django tables from database
python manage.py dbshell
```

In PostgreSQL shell, run:
```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
\q
```

```bash
# Delete migration files (keep __init__.py)
rm members/migrations/0*.py
rm -rf members/migrations/__pycache__

# Verify migrations are gone
ls members/migrations/

# Should only show: __init__.py
```

### 2. Create Fresh Migrations

```bash
# Generate initial migrations for updated models
python manage.py makemigrations

# Apply migrations to create new database schema
python manage.py migrate

# Verify tables were created correctly
python manage.py dbshell
```

In PostgreSQL shell:
```sql
\dt
\q
```

### 3. Run Imports in Correct Order

**IMPORTANT:** Run these commands in exactly this order:

```bash
# Step 1: Import Member Types (no dependencies)
python manage.py import_member_types

# Step 2: Import Payment Methods (no dependencies)  
python manage.py import_payment_methods

# Step 3: Import Members (depends on Member Types)
python manage.py import_members

# Step 4: Import Payments (depends on Members + Payment Methods)
python manage.py import_payments
```

### 4. Check Import Results

After each import, check the generated log files:

```bash
# View the logs directory
ls -la logs/imports/

# Each import creates 3 files:
# - *_ERRORS.log     (All errors, skipped records, duplicates)
# - *_SUCCESS.log    (All successful imports)
# - *_SUMMARY.txt    (Final statistics and file paths)
```

### 5. Example Log File Locations

After running imports, you'll find logs like:
```
logs/imports/
├── import_member_types_2025-01-06_15-30-45_ERRORS.log
├── import_member_types_2025-01-06_15-30-45_SUCCESS.log
├── import_member_types_2025-01-06_15-30-45_SUMMARY.txt
├── import_payment_methods_2025-01-06_15-31-12_ERRORS.log
├── import_payment_methods_2025-01-06_15-31-12_SUCCESS.log
├── import_payment_methods_2025-01-06_15-31-12_SUMMARY.txt
├── import_active_members_2025-01-06_15-32-05_ERRORS.log
├── import_active_members_2025-01-06_15-32-05_SUCCESS.log
├── import_active_members_2025-01-06_15-32-05_SUMMARY.txt
├── import_inactive_members_2025-01-06_15-32-45_ERRORS.log
├── import_inactive_members_2025-01-06_15-32-45_SUCCESS.log
├── import_inactive_members_2025-01-06_15-32-45_SUMMARY.txt
├── import_payments_2025-01-06_15-33-30_ERRORS.log
├── import_payments_2025-01-06_15-33-30_SUCCESS.log
└── import_payments_2025-01-06_15-33-30_SUMMARY.txt
```

### 6. Troubleshooting

If any import fails:

1. **Check the ERROR log** for that specific import
2. **Review the exact row and data** that caused problems
3. **Fix the CSV data** if needed
4. **Re-run that specific import** with `--clear-existing` flag

```bash
# Example: Re-run member types import after fixing data
python manage.py import_member_types --clear-existing
```

### 7. Data Validation Commands

After all imports complete, you can run these to verify data integrity:

```bash
# Check counts
python manage.py shell -c "
from members.models import *
print(f'Member Types: {MemberType.objects.count()}')
print(f'Payment Methods: {PaymentMethod.objects.count()}')  
print(f'Active Members: {Member.objects.filter(status=\"active\").count()}')
print(f'Inactive Members: {Member.objects.filter(status=\"inactive\").count()}')
print(f'Payments: {Payment.objects.count()}')
"

# Check member ID usage
python manage.py shell -c "
from members.models import Member
active_ids = Member.objects.filter(status='active', member_id__isnull=False).values_list('member_id', flat=True)
print(f'Active member IDs: {sorted(active_ids)}')
print(f'Total active with IDs: {len(active_ids)}')
print(f'ID range: {min(active_ids) if active_ids else \"None\"} - {max(active_ids) if active_ids else \"None\"}')
"
```

### 8. Important Notes

- **Log files contain EVERY error** - no longer limited to 5-10 like console output
- **Row data is included** for every problematic record for easy debugging
- **File names and row numbers** are clearly identified in all log entries
- **Console output is summary only** - check log files for complete details
- **Timestamps in filenames** ensure logs don't overwrite each other

### 9. Clean Re-import Process

If you need to start completely over:

```bash
# Clear all data and re-import everything
python manage.py import_member_types --clear-existing
python manage.py import_payment_methods --clear-existing  
python manage.py import_members --clear-existing
python manage.py import_payments --clear-existing
```

This ensures a clean slate for all imports.
