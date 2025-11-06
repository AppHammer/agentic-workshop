# Test Documentation: v0.0.1-1-2-1 - Add Task Context to Message Creation

## Overview
This document outlines the comprehensive test coverage for the task context feature in message creation, ensuring proper validation and permission checks when associating messages with specific tasks.

## Feature Summary
The POST /messages endpoint now accepts an optional `task_id` parameter that:
- Links messages to specific tasks for better conversation context
- Validates that the task exists in the database
- Ensures users have permission to discuss the task
- Maintains backward compatibility for general messages (without task_id)

## Acceptance Criteria Coverage

### ✅ POST /messages endpoint accepts optional task_id parameter
- **Test:** `test_message_with_valid_task_id`, `test_message_without_task_id`
- **Status:** Implemented
- **Details:** Messages can be created with or without task_id

### ✅ Task validation: task_id must exist in database
- **Test:** `test_message_with_invalid_task_id`
- **Status:** Implemented
- **Details:** Returns 404 error when task_id doesn't exist

### ✅ Task permission: sender must have permission to discuss that task
- **Test:** `test_message_task_permission_customer_not_owner`, `test_message_task_permission_tasker_no_relationship`
- **Status:** Implemented
- **Details:** Returns 403 error when user lacks permission

### ✅ Task_id properly stored in database with message
- **Test:** `test_message_with_valid_task_id` (includes database verification)
- **Status:** Implemented
- **Details:** Task_id persists correctly in Message table

### ✅ Error handling for invalid task_id
- **Test:** `test_message_with_invalid_task_id`, `test_message_task_permission_customer_not_owner`, `test_message_task_permission_tasker_no_relationship`
- **Status:** Implemented
- **Details:** Appropriate HTTP status codes and error messages

### ✅ Integration tests verify task association
- **Test:** All new test cases in `test_messages_integration.py`
- **Status:** Implemented
- **Details:** 8 new test cases covering all scenarios

### ✅ Messages without task_id still supported
- **Test:** `test_message_without_task_id`
- **Status:** Implemented
- **Details:** General messaging functionality preserved

## Test Cases

### 1. Positive Test Cases

#### Test: Message Creation with Valid Task ID
**Function:** `test_message_with_valid_task_id`
**Purpose:** Verify messages can be created with valid task_id when user has permission

**Setup:**
- Create customer and tasker users
- Create task owned by customer
- Create bid relationship (tasker bids on task)

**Steps:**
1. Tasker sends POST /messages with valid task_id
2. Verify response status 200
3. Verify task_id in response matches request
4. Query database to confirm task_id persisted

**Expected Results:**
- Status code: 200 OK
- Response contains task_id field
- Message stored in database with task_id

**Actual Results:** ✅ Pass

---

#### Test: Message Creation without Task ID (General Message)
**Function:** `test_message_without_task_id`
**Purpose:** Verify backward compatibility - messages can still be sent without task_id

**Setup:**
- Create customer and tasker users
- Create task and bid to establish relationship

**Steps:**
1. Tasker sends POST /messages without task_id field
2. Verify response status 200
3. Verify task_id is null in response

**Expected Results:**
- Status code: 200 OK
- Response task_id field is null
- Message created successfully

**Actual Results:** ✅ Pass

---

#### Test: Tasker Permission via Offer
**Function:** `test_message_task_permission_tasker_with_offer`
**Purpose:** Verify tasker can message about task when they have an offer

**Setup:**
- Create customer and tasker users
- Create task owned by customer
- Customer creates offer to tasker for the task

**Steps:**
1. Tasker sends POST /messages with task_id
2. Verify response status 200

**Expected Results:**
- Status code: 200 OK
- Message created with task_id

**Actual Results:** ✅ Pass

---

#### Test: Tasker Permission via Agreement
**Function:** `test_message_task_permission_tasker_with_agreement`
**Purpose:** Verify tasker can message about task when they have an agreement

**Setup:**
- Create customer and tasker users
- Create task with IN_PROGRESS status
- Create agreement between customer and tasker

**Steps:**
1. Tasker sends POST /messages with task_id
2. Verify response status 200

**Expected Results:**
- Status code: 200 OK
- Message created with task_id

**Actual Results:** ✅ Pass

---

### 2. Negative Test Cases

#### Test: Invalid Task ID
**Function:** `test_message_with_invalid_task_id`
**Purpose:** Verify proper error handling for non-existent task_id

**Setup:**
- Create customer and tasker users
- Create task and bid to establish messaging relationship
- Use non-existent task_id (99999)

**Steps:**
1. Tasker sends POST /messages with invalid task_id
2. Verify response status 404
3. Verify error message contains "not found"

**Expected Results:**
- Status code: 404 Not Found
- Error detail: "Task with id {id} not found"

**Actual Results:** ✅ Pass

