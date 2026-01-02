# Database Backup Guide

**Created:** January 2025  
**Purpose:** Guide for creating database backups using both command-line and web interface methods.

---

## Overview

The Alano Club application provides two ways to create database backups:

1. **Command-Line Interface** - For local development and server administration
2. **Web Interface** - For staff users on the deployed application (Render)

Both methods create JSON backups using Django's `dumpdata` command, which can be restored using Django's `loaddata` command.

---

## Backup File Format

- **Format:** JSON (Django `dumpdata` format)
- **Naming:** `backup_{db_type}_{YYYY-MM-DD}_{HH-MM-SS}.json`
- **Location:** `backups/{db_type}/` directory
- **Example:** `backup_dev_2025-01-15_14-30-00.json`

---

## Method 1: Command-Line Interface (Local Development)

### Prerequisites

- Virtual environment activated
- Database connection configured (`DATABASE_URL` in `.env` file)
- Access to terminal/command line

### Basic Usage

**Backup current database (auto-detects type):**
```bash
source .venv/bin/activate
python manage.py backup_database
```

**Backup specific database type:**
```bash
# Backup development database
python manage.py backup_database --db-type dev

# Backup production database (requires DATABASE_URL_PROD in .env)
python manage.py backup_database --db-type prod
```

### How It Works

1. **Auto-Detection Mode** (no `--db-type` flag):
   - Detects database type by comparing current `DATABASE_URL` host with `DATABASE_URL_PROD`
   - If host matches `DATABASE_URL_PROD` → labels as "prod"
   - Otherwise → labels as "dev"
   - Backs up the database specified in `DATABASE_URL`

2. **Explicit Type Mode** (`--db-type` flag):
   - **`--db-type dev`**: Backs up the database specified in `DATABASE_URL`
   - **`--db-type prod`**: Backs up the database specified in `DATABASE_URL_PROD`
     - Requires `DATABASE_URL_PROD` to be set in `.env` file
     - Temporarily uses `DATABASE_URL_PROD` for the backup operation
     - Does not change your current `DATABASE_URL` connection

### Output Example

```
✓ Backup created: backup_dev_2025-01-15_14-30-00.json (946,702 bytes)
  Location: backups/dev/backup_dev_2025-01-15_14-30-00.json
  Database: dev
```

### Backup File Storage

- Files are saved to `backups/{db_type}/` directory
- Files persist on the server until manually deleted
- The `backups/` directory is excluded from git (see `.gitignore`)

### Environment Variables Required

**For development backups:**
- `DATABASE_URL` - Your development database connection string

**For production backups:**
- `DATABASE_URL` - Your current database connection (can be dev or prod)
- `DATABASE_URL_PROD` - Your production database connection string

