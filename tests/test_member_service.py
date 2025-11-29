"""
Tests for Member Service (Step 4: Extract Member Service)

Tests the MemberService class methods:
- get_suggested_ids()
- create_member()
"""

import pytest
from datetime import date

from members.services import MemberService
from members.models import Member, MemberType


@pytest.mark.django_db
@pytest.mark.unit
class TestMemberServiceGetSuggestedIds:
    """Test MemberService.get_suggested_ids() method"""

    @pytest.fixture
    def member_type(self, db):
        """Create a test member type"""
        return MemberType.objects.create(
            member_type="Regular",
            member_dues=30.00,
            num_months=1,
        )

    def test_get_suggested_ids_default_count(self, db):
        """Test that get_suggested_ids returns 5 IDs by default"""
        next_id, suggested_ids = MemberService.get_suggested_ids()

        assert isinstance(next_id, int)
        assert isinstance(suggested_ids, list)
        assert len(suggested_ids) == 5
        assert next_id == suggested_ids[0]

    def test_get_suggested_ids_custom_count(self, db):
        """Test that get_suggested_ids returns requested number of IDs"""
        next_id, suggested_ids = MemberService.get_suggested_ids(count=3)

        assert len(suggested_ids) == 3
        assert next_id == suggested_ids[0]

    def test_get_suggested_ids_returns_available_ids(self, db, member_type):
        """Test that suggested IDs are actually available (not in use)"""
        # Create a member with ID 1
        Member.objects.create(
            first_name="Test",
            last_name="Member",
            email="test@example.com",
            member_type=member_type,
            status="active",
            member_id=1,
            expiration_date=date(2025, 12, 31),
            date_joined=date(2020, 1, 1),
        )

        next_id, suggested_ids = MemberService.get_suggested_ids(count=5)

        # ID 1 should not be in suggested_ids
        assert 1 not in suggested_ids
        # Next ID should be 2 (first available)
        assert next_id == 2
        assert 2 in suggested_ids

    def test_get_suggested_ids_skips_inactive_members(self, db, member_type):
        """Test that inactive members don't block ID suggestions"""
        # Create an inactive member with ID 1
        Member.objects.create(
            first_name="Inactive",
            last_name="Member",
            email="inactive@example.com",
            member_type=member_type,
            status="inactive",
            member_id=1,
            expiration_date=date(2024, 12, 31),
            date_joined=date(2020, 1, 1),
        )

        next_id, suggested_ids = MemberService.get_suggested_ids(count=5)

        # ID 1 should be available (inactive members don't block)
        assert 1 in suggested_ids
        assert next_id == 1

    def test_get_suggested_ids_handles_no_available_ids(self, db, member_type):
        """Test behavior when many IDs are used"""
        # Create members with IDs 1-10
        for i in range(1, 11):
            Member.objects.create(
                first_name=f"Test{i}",
                last_name="Member",
                email=f"test{i}@example.com",
                member_type=member_type,
                status="active",
                member_id=i,
                expiration_date=date(2025, 12, 31),
                date_joined=date(2020, 1, 1),
            )

        next_id, suggested_ids = MemberService.get_suggested_ids(count=5)

        # Should return IDs starting from 11
        assert next_id == 11
        assert 11 in suggested_ids
        assert len(suggested_ids) == 5

    def test_get_suggested_ids_returns_correct_format(self, db):
        """Test that return value is correct tuple format"""
        result = MemberService.get_suggested_ids(count=3)

        assert isinstance(result, tuple)
        assert len(result) == 2
        next_id, suggested_ids = result
        assert isinstance(next_id, int)
        assert isinstance(suggested_ids, list)
        assert all(isinstance(id_num, int) for id_num in suggested_ids)


@pytest.mark.django_db
@pytest.mark.integration
class TestMemberServiceCreateMember:
    """Test MemberService.create_member() method"""

    @pytest.fixture
    def member_type(self, db):
        """Create a test member type"""
        return MemberType.objects.create(
            member_type="Regular",
            member_dues=30.00,
            num_months=1,
        )

    @pytest.fixture
    def member_data(self, member_type):
        """Create sample member data"""
        return {
            "member_type_id": str(member_type.pk),
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "member_id": 100,
            "milestone_date": "2020-01-15",
            "date_joined": "2025-01-01",
            "home_address": "123 Main St",
            "home_city": "Anytown",
            "home_state": "CA",
            "home_zip": "12345",
            "home_phone": "555-1234",
            "initial_expiration": "2025-12-31",
        }

    def test_create_member_creates_member(self, db, member_data):
        """Test that create_member creates a Member record"""
        initial_count = Member.objects.count()

        member = MemberService.create_member(member_data)

        assert Member.objects.count() == initial_count + 1
        assert isinstance(member, Member)
        assert member.first_name == "John"
        assert member.last_name == "Doe"

    def test_create_member_sets_correct_member_id(self, db, member_data):
        """Test that member_id is set correctly"""
        member = MemberService.create_member(member_data)

        assert member.member_id == 100

    def test_create_member_sets_all_fields(self, db, member_data):
        """Test that all member fields are set correctly"""
        member = MemberService.create_member(member_data)

        assert member.first_name == "John"
        assert member.last_name == "Doe"
        assert member.email == "john.doe@example.com"
        assert member.member_id == 100
        assert member.milestone_date == date(2020, 1, 15)
        assert member.date_joined == date(2025, 1, 1)
        assert member.home_address == "123 Main St"
        assert member.home_city == "Anytown"
        assert member.home_state == "CA"
        assert member.home_zip == "12345"
        assert member.home_phone == "555-1234"
        assert member.expiration_date == date(2025, 12, 31)

    def test_create_member_sets_member_type(self, db, member_type, member_data):
        """Test that member_type is set correctly"""
        member = MemberService.create_member(member_data)

        assert member.member_type == member_type

    def test_create_member_handles_empty_optional_fields(self, db, member_type):
        """Test that optional fields can be empty"""
        member_data = {
            "member_type_id": str(member_type.pk),
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "",
            "member_id": 200,
            "milestone_date": "2020-06-01",
            "date_joined": "2025-01-01",
            "home_address": "",
            "home_city": "",
            "home_state": "",
            "home_zip": "",
            "home_phone": "",
            "initial_expiration": "2025-12-31",
        }

        member = MemberService.create_member(member_data)

        assert member.email == ""
        assert member.home_address == ""
        assert member.home_city == ""

    def test_create_member_returns_member_instance(self, db, member_data):
        """Test that create_member returns a Member instance"""
        member = MemberService.create_member(member_data)

        assert isinstance(member, Member)
        assert hasattr(member, "member_uuid")
        assert hasattr(member, "full_name")
