"""
Views for database backup functionality.
"""

import os
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from members.backup_utils import create_backup


@staff_member_required
def download_backup_view(request):
    """
    Create and immediately download database backup.

    Creates a temporary backup file, reads it into memory, deletes it,
    and streams it to the user's browser as a download.
    """
    result = create_backup()

    if not result["success"]:
        return HttpResponse(
            f"Backup failed: {result['error']}", status=500, content_type="text/plain"
        )

    # Read the backup file content
    try:
        with open(result["filepath"], "rb") as f:
            file_content = f.read()

        # Delete the temporary file (cleanup)
        os.unlink(result["filepath"])

        # Create HTTP response with file download
        response = HttpResponse(file_content, content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="{result["filename"]}"'

        return response

    except Exception as e:
        # Try to clean up file if it exists
        try:
            if result.get("filepath") and os.path.exists(result["filepath"]):
                os.unlink(result["filepath"])
        except Exception:
            pass

        return HttpResponse(
            f"Error reading backup file: {str(e)}",
            status=500,
            content_type="text/plain",
        )

