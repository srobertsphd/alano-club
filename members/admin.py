from django.contrib import admin
from django.utils.html import format_html
from .models import Member, MemberType, PaymentMethod, Payment, Friend


@admin.register(MemberType)
class MemberTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "monthly_dues", "annual_dues", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["name"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = [
        "payment_date",
        "amount",
        "payment_method",
        "period_start",
        "period_end",
        "check_number",
    ]
    ordering = ["-payment_date"]


class FriendInline(admin.TabularInline):
    model = Friend
    extra = 1
    fields = ["friend_name", "relationship", "phone", "email"]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        "member_id",
        "full_name",
        "member_type",
        "city",
        "state",
        "home_phone",
        "date_joined",
        "expires",
        "membership_status",
        "payment_status",
    ]
    list_filter = [
        "member_type",
        "is_active",
        "is_deceased",
        "state",
        "date_joined",
        "expires",
    ]
    search_fields = [
        "member_id",
        "first_name",
        "last_name",
        "email",
        "home_phone",
        "city",
        "company_name",
    ]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Member Identification", {"fields": ("member_id", "member_type")}),
        ("Personal Information", {"fields": ("first_name", "last_name", "email")}),
        (
            "Home Contact Information",
            {
                "fields": (
                    "home_phone",
                    "home_address",
                    "city",
                    "state",
                    "zip_code",
                    "country",
                )
            },
        ),
        (
            "Work Information",
            {
                "fields": (
                    "company_name",
                    "work_title",
                    "work_phone",
                    "extension",
                    "work_address",
                    "work_city",
                    "work_state",
                    "work_zip_code",
                    "work_country",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            "Additional Contact",
            {"fields": ("mobile_phone", "fax_number"), "classes": ["collapse"]},
        ),
        ("Membership Details", {"fields": ("date_joined", "expires", "milestone")}),
        ("Status & Notes", {"fields": ("is_active", "is_deceased", "notes")}),
        (
            "System Information",
            {"fields": ("created_at", "updated_at"), "classes": ["collapse"]},
        ),
    )

    inlines = [PaymentInline, FriendInline]

    ordering = ["last_name", "first_name"]

    def membership_status(self, obj):
        if obj.is_deceased:
            return format_html('<span style="color: red;">Deceased</span>')
        elif not obj.is_active:
            return format_html('<span style="color: orange;">Inactive</span>')
        elif obj.is_membership_expired():
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')

    membership_status.short_description = "Status"

    def payment_status(self, obj):
        recent_payments = obj.payments.filter(payment_date__gte="2024-01-01").count()
        if recent_payments > 0:
            return format_html(
                f'<span style="color: green;">{recent_payments} payments (2024)</span>'
            )
        else:
            return format_html('<span style="color: orange;">No recent payments</span>')

    payment_status.short_description = "Payment Status"

    actions = ["mark_as_active", "mark_as_inactive", "mark_as_deceased"]

    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True, is_deceased=False)
        self.message_user(request, f"Marked {queryset.count()} members as active.")

    mark_as_active.short_description = "Mark selected members as active"

    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Marked {queryset.count()} members as inactive.")

    mark_as_inactive.short_description = "Mark selected members as inactive"

    def mark_as_deceased(self, request, queryset):
        queryset.update(is_active=False, is_deceased=True)
        self.message_user(request, f"Marked {queryset.count()} members as deceased.")

    mark_as_deceased.short_description = "Mark selected members as deceased"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "member",
        "amount",
        "payment_date",
        "payment_method",
        "period_start",
        "period_end",
        "check_number",
        "created_at",
    ]
    list_filter = [
        "payment_method",
        "payment_date",
        "created_at",
        "member__member_type",
    ]
    search_fields = [
        "member__first_name",
        "member__last_name",
        "member__member_id",
        "check_number",
        "transaction_id",
        "notes",
    ]
    date_hierarchy = "payment_date"
    ordering = ["-payment_date", "-created_at"]

    fieldsets = (
        (
            "Payment Information",
            {"fields": ("member", "amount", "payment_date", "payment_method")},
        ),
        ("Period Covered", {"fields": ("period_start", "period_end")}),
        (
            "Payment Details",
            {"fields": ("check_number", "transaction_id", "notes", "created_by")},
        ),
        ("System Information", {"fields": ("created_at",), "classes": ["collapse"]}),
    )

    readonly_fields = ["created_at"]


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ["friend_name", "member", "relationship", "phone", "email"]
    list_filter = ["relationship", "created_at"]
    search_fields = [
        "friend_name",
        "member__first_name",
        "member__last_name",
        "phone",
        "email",
        "relationship",
    ]
    ordering = ["friend_name"]
