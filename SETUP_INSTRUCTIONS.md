# Alano Club Member Management System

## Setup Instructions

### 1. Current Status
✅ Django project created  
✅ Member management models designed  
✅ Django Admin interface configured  
✅ Sample data script ready  
✅ SQLite database working locally  

### 2. Supabase Setup (Next Steps)

**Create Supabase Project:**
1. Go to [supabase.com](https://supabase.com)
2. Sign up with your email
3. Create new project: "alano-club-members"
4. Choose a region (US West recommended)
5. Set a secure database password

**Get Connection Details:**
1. Go to Project Settings → Database
2. Copy the connection string
3. It will look like: `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

**Configure Environment:**
1. Copy `env_example.txt` to `.env`
2. Update `DATABASE_URL` with your Supabase connection string
3. Generate a new `SECRET_KEY` for production

### 3. Database Migration

**Once Supabase is configured:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Migrate to Supabase
python manage.py migrate

# Create superuser for Supabase
python manage.py createsuperuser

# Load sample data
python setup_sample_data.py
```

### 4. Running the Application

```bash
# Start development server
python manage.py runserver

# Access the admin interface
# http://127.0.0.1:8000/admin/
```

### 5. Admin Interface Features

**Member Management:**
- Add/Edit/Delete members
- Organized form sections (Personal, Contact, Work, Membership)
- Search by name, ID, phone, city
- Filter by membership type, status, state
- Bulk actions (activate, deactivate, mark deceased)

**Payment Tracking:**
- Record member payments
- Track payment methods
- Period coverage tracking
- Payment history per member

**Member Types & Payment Methods:**
- Configure membership categories
- Set up payment options
- Manage dues structure

### 6. Excel Data Import

Your existing Excel files have been organized in the `data/` directory:
- `data/xlsx_data/` - Original Excel files
- `data/csv_data/` - Converted CSV files for processing

**Convert Excel to CSV:**
```bash
# From project root
python data/convert_xlsx_to_csv.py

# Or from data directory
cd data && python convert_xlsx_to_csv.py
```

**Available data files:**
- `2025_08_26_Members.csv` → 325 member records
- `2025_08_26_MemberTypes.csv` → Membership categories  
- `2025_08_26_Payments.csv` → 1,337 payment records
- `2025_08_26_Payment Methods.csv` → Payment options
- `2025_08_26_Friends.csv` → 60 member connections
- `2025_08_26_Dead.csv` → 1,400 historical records
- `2025_08_26_Frequency.csv` → Frequency data

Import script can be created once data structure is confirmed.

### 7. Deployment to Render

**Ready for deployment:**
- Requirements.txt configured
- WhiteNoise for static files
- Environment variable support
- PostgreSQL optimized

**Deploy steps:**
1. Push code to GitHub
2. Connect Render to repository
3. Add environment variables in Render dashboard
4. Deploy!

### 8. Account Transfer

When ready to transfer to organization:
1. **Supabase:** Use project transfer feature
2. **Render:** Transfer project ownership
3. **GitHub:** Transfer repository ownership

### 9. Login Credentials

**Current superuser:**
- Username: `admin`
- Password: `[set during createsuperuser]`
- URL: `http://127.0.0.1:8000/admin/`

### 10. Next Steps

1. **Set up Supabase account**
2. **Test member management interface**
3. **Import existing Excel data** 
4. **Deploy to Render**
5. **Train organization users**

## Support

The Django Admin interface provides:
- Form-based member entry (like your screenshot)
- Search and filtering
- Payment tracking
- Data export capabilities
- User permissions management

This replaces complex desktop applications with a simple web interface accessible from any device.
