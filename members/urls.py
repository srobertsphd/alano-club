from django.urls import path
from . import views

app_name = "members"

urlpatterns = [
    # Main pages
    path("", views.landing_view, name="landing"),
    path("search/", views.search_view, name="search"),
    path("<uuid:member_uuid>/", views.member_detail_view, name="member_detail"),
    # Member management
    path("add/", views.add_member_view, name="add_member"),
    # Payment functionality
    path("payments/add/", views.add_payment_view, name="add_payment"),
]
