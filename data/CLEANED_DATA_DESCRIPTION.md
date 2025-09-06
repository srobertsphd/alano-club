# Alano Club Data Description

This document describes the structure and content of the five cleaned CSV files containing Alano Club member and payment data.

## Overview

The data consists of five interconnected CSV files representing different aspects of the club's membership system:

- **current_members.csv** - Active club members (335 records)
- **current_payments.csv** - Payment transaction history (722 records)  
- **current_dead.csv** - Inactive/deceased members (1,346 records)
- **current_member_types.csv** - Membership categories and pricing (8 types)
- **current_payment_methods.csv** - Payment methods lookup (10 methods)

## File Descriptions

### 1. current_members.csv

**Purpose**: Contains all currently active club members
**Records**: 335 members
**Primary Identifier**: `member_id` (note: not a primary key, rotates based on membership status)

#### Columns:

| Column | Data Type | Description | Notes |
|--------|-----------|-------------|-------|
| `member_id` | Integer | Assigned member ID | Rotates based on membership status |
| `first_name` | String | Member's first name | Required field |
| `last_name` | String | Member's last name | Required field |
| `member_type` | String | Type of membership | References `current_member_types.csv` |
| `home_address` | String | Street address | Optional, ~96% populated |
| `home_city` | String | City | ~98% populated |
| `home_state` | String | State abbreviation | 2-letter uppercase (e.g., CA, NY) |
| `home_zip` | String | ZIP code | 5-digit format, ~95% populated |
| `home_phone` | String | Phone number | Format: (XXX) XXX-XXXX, ~90% populated |
| `email` | String | Email address | ~90% populated |
| `date_joined` | Date | Date became a member | YYYY-MM-DD format |
| `milestone_date` | Date | Sobriety anniversary date | YYYY-MM-DD format, ~93% populated |
| `expiration_date` | Date | Membership paid through date | YYYY-MM-DD, Lifetime = 2099-12-31 |

#### Key Notes:
- **Lifetime members**: Have `expiration_date` set to `2099-12-31` (25 years from membership)
- **Member types**: Must reference valid entries in `current_member_types.csv`
- **Data quality**: All phone numbers follow standard (XXX) XXX-XXXX format

### 2. current_payments.csv

**Purpose**: Transaction history for all member payments
**Records**: 722 payment transactions
**Relationship**: Each record links to a member via `member_id`

#### Columns:

| Column | Data Type | Description | Notes |
|--------|-----------|-------------|-------|
| `member_id` | Integer | Member identifier | Links to members table |
| `first_name` | String | Member's first name | Duplicated from member record |
| `last_name` | String | Member's last name | Duplicated from member record |
| `member_type` | String | Type of membership | References `current_member_types.csv` |
| `home_address` | String | Street address | From member record at time of payment |
| `home_city` | String | City | From member record |
| `home_state` | String | State abbreviation | 2-letter uppercase |
| `home_zip` | String | ZIP code | 5-digit format |
| `home_phone` | String | Phone number | Format: (XXX) XXX-XXXX |
| `email` | String | Email address | From member record |
| `milestone_date` | Date | Sobriety anniversary | YYYY-MM-DD format |
| `date_joined` | Date | Date became member | YYYY-MM-DD format |
| `mobile_phone` | String | Mobile phone number | Very sparse data (~0.8%) |
| `expiration_date` | Date | Membership expiration | YYYY-MM-DD format |
| `payment_amount` | Float | Payment amount in USD | Required field |
| `payment_date` | Date | Date payment was made | YYYY-MM-DD format |
| `payment_method` | String | How payment was made | References `current_payment_methods.csv` |
| `receipt_number` | Integer | Manual receipt number | System-generated identifier |

#### Key Notes:
- **Multiple payments per member**: Members can have multiple payment records
- **Historical data**: Contains member information as it was at time of payment
- **Payment validation**: All records have valid `payment_amount` and `payment_method`

### 3. current_dead.csv

**Purpose**: Members who are inactive or deceased
**Records**: 1,346 historical members
**Status**: All members in this file are considered inactive

#### Columns:

