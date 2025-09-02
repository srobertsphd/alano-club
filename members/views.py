from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Max
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
import calendar

from .models import Member, Payment, PaymentMethod


def add_months_to_date(date, months):
    """Add months to a date and return the last day of the resulting month

    Examples:
    - Current expiration: Mar 15, 2025 + 1 month = Mar 31, 2025
    - Current expiration: Jan 31, 2025 + 1 month = Feb 28, 2025 (or Feb 29 in leap year)
    - Current expiration: Dec 15, 2024 + 2 months = Feb 29, 2025

    This ensures all memberships expire at the end of the month regardless of payment date.
    """
    # Calculate the target year and month
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1

    # Get the last day of the target month
    last_day = calendar.monthrange(year, month)[1]

    return date.replace(year=year, month=month, day=last_day)


def landing_view(request):
    """Landing page with system overview"""
    return render(request, "members/landing.html")


def search_view(request):
    """Simple member search page with alphabet browsing and status filtering"""
    query = request.GET.get("q", "").strip()
    browse_range = request.GET.get("browse", "").strip()
    status_filter = request.GET.get("status", "all").strip()
    members = None

    # Get quick stats for the search page
    active_members_count = Member.objects.filter(status="active").count()
    total_payments_count = Payment.objects.count()

    # Calculate available IDs (1-1000 range)
    used_ids = set(
        Member.objects.filter(status="active", member_id__isnull=False).values_list(
            "member_id", flat=True
        )
    )
    available_ids_count = 1000 - len(used_ids)

    # Start with base queryset and apply status filter
    base_queryset = Member.objects.select_related("member_type")

    # Apply status filter
    if status_filter == "active":
        base_queryset = base_queryset.filter(status="active")
    elif status_filter == "inactive":
        base_queryset = base_queryset.filter(status="inactive")
    # "all" or any other value shows all members (no additional filter)

    # Handle alphabet browsing
    if browse_range:
        # Define the letter ranges
        range_mapping = {
            "A-C": ["A", "B", "C"],
            "D-F": ["D", "E", "F"],
            "G-I": ["G", "H", "I"],
            "J-L": ["J", "K", "L"],
            "M-O": ["M", "N", "O"],
            "P-R": ["P", "Q", "R"],
            "S-U": ["S", "T", "U"],
            "V-Z": ["V", "W", "X", "Y", "Z"],
        }

        if browse_range in range_mapping:
            letters = range_mapping[browse_range]
            # Create Q objects for each letter in the range
            letter_filters = Q()
            for letter in letters:
                letter_filters |= Q(last_name__istartswith=letter)

            members = base_queryset.filter(letter_filters).order_by(
                "last_name", "first_name"
            )

    # Perform search if query provided (takes precedence over browse)
    elif query:
        try:
            # Try to parse as member ID
            member_id = int(query)
            members = base_queryset.filter(member_id=member_id)
        except ValueError:
            # Search by name
            members = base_queryset.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).order_by("last_name", "first_name")

    context = {
        "query": query,
        "browse_range": browse_range,
        "status_filter": status_filter,
        "members": members,
        "active_members_count": active_members_count,
        "total_payments_count": total_payments_count,
        "available_ids_count": available_ids_count,
    }

    return render(request, "members/search.html", context)


