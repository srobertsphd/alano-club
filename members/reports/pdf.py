"""
PDF generation for member reports.

This module handles PDF generation using WeasyPrint.
"""

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib import messages


def generate_members_pdf(request, context):
    """Generate PDF version of current members report"""
    try:
        from weasyprint import HTML

        # Render HTML template
        html_string = render_to_string(
            "members/reports/current_members_pdf.html", context
        )

        # Create PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        # Return PDF response
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="current_members_{context["report_date"].strftime("%Y_%m_%d")}.pdf"'
        )
        return response

    except ImportError as e:
        # WeasyPrint not installed, return HTML version with error message
        messages.error(
            request,
            f"PDF generation not available. Install WeasyPrint for PDF reports. Error: {e}",
        )
        return render(request, "members/reports/current_members.html", context)

    except Exception as e:
        # Other PDF generation errors
        messages.error(request, f"Error generating PDF: {e}")
        return render(request, "members/reports/current_members.html", context)
