# Test Documentation: v0.0.1-2-4-1 - Implement Task-Filtered Message View

## Feature Summary
This feature adds task filtering functionality to the Messages component, allowing users to filter conversations by specific tasks. Users can select a task from a dropdown to view only conversations related to that task, or choose "All Tasks" to view all conversations.

## Acceptance Criteria
- [x] Task filter dropdown added to Messages component header
- [x] Dropdown populated with all tasks user is involved with
- [x] Tasks sorted by most recent activity (handled by backend)
- [x] "All Tasks" option to clear filter and show all conversations
- [x] Filter updates conversation list in real-time (no page refresh)
- [x] Empty state message when no conversations match selected task
- [x] Filter state persists during component session
- [x] Dropdown accessible via keyboard
- [x] Screen reader compatible

## Test Cases

### 1. Backend API Tests

#### Test Case 1.1: Get User Tasks - Customer Role
**Objective:** Verify that customers can retrieve all tasks they created

**Prerequisites:**
- Customer user account exists and is authenticated
- Customer has created multiple tasks

**Test Steps:**
1. Authenticate as a customer user
2. Send GET request to `/tasks/my-tasks`
3. Verify response contains all tasks created by the customer
4. Verify response status is 200

**Expected Results:**
- API returns 200 status code
- Response contains array of tasks
- All tasks have `customer_id` matching the authenticated user
- Tasks include all required fields (id, title, status, etc.)

**Test Data:**
```python
# Customer with tasks
customer_id = 1
expected_tasks = [
    {"id": 1, "title": "Task 1", "customer_id": 1, "status": "open"},
    {"id": 2, "title": "Task 2", "customer_id": 1, "status": "in_progress"}
]
```

#### Test Case 1.2: Get User Tasks - Tasker Role with Bids
**Objective:** Verify that taskers can retrieve tasks they have bid on

**Prerequisites:**
- Tasker user account exists and is authenticated
- Tasker has placed bids on multiple tasks

**Test Steps:**
1. Authenticate as a tasker user
2. Send GET request to `/tasks/my-tasks`
3. Verify response contains all tasks the tasker has bid on
4. Verify response status is 200

**Expected Results:**
- API returns 200 status code
- Response contains array of tasks
- All returned tasks have associated bids from the authenticated tasker
- No duplicate tasks in response

**Test Data:**
```python
# Tasker with bids
tasker_id = 2
bid_task_ids = [1, 3, 5]
```

#### Test Case 1.3: Get User Tasks - Tasker Role with Offers
**Objective:** Verify that taskers can retrieve tasks with offers

**Prerequisites:**
- Tasker user account exists and is authenticated
- Tasker has received offers on multiple tasks

**Test Steps:**
1. Authenticate as a tasker user
2. Send GET request to `/tasks/my-tasks`
3. Verify response contains tasks with offers for the tasker
4. Verify response status is 200

**Expected Results:**
- API returns 200 status code
- Response includes tasks where tasker received offers
- Tasks are not duplicated

#### Test Case 1.4: Get User Tasks - Tasker Role with Agreements
**Objective:** Verify that taskers can retrieve tasks they have agreements for

**Prerequisites:**
- Tasker user account exists and is authenticated
- Tasker has accepted agreements on multiple tasks

**Test Steps:**
1. Authenticate as a tasker user
2. Send GET request to `/tasks/my-tasks`
3. Verify response contains tasks with active agreements
4. Verify response status is 200

**Expected Results:**
- API returns 200 status code
- Response includes tasks with agreements involving the tasker
- No duplicate tasks

#### Test Case 1.5: Get User Tasks - No Tasks
**Objective:** Verify correct response when user has no associated tasks

**Prerequisites:**
- User account exists and is authenticated
- User has not created any tasks (customer) or participated in any tasks (tasker)

**Test Steps:**
1. Authenticate as a new user
2. Send GET request to `/tasks/my-tasks`
3. Verify response is an empty array
4. Verify response status is 200

**Expected Results:**
- API returns 200 status code
- Response is an empty array `[]`

#### Test Case 1.6: Get User Tasks - Unauthorized
**Objective:** Verify unauthorized access is properly rejected

**Prerequisites:**
- No authentication token provided

**Test Steps:**
1. Send GET request to `/tasks/my-tasks` without authentication
2. Verify response status is 401

**Expected Results:**
- API returns 401 Unauthorized status
- Error message indicates authentication required

### 2. Frontend Component Tests

#### Test Case 2.1: Task Filter Dropdown Renders
**Objective:** Verify task filter dropdown renders correctly