def member_detail_view(request, member_uuid):
    """Member detail page with payment history and optional date filtering"""
    member = get_object_or_404(Member, member_uuid=member_uuid)

    # Get payment history with optional date filtering
    payments_queryset = (
        Payment.objects.filter(member=member)
        .select_related("payment_method")
        .order_by("-date")
    )

    # Apply date filters if provided
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            payments_queryset = payments_queryset.filter(date__gte=start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            payments_queryset = payments_queryset.filter(date__lte=end_date_obj)
        except ValueError:
            pass

    # Paginate payment history (20 per page)
    paginator = Paginator(payments_queryset, 20)
    page_number = request.GET.get("page")
    payments = paginator.get_page(page_number)

    context = {
        "member": member,
        "payments": payments,
        "start_date": start_date,
        "end_date": end_date,
        "total_payments": payments_queryset.count(),
    }

    return render(request, "members/member_detail.html", context)


def add_payment_view(request):
    """Payment entry workflow with member search, form, and confirmation"""

    # Get workflow step
    step = request.GET.get("step", "search")
    member_uuid = request.GET.get("member", "")

    if step == "search":
        # Step 1: Member Search
        query = request.GET.get("q", "").strip()
        members = None

        if query:
            try:
                # Try to parse as member ID
                member_id = int(query)
                members = Member.objects.filter(member_id=member_id).exclude(
                    status="deceased"
                )
            except ValueError:
                # Search by name
                members = (
                    Member.objects.filter(
                        Q(first_name__icontains=query) | Q(last_name__icontains=query)
                    )
                    .exclude(status="deceased")
                    .select_related("member_type")
                    .order_by("last_name", "first_name")
                )

        context = {
            "step": "search",
            "query": query,
            "members": members,
        }
        return render(request, "members/add_payment.html", context)

    elif step == "form":
        # Step 2: Payment Form (member selected)
        if not member_uuid:
            messages.error(request, "Please select a member first.")
            return redirect("members:add_payment")

        member = get_object_or_404(Member, member_uuid=member_uuid)

        # Don't allow payments for deceased members
        if member.status == "deceased":
            messages.error(request, "Cannot add payments for deceased members.")
            return redirect("members:add_payment")

        # Check if this is a Life member - no payments allowed
        if member.member_type and member.member_type.name == "Life":
            context = {
                "step": "life_member",
                "member": member,
            }
            return render(request, "members/add_payment.html", context)

        payment_methods = PaymentMethod.objects.filter(is_active=True).order_by("name")

        # Auto-populate suggested payment amount (monthly dues)
        suggested_amount = (
            member.member_type.monthly_dues if member.member_type else Decimal("0.00")
        )

        # Calculate new expiration date if they pay the monthly amount
        coverage_months = (
            float(member.member_type.coverage_months) if member.member_type else 1.0
        )
        # Add months and set to last day of month
        months_to_add = int(coverage_months)
        new_expiration = add_months_to_date(member.expiration_date, months_to_add)

        context = {
            "step": "form",
            "member": member,
            "payment_methods": payment_methods,
            "suggested_amount": suggested_amount,
            "new_expiration": new_expiration,
            "today": timezone.now().date(),
        }
        return render(request, "members/add_payment.html", context)

    elif step == "confirm":
        # Step 3: Confirmation (form submitted)
        if request.method == "POST":
            member_uuid = request.POST.get("member_uuid")
            amount = request.POST.get("amount")
            payment_date = request.POST.get("payment_date")
            payment_method_id = request.POST.get("payment_method")
            receipt_number = request.POST.get("receipt_number", "").strip()

            # Validate form data
            try:
                member = get_object_or_404(Member, member_uuid=member_uuid)

                # Don't allow payments for deceased members
                if member.status == "deceased":
                    raise ValueError("Cannot add payments for deceased members")
                amount = Decimal(amount)
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
                payment_method = get_object_or_404(
                    PaymentMethod, payment_method_id=payment_method_id
                )

                # Validate receipt number is provided
                if not receipt_number:
                    raise ValueError("Receipt number is required")

                # Calculate new expiration date based on payment amount
                # Examples:
                # - $30 payment / $30 monthly dues = 1 month paid
                # - $60 payment / $30 monthly dues = 2 months paid
                # - $15 payment / $30 monthly dues = 0.5 months = 0 months (rounded down)
                if member.member_type and member.member_type.monthly_dues > 0:
                    months_paid = float(amount) / float(member.member_type.monthly_dues)
                    coverage_months = float(member.member_type.coverage_months)
                    total_months_to_add = int(months_paid * coverage_months)
                    new_expiration = add_months_to_date(
                        member.expiration_date, total_months_to_add
                    )
                else:
                    # Default to 1 month if no member type or dues
                    new_expiration = add_months_to_date(member.expiration_date, 1)

                # Store in session for final processing
                request.session["payment_data"] = {
                    "member_uuid": str(member_uuid),
                    "amount": str(amount),
                    "payment_date": payment_date.isoformat(),
                    "payment_method_id": payment_method_id,
                    "receipt_number": receipt_number,
                    "new_expiration": new_expiration.isoformat(),
                }

                context = {
                    "step": "confirm",
                    "member": member,
                    "amount": amount,
                    "payment_date": payment_date,
                    "payment_method": payment_method,
                    "receipt_number": receipt_number,
                    "current_expiration": member.expiration_date,
                    "new_expiration": new_expiration,
                }
                return render(request, "members/add_payment.html", context)

            except (ValueError, Member.DoesNotExist, PaymentMethod.DoesNotExist) as e:
                messages.error(request, f"Invalid payment data: {e}")
                # If we have a member_uuid, redirect back to form with member selected
                if member_uuid:
                    return redirect(f"/payments/add/?step=form&member={member_uuid}")
                else:
                    return redirect("members:add_payment")

        else:
            messages.error(request, "Invalid request.")
            return redirect("members:add_payment")

    elif step == "process":
        # Step 4: Final Processing
        if request.method == "POST" and request.POST.get("confirm") == "yes":
            payment_data = request.session.get("payment_data")
            if not payment_data:
                messages.error(request, "Payment session expired. Please try again.")
                return redirect("members:add_payment")

            try:
                # Get member and create payment
                member = get_object_or_404(
                    Member, member_uuid=payment_data["member_uuid"]
                )
                payment_method = get_object_or_404(
                    PaymentMethod, payment_method_id=payment_data["payment_method_id"]
                )

                # Generate unique original_payment_id (for new payments, use next available ID)
                max_original_id = (
                    Payment.objects.aggregate(max_id=Max("original_payment_id"))[
                        "max_id"
                    ]
                    or 0
                )
                new_original_id = max_original_id + 1

                # Create the payment record
                payment = Payment.objects.create(
                    member=member,
                    payment_method=payment_method,
                    amount=Decimal(payment_data["amount"]),
                    date=datetime.fromisoformat(payment_data["payment_date"]).date(),
                    receipt_number=payment_data["receipt_number"],
                    original_payment_id=new_original_id,
                )

                # Update member expiration date and reactivate if inactive
                member.expiration_date = datetime.fromisoformat(
                    payment_data["new_expiration"]
                ).date()

                # If member is inactive, reactivate them when they make a payment
                was_inactive = member.status == "inactive"
                if was_inactive:
                    member.status = "active"
                    member.date_inactivated = None

                member.save()

                # Clear session data
                if "payment_data" in request.session:
                    del request.session["payment_data"]

                # Create success message
                success_msg = f"Payment of ${payment.amount} successfully recorded for {member.full_name}. Membership expires {member.expiration_date.strftime('%B %d, %Y')}."
                if was_inactive:
                    success_msg += " Member status changed from Inactive to Active."

                messages.success(request, success_msg)
                return redirect("members:member_detail", member_uuid=member.member_uuid)

            except Exception as e:
                messages.error(request, f"Error processing payment: {e}")
                return redirect("members:add_payment")

        else:
            # User cancelled or invalid request
            if "payment_data" in request.session:
                del request.session["payment_data"]
            messages.info(request, "Payment cancelled.")
            return redirect("members:add_payment")

    else:
        # Invalid step
        return redirect("members:add_payment")