**Example `.env` file:**
```bash
DATABASE_URL=postgresql://postgres.xxx@aws-0-us-west-2.pooler.supabase.com:6543/postgres
DATABASE_URL_PROD=postgresql://postgres.xxx@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

---

## Method 2: Web Interface (Render Deployment)

### Prerequisites

- Deployed application on Render
- Staff user account (logged in)
- Access to Reports page

### How to Use

1. Log in to the deployed application as a staff user
2. Navigate to **Reports** page (from sidebar menu)
3. Click on **"Database Backup"** card
4. Click **"Download Backup"** button
5. Backup file downloads immediately to your computer

### How It Works

1. **Database Detection:**
   - Uses the database specified in `DATABASE_URL` (set by Render)
   - On Render, `DATABASE_URL` points to your production database
   - Auto-detects database type by comparing host with `DATABASE_URL_PROD` (if set)
   - If `DATABASE_URL_PROD` is not set or doesn't match → defaults to "dev" label (but still backs up production)

2. **Backup Process:**
   - Creates temporary backup file on server
   - Streams file content to your browser as download
   - Deletes temporary file immediately after download
   - No server storage - file only exists on your computer

3. **File Naming:**
   - Filename includes detected database type and timestamp
   - Example: `backup_prod_2025-01-15_14-30-00.json` (if detected as prod)
   - Example: `backup_dev_2025-01-15_14-30-00.json` (if detected as dev, but still production data)

### Important Notes for Render

- **Single Database:** Render deployment uses one `DATABASE_URL` (production database)
- **What Gets Backed Up:** Always backs up the production database (whatever `DATABASE_URL` points to)
- **File Labeling:** 
  - If `DATABASE_URL_PROD` is set in Render environment variables and matches → labeled as "prod"
  - Otherwise → labeled as "dev" (but contains production data)
- **No Server Storage:** Files are temporary and deleted immediately after download
- **User Storage:** Each user downloads backups to their own computer

### Render Environment Variables

**Required:**
- `DATABASE_URL` - Production database connection string (set by Render or manually)

**Optional (for correct labeling):**
- `DATABASE_URL_PROD` - Set to same value as `DATABASE_URL` to ensure backups are labeled as "prod"

**Note:** Setting `DATABASE_URL_PROD` on Render is optional. The backup will work correctly either way - it only affects the filename label. The actual data backed up is always from `DATABASE_URL` (production).

---

## Restoring Backups

### Using Django's loaddata Command

```bash
source .venv/bin/activate
python manage.py loaddata backups/dev/backup_dev_2025-01-15_14-30-00.json
```

**Important:** 
- Restore to a development database only (never restore to production via command line)
- Ensure you're connected to the correct database before restoring
- Backups can be large - ensure sufficient disk space

---

## Comparison: Command-Line vs Web Interface

| Feature | Command-Line | Web Interface |
|---------|-------------|---------------|
| **Location** | Local development | Render deployment |
| **Access** | Terminal access required | Staff user login required |
| **Database Options** | Can backup dev or prod | Backs up production only |
| **File Storage** | Saved on server | Downloaded to user's computer |
| **File Persistence** | Files remain until deleted | Temporary (deleted after download) |
| **Use Case** | Development, server admin | Quick backups for staff users |

---

## Troubleshooting

### Command-Line Issues

**Error: "DATABASE_URL_PROD not set in environment"**
- **Cause:** Trying to backup prod without `DATABASE_URL_PROD` set
- **Solution:** Add `DATABASE_URL_PROD` to your `.env` file, or use `--db-type dev` instead

**Error: "Export seems empty or very small"**
- **Cause:** Database connection issue or empty database
- **Solution:** Verify `DATABASE_URL` is correct and database is accessible

**Error: "Backup failed: [error message]"**
- **Cause:** Database connection or permissions issue
- **Solution:** Check database credentials and connection string

### Web Interface Issues

**Error: "Backup failed"**
- **Cause:** Database connection issue on Render
- **Solution:** Verify `DATABASE_URL` is set correctly in Render dashboard

**403 Forbidden Error**
- **Cause:** User is not a staff member
- **Solution:** Log in with a staff user account

**Download doesn't start**
- **Cause:** Browser blocking download or network issue
- **Solution:** Check browser download settings, try different browser

---

## Security Notes

- **Staff-Only Access:** Web interface requires staff user authentication
- **No Public Access:** Backup functionality is not accessible to regular users
- **Secure Storage:** Backup files contain sensitive member data - store securely
- **Git Exclusion:** Backup files are excluded from version control (see `.gitignore`)

---

## Best Practices

1. **Regular Backups:** Create backups before major changes or deployments
2. **Test Restores:** Periodically test restoring backups to ensure they work
3. **Secure Storage:** Store downloaded backups in secure locations
4. **Naming Convention:** Keep original filenames to identify database type and date
5. **Production Backups:** Use web interface on Render for production backups
6. **Development Backups:** Use command-line for development database backups

---

## Related Documentation

- `docs/CHANGE_LOG.md` - Change #023: Database Backup Feature implementation details
- `docs/DATABASE_SYNC_GUIDE.md` - Guide for syncing production to development

