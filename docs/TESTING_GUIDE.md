# Testing Guide - Manual Testing After Server Setup

**Created:** November 29, 2025

This guide provides step-by-step instructions for manually testing the Alano Club Member Management System after the server is running.

## Prerequisites

- Server is running (see `README.md` for setup instructions)
- Development server accessible at `http://127.0.0.1:8001`
- Admin/staff user credentials available
- Database is configured and accessible

---

## Member Creation Testing

### Step 1: Access the Add Member Page

**URL:** `http://127.0.0.1:8001/add/`

**Note:** You may need to log in as a staff user first if the view requires authentication.

### Step 2: What to Test

#### Form Step (Initial Page)

**Test Suggested IDs:**
- ✅ The form should display **5 suggested member IDs** (e.g., 1, 2, 3, 4, 5 if available)
- ✅ These IDs should be **available** (not currently in use by active members)
- ✅ The first suggested ID should be pre-selected or highlighted

**Test Form Fields:**
- ✅ Member Types dropdown should list all available member types
- ✅ Today's date should be pre-filled for date fields
- ✅ All required fields are present:
  - First Name
  - Last Name
  - Email
  - Member Type
  - Member ID
  - Milestone Date
  - Date Joined
  - Contact information fields (address, city, state, zip, phone)

**Test Suggested IDs Functionality:**
- ✅ Suggested IDs update correctly if you create a member with one of the suggested IDs
- ✅ After creating a member, the next time you visit the form, that ID should no longer appear in suggestions

#### Confirm Step (After Submitting Form)

**Test Data Display:**
- ✅ All entered information is displayed correctly
- ✅ Calculated expiration date is shown (should be end of current month + member type months)
- ✅ Member ID is displayed correctly
- ✅ All contact information is displayed correctly

