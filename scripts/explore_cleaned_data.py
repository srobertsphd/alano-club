"""
Data Exploration Script for Cleaned CSV Files

This script performs comprehensive data quality checks on cleaned CSV files.
Modify the DATE variable at the top to explore different data sets.
"""

import pandas as pd
from pathlib import Path

################################################################
# CONFIGURATION - Modify this date to explore different datasets
################################################################
DATE = "2025_12_06"  # Format: YYYY_MM_DD

################################################################
# Setup
################################################################
base_dir = Path(__file__).parent.parent
cleaned_dir = base_dir / "data" / DATE / "cleaned"

print("=" * 80)
print(f"DATA EXPLORATION REPORT: {DATE}")
print("=" * 80)
print(f"Cleaned directory: {cleaned_dir}")
print()

if not cleaned_dir.exists():
    print(f"❌ ERROR: Cleaned directory does not exist: {cleaned_dir}")
    exit(1)

################################################################
# Helper Functions
################################################################


def check_phone_format(phone_series, file_name):
    """Check phone number formatting"""
    pattern = r"^\(\d{3}\) \d{3}-\d{4}$"
    non_null_phones = phone_series.dropna()

    if len(non_null_phones) == 0:
        return {"total": 0, "correct": 0, "incorrect": 0, "examples": []}

    properly_formatted = non_null_phones.str.match(pattern, na=False)
    correct_count = properly_formatted.sum()
    incorrect_count = len(non_null_phones) - correct_count

    examples = []
    if incorrect_count > 0:
        incorrect_phones = non_null_phones[~properly_formatted].head(10)
        examples = incorrect_phones.tolist()

    return {
        "total": len(non_null_phones),
        "correct": correct_count,
        "incorrect": incorrect_count,
        "examples": examples,
    }


def check_state_abbreviations(state_series, file_name):
    """Check state abbreviations are proper 2-letter codes"""
    valid_states = {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
    }

    non_null_states = state_series.dropna()

    if len(non_null_states) == 0:
        return {"total": 0, "valid": 0, "invalid": 0, "invalid_examples": {}}

    valid_mask = non_null_states.str.upper().isin(valid_states)
    valid_count = valid_mask.sum()
    invalid_count = len(non_null_states) - valid_count

    invalid_examples = {}
    if invalid_count > 0:
        invalid_states = non_null_states[~valid_mask]
        invalid_counts = invalid_states.value_counts().head(10)
        invalid_examples = invalid_counts.to_dict()

    return {
        "total": len(non_null_states),
        "valid": valid_count,
        "invalid": invalid_count,
        "invalid_examples": invalid_examples,
    }


def check_zip_format(zip_series, file_name):
    """Check zip codes are 5-digit format"""
    non_null_zips = zip_series.dropna().astype(str)

    if len(non_null_zips) == 0:
        return {"total": 0, "valid": 0, "invalid": 0, "examples": []}

    # Convert float strings like "95070.0" to "95070"
    non_null_zips = non_null_zips.str.replace(r"\.0$", "", regex=True)

    # Check if all are 5 digits (after removing any hyphens/extensions)
    valid_mask = (
        non_null_zips.str.replace("-", "").str.replace(" ", "").str.match(r"^\d{5}$")
    )
    valid_count = valid_mask.sum()
    invalid_count = len(non_null_zips) - valid_count

    examples = []
    if invalid_count > 0:
        invalid_zips = non_null_zips[~valid_mask].head(10)
        examples = invalid_zips.tolist()

    return {
        "total": len(non_null_zips),
        "valid": valid_count,
        "invalid": invalid_count,
        "examples": examples,
    }


