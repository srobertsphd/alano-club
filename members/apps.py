from django.apps import AppConfig


class MembersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "members"

    def ready(self):
        """Register custom admin URLs when Django is fully initialized"""
        from django.urls import path
        from django.contrib import admin
        from .admin_views import deactivate_expired_members_view

        # Monkey-patch admin site's get_urls method to add custom URL
        # This happens AFTER Django is ready, ensuring proper initialization
        original_get_urls = admin.site.get_urls

        def custom_get_urls():
            urls = original_get_urls()
            custom_urls = [
                path(
                    "deactivate-expired-members/",
                    admin.site.admin_view(deactivate_expired_members_view),
                    name="deactivate_expired_members",
                ),
            ]
            return custom_urls + urls

        admin.site.get_urls = custom_get_urls
