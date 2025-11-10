# Test Documentation: v0.0.1-1-1-3 - Permission Validation Unit Tests

## Overview

This document describes the comprehensive unit test suite for the permission validation module (`permissions.py`). The test suite ensures that messaging permissions are correctly enforced based on relationships between users through bids, offers, and agreements.

## Test Coverage Summary

- **Total Test Cases**: 24
- **Coverage**: >90% of permissions.py module
- **Performance**: All validations complete in <100ms
- **Test Framework**: pytest with pytest-benchmark and pytest-cov

## Test Structure

The test suite is organized into the following classes:

### 1. TestBidBasedPermissions
Tests messaging permissions based on bid relationships between customers and taskers.

**Test Cases:**
- `test_can_message_with_active_bid_tasker_to_customer` - Verifies tasker can message customer when they bid on customer's task
- `test_can_message_with_active_bid_customer_to_tasker` - Verifies customer can message tasker who bid on their task
- `test_multiple_bids_on_same_task` - Verifies customer can message all taskers who bid on their task
- `test_no_permission_without_bid` - Verifies messaging is blocked when no bid relationship exists

### 2. TestOfferBasedPermissions
Tests messaging permissions based on offer relationships.

**Test Cases:**
- `test_can_message_with_active_offer_customer_to_tasker` - Verifies customer can message tasker when they sent an offer
- `test_can_message_with_accepted_offer` - Verifies messaging works with accepted offers
- `test_can_message_with_declined_offer` - Verifies messaging still works even if offer was declined

### 3. TestAgreementBasedPermissions
Tests messaging permissions based on agreement relationships.

**Test Cases:**
- `test_can_message_with_active_agreement` - Verifies messaging with active agreements
- `test_can_message_with_completed_agreement` - Verifies messaging still works after agreement completion
- `test_can_message_with_pending_agreement` - Verifies messaging with pending agreements

### 4. TestNoRelationship
Tests scenarios where no relationship exists between users.

**Test Cases:**
- `test_no_relationship_returns_false` - Verifies False is returned when no relationship exists
- `test_different_customers_cannot_message` - Verifies customers cannot message each other
- `test_different_taskers_cannot_message` - Verifies taskers cannot message each other
- `test_task_without_bids_offers_or_agreement` - Verifies task existence alone doesn't grant messaging rights

### 5. TestEdgeCases
Tests edge cases and boundary conditions.

**Test Cases:**
- `test_self_messaging_not_allowed` - Verifies users cannot message themselves
- `test_multiple_relationships_same_users` - Verifies users with multiple relationship types can message
- `test_bid_on_other_customers_task` - Verifies tasker who bid on customer1's task cannot message customer2
- `test_cannot_message_after_bid_withdrawal` - **NEW** Verifies messaging is blocked after bid withdrawal
- `test_multiple_bids_same_tasker_one_withdrawn` - **NEW** Verifies tasker can still message if at least one active bid exists
- `test_nonexistent_user_ids` - Verifies handling of non-existent user IDs

### 6. TestPerformance
Tests performance requirements using pytest-benchmark.

**Test Cases:**
- `test_permission_validation_performance` - Benchmarks basic permission validation (<100ms)
- `test_performance_with_many_relationships` - Tests performance with 100+ relationships
- `test_performance_with_no_relationship` - Tests performance when no relationship exists

### 7. TestGetMessageableUsers
Tests the helper function for getting list of messageable users.

**Test Cases:**
- `test_get_messageable_users_with_bids` - Tests getting messageable users via bids
- `test_get_messageable_users_empty` - Tests when there are no messageable users
- `test_get_messageable_users_no_duplicates` - Tests that users appear only once with multiple relationships

## New Features Tested

### Withdrawn Bids Feature
Two new test cases were added to thoroughly test the withdrawn bids functionality:

1. **test_cannot_message_after_bid_withdrawal**
   - Creates a bid relationship between customer and tasker
   - Verifies both can message initially
   - Withdraws the bid
   - Verifies both cannot message after withdrawal

2. **test_multiple_bids_same_tasker_one_withdrawn**
   - Creates two bids from same tasker on different tasks
   - One bid is withdrawn, one is active
   - Verifies messaging still works due to active bid
   - Withdraws second bid
   - Verifies messaging is now blocked

## Test Fixtures

### db_session
- Scope: function
- Purpose: Creates a fresh in-memory SQLite database for each test
- Ensures test isolation and no data contamination

### sample_users
- Scope: function
- Purpose: Creates standard set of users for testing
- Users created:
  - customer1, customer2 (CUSTOMER role)
  - tasker1, tasker2, tasker3 (TASKER role)

## Performance Requirements

All permission validation operations must complete in <100ms:
- Basic permission check: <100ms
- Permission check with 100+ relationships: <100ms
- Permission check with no relationship: <100ms

Performance is verified using pytest-benchmark which provides:
- Minimum, maximum, and mean execution times
- Standard deviation
- Rounds and iterations statistics

## Running the Tests

### Run all tests:
```bash
cd app/backend
python -m pytest test_permissions.py -v
```

### Run with coverage:
```bash
python -m pytest test_permissions.py --cov=permissions --cov-report=term-missing
```

### Run specific test class:
```bash
python -m pytest test_permissions.py::TestBidBasedPermissions -v
```

### Run performance benchmarks:
```bash
python -m pytest test_permissions.py::TestPerformance -v --benchmark-only
```

## Code Changes Summary

### database.py
- Added `withdrawn` field to Bid model (Boolean, default=False)

### permissions.py
- Updated `can_message_user()` to filter out withdrawn bids
- Updated `get_messageable_users()` to exclude withdrawn bids

### test_permissions.py
- Added 2 new test cases for withdrawn bid functionality
- Updated 3 performance tests to use pytest-benchmark
- All existing tests maintained and passing

### requirements.txt
- Added pytest-benchmark==4.0.0
- Added pytest-cov==4.1.0

## Acceptance Criteria Status

✅ Test suite covers all four validation scenarios (bid, offer, agreement, none)  
✅ Test edge cases: withdrawn bids, declined offers, multiple bids from same tasker  
✅ Test performance: validation completes in <100ms  
✅ Test coverage >90% for permissions module  
✅ Tests are isolated and use database fixtures  
✅ All tests pass consistently  
✅ Tests clearly document expected behavior  

## Conclusion

The comprehensive test suite successfully validates all permission scenarios including the new withdrawn bids feature. All tests pass consistently with >90% code coverage, and performance benchmarks confirm all operations complete well within the 100ms requirement.