**Test Validation:**
- ✅ Required fields are validated (try submitting with missing required fields)
- ✅ Member ID validation works (try using an ID that's already in use)
- ✅ Date validation works (try invalid dates)

#### Process Step (After Clicking "Confirm")

**Test Member Creation:**
- ✅ Member is created successfully
- ✅ Success message appears: "Member [Name] (#[ID]) successfully created. Membership expires [Date]."
- ✅ Redirect occurs to the search page (`/search/`)

**Test Member Verification:**
- ✅ Search for the newly created member by name
- ✅ Member appears in search results
- ✅ Click on member to view details
- ✅ Verify all member information is correct:
  - Name, email, member ID
  - Member type
  - Expiration date (matches calculated date)
  - Contact information
  - Dates (milestone date, date joined)

### Step 3: What to Verify

**Verify Suggested IDs Functionality:**
- ✅ Suggested IDs are generated using `MemberService.get_suggested_ids()` (backend)
- ✅ IDs are actually available (not in use by active members)
- ✅ Inactive members don't block ID suggestions
- ✅ IDs are returned in correct format (tuple: next_id, list_of_ids)

**Verify Member Creation Functionality:**
- ✅ Member creation uses `MemberService.create_member()` (backend)
- ✅ All member fields are saved correctly
- ✅ Member ID is assigned correctly
- ✅ Expiration date is calculated correctly (end of current month + member type months)
- ✅ Member type is associated correctly
- ✅ Member appears in database and is searchable

**Verify Workflow:**
- ✅ Form → Confirm → Process workflow works smoothly
- ✅ Session data is handled correctly (can go back and edit)
- ✅ Error handling works (invalid data, expired sessions)
- ✅ Success messages display correctly
- ✅ Redirects work correctly

### Step 4: Quick Test Checklist

**Form Step:**
- [ ] Form loads successfully
- [ ] 5 suggested member IDs are displayed
- [ ] Suggested IDs are actually available (not in use)
- [ ] Member types dropdown populates correctly
- [ ] Today's date is pre-filled
- [ ] All required fields are present

**Confirm Step:**
- [ ] Can fill out all member fields
- [ ] Form validation works (required fields)
- [ ] Member ID validation works (duplicate ID check)
- [ ] Confirmation page shows correct data
- [ ] Calculated expiration date is correct
- [ ] Can go back to edit form

**Process Step:**
- [ ] Member is created successfully
- [ ] Success message appears with correct information
- [ ] Redirects to search page
- [ ] Member appears in search results
- [ ] Member detail page shows all information correctly
- [ ] Expiration date matches calculated date
- [ ] Member ID is correct

**Edge Cases:**
- [ ] Creating member with first suggested ID removes it from next suggestions
- [ ] Creating multiple members in sequence works correctly
- [ ] Session expiration handling works (try waiting, then confirming)
- [ ] Cancelling member creation works correctly
- [ ] Invalid form data shows appropriate error messages

---

## Payment Creation Testing

### Step 1: Access the Add Payment Page

**URL:** `http://127.0.0.1:8001/payments/add/`

### Step 2: What to Test

#### Search Step (Initial Page)

**Test Member Search:**
- ✅ Can search for members by name
- ✅ Can search for members by member ID
- ✅ Search results display correctly
- ✅ Can select a member from search results

#### Form Step (After Selecting Member)

**Test Payment Form:**
- ✅ Member information is displayed
- ✅ Payment amount field is present
- ✅ Suggested payment amount (monthly dues) is pre-filled
- ✅ Payment date defaults to today
- ✅ Payment methods dropdown populates
- ✅ Receipt number field is present

**Test Expiration Calculation:**
- ✅ Changing payment amount updates expiration date preview
- ✅ Expiration calculation is correct (payment amount ÷ monthly dues = months)
- ✅ Override expiration dropdown appears on confirmation page

#### Confirm Step (After Submitting Form)

**Test Payment Confirmation:**
- ✅ Payment details are displayed correctly
- ✅ Current expiration date is shown
- ✅ New expiration date is calculated correctly
- ✅ Override expiration dropdown is available (6 months forward)
- ✅ Can change override expiration date
- ✅ Confirmation shows payment amount, date, method, receipt number

#### Process Step (After Clicking "Confirm")

**Test Payment Processing:**
- ✅ Payment is created successfully
- ✅ Member expiration date is updated correctly
- ✅ Success message appears
- ✅ Redirects to member detail page
- ✅ Payment appears in member's payment history

**Test Inactive Member Reactivation:**
- ✅ If member is inactive, making a payment reactivates them
- ✅ Status changes from "inactive" to "active"
- ✅ Success message mentions reactivation

### Step 3: What to Verify

**Verify Payment Service Functionality:**
- ✅ Expiration calculation uses `PaymentService.calculate_expiration()` (backend)
- ✅ Payment processing uses `PaymentService.process_payment()` (backend)
- ✅ Override expiration date works correctly
- ✅ Payment amount calculation is correct
- ✅ Member expiration updates correctly
- ✅ Inactive member reactivation works

**Verify Override Expiration:**
- ✅ Override expiration dropdown shows 6 months forward
- ✅ Selecting override date updates member expiration correctly
- ✅ Override date is set to end of selected month
- ✅ Override takes precedence over calculated expiration

### Step 4: Quick Test Checklist

**Search Step:**
- [ ] Can search for members by name
- [ ] Can search for members by ID
- [ ] Search results display correctly
- [ ] Can select member from results

**Form Step:**
- [ ] Member information displays correctly
- [ ] Payment amount field works
- [ ] Suggested amount (monthly dues) is pre-filled
- [ ] Payment date defaults to today
- [ ] Payment methods dropdown works
- [ ] Expiration preview updates with amount changes

**Confirm Step:**
- [ ] Payment details display correctly
- [ ] Current and new expiration dates shown
- [ ] Override expiration dropdown available
- [ ] Can change override expiration date
- [ ] All payment information is correct

**Process Step:**
- [ ] Payment is created successfully
- [ ] Member expiration date updates correctly
- [ ] Success message appears
- [ ] Redirects to member detail page
- [ ] Payment appears in payment history
- [ ] Inactive members are reactivated (if applicable)

**Override Expiration:**
- [ ] Override dropdown shows 6 months forward
- [ ] Selecting override date works
- [ ] Override date sets expiration to end of selected month
- [ ] Override takes precedence over calculated expiration

---

## Member Search and Detail Testing

### Step 1: Access Search Page

**URL:** `http://127.0.0.1:8001/search/`

### Step 2: What to Test

**Test Search Functionality:**
- ✅ Can search by member name (first or last)
- ✅ Can search by member ID
- ✅ Search results display correctly
- ✅ Can click on member to view details
- ✅ Pagination works (if many results)

**Test Member Detail Page:**
- ✅ All member information displays correctly
- ✅ Payment history displays correctly
- ✅ Recent payments show (last 3)
- ✅ Expiration date is correct
- ✅ Member status displays correctly
- ✅ Can navigate back to search

### Step 3: Quick Test Checklist

- [ ] Search by name works
- [ ] Search by ID works
- [ ] Search results display correctly
- [ ] Can click member to view details
- [ ] Member detail page shows all information
- [ ] Payment history displays correctly
- [ ] Recent payments show correctly
- [ ] Navigation works correctly

---

## Reports Testing

### Step 1: Access Current Members Report

**URL:** `http://127.0.0.1:8001/reports/current-members/`

### Step 2: What to Test

**Test HTML Report:**
- ✅ Report displays all active members
- ✅ Members are separated by type (regular vs. life)
- ✅ Payment history shows for each member
- ✅ Report date is displayed
- ✅ Totals are calculated correctly

**Test PDF Report:**
- ✅ Can generate PDF version (`?format=pdf`)
- ✅ PDF downloads correctly
- ✅ PDF contains all member information
- ✅ PDF formatting is correct

### Step 3: Quick Test Checklist

- [ ] HTML report displays correctly
- [ ] All active members are shown
- [ ] Members separated by type
- [ ] Payment history displays
- [ ] Totals are correct
- [ ] PDF generation works
- [ ] PDF downloads correctly
- [ ] PDF contains all information

---

## General Testing Notes

### Common Issues to Check

1. **Session Expiration:**
   - Start a workflow (add member or payment)
   - Wait a few minutes
   - Try to complete the workflow
   - Should handle gracefully with error message

2. **Validation:**
   - Try submitting forms with missing required fields
   - Try invalid data (dates, IDs, etc.)
   - Should show appropriate error messages

3. **Navigation:**
   - Test "Back" buttons
   - Test "Cancel" buttons
   - Test redirects after successful operations
   - Test browser back button

4. **Data Integrity:**
   - Verify all data saves correctly
   - Verify relationships (member → payments, member → member_type)
   - Verify calculated fields (expiration dates)

### Testing After Refactoring

When testing after code refactoring (Steps 1-4), verify:

- ✅ All functionality still works as before
- ✅ No regressions introduced
- ✅ Performance is acceptable
- ✅ Error messages are clear
- ✅ User experience is unchanged

### Reporting Issues

When reporting issues, include:
- What you were trying to do
- What you expected to happen
- What actually happened
- Steps to reproduce
- Screenshots (if applicable)
- Browser/OS information

---

## Automated Testing

In addition to manual testing, automated tests are available:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_member_service.py -v
uv run pytest tests/test_payment_service.py -v
uv run pytest tests/test_utils.py -v

# Run tests with coverage
uv run pytest tests/ --cov=members --cov-report=html
```

See `tests/README.md` for more information about automated testing.

