"""
Business logic services for members and payments.

This module contains service classes that encapsulate business logic
for member and payment operations, separating concerns from views.
"""

from decimal import Decimal
from datetime import datetime
from .models import Payment, PaymentMethod
from .utils import add_months_to_date


class PaymentService:
    """Service class for payment-related business logic"""

    @staticmethod
    def calculate_expiration(member, payment_amount, override_expiration=None):
        """
        Calculate new expiration date based on payment amount.

        Args:
            member: Member instance
            payment_amount: Decimal payment amount
            override_expiration: Optional date to override calculation

        Returns:
            date: New expiration date
        """
        if override_expiration:
            return override_expiration

        if member.member_type and member.member_type.member_dues > 0:
            months_paid = float(payment_amount) / float(member.member_type.member_dues)
            total_months_to_add = int(months_paid)
            return add_months_to_date(member.expiration_date, total_months_to_add)
        else:
            return add_months_to_date(member.expiration_date, 1)

    @staticmethod
    def process_payment(member, payment_data):
        """
        Create payment record and update member expiration.

        Args:
            member: Member instance
            payment_data: Dict with payment details:
                - payment_method_id: PaymentMethod ID
                - amount: Payment amount (string)
                - payment_date: Payment date (ISO format string)
                - receipt_number: Receipt number (string)
                - new_expiration: New expiration date (ISO format string)

        Returns:
            tuple: (payment_instance, was_reactivated_bool)
        """
        payment_method = PaymentMethod.objects.get(pk=payment_data["payment_method_id"])

        # Create payment
        payment = Payment.objects.create(
            member=member,
            payment_method=payment_method,
            amount=Decimal(payment_data["amount"]),
            date=datetime.fromisoformat(payment_data["payment_date"]).date(),
            receipt_number=payment_data["receipt_number"],
        )

        # Update member expiration
        member.expiration_date = datetime.fromisoformat(
            payment_data["new_expiration"]
        ).date()

        # Reactivate if inactive
        was_inactive = member.status == "inactive"
        if was_inactive:
            member.status = "active"
            member.date_inactivated = None

        member.save()

        return payment, was_inactive
