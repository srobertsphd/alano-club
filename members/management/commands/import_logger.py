"""
Enhanced logging utility for import commands.
Creates detailed log files with all errors, successes, and skipped records.
"""

import os
from datetime import datetime
from pathlib import Path


class ImportLogger:
    """Enhanced logging for import commands with file output"""

    def __init__(self, command_name, csv_file_path):
        self.command_name = command_name
        self.csv_file_path = Path(csv_file_path)
        self.csv_filename = self.csv_file_path.name

        # Create logs directory if it doesn't exist
        self.logs_dir = Path("logs/imports")
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for this import session
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create log file paths
        self.error_log_file = (
            self.logs_dir / f"{self.command_name}_{self.timestamp}_ERRORS.log"
        )
        self.success_log_file = (
            self.logs_dir / f"{self.command_name}_{self.timestamp}_SUCCESS.log"
        )
        self.summary_log_file = (
            self.logs_dir / f"{self.command_name}_{self.timestamp}_SUMMARY.txt"
        )

        # Initialize counters
        self.created_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.duplicate_count = 0

        # Initialize log files
        self._init_log_files()

    def _init_log_files(self):
        """Initialize log files with headers"""
        # Error log header
        with open(self.error_log_file, "w") as f:
            f.write(f"ERROR LOG - {self.command_name.upper()}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"CSV File: {self.csv_file_path}\n")
            f.write("=" * 80 + "\n\n")

        # Success log header
        with open(self.success_log_file, "w") as f:
            f.write(f"SUCCESS LOG - {self.command_name.upper()}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"CSV File: {self.csv_file_path}\n")
            f.write("=" * 80 + "\n\n")

    def log_error(self, row_num, error_message, row_data=None):
        """Log an error with row details"""
        self.error_count += 1

        with open(self.error_log_file, "a") as f:
            f.write(f"ERROR #{self.error_count}\n")
            f.write(f"File: {self.csv_filename}\n")
            f.write(f"Row: {row_num}\n")
            f.write(f"Error: {error_message}\n")

            if row_data:
                f.write("Row Data:\n")
                for key, value in row_data.items():
                    f.write(f"  {key}: {value}\n")

            f.write("-" * 50 + "\n\n")

    def log_success(self, row_num, success_message, created_object=None):
        """Log a successful import"""
        self.created_count += 1

        with open(self.success_log_file, "a") as f:
            f.write(f"SUCCESS #{self.created_count}\n")
            f.write(f"File: {self.csv_filename}\n")
            f.write(f"Row: {row_num}\n")
            f.write(f"Result: {success_message}\n")

            if created_object:
                f.write(f"Created: {created_object}\n")

            f.write("-" * 30 + "\n\n")

    def log_skipped(self, row_num, reason, row_data=None):
        """Log a skipped record"""
        self.skipped_count += 1

        with open(self.error_log_file, "a") as f:
            f.write(f"SKIPPED #{self.skipped_count}\n")
            f.write(f"File: {self.csv_filename}\n")
            f.write(f"Row: {row_num}\n")
            f.write(f"Reason: {reason}\n")

            if row_data:
                f.write("Row Data:\n")
                for key, value in row_data.items():
                    f.write(f"  {key}: {value}\n")

            f.write("-" * 40 + "\n\n")

    def log_duplicate(self, row_num, duplicate_info, row_data=None):
        """Log a duplicate record"""
        self.duplicate_count += 1

        with open(self.error_log_file, "a") as f:
            f.write(f"DUPLICATE #{self.duplicate_count}\n")
            f.write(f"File: {self.csv_filename}\n")
            f.write(f"Row: {row_num}\n")
            f.write(f"Duplicate: {duplicate_info}\n")

            if row_data:
                f.write("Row Data:\n")
                for key, value in row_data.items():
                    f.write(f"  {key}: {value}\n")

            f.write("-" * 40 + "\n\n")

    def write_summary(self, additional_stats=None):
        """Write final summary to summary log file"""
        with open(self.summary_log_file, "w") as f:
            f.write(f"IMPORT SUMMARY - {self.command_name.upper()}\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"CSV File: {self.csv_file_path}\n")
            f.write("=" * 60 + "\n\n")

            f.write("RESULTS:\n")
            f.write(f"  ✅ Successfully Created: {self.created_count}\n")
            f.write(f"  ❌ Errors: {self.error_count}\n")
            f.write(f"  ⚠️  Skipped: {self.skipped_count}\n")
            f.write(f"  🔄 Duplicates: {self.duplicate_count}\n")
            f.write(
                f"  📊 Total Processed: {self.created_count + self.error_count + self.skipped_count + self.duplicate_count}\n\n"
            )

            if additional_stats:
                f.write("ADDITIONAL STATISTICS:\n")
                for key, value in additional_stats.items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

            f.write("LOG FILES:\n")
            f.write(f"  Errors/Skipped: {self.error_log_file}\n")
            f.write(f"  Successes: {self.success_log_file}\n")
            f.write(f"  Summary: {self.summary_log_file}\n")

    def print_console_summary(self, stdout):
        """Print summary to console"""
        stdout.write(f"\n📊 Import Summary:")
        stdout.write(f"   ✅ Created: {self.created_count}")
        stdout.write(f"   ❌ Errors: {self.error_count}")
        stdout.write(f"   ⚠️  Skipped: {self.skipped_count}")
        stdout.write(f"   🔄 Duplicates: {self.duplicate_count}")
        stdout.write(f"\n📁 Detailed logs written to:")
        stdout.write(f"   {self.error_log_file}")
        stdout.write(f"   {self.success_log_file}")
        stdout.write(f"   {self.summary_log_file}")

    def get_stats(self):
        """Return current statistics"""
        return {
            "created": self.created_count,
            "errors": self.error_count,
            "skipped": self.skipped_count,
            "duplicates": self.duplicate_count,
            "total": self.created_count
            + self.error_count
            + self.skipped_count
            + self.duplicate_count,
        }