**Prerequisites:**
- User is authenticated
- Messages component is mounted
- User has tasks available

**Test Steps:**
1. Navigate to Messages page
2. Verify task filter dropdown is visible in header
3. Verify "Filter by Task:" label is displayed
4. Verify dropdown has "All Tasks" as default option

**Expected Results:**
- Dropdown element is rendered
- Label text is "Filter by Task:"
- Default selection shows "All Tasks"
- Dropdown is accessible and focusable

**Test Code:**
```javascript
test('renders task filter dropdown', () => {
  render(<Messages user={mockUser} />);
  
  const label = screen.getByText(/filter by task/i);
  expect(label).toBeInTheDocument();
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  expect(dropdown).toBeInTheDocument();
  expect(dropdown).toHaveValue('');
});
```

#### Test Case 2.2: Task Filter Dropdown Populated
**Objective:** Verify dropdown is populated with user's tasks

**Prerequisites:**
- User is authenticated
- User has multiple tasks
- Messages component is mounted

**Test Steps:**
1. Mock getUserTasks API to return task list
2. Render Messages component
3. Wait for tasks to load
4. Verify dropdown contains all tasks
5. Verify task titles and statuses are displayed

**Expected Results:**
- Dropdown contains one option per task
- Each option displays task title and status
- "All Tasks" option is present
- Options are in correct format: "Title (status)"

**Test Code:**
```javascript
test('populates dropdown with user tasks', async () => {
  const mockTasks = [
    { id: 1, title: 'Fix plumbing', status: 'open' },
    { id: 2, title: 'Paint walls', status: 'in_progress' }
  ];
  
  getUserTasks.mockResolvedValue({ data: mockTasks });
  
  render(<Messages user={mockUser} />);
  
  await waitFor(() => {
    const dropdown = screen.getByLabelText(/filter messages by task/i);
    expect(dropdown).toHaveLength(3); // All Tasks + 2 tasks
    expect(screen.getByText(/fix plumbing \(open\)/i)).toBeInTheDocument();
    expect(screen.getByText(/paint walls \(in_progress\)/i)).toBeInTheDocument();
  });
});
```

#### Test Case 2.3: Filter Conversations by Task
**Objective:** Verify selecting a task filters conversations correctly

**Prerequisites:**
- User is authenticated
- Multiple conversations exist with different task_ids
- Tasks are loaded

**Test Steps:**
1. Render Messages component with conversations
2. Select a specific task from dropdown
3. Verify only conversations with messages for that task are shown
4. Verify other conversations are hidden

**Expected Results:**
- Conversation list updates immediately
- Only matching conversations are displayed
- Conversation count reflects filtered results
- No page refresh occurs

**Test Code:**
```javascript
test('filters conversations when task is selected', async () => {
  const mockConversations = [
    {
      partnerId: 1,
      messages: [{ task_id: 1, content: 'About task 1' }]
    },
    {
      partnerId: 2,
      messages: [{ task_id: 2, content: 'About task 2' }]
    }
  ];
  
  getMessages.mockResolvedValue({ data: mockConversations });
  
  render(<Messages user={mockUser} />);
  
  await waitFor(() => {
    expect(screen.getAllByRole('button')).toHaveLength(2);
  });
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  fireEvent.change(dropdown, { target: { value: '1' } });
  
  await waitFor(() => {
    expect(screen.getAllByRole('button')).toHaveLength(1);
  });
});
```

#### Test Case 2.4: Clear Filter with "All Tasks"
**Objective:** Verify "All Tasks" option clears the filter

**Prerequisites:**
- User is authenticated
- A task filter is currently applied
- Multiple conversations exist

**Test Steps:**
1. Render Messages component with active filter
2. Select "All Tasks" from dropdown
3. Verify all conversations are displayed
4. Verify filter state is cleared

**Expected Results:**
- All conversations become visible
- Conversation list shows complete list
- Filter value is null/empty
- No error messages

**Test Code:**
```javascript
test('shows all conversations when "All Tasks" is selected', async () => {
  render(<Messages user={mockUser} />);
  
  // Apply filter
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  fireEvent.change(dropdown, { target: { value: '1' } });
  
  // Clear filter
  fireEvent.change(dropdown, { target: { value: '' } });
  
  await waitFor(() => {
    expect(screen.getAllByRole('button').length).toBeGreaterThan(1);
  });
});
```

#### Test Case 2.5: Empty State for No Matches
**Objective:** Verify appropriate message when filter has no matches

**Prerequisites:**
- User is authenticated
- Conversations exist but none match selected task

