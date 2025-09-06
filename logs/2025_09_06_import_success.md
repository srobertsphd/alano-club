(alano-club) sng@SnG:~/alano-club$ python manage.py makemigrations
Migrations for 'members':
  members/migrations/0001_initial.py
    - Create model MemberType
    - Create model PaymentMethod
    - Create model Member
    - Create model Payment
    - Create index members_mem_member__1c9876_idx on field(s) member_id of model member
    - Create index members_mem_last_na_92a910_idx on field(s) last_name, first_name of model member
    - Create index members_mem_status_734de0_idx on field(s) status of model member
    - Create index members_mem_expirat_e91d68_idx on field(s) expiration_date of model member
(alano-club) sng@SnG:~/alano-club$ python manage.py migrate
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, members, sessions
Running migrations:
  Applying members.0001_initial... OK
(alano-club) sng@SnG:~/alano-club$ python manage.py import_member_types

🏷️  Importing member types from: data/2025_09_02/cleaned/current_member_types.csv
   ✅ Created: Couple ($40.0/month)
   ✅ Created: FarAway Friends ($20.0/month)
   ✅ Created: Fixed/Income ($20.0/month)
   ✅ Created: 500 Club ($500.0/month)
   ✅ Created: Honorary ($0.0/month)
   ✅ Created: Life ($3000.0/month)
   ✅ Created: Regular ($30.0/month)
   ✅ Created: Senior ($20.0/month)

📊 Import Summary:
   🏷️  Member types created: 8
   ❌ Errors: 0

✅ Member types import completed successfully!
(alano-club) sng@SnG:~/alano-club$ python manage.py import_payment_methods

💳 Importing payment methods from: data/2025_09_02/cleaned/current_payment_methods.csv
   ✅ Created: Other
   ✅ Created: Cash
   ✅ Created: Check
   ✅ Created: Life
   ✅ Created: Work
   ✅ Created: Board Elect
   ✅ Created: Partial Payment
   ✅ Created: Venmo
   ✅ Created: PayPal
   ✅ Created: Zelle

📊 Import Summary:
   💳 Payment methods created: 10
   ❌ Errors: 0

✅ Payment methods import completed successfully!
(alano-club) sng@SnG:~/alano-club$ python manage.py import_members

👥 Importing ACTIVE members from: data/2025_09_02/cleaned/current_members.csv
   ✅ Created: #1 - John Mack
   ✅ Created: #2 - Audrey Garcia
   ✅ Created: #3 - Curtis Hicks
   ✅ Created: #4 - Garry Belcher
   ✅ Created: #5 - Kent Goetz
   📊 Active members processed: 332
   ❌ Errors: 3
      Row 14: Invalid or missing date_joined
      Row 118: Invalid or missing expiration_date
      Row 183: Invalid or missing date_joined

💀 Importing INACTIVE members from: data/2025_09_02/cleaned/current_dead.csv
   ✅ Created: #No ID - Yvonne Aboujudom
   ✅ Created: #No ID - Sedrick Add
   ✅ Created: #No ID - Ann Agpalasin
   ✅ Created: #No ID - Max Aguilar
   ✅ Created: #No ID - Monalisa Aguilar
   ⚠️  Duplicate skipped: Victor Castaneda
   ⚠️  Duplicate skipped: Rodney De Jesus
   ⚠️  Duplicate skipped: Ryan Deanda
   ⚠️  Duplicate skipped: Noemi Deleon
   ⚠️  Duplicate skipped: Melody Garcia
   📊 Inactive members processed: 1290
   ⚠️  Total duplicates skipped: 20
   ❌ Errors: 24
      Row 3: Missing member_type
      Row 92: Missing member_type
      Row 371: Missing member_type
      Row 378: Missing member_type
      Row 382: Invalid or missing date_joined

✅ Member import completed successfully!
   👥 Active members imported: 332
   💀 Inactive members imported: 1290
   ⚠️  Duplicates skipped: 20

    Importing payments from: data/2025_09_02/cleaned/current_payments.csv
   ✅ Created: John Mack - $300.0 on 2025-05-24
   ✅ Created: Audrey Garcia - $2000.0 on 2023-10-15
   ✅ Created: Curtis Hicks - $40.0 on 2025-06-02
   ✅ Created: Curtis Hicks - $40.0 on 2025-05-05
   ✅ Created: Curtis Hicks - $40.0 on 2025-08-26

📊 Import Summary:
   💰 Payments processed: 714
   ❌ Errors: 6

❌ Errors encountered:
   Row 272: Member not found - ID: 119, Name: Kiki Martinez
   Row 273: Member not found - ID: 119, Name: Kiki Martinez
   Row 421: Member not found - ID: 185, Name: Kiven Christine
   Row 422: Member not found - ID: 185, Name: Kiven Christine
   Row 423: Member not found - ID: 185, Name: Kiven Christine
   Row 424: Member not found - ID: 185, Name: Kiven Christine

✅ Payment import completed successfully!
   💰 Payments imported: 714