def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_field_summary(df, field_name, file_name):
    """Print summary for a field"""
    if field_name not in df.columns:
        print(f"  ⚠️  Field '{field_name}' not found in {file_name}")
        return

    non_null = df[field_name].notna().sum()
    null_count = df[field_name].isna().sum()
    total = len(df)
    pct = (non_null / total * 100) if total > 0 else 0

    print(f"\n  📊 {field_name}:")
    print(f"     Non-null: {non_null:,} ({pct:.1f}%)")
    print(f"     Null: {null_count:,} ({100 - pct:.1f}%)")

    if non_null > 0:
        if df[field_name].dtype in ["object", "string"]:
            unique_count = df[field_name].nunique()
            print(f"     Unique values: {unique_count:,}")
            if unique_count <= 20:
                print("     Value counts:")
                for val, count in df[field_name].value_counts().head(10).items():
                    print(f"       {val}: {count:,}")


################################################################
# Explore current_members.csv
################################################################

members_file = cleaned_dir / "current_members.csv"
if members_file.exists():
    print_section_header("CURRENT MEMBERS (Active)")
    print(f"File: {members_file.name}")

    df_members = pd.read_csv(members_file)
    print(f"\n  📈 Total Records: {len(df_members):,}")
    print(f"  📋 Columns: {len(df_members.columns)}")
    print(
        f"  💾 Memory Usage: {df_members.memory_usage(deep=True).sum() / 1024:.1f} KB"
    )

    # Check critical fields
    print_field_summary(df_members, "member_id", "current_members.csv")
    print_field_summary(df_members, "first_name", "current_members.csv")
    print_field_summary(df_members, "last_name", "current_members.csv")
    print_field_summary(df_members, "member_type", "current_members.csv")
    print_field_summary(df_members, "email", "current_members.csv")

    # Check for missing critical data
    print("\n  🔍 Critical Data Checks:")
    missing_last_name = df_members["last_name"].isna().sum()
    missing_first_name = df_members["first_name"].isna().sum()
    missing_member_id = df_members["member_id"].isna().sum()
    missing_member_type = df_members["member_type"].isna().sum()

    if missing_last_name > 0:
        print(f"     ⚠️  Missing last_name: {missing_last_name} records")
        print(
            f"        Examples: {df_members[df_members['last_name'].isna()][['member_id', 'first_name']].head().to_string()}"
        )
    else:
        print("     ✅ All records have last_name")

    if missing_first_name > 0:
        print(f"     ⚠️  Missing first_name: {missing_first_name} records")
    else:
        print("     ✅ All records have first_name")

    if missing_member_id > 0:
        print(f"     ⚠️  Missing member_id: {missing_member_id} records")
    else:
        print("     ✅ All records have member_id")

    if missing_member_type > 0:
        print(f"     ⚠️  Missing member_type: {missing_member_type} records")
    else:
        print("     ✅ All records have member_type")

    # Phone number check
    if "home_phone" in df_members.columns:
        phone_check = check_phone_format(
            df_members["home_phone"], "current_members.csv"
        )
        print("\n  📞 Phone Number Format Check:")
        print(f"     Total: {phone_check['total']:,}")
        print(
            f"     Correctly formatted: {phone_check['correct']:,} ({phone_check['correct'] / phone_check['total'] * 100:.1f}%)"
            if phone_check["total"] > 0
            else "     No phone numbers"
        )
        if phone_check["incorrect"] > 0:
            print(f"     ⚠️  Incorrectly formatted: {phone_check['incorrect']:,}")
            print(f"        Examples: {phone_check['examples'][:5]}")
        else:
            print("     ✅ All phone numbers properly formatted")

    # State check
    if "home_state" in df_members.columns:
        state_check = check_state_abbreviations(
            df_members["home_state"], "current_members.csv"
        )
        print("\n  🗺️  State Abbreviation Check:")
        print(f"     Total: {state_check['total']:,}")
        print(
            f"     Valid abbreviations: {state_check['valid']:,} ({state_check['valid'] / state_check['total'] * 100:.1f}%)"
            if state_check["total"] > 0
            else "     No states"
        )
        if state_check["invalid"] > 0:
            print(f"     ⚠️  Invalid abbreviations: {state_check['invalid']:,}")
            print(
                f"        Examples: {list(state_check['invalid_examples'].items())[:5]}"
            )
        else:
            print("     ✅ All states are valid abbreviations")

    # Zip code check
    if "home_zip" in df_members.columns:
        zip_check = check_zip_format(df_members["home_zip"], "current_members.csv")
        print("\n  📮 Zip Code Format Check:")
        print(f"     Total: {zip_check['total']:,}")
        print(
            f"     Valid format: {zip_check['valid']:,} ({zip_check['valid'] / zip_check['total'] * 100:.1f}%)"
            if zip_check["total"] > 0
            else "     No zip codes"
        )
        if zip_check["invalid"] > 0:
            print(f"     ⚠️  Invalid format: {zip_check['invalid']:,}")
            print(f"        Examples: {zip_check['examples'][:5]}")
        else:
            print("     ✅ All zip codes properly formatted")

    # Date checks
    print("\n  📅 Date Field Checks:")
    for date_field in ["date_joined", "milestone_date", "expiration_date"]:
        if date_field in df_members.columns:
            non_null = df_members[date_field].notna().sum()
            null_count = df_members[date_field].isna().sum()
            print(f"     {date_field}: {non_null:,} non-null, {null_count:,} null")

    # Check for duplicate member IDs
    if "member_id" in df_members.columns:
        duplicate_ids = (
            df_members[df_members["member_id"].notna()]["member_id"].duplicated().sum()
        )
        if duplicate_ids > 0:
            print(f"\n  ⚠️  Duplicate member_ids found: {duplicate_ids}")
            dup_ids = df_members[df_members["member_id"].notna()][
                df_members[df_members["member_id"].notna()]["member_id"].duplicated(
                    keep=False
                )
            ]["member_id"].unique()
            print(f"        Duplicate IDs: {dup_ids[:10].tolist()}")
        else:
            print("\n  ✅ No duplicate member_ids")