**Test Steps:**
1. Render Messages component
2. Select a task that has no associated conversations
3. Verify empty state message is displayed
4. Verify message text indicates no conversations for task

**Expected Results:**
- Empty state element is visible
- Message reads "No conversations found for this task"
- No conversation items are displayed
- Dropdown remains functional

**Test Code:**
```javascript
test('displays empty state when no conversations match filter', async () => {
  const mockConversations = [
    {
      partnerId: 1,
      messages: [{ task_id: 1, content: 'Message' }]
    }
  ];
  
  getMessages.mockResolvedValue({ data: mockConversations });
  
  render(<Messages user={mockUser} />);
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  fireEvent.change(dropdown, { target: { value: '99' } }); // Non-existent task
  
  await waitFor(() => {
    expect(screen.getByText(/no conversations found for this task/i)).toBeInTheDocument();
  });
});
```

#### Test Case 2.6: Filter State Persistence
**Objective:** Verify filter state persists during component lifecycle

**Prerequisites:**
- User is authenticated
- A task filter is applied

**Test Steps:**
1. Render Messages component
2. Select a task filter
3. Select a conversation
4. Send a message
5. Verify filter remains applied after message sent

**Expected Results:**
- Filter selection persists after actions
- Filtered conversations remain filtered
- Dropdown value doesn't reset
- New messages appear in filtered view if applicable

**Test Code:**
```javascript
test('filter state persists after sending message', async () => {
  render(<Messages user={mockUser} />);
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  fireEvent.change(dropdown, { target: { value: '1' } });
  
  // Send a message
  const input = screen.getByLabelText(/message input/i);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.submit(input.closest('form'));
  
  await waitFor(() => {
    expect(dropdown).toHaveValue('1');
  });
});
```

#### Test Case 2.7: Keyboard Navigation
**Objective:** Verify keyboard accessibility of dropdown

**Prerequisites:**
- User is authenticated
- Messages component is rendered

**Test Steps:**
1. Tab to task filter dropdown
2. Verify dropdown receives focus
3. Use arrow keys to navigate options
4. Press Enter to select option
5. Verify selection works via keyboard

**Expected Results:**
- Dropdown is keyboard focusable
- Focus indicator is visible
- Arrow keys navigate options
- Enter/Space selects option
- Escape closes dropdown

**Test Code:**
```javascript
test('dropdown is keyboard accessible', () => {
  render(<Messages user={mockUser} />);
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  
  dropdown.focus();
  expect(dropdown).toHaveFocus();
  
  fireEvent.keyDown(dropdown, { key: 'ArrowDown' });
  fireEvent.keyDown(dropdown, { key: 'Enter' });
  
  // Verify selection changed
  expect(dropdown.value).toBeTruthy();
});
```

#### Test Case 2.8: Screen Reader Compatibility
**Objective:** Verify proper ARIA labels and screen reader support

**Prerequisites:**
- Screen reader testing tools available
- Messages component is rendered

**Test Steps:**
1. Inspect dropdown element for ARIA attributes
2. Verify label association
3. Check for aria-label or aria-labelledby
4. Verify options have descriptive text
5. Test with screen reader software

**Expected Results:**
- Dropdown has proper aria-label
- Label element is correctly associated
- Options are announced clearly
- Selection changes are announced
- Empty state is announced

**Test Code:**
```javascript
test('dropdown has proper accessibility attributes', () => {
  render(<Messages user={mockUser} />);
  
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  expect(dropdown).toHaveAttribute('aria-label', 'Filter messages by task');
  expect(dropdown).toHaveAttribute('id', 'task-filter');
  
  const label = screen.getByText(/filter by task/i);
  expect(label).toHaveAttribute('for', 'task-filter');
});
```

### 3. Integration Tests

#### Test Case 3.1: End-to-End Filter Flow
**Objective:** Verify complete filtering workflow

**Prerequisites:**
- Backend and frontend running
- Test user with tasks and messages

**Test Steps:**
1. Login as test user
2. Navigate to Messages page
3. Verify dropdown loads with tasks
4. Select a task
5. Verify conversations filter correctly
6. Send a message in filtered view
7. Switch to "All Tasks"
8. Verify all conversations visible

**Expected Results:**
- Complete flow works without errors
- Data loads correctly from API
- Filtering works in real-time
- Messages send successfully while filtered
- UI remains responsive

#### Test Case 3.2: Multiple Task Types
**Objective:** Verify filtering works with different task statuses

**Prerequisites:**
- User has tasks in different statuses (open, in_progress, completed)
- Conversations exist for each task type

