# Alano Club Member Management System

A Django-based web application for managing club members, payments, and organizational data.

## Project Structure

```
alano-club/
├── alano_club_site/          # Django project settings
├── members/                  # Main Django app
├── data/                     # Data files and utilities
│   ├── xlsx_data/           # Original Excel files
│   ├── csv_data/            # Converted CSV files
│   └── convert_xlsx_to_csv.py  # Data conversion utility
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── SETUP_INSTRUCTIONS.md     # Detailed setup guide
```

## Features

- **Member Management**: Add, edit, view members with detailed contact information
- **Payment Tracking**: Record and track membership dues and payments
- **Member Types**: Configure different membership categories
- **Admin Interface**: Full administrative control via Django Admin
- **Data Import**: Tools for importing existing Excel data
- **Modern UI**: Bootstrap-styled forms and interfaces

## Quick Start

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run development server:**
   ```bash
   python manage.py runserver 8001
   ```

4. **Access admin interface:**
   - URL: http://127.0.0.1:8001/admin/
   - Login with your admin credentials

## Data Management

**Convert Excel files to CSV:**
```bash
python data/convert_xlsx_to_csv.py
```

**Current data:**
- 325 active members
- 1,337 payment records  
- 10 member types
- 11 payment methods

## Next Steps

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed setup, database configuration, and deployment instructions.