| Column | Data Type | Description | Notes |
|--------|-----------|-------------|-------|
| `member_id` | Integer (nullable) | Former member ID | Can be null, IDs may be reused |
| `first_name` | String | Member's first name | Required field |
| `last_name` | String | Member's last name | Required field |
| `member_type` | String | Type of membership | When they were active |
| `home_address` | String | Street address | Last known address |
| `home_city` | String | City | Last known |
| `home_state` | String | State abbreviation | 2-letter uppercase |
| `home_zip` | String | ZIP code | 5-digit format |
| `home_phone` | String | Phone number | Format: (XXX) XXX-XXXX |
| `email` | String | Email address | Last known |
| `milestone_date` | Date | Sobriety anniversary | YYYY-MM-DD format |
| `date_joined` | Date | Date became member | YYYY-MM-DD format |
| `expiration_date` | Date | Last membership expiration | YYYY-MM-DD format |

#### Key Notes:
- **ID reuse**: `member_id` values may be rotated and assigned to new active members
- **Deduplication**: Duplicate names removed, keeping record with most recent `expiration_date`
- **Data preservation**: Contains historical membership information for record-keeping

### 4. current_member_types.csv

**Purpose**: Lookup table for membership categories and pricing
**Records**: 8 membership types
**Usage**: Referenced by all member and payment files

#### Columns:

| Column | Data Type | Description | Notes |
|--------|-----------|-------------|-------|
| `member_type` | String | Name of membership type | Primary identifier |
| `member_dues` | Float | Monthly dues amount in USD | Pricing structure |
| `num_months` | Float | Duration in months | 1.0 = monthly, 300.0 = lifetime |

#### Membership Types:

| Type | Monthly Dues | Duration | Description |
|------|--------------|----------|-------------|
| Senior | $20.00 | 1 month | Senior citizen discount |
| Fixed/Income | $20.00 | 1 month | Low-income discount |
| Regular | $30.00 | 1 month | Standard membership |
| Life | $3,000.00 | 300 months | One-time lifetime payment |
| Couple | $40.00 | 1 month | Two-person membership |
| FarAway Friends | $20.00 | 1 month | Non-local members |
| 500 Club | $500.00 | 12 months | Annual premium membership |
| Honorary | $0.00 | 1 month | Complimentary membership |

### 5. current_payment_methods.csv

**Purpose**: Lookup table for valid payment methods
**Records**: 10 payment methods
**Usage**: Referenced by payment records

#### Payment Methods:

| Method | Description |
|--------|-------------|
| Cash | Cash payments |
| Check | Paper checks |
| Venmo | Digital payment app |
| PayPal | Digital payment platform |
| Zelle | Bank transfer app |
| Work | Work-related payments |
| Life | Lifetime membership payments |
| Board Elect | Board election related |
| Partial Payment | Installment payments |
| Other | Miscellaneous methods |

## Data Relationships

```
current_member_types.csv
    ↓ (member_type)
current_members.csv ← current_dead.csv
    ↓ (member_id)
current_payments.csv
    ↓ (payment_method)
current_payment_methods.csv
```

## Data Quality Notes

1. **Phone Numbers**: All standardized to (XXX) XXX-XXXX format
2. **State Codes**: Standardized to 2-letter uppercase abbreviations
3. **ZIP Codes**: Cleaned to 5-digit format
4. **Duplicates**: Removed from dead members file using latest expiration date
5. **Required Fields**: Member ID, names, and core payment data fully populated
6. **Optional Fields**: Contact information may be missing for some records

## Data Processing History

All files have been cleaned and standardized from original Excel sources:
- Column names converted to snake_case
- Date fields converted to YYYY-MM-DD format
- Phone numbers standardized
- State abbreviations normalized
- Duplicate records removed
- Invalid data cleaned or removed

## Usage Recommendations

1. **Primary Keys**: Use combination of `member_id` + `first_name` + `last_name` for unique identification
2. **Member Lookups**: Always validate against both active and inactive member lists
3. **Payment Validation**: Ensure payment methods and member types reference lookup tables
4. **ID Management**: Be aware that `member_id` values may be reused from inactive members