**Test Steps:**
1. Load Messages component
2. Verify tasks of all statuses appear in dropdown
3. Filter by open task
4. Filter by in_progress task
5. Filter by completed task
6. Verify each filter shows correct conversations

**Expected Results:**
- All task statuses are shown
- Each filter correctly isolates conversations
- Status is displayed in dropdown
- No cross-contamination of results

### 4. Error Handling Tests

#### Test Case 4.1: API Error Loading Tasks
**Objective:** Verify graceful handling of task loading errors

**Prerequisites:**
- Messages component mounted
- getUserTasks API fails

**Test Steps:**
1. Mock getUserTasks to reject
2. Render Messages component
3. Verify error is handled gracefully
4. Verify component remains functional
5. Check console for error logging

**Expected Results:**
- No crash or white screen
- Error is logged to console
- Dropdown shows only "All Tasks"
- Conversations still load and display
- Error message may be shown to user

**Test Code:**
```javascript
test('handles error when loading tasks fails', async () => {
  const consoleError = jest.spyOn(console, 'error').mockImplementation();
  getUserTasks.mockRejectedValue(new Error('API Error'));
  
  render(<Messages user={mockUser} />);
  
  await waitFor(() => {
    expect(consoleError).toHaveBeenCalledWith('Error loading tasks:', expect.any(Error));
  });
  
  // Component should still work
  const dropdown = screen.getByLabelText(/filter messages by task/i);
  expect(dropdown).toBeInTheDocument();
  
  consoleError.mockRestore();
});
```

#### Test Case 4.2: Invalid Task ID
**Objective:** Verify handling of invalid or deleted task IDs

**Prerequisites:**
- User selects a task
- Task is deleted while dropdown is open

**Test Steps:**
1. Load component with tasks
2. Apply filter for a task
3. Task gets deleted from backend
4. Reload messages
5. Verify graceful handling

**Expected Results:**
- No errors thrown
- Filter may reset or show empty
- User can select different task
- Component remains functional

### 5. Performance Tests

#### Test Case 5.1: Large Task List
**Objective:** Verify performance with many tasks

**Prerequisites:**
- User has 50+ tasks

**Test Steps:**
1. Load Messages with 50+ tasks
2. Measure dropdown render time
3. Select task from bottom of list
4. Measure filter application time

**Expected Results:**
- Dropdown renders in < 1 second
- All tasks are visible
- Filtering completes in < 500ms
- No UI lag or freezing

#### Test Case 5.2: Large Conversation List
**Objective:** Verify filter performance with many conversations

**Prerequisites:**
- User has 100+ conversations

**Test Steps:**
1. Load Messages with 100+ conversations
2. Apply task filter
3. Measure time to filter results
4. Switch between different tasks

**Expected Results:**
- Filtering completes quickly (< 1 second)
- UI remains responsive
- No memory leaks
- Scrolling remains smooth

## Test Coverage Goals

### Unit Tests
- Target: >85% code coverage
- Focus areas:
  - Filter logic
  - State management
  - Event handlers
  - Empty state handling

### Integration Tests
- Backend endpoint functionality
- API-Frontend integration
- User interaction flows

### Accessibility Tests
- Keyboard navigation
- Screen reader compatibility
- ARIA attributes
- Focus management

## Test Execution

### Manual Testing Checklist
- [ ] Dropdown renders correctly
- [ ] Tasks load properly
- [ ] Filtering works as expected
- [ ] "All Tasks" clears filter
- [ ] Empty state displays correctly
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Filter persists during session
- [ ] Works on desktop browsers
- [ ] Works on mobile devices
- [ ] Error handling works
- [ ] Performance is acceptable

### Automated Testing
```bash
# Run frontend tests
cd app/frontend
npm test -- --coverage

# Run backend tests
cd app/backend
pytest test_main.py -v --cov
```

## Known Issues and Limitations

1. **Task Sorting**: Tasks are not explicitly sorted by recent activity in the current implementation. They rely on database order.
2. **Real-time Updates**: If new tasks are created during the session, they won't appear until page refresh.
3. **Message Context**: The filter checks if ANY message in a conversation matches the task_id, which may include older messages.

## Future Enhancements

1. Add task search/filtering in dropdown for large lists
2. Show conversation count per task
3. Add visual indicators for unread messages per task
4. Implement real-time task list updates
5. Add sorting options (recent, alphabetical, status)
6. Cache filter selection in localStorage

## Test Sign-off

**Tested By:** _________________  
**Date:** _________________  
**Result:** ☐ Pass ☐ Fail ☐ Pass with Issues  
**Notes:** _________________