---

#### Test: Customer Without Task Ownership
**Function:** `test_message_task_permission_customer_not_owner`
**Purpose:** Verify customer cannot message about tasks they don't own

**Setup:**
- Create customer, tasker, and other user
- Create task owned by "other" user
- Establish customer-tasker messaging relationship via different task

**Steps:**
1. Customer attempts to send message with other user's task_id
2. Verify response status 403
3. Verify error contains "permission"

**Expected Results:**
- Status code: 403 Forbidden
- Error detail: "You do not have permission to discuss this task"

**Actual Results:** ✅ Pass

---

#### Test: Tasker Without Task Relationship
**Function:** `test_message_task_permission_tasker_no_relationship`
**Purpose:** Verify tasker cannot message about task without bid/offer/agreement

**Setup:**
- Create customer and tasker users
- Create two tasks owned by customer
- Tasker has bid on one task but not the other

**Steps:**
1. Tasker attempts to message about task without relationship
2. Verify response status 403
3. Verify error contains "permission"

**Expected Results:**
- Status code: 403 Forbidden
- Error detail: "You do not have permission to discuss this task"

**Actual Results:** ✅ Pass

---

### 3. Edge Cases

#### Test: Existing Message Tests Still Pass
**Functions:** All existing tests in `test_messages_integration.py`
**Purpose:** Verify backward compatibility with existing functionality

**Covered Scenarios:**
- Message with bid relationship
- Message with offer relationship  
- Message with agreement relationship
- Message without relationship (forbidden)
- Forbidden response format
- User ID from JWT verification
- Cannot message self
- Multiple relationship types
- Unauthenticated attempts

**Expected Results:**
- All existing tests continue to pass
- No regression in functionality

**Actual Results:** ✅ Pass

---

## Test Execution

### Running Tests
```bash
cd app/backend
python -m pytest test_messages_integration.py -v
```

### Running Specific Test
```bash
python -m pytest test_messages_integration.py::test_message_with_valid_task_id -v
```

### Coverage Report
```bash
python -m pytest test_messages_integration.py --cov=main --cov-report=html
```

## Test Coverage Summary

| Category | Test Count | Status |
|----------|------------|--------|
| Positive Tests | 4 | ✅ Pass |
| Negative Tests | 3 | ✅ Pass |
| Edge Cases | 9 | ✅ Pass |
| **Total** | **16** | **✅ Pass** |

**Coverage Percentage:** >85% (Target Met)

## Permission Matrix

| User Role | Task Relationship | Can Message with task_id? |
|-----------|-------------------|---------------------------|
| Customer | Task Owner | ✅ Yes |
| Customer | Not Task Owner | ❌ No (403) |
| Tasker | Has Bid | ✅ Yes |
| Tasker | Has Offer | ✅ Yes |
| Tasker | Has Agreement | ✅ Yes |
| Tasker | No Relationship | ❌ No (403) |
| Any | Task Doesn't Exist | ❌ No (404) |

## Error Response Examples

### 404 - Task Not Found
```json
{
  "detail": "Task with id 99999 not found"
}
```

### 403 - Permission Denied
```json
{
  "detail": "You do not have permission to discuss this task"
}
```

## Database Verification

The test suite includes direct database queries to verify:
1. Task_id is correctly stored in Message table
2. Task_id can be null for general messages
3. Foreign key relationships are maintained
4. No orphaned messages created

## Integration Points

The task context feature integrates with:
1. **Permission System** - Uses existing `can_message_user()` function
2. **Task Model** - Validates against Task table
3. **Bid/Offer/Agreement Models** - Checks for task relationships
4. **Message Model** - Stores task_id reference

## Known Limitations

None identified. All acceptance criteria met and tested.

## Next Steps

1. ✅ All unit tests passing
2. ✅ Integration tests passing  
3. ✅ Permission validation working
4. ✅ Error handling comprehensive
5. 🔲 Frontend integration (blocked by this issue)
6. 🔲 End-to-end testing in staging environment

## Related Documentation

- Issue: v0.0.1-1-2-1
- Depends on: v0.0.1-1-1-2 (Integrate Permission Validation)
- Blocks: v0.0.1-1-2-2 (Enhance Message Response with Task Details)

## Test Maintenance

### Adding New Tests
When adding new test scenarios:
1. Follow existing naming convention: `test_message_task_<scenario>`
2. Include proper docstrings explaining purpose
3. Use fixtures for common setup (test_users, auth_headers)
4. Verify both response status and content
5. Clean up test database after test

### Updating Tests
If modifying the task context feature:
1. Update affected test assertions
2. Add new tests for new scenarios
3. Ensure all existing tests still pass
4. Update this documentation

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-06  
**Test Framework:** pytest 7.4.3  
**Code Coverage Tool:** pytest-cov 4.1.0