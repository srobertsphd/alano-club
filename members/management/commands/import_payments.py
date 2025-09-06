import csv
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from members.models import Member, PaymentMethod, Payment


class Command(BaseCommand):
    help = "Import payments from current_payments.csv, linking to existing members"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="data/2025_09_02/cleaned/current_payments.csv",
            help="Path to payments CSV file",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing payments before import",
        )

    def handle(self, *args, **options):
        csv_file = Path(options["csv_file"])

        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_file}")

        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing payments...")
            Payment.objects.all().delete()
            self.stdout.write("   ✅ Payments cleared")

        try:
            with transaction.atomic():
                created_count = self.import_payments(csv_file)
                self.stdout.write(
                    self.style.SUCCESS("\n✅ Payment import completed successfully!")
                )
                self.stdout.write(f"   💰 Payments imported: {created_count}")

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def import_payments(self, csv_file):
        """Import payments from CSV file"""
        self.stdout.write(f"\n💰 Importing payments from: {csv_file}")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            created_count = 0
            errors = []

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Skip rows without payment data
                    if not row.get("payment_amount") or not row.get("payment_date"):
                        continue

                    # 1. Find member by member_id first, then by name as fallback
                    member = self.find_member(row, row_num, errors)
                    if not member:
                        continue

                    # 2. Find payment method
                    payment_method = self.find_payment_method(row, row_num, errors)
                    if not payment_method:
                        continue

                    # 3. Parse payment amount
                    try:
                        amount = Decimal(str(row["payment_amount"]).strip())
                    except (ValueError, TypeError):
                        errors.append(
                            f"Row {row_num}: Invalid payment amount '{row.get('payment_amount')}'"
                        )
                        continue

                    # 4. Parse payment date
                    payment_date = parse_date(row["payment_date"])
                    if not payment_date:
                        errors.append(
                            f"Row {row_num}: Invalid payment date '{row.get('payment_date')}'"
                        )
                        continue

                    # 5. Get receipt number (optional)
                    receipt_number = row.get("receipt_number", "").strip()

                    # 6. Check for duplicate payments (same member, amount, date)
                    existing_payment = Payment.objects.filter(
                        member=member, amount=amount, date=payment_date
                    ).first()

                    if existing_payment:
                        if created_count <= 5:  # Show first 5 duplicates
                            self.stdout.write(
                                f"   ⚠️  Duplicate skipped: ${amount} on {payment_date} for {member.full_name}"
                            )
                    else:
                        # Create payment
                        payment = Payment.objects.create(
                            member=member,
                            payment_method=payment_method,
                            amount=amount,
                            date=payment_date,
                            receipt_number=receipt_number,
                        )
                        created_count += 1

                        if created_count <= 5:  # Show first 5 created
                            self.stdout.write(f"   ✅ Created: {payment}")

                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error - {e}")

        # Show summary
        self.stdout.write("\n📊 Import Summary:")
        self.stdout.write(f"   💰 Payments processed: {created_count}")
        self.stdout.write(f"   ❌ Errors: {len(errors)}")

        # Show errors if any
        if errors:
            self.stdout.write("\n❌ Errors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(f"   {error}")
            if len(errors) > 10:
                self.stdout.write(f"   ... and {len(errors) - 10} more errors")

        return created_count

    def find_member(self, row, row_num, errors):
        """Find member by member_id first, then by name"""
        member_id = row.get("member_id")
        first_name = row.get("first_name", "").strip()
        last_name = row.get("last_name", "").strip()

        # Try to find by member_id first (for active members)
        if member_id:
            try:
                member_id_int = int(member_id)
                member = Member.objects.filter(member_id=member_id_int).first()
                if member:
                    return member
            except (ValueError, TypeError):
                pass

        # Fallback to name lookup (for both active and inactive members)
        if first_name and last_name:
            member = Member.objects.filter(
                first_name__iexact=first_name, last_name__iexact=last_name
            ).first()

            if member:
                return member

        # Member not found
        error_msg = f"Row {row_num}: Member not found - "
        if member_id:
            error_msg += f"ID: {member_id}, "
        error_msg += f"Name: {first_name} {last_name}"
        errors.append(error_msg)
        return None

    def find_payment_method(self, row, row_num, errors):
        """Find payment method by name"""
        payment_method_name = row.get("payment_method", "").strip()

        if not payment_method_name:
            errors.append(f"Row {row_num}: Missing payment_method")
            return None

        try:
            payment_method = PaymentMethod.objects.get(
                payment_method__iexact=payment_method_name
            )
            return payment_method
        except PaymentMethod.DoesNotExist:
            errors.append(
                f"Row {row_num}: Payment method '{payment_method_name}' not found"
            )
            return None
        except PaymentMethod.MultipleObjectsReturned:
            # If multiple found, get the first one
            payment_method = PaymentMethod.objects.filter(
                payment_method__iexact=payment_method_name
            ).first()
            return payment_method
