import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from members.models import PaymentMethod


class Command(BaseCommand):
    help = "Import payment methods from current_payment_methods.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="data/2025_09_02/cleaned/current_payment_methods.csv",
            help="Path to payment methods CSV file",
        )
        parser.add_argument(
            "--clear-existing",
            action="store_true",
            help="Clear existing payment methods before import",
        )

    def handle(self, *args, **options):
        csv_file = Path(options["csv_file"])

        if not csv_file.exists():
            raise CommandError(f"CSV file not found: {csv_file}")

        if options["clear_existing"]:
            self.stdout.write("🗑️  Clearing existing payment methods...")
            PaymentMethod.objects.all().delete()
            self.stdout.write("   ✅ Payment methods cleared")

        try:
            with transaction.atomic():
                self.import_payment_methods(csv_file)
                self.stdout.write(
                    self.style.SUCCESS(
                        "\n✅ Payment methods import completed successfully!"
                    )
                )

        except Exception as e:
            raise CommandError(f"Import failed: {e}")

    def import_payment_methods(self, csv_file):
        """Import payment methods from CSV file"""
        self.stdout.write(f"\n💳 Importing payment methods from: {csv_file}")

        with open(csv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            created_count = 0
            error_count = 0
            errors = []

            for row_num, row in enumerate(reader, 2):  # Start at 2 (after header)
                try:
                    # Required field
                    payment_method = row.get("payment_method", "").strip()
                    if not payment_method:
                        errors.append(f"Row {row_num}: Missing payment_method")
                        continue

                    # Create or get payment method
                    payment_method_obj, created = PaymentMethod.objects.get_or_create(
                        payment_method=payment_method
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f"   ✅ Created: {payment_method_obj}")
                    else:
                        self.stdout.write(f"   ⚠️  Exists: {payment_method_obj}")

                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error - {e}")
                    error_count += 1

        # Show summary
        self.stdout.write("\n📊 Import Summary:")
        self.stdout.write(f"   💳 Payment methods created: {created_count}")
        self.stdout.write(f"   ❌ Errors: {len(errors)}")

        # Show errors if any
        if errors:
            self.stdout.write("\n❌ Errors encountered:")
            for error in errors:
                self.stdout.write(f"   {error}")
