#!/usr/bin/env python
"""
Script to create sample data for the Alano Club member management system.
Run this after setting up the database to get some initial data.

Usage: python setup_sample_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alano_club_site.settings")
django.setup()

from members.models import MemberType, PaymentMethod, Member, Payment, Friend


def create_sample_data():
    print("Creating sample data for Alano Club...")

    # Create Member Types
    regular, created = MemberType.objects.get_or_create(
        name="Regular",
        defaults={
            "description": "Standard club membership",
            "monthly_dues": Decimal("150.00"),
            "annual_dues": Decimal("1800.00"),
        },
    )

    honorary, created = MemberType.objects.get_or_create(
        name="Honorary",
        defaults={
            "description": "Honorary membership - no dues",
            "monthly_dues": Decimal("0.00"),
            "annual_dues": Decimal("0.00"),
        },
    )

    life, created = MemberType.objects.get_or_create(
        name="Life",
        defaults={
            "description": "Lifetime membership",
            "monthly_dues": Decimal("0.00"),
            "annual_dues": Decimal("0.00"),
        },
    )

    # Create Payment Methods
    cash, created = PaymentMethod.objects.get_or_create(name="Cash")
    check, created = PaymentMethod.objects.get_or_create(name="Check")
    credit_card, created = PaymentMethod.objects.get_or_create(name="Credit Card")
    bank_transfer, created = PaymentMethod.objects.get_or_create(name="Bank Transfer")

    # Create Sample Members
    member1, created = Member.objects.get_or_create(
        member_id="332",
        defaults={
            "first_name": "Maria",
            "last_name": "Salazar",
            "email": "maria.salazar@email.com",
            "home_phone": "(408) 705-3792",
            "home_address": "238 N. 15th St.",
            "city": "San Jose",
            "state": "CA",
            "zip_code": "95112",
            "member_type": regular,
            "date_joined": date(2025, 5, 4),
            "expires": date(2025, 11, 30),
            "milestone": date(2025, 4, 1),
        },
    )

    member2, created = Member.objects.get_or_create(
        member_id="445",
        defaults={
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@email.com",
            "home_phone": "(408) 555-1234",
            "home_address": "123 Main St.",
            "city": "San Jose",
            "state": "CA",
            "zip_code": "95110",
            "member_type": regular,
            "date_joined": date(2020, 1, 15),
            "expires": date(2025, 12, 31),
        },
    )

    member3, created = Member.objects.get_or_create(
        member_id="100",
        defaults={
            "first_name": "Betty",
            "last_name": "Johnson",
            "email": "betty.johnson@email.com",
            "home_phone": "(408) 555-5678",
            "home_address": "456 Oak Avenue",
            "city": "Santa Clara",
            "state": "CA",
            "zip_code": "95051",
            "member_type": honorary,
            "date_joined": date(2010, 3, 20),
        },
    )

    # Create Sample Payments
    Payment.objects.get_or_create(
        member=member1,
        payment_date=date(2025, 1, 15),
        defaults={
            "amount": Decimal("150.00"),
            "payment_method": check,
            "check_number": "1234",
            "period_start": date(2025, 1, 1),
            "period_end": date(2025, 1, 31),
            "created_by": "admin",
        },
    )

    Payment.objects.get_or_create(
        member=member2,
        payment_date=date(2025, 1, 10),
        defaults={
            "amount": Decimal("1800.00"),
            "payment_method": bank_transfer,
            "period_start": date(2025, 1, 1),
            "period_end": date(2025, 12, 31),
            "notes": "Annual payment",
            "created_by": "admin",
        },
    )

    # Create Sample Friends
    Friend.objects.get_or_create(
        member=member1,
        friend_name="Carlos Salazar",
        defaults={
            "relationship": "Spouse",
            "phone": "(408) 705-3793",
            "email": "carlos.salazar@email.com",
        },
    )

    print("Sample data created successfully!")
    print(f"Created {MemberType.objects.count()} member types")
    print(f"Created {PaymentMethod.objects.count()} payment methods")
    print(f"Created {Member.objects.count()} members")
    print(f"Created {Payment.objects.count()} payments")
    print(f"Created {Friend.objects.count()} friends")


if __name__ == "__main__":
    create_sample_data()