else:
    print(f"⚠️  File not found: {members_file}")


################################################################
# Explore current_dead.csv
################################################################

dead_file = cleaned_dir / "current_dead.csv"
if dead_file.exists():
    print_section_header("CURRENT DEAD (Inactive/Deceased)")
    print(f"File: {dead_file.name}")

    df_dead = pd.read_csv(dead_file)
    print(f"\n  📈 Total Records: {len(df_dead):,}")
    print(f"  📋 Columns: {len(df_dead.columns)}")
    print(f"  💾 Memory Usage: {df_dead.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # Check critical fields
    print_field_summary(df_dead, "member_id", "current_dead.csv")
    print_field_summary(df_dead, "first_name", "current_dead.csv")
    print_field_summary(df_dead, "last_name", "current_dead.csv")
    print_field_summary(df_dead, "member_type", "current_dead.csv")

    # Check for missing critical data
    print("\n  🔍 Critical Data Checks:")
    missing_last_name = df_dead["last_name"].isna().sum()
    missing_first_name = df_dead["first_name"].isna().sum()
    missing_member_id = df_dead["member_id"].isna().sum()

    if missing_last_name > 0:
        print(f"     ⚠️  Missing last_name: {missing_last_name} records")
    else:
        print("     ✅ All records have last_name")

    if missing_first_name > 0:
        print(f"     ⚠️  Missing first_name: {missing_first_name} records")
    else:
        print("     ✅ All records have first_name")

    if missing_member_id > 0:
        print(
            f"     ℹ️  Missing member_id: {missing_member_id} records (expected for historical records)"
        )
    else:
        print("     ✅ All records have member_id")

    # Phone number check
    if "home_phone" in df_dead.columns:
        phone_check = check_phone_format(df_dead["home_phone"], "current_dead.csv")
        print("\n  📞 Phone Number Format Check:")
        print(f"     Total: {phone_check['total']:,}")
        print(
            f"     Correctly formatted: {phone_check['correct']:,} ({phone_check['correct'] / phone_check['total'] * 100:.1f}%)"
            if phone_check["total"] > 0
            else "     No phone numbers"
        )
        if phone_check["incorrect"] > 0:
            print(f"     ⚠️  Incorrectly formatted: {phone_check['incorrect']:,}")
            print(f"        Examples: {phone_check['examples'][:5]}")
        else:
            print("     ✅ All phone numbers properly formatted")

    # State check
    if "home_state" in df_dead.columns:
        state_check = check_state_abbreviations(
            df_dead["home_state"], "current_dead.csv"
        )
        print("\n  🗺️  State Abbreviation Check:")
        print(f"     Total: {state_check['total']:,}")
        print(
            f"     Valid abbreviations: {state_check['valid']:,} ({state_check['valid'] / state_check['total'] * 100:.1f}%)"
            if state_check["total"] > 0
            else "     No states"
        )
        if state_check["invalid"] > 0:
            print(f"     ⚠️  Invalid abbreviations: {state_check['invalid']:,}")
            print(
                f"        Examples: {list(state_check['invalid_examples'].items())[:5]}"
            )
        else:
            print("     ✅ All states are valid abbreviations")

    # Check for duplicate names
    if "first_name" in df_dead.columns and "last_name" in df_dead.columns:
        df_dead["full_name"] = df_dead["first_name"] + " " + df_dead["last_name"]
        duplicate_names = df_dead["full_name"].duplicated().sum()
        if duplicate_names > 0:
            print(f"\n  ⚠️  Duplicate name combinations found: {duplicate_names}")
            dup_names = (
                df_dead[df_dead["full_name"].duplicated(keep=False)]["full_name"]
                .value_counts()
                .head(5)
            )
            print("        Top duplicates:")
            for name, count in dup_names.items():
                print(f"          {name}: {count}")
        else:
            print("\n  ✅ No duplicate name combinations")
else:
    print(f"⚠️  File not found: {dead_file}")


################################################################
# Explore current_payments.csv
################################################################

payments_file = cleaned_dir / "current_payments.csv"
if payments_file.exists():
    print_section_header("CURRENT PAYMENTS")
    print(f"File: {payments_file.name}")

    df_payments = pd.read_csv(payments_file)
    print(f"\n  📈 Total Records: {len(df_payments):,}")
    print(f"  📋 Columns: {len(df_payments.columns)}")
    print(
        f"  💾 Memory Usage: {df_payments.memory_usage(deep=True).sum() / 1024:.1f} KB"
    )

    # Check critical fields
    print_field_summary(df_payments, "member_id", "current_payments.csv")
    print_field_summary(df_payments, "payment_method", "current_payments.csv")
    print_field_summary(df_payments, "payment_amount", "current_payments.csv")
    print_field_summary(df_payments, "payment_date", "current_payments.csv")

    # Check for missing critical data
    print("\n  🔍 Critical Data Checks:")
    missing_member_id = df_payments["member_id"].isna().sum()
    missing_payment_amount = df_payments["payment_amount"].isna().sum()
    missing_payment_date = df_payments["payment_date"].isna().sum()
    missing_payment_method = df_payments["payment_method"].isna().sum()

    if missing_member_id > 0:
        print(f"     ⚠️  Missing member_id: {missing_member_id} records")
    else:
        print("     ✅ All records have member_id")

    if missing_payment_amount > 0:
        print(f"     ⚠️  Missing payment_amount: {missing_payment_amount} records")
    else:
        print("     ✅ All records have payment_amount")

    if missing_payment_date > 0:
        print(f"     ⚠️  Missing payment_date: {missing_payment_date} records")
    else:
        print("     ✅ All records have payment_date")

    if missing_payment_method > 0:
        print(f"     ⚠️  Missing payment_method: {missing_payment_method} records")
    else:
        print("     ✅ All records have payment_method")

    # Payment amount analysis
    if "payment_amount" in df_payments.columns:
        print("\n  💰 Payment Amount Analysis:")
        print(f"     Total payments: ${df_payments['payment_amount'].sum():,.2f}")
        print(f"     Average payment: ${df_payments['payment_amount'].mean():,.2f}")
        print(f"     Median payment: ${df_payments['payment_amount'].median():,.2f}")
        print(f"     Min payment: ${df_payments['payment_amount'].min():,.2f}")
        print(f"     Max payment: ${df_payments['payment_amount'].max():,.2f}")

        # Check for zero or negative amounts
        zero_or_negative = (df_payments["payment_amount"] <= 0).sum()
        if zero_or_negative > 0:
            print(f"     ⚠️  Zero or negative amounts: {zero_or_negative} records")
        else:
            print("     ✅ All payment amounts are positive")

    # Check for duplicate payments (same member, amount, date)
    if all(
        col in df_payments.columns
        for col in ["member_id", "payment_amount", "payment_date"]
    ):
        duplicate_payments = df_payments.duplicated(
            subset=["member_id", "payment_amount", "payment_date"]
        ).sum()
        if duplicate_payments > 0:
            print(f"\n  ⚠️  Potential duplicate payments: {duplicate_payments}")
            print("        (Same member_id, payment_amount, and payment_date)")
        else:
            print("\n  ✅ No duplicate payments detected")

    # Date range check
    if "payment_date" in df_payments.columns:
        try:
            df_payments["payment_date_parsed"] = pd.to_datetime(
                df_payments["payment_date"], errors="coerce"
            )
            min_date = df_payments["payment_date_parsed"].min()
            max_date = df_payments["payment_date_parsed"].max()
            print("\n  📅 Payment Date Range:")
            print(f"     Earliest payment: {min_date}")
            print(f"     Latest payment: {max_date}")
        except Exception:
            print("\n  ⚠️  Could not parse payment dates")
else:
    print(f"⚠️  File not found: {payments_file}")


################################################################
# Cross-file Validation
################################################################

print_section_header("CROSS-FILE VALIDATION")

if members_file.exists() and payments_file.exists():
    df_members = pd.read_csv(members_file)
    df_payments = pd.read_csv(payments_file)

    # Check if all payment members exist in members file
    payment_member_ids = set(df_payments["member_id"].dropna().unique())
    member_ids = set(df_members["member_id"].dropna().unique())

    missing_members = payment_member_ids - member_ids

    print("\n  🔗 Payment-to-Member Validation:")
    print(f"     Unique members in payments: {len(payment_member_ids):,}")
    print(f"     Unique members in members file: {len(member_ids):,}")
    print(f"     Payment members not in members file: {len(missing_members):,}")

    if len(missing_members) > 0:
        print(f"     ⚠️  Missing member IDs: {list(missing_members)[:10]}")
    else:
        print("     ✅ All payment members exist in members file")


################################################################
# Summary
################################################################

print_section_header("SUMMARY")

files_found = []
if members_file.exists():
    files_found.append(
        f"current_members.csv ({len(pd.read_csv(members_file)):,} records)"
    )
if dead_file.exists():
    files_found.append(f"current_dead.csv ({len(pd.read_csv(dead_file)):,} records)")
if payments_file.exists():
    files_found.append(
        f"current_payments.csv ({len(pd.read_csv(payments_file)):,} records)"
    )

print(f"\n  ✅ Files found: {len(files_found)}")
for file_info in files_found:
    print(f"     - {file_info}")

print("\n  📊 Data Quality Checks Completed")
print("     - Phone number format validation")
print("     - State abbreviation validation")
print("     - Zip code format validation")
print("     - Critical field completeness")
print("     - Duplicate detection")
print("     - Cross-file validation")

print("\n" + "=" * 80)
print("Exploration complete!")
print("=" * 80)
