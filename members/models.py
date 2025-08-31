from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal


class MemberType(models.Model):
    """Different types of membership (Regular, Honorary, Life, etc.)"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    monthly_dues = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    annual_dues = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    """Payment methods (Cash, Check, Credit Card, etc.)"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Member(models.Model):
    """Main member information"""

    # Member identification
    member_id = models.CharField(
        max_length=20, unique=True, help_text="Unique member ID number"
    )

    # Personal information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)

    # Contact information
    home_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    work_phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    fax_number = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True)

    # Home address
    home_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")

    # Work information
    company_name = models.CharField(max_length=200, blank=True)
    work_title = models.CharField(max_length=100, blank=True)
    work_address = models.CharField(max_length=200, blank=True)
    work_city = models.CharField(max_length=100, blank=True)
    work_state = models.CharField(max_length=50, blank=True)
    work_zip_code = models.CharField(max_length=20, blank=True)
    work_country = models.CharField(max_length=100, blank=True)

    # Membership information
    member_type = models.ForeignKey(
        MemberType, on_delete=models.PROTECT, help_text="Type of membership"
    )
    date_joined = models.DateField(help_text="Date member joined the club")
    expires = models.DateField(
        blank=True, null=True, help_text="Membership expiration date"
    )
    milestone = models.DateField(
        blank=True, null=True, help_text="Important milestone date"
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_deceased = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Additional notes about the member")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["member_id"]),
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["member_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.member_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        parts = [self.home_address, self.city, self.state, self.zip_code]
        return ", ".join([part for part in parts if part])

    def is_membership_expired(self):
        """Check if membership has expired"""
        if not self.expires:
            return False
        return self.expires < timezone.now().date()


class Payment(models.Model):
    """Payment records for member dues"""

    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="payments"
    )
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

    # Payment details
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Payment amount"
    )
    payment_date = models.DateField(help_text="Date payment was received")
    period_start = models.DateField(
        blank=True, null=True, help_text="Start date of the period this payment covers"
    )
    period_end = models.DateField(
        blank=True, null=True, help_text="End date of the period this payment covers"
    )

    # Payment tracking
    check_number = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        max_length=100, blank=True
    )  # Who recorded the payment

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        indexes = [
            models.Index(fields=["member", "payment_date"]),
            models.Index(fields=["payment_date"]),
            models.Index(fields=["amount"]),
        ]

    def __str__(self):
        return f"{self.member.full_name} - ${self.amount} on {self.payment_date}"


class Friend(models.Model):
    """Friend/Associate members or connections"""

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="friends")
    friend_name = models.CharField(max_length=200)
    relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Relationship to member (spouse, friend, sponsor, etc.)",
    )
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["friend_name"]

    def __str__(self):
        return f"{self.friend_name} (friend of {self.member.full_name})"
