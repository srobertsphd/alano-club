import csv
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from members.models import Member, MemberType, PaymentMethod, Payment


class Command(BaseCommand):
    help = "Import member data from CSV files in correct dependency order"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            type=str,
            default="data/cleaned_data",
            help="Directory containing CSV files (default: data/cleaned_data)",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing data before importing",
        )

    def handle(self, *args, **options):
        self.data_dir = Path(options["data_dir"])

        if not self.data_dir.exists():
            raise CommandError(f"Data directory not found: {self.data_dir}")

        # Clear existing data if requested
        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing data...")
            self.clear_existing_data()

        # Import in dependency order
        try:
            with transaction.atomic():
                self.stdout.write("\n🚀 Starting CSV data import...")

                # Step 1: Import MemberTypes (no dependencies)
                self.import_member_types()

                # Step 2: Import PaymentMethods (no dependencies)
                self.import_payment_methods()

                # Step 3: Import Members (depends on MemberTypes)
                self.import_members()

                # Step 4: Import Payments (depends on Members + PaymentMethods)
                self.import_payments()

                self.stdout.write(
                    self.style.SUCCESS("\n✅ All data imported successfully!")
                )

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def clear_existing_data(self):
        """Clear existing data in reverse dependency order"""
        Payment.objects.all().delete()
        Member.objects.all().delete()
        PaymentMethod.objects.all().delete()
        MemberType.objects.all().delete()
        self.stdout.write("   ✅ Existing data cleared")

    def import_member_types(self):
        """Import member types from member_types.csv"""
        csv_file = self.data_dir / "member_types.csv"
        if not csv_file.exists():
            raise CommandError(f"Member types CSV not found: {csv_file}")

        self.stdout.write("\n📋 Importing Member Types...")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            created_count = 0

            for row in reader:
                # Skip empty rows
                if not row.get("MemberTypeID") or not row.get("MemberType"):
                    continue

                member_type, created = MemberType.objects.get_or_create(
                    member_type_id=int(row["MemberTypeID"]),
                    defaults={
                        "name": row["MemberType"].strip(),
                        "monthly_dues": Decimal(row["Member Dues"])
                        if row["Member Dues"]
                        else Decimal("0.00"),
                        "coverage_months": Decimal(row["NumMonths"])
                        if row["NumMonths"]
                        else Decimal("1.0"),
                        "is_active": True,
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(f"   ✅ Created: {member_type}")
                else:
                    self.stdout.write(f"   ⚠️  Exists: {member_type}")

        self.stdout.write(f"   📊 Member Types: {created_count} created")

    def import_payment_methods(self):
        """Import payment methods from payment_methods.csv"""
        csv_file = self.data_dir / "payment_methods.csv"
        if not csv_file.exists():
            raise CommandError(f"Payment methods CSV not found: {csv_file}")

        self.stdout.write("\n💳 Importing Payment Methods...")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            created_count = 0

            for row in reader:
                # Skip empty rows
                if not row.get("PaymentMethodID") or not row.get("PaymentMethod"):
                    continue

                # Convert Credit Card boolean
                is_credit_card = row.get("Credit Card?", "False").lower() in [
                    "true",
                    "1",
                    "yes",
                ]

                # Check if name already exists (handle duplicates)
                method_name = row["PaymentMethod"].strip()
                try:
                    payment_method = PaymentMethod.objects.get(name=method_name)
                    created = False
                    self.stdout.write(
                        f"   ⚠️  Duplicate name '{method_name}' - using existing"
                    )
                except PaymentMethod.DoesNotExist:
                    payment_method, created = PaymentMethod.objects.get_or_create(
                        payment_method_id=int(row["PaymentMethodID"]),
                        defaults={
                            "name": method_name,
                            "is_credit_card": is_credit_card,
                            "is_active": True,
                        },
                    )

                if created:
                    created_count += 1
                    self.stdout.write(f"   ✅ Created: {payment_method}")
                else:
                    self.stdout.write(f"   ⚠️  Exists: {payment_method}")

        self.stdout.write(f"   📊 Payment Methods: {created_count} created")

    def import_members(self):
        """Import members from members.csv"""
        csv_file = self.data_dir / "members.csv"
        if not csv_file.exists():
            raise CommandError(f"Members CSV not found: {csv_file}")

        self.stdout.write("\n👥 Importing Members...")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Skip empty rows
                    if (
                        not row.get("Member ID")
                        or not row.get("First Name")
                        or not row.get("Last Name")
                    ):
                        continue

                    # Get member type
                    member_type_name = row.get("Member Type", "").strip()
                    if not member_type_name:
                        errors.append(f"Row {row_num}: Missing Member Type")
                        continue

                    try:
                        member_type = MemberType.objects.get(name=member_type_name)
                    except MemberType.DoesNotExist:
                        errors.append(
                            f"Row {row_num}: Member Type '{member_type_name}' not found"
                        )
                        continue

                    # Parse dates
                    milestone_date = None
                    if row.get("Milestone"):
                        milestone_date = parse_date(row["Milestone"])

                    date_joined = parse_date(row["Date Joined"])
                    if not date_joined:
                        errors.append(f"Row {row_num}: Invalid Date Joined")
                        continue

                    # Set expiration date to September 30, 2025
                    expiration_date = datetime(2025, 9, 30).date()

                    # Get member ID
                    member_id = int(row["Member ID"])

                    member, created = Member.objects.get_or_create(
                        member_id=member_id,
                        defaults={
                            "member_uuid": uuid.uuid4(),
                            "preferred_member_id": member_id,  # Same as current ID initially
                            "first_name": row["First Name"].strip(),
                            "last_name": row["Last Name"].strip(),
                            "email": row.get("E Mail", "").strip(),
                            "member_type": member_type,
                            "status": "active",
                            "expiration_date": expiration_date,
                            "milestone_date": milestone_date,
                            "date_joined": date_joined,
                            "home_address": row.get("Home Address", "").strip(),
                            "home_country": row.get("Home Country", "US").strip()
                            or "US",
                            "home_phone": row.get("Home Phone", "").strip(),
                        },
                    )

                    if created:
                        created_count += 1
                        if created_count <= 5:  # Show first 5
                            self.stdout.write(f"   ✅ Created: {member}")
                    else:
                        self.stdout.write(f"   ⚠️  Exists: {member}")

                except Exception as e:
                    errors.append(f"Row {row_num}: {e}")

            if errors:
                self.stdout.write(f"   ❌ Errors encountered:")
                for error in errors[:10]:  # Show first 10 errors
                    self.stdout.write(f"      {error}")
                if len(errors) > 10:
                    self.stdout.write(f"      ... and {len(errors) - 10} more errors")

        self.stdout.write(
            f"   📊 Members: {created_count} created, {len(errors)} errors"
        )

    def import_payments(self):
        """Import payments from payments.csv"""
        csv_file = self.data_dir / "payments.csv"
        if not csv_file.exists():
            raise CommandError(f"Payments CSV not found: {csv_file}")

        self.stdout.write("\n💰 Importing Payments...")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Skip empty rows
                    if not row.get("Payment ID") or not row.get("Member_ID"):
                        continue

                    # Get member by member_id
                    member_id = int(row["Member_ID"])
                    try:
                        member = Member.objects.get(member_id=member_id)
                    except Member.DoesNotExist:
                        errors.append(f"Row {row_num}: Member ID {member_id} not found")
                        continue

                    # Get payment method by name (CSV has method name, not ID)
                    payment_method_name = row.get("PaymentMethodID", "").strip()
                    if not payment_method_name:
                        errors.append(f"Row {row_num}: Missing PaymentMethodID")
                        continue

                    try:
                        payment_method = PaymentMethod.objects.get(
                            name=payment_method_name
                        )
                    except PaymentMethod.DoesNotExist:
                        errors.append(
                            f"Row {row_num}: Payment Method '{payment_method_name}' not found"
                        )
                        continue

                    # Parse date
                    payment_date = parse_date(row["Date"])
                    if not payment_date:
                        errors.append(f"Row {row_num}: Invalid Date")
                        continue

                    # Parse amount
                    try:
                        amount = Decimal(row["Amount"])
                    except (ValueError, TypeError):
                        errors.append(f"Row {row_num}: Invalid Amount")
                        continue

                    payment, created = Payment.objects.get_or_create(
                        original_payment_id=int(row["Payment ID"]),
                        defaults={
                            "member": member,
                            "payment_method": payment_method,
                            "amount": amount,
                            "date": payment_date,
                            "receipt_number": row.get("Reciept No.", "").strip(),
                        },
                    )

                    if created:
                        created_count += 1
                        if created_count <= 5:  # Show first 5
                            self.stdout.write(f"   ✅ Created: {payment}")
                    else:
                        self.stdout.write(f"   ⚠️  Exists: {payment}")

                except Exception as e:
                    errors.append(f"Row {row_num}: {e}")

            if errors:
                self.stdout.write(f"   ❌ Errors encountered:")
                for error in errors[:10]:  # Show first 10 errors
                    self.stdout.write(f"      {error}")
                if len(errors) > 10:
                    self.stdout.write(f"      ... and {len(errors) - 10} more errors")

        self.stdout.write(
            f"   📊 Payments: {created_count} created, {len(errors)} errors"
        )

    def style_success(self, message):
        """Style success message (fallback if self.style not available)"""
        try:
            return self.style.SUCCESS(message)
        except:
            return message
