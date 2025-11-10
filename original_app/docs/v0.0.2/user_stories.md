# v0.0.2 User Profile: Self-Service Profile Viewing - User Stories

## Overview

This document contains detailed user stories for the User Profile: Self-Service Profile Viewing feature in version 0.0.2 of the Tasker Platform. This feature enables logged-in users to view their own profile information by making their username clickable in the navigation bar, which navigates to a dedicated profile page displaying all relevant user account details from the User model. This enhancement provides transparency about stored user information, allows verification of account details, and enables taskers to review their professional presentation to customers.

---

## Story Summary

| Story ID | Epic | Title | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- |
| v0.0.2-1-1 | Epic 1 | Clickable Username Navigation | 3 | High |
| v0.0.2-2-1 | Epic 2 | Customer Profile View | 5 | High |
| v0.0.2-2-2 | Epic 2 | Tasker Profile View with Professional Details | 8 | High |
| v0.0.2-2-3 | Epic 2 | Read-Only Profile Display | 3 | Medium |
| v0.0.2-3-1 | Epic 3 | Dashboard Navigation from Profile | 2 | Low |

---

## Epic 1: Navigation Enhancement

### Story v0.0.2-1-1: Clickable Username Navigation

**User Story:**
As a logged-in user  
I want to click on my username in the navigation bar  
So that I can navigate to my profile page

**Acceptance Criteria (Gherkin Format):**

**Scenario 1: Username displays as clickable link**
**Given** I am logged in to the Tasker Platform  
**When** I view the navigation bar  
**Then** my username should be displayed as a clickable link  
**And** the link should show visual indication on hover (e.g., underline, cursor change)

**Scenario 2: Navigation to profile page**
**Given** I am logged in and viewing any page  
**When** I click on my username in the navigation bar  
**Then** I should be navigated to the `/profile` route  
**And** the profile page should load and display my information

**Scenario 3: Navigation maintains authentication**
**Given** I am logged in and click my username  
**When** the profile page loads  
**Then** I should remain authenticated  
**And** my session should not be disrupted

**Detailed Acceptance Criteria:**
- Navbar component must convert the static `<span>` element to a React Router `<Link>` component
- Link must maintain existing display format: `{user.full_name} ({user.role})`
- Visual feedback must be provided on hover (CSS styling)
- Link must use React Router's `<Link>` component for client-side navigation (no page reload)
- Link must navigate to `/profile` route
- Current role display `({user.role})` must remain visible in the link text
- Link must be accessible (keyboard navigable, screen reader friendly)
- Navigation must work from all pages where navbar is displayed

**Definition of Done:**
- [ ] [`Navbar.js`](../../app/frontend/src/components/Navbar.js) updated to convert username span to Link component
- [ ] CSS styling added for hover state on username link
- [ ] Link navigates to `/profile` route using React Router
- [ ] Manual testing confirms link works from all dashboard pages
- [ ] Accessibility verified (keyboard navigation, screen reader)
- [ ] Code reviewed and approved by at least one peer
- [ ] No regressions in existing navbar functionality

**Technical Implementation Notes:**

**File to Modify:** [`app/frontend/src/components/Navbar.js`](../../app/frontend/src/components/Navbar.js)

**Current Implementation (lines 13-15):**
```jsx
<span>
  {user.full_name} ({user.role})
</span>
```

**Updated Implementation:**
```jsx
<Link to="/profile" style={{ color: 'white', textDecoration: 'none' }}>
  {user.full_name} ({user.role})
</Link>
```

**CSS Addition (in component or index.css):**
```css
/* Username link hover effect */
.navbar a:hover {
  text-decoration: underline;
  opacity: 0.9;
}
```

**Dependencies:**
- Ensure `Link` is imported from `react-router-dom` at the top of Navbar.js
- Profile route must be created in App.js (handled in Epic 2)

---

## Epic 2: Profile Display

### Story v0.0.2-2-1: Customer Profile View

**User Story:**
As a customer  
I want to view my profile information (email, full name, role, phone, location, account creation date)  
So that I can verify my account details are correct

**Acceptance Criteria (Gherkin Format):**

**Scenario 1: Navigate to profile page**
**Given** I am logged in as a customer  
**When** I click on my username in the navbar  
**Then** I should be navigated to my profile page  
**And** the page should display "My Profile" or similar heading

**Scenario 2: Display common user fields**
**Given** I am viewing my profile page as a customer  
**When** the page loads  
**Then** I should see my full name displayed  
**And** I should see my email address  
**And** I should see my role displayed as "Customer"  
**And** I should see my phone number (or "Not provided" if null)  
**And** I should see my location (or "Not provided" if null)  
**And** I should see my account creation date in a readable format

**Scenario 3: Fields are properly formatted**
**Given** I am viewing my profile as a customer  
**When** I review the displayed fields  
**Then** the creation date should be formatted as a human-readable string (e.g., "November 10, 2025")  
**And** the role should be capitalized (e.g., "Customer" not "customer")  
**And** empty optional fields should show "Not provided" or "N/A"

**Scenario 4: Sensitive data is hidden**
**Given** I am viewing my profile page  
**When** the page displays my information  
**Then** my password should never be shown  
**And** my user ID should not be displayed to me

**Detailed Acceptance Criteria:**
- Profile component must fetch user data using existing `/users/me` endpoint via [`getCurrentUser()`](../../app/frontend/src/api.js)
- All common user fields must be displayed: `full_name`, `email`, `role`, `phone`, `location`, `created_at`
- Fields must be displayed in a clean, organized layout (consider card or section-based design)
- Date formatting must convert ISO timestamp to human-readable format
- Role must be displayed with first letter capitalized
- Null or empty optional fields (`phone`, `location`) must show placeholder text "Not provided"
- Sensitive fields (`id`, `hashed_password`) must never be displayed
- Profile page must be protected by authentication (redirect to login if not authenticated)
- Component must handle loading states while fetching data
- Component must handle error states if data fetch fails

**Definition of Done:**
- [ ] New `Profile.js` component created in [`app/frontend/src/components/`](../../app/frontend/src/components/)
- [ ] Component fetches user data using existing `getCurrentUser()` API function
- [ ] All six common fields displayed correctly with proper formatting
- [ ] Date formatting implemented (e.g., using `new Date().toLocaleDateString()`)
- [ ] Placeholder text shown for null/empty optional fields
- [ ] Loading state displayed while data is being fetched
- [ ] Error state handled gracefully with user-friendly message
- [ ] Protected route added in [`App.js`](../../app/frontend/src/App.js) for `/profile`
- [ ] Manual testing confirms all fields display correctly for customer users
- [ ] Code reviewed and approved by at least one peer

**Technical Implementation Notes:**

**New File:** `app/frontend/src/components/Profile.js`

**Component Structure:**
```jsx
import React, { useState, useEffect } from 'react';
import { getCurrentUser } from '../api';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (err) {
        setError('Failed to load profile');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) return <div>Loading profile...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!user) return <div>No profile data available</div>;

  return (
    <div className="profile-container">
      <h2>My Profile</h2>
      
      <div className="profile-section">
        <h3>Account Information</h3>
        <div className="profile-field">
          <label>Full Name:</label>
          <span>{user.full_name}</span>
        </div>
        <div className="profile-field">
          <label>Email:</label>
          <span>{user.email}</span>
        </div>
        <div className="profile-field">
          <label>Role:</label>
          <span>{user.role.charAt(0).toUpperCase() + user.role.slice(1)}</span>
        </div>
        <div className="profile-field">
          <label>Phone:</label>
          <span>{user.phone || 'Not provided'}</span>
        </div>
        <div className="profile-field">
          <label>Location:</label>
          <span>{user.location || 'Not provided'}</span>
        </div>
        <div className="profile-field">
          <label>Member Since:</label>
          <span>{formatDate(user.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

export default Profile;
```

**Route Addition in App.js:**
```jsx
import Profile from './components/Profile';

// Inside Routes component
<Route path="/profile" element={
  isAuthenticated ? <Profile /> : <Navigate to="/login" />
} />
```

**Data Source:**
- Uses existing `/users/me` endpoint (already implemented in backend)
- Endpoint returns complete user object per [`UserResponse` schema](../../app/backend/schemas.py)

---

### Story v0.0.2-2-2: Tasker Profile View with Professional Details

**User Story:**
As a tasker  
I want to view my complete profile including my professional details (skills, hourly rate, bio) in addition to basic account information  
So that I can see what customers will see about me

**Acceptance Criteria (Gherkin Format):**

**Scenario 1: Display all customer fields**
**Given** I am logged in as a tasker  
**When** I view my profile page  
**Then** I should see all the same fields a customer sees (full name, email, role, phone, location, creation date)

**Scenario 2: Display tasker-specific fields**
**Given** I am logged in as a tasker  
**When** I view my profile page  
**Then** I should see a "Professional Information" section  
**And** I should see my skills listed  
**And** I should see my hourly rate formatted as currency  
**And** I should see my bio/description

**Scenario 3: Handle missing professional data**
**Given** I am a tasker who has not fully completed my professional profile  
**When** I view my profile page  
**Then** empty professional fields should display "Not provided" or similar placeholder  
**And** the lack of data should be clearly indicated

**Scenario 4: Conditional rendering for role**
**Given** the profile component is rendered  
**When** the user role is "customer"  
**Then** professional information section should not be displayed  
**And when** the user role is "tasker"  
**Then** professional information section should be displayed

**Detailed Acceptance Criteria:**
- Component must conditionally render "Professional Information" section only for taskers
- Conditional rendering must check `user.role === 'tasker'`
- Skills field must be displayed (handle string or array format if applicable)
- Hourly rate must be formatted as currency with $ symbol (e.g., "$25.00")
- Bio must be displayed with proper text formatting (preserve line breaks if applicable)
- Empty tasker-specific fields must show "Not provided" placeholder
- Section must be clearly visually separated from account information (e.g., separate card or divider)
- Hourly rate formatting must handle decimal places correctly
- If a tasker has no professional data, the section should still display with placeholders

**Definition of Done:**
- [ ] Profile component updated to include conditional tasker-specific section
- [ ] Skills field displays correctly (string or formatted list)
- [ ] Hourly rate formatted as currency with two decimal places
- [ ] Bio displays with proper text formatting
- [ ] Conditional rendering logic implemented using `user.role === 'tasker'`
- [ ] Placeholder text shown for empty professional fields
- [ ] Visual separation between account and professional sections
- [ ] Manual testing with both customer and tasker accounts confirms correct display
- [ ] Code handles edge cases (null values, zero hourly rate, empty strings)
- [ ] Code reviewed and approved by at least one peer

**Technical Implementation Notes:**

**Profile.js Enhancement:**

Add after Account Information section:

```jsx
{user.role === 'tasker' && (
  <div className="profile-section">
    <h3>Professional Information</h3>
    <div className="profile-field">
      <label>Skills:</label>
      <span>{user.skills || 'Not provided'}</span>
    </div>
    <div className="profile-field">
      <label>Hourly Rate:</label>
      <span>
        {user.hourly_rate 
          ? `$${parseFloat(user.hourly_rate).toFixed(2)}` 
          : 'Not provided'}
      </span>
    </div>
    <div className="profile-field">
      <label>Bio:</label>
      <span style={{ whiteSpace: 'pre-wrap' }}>
        {user.bio || 'Not provided'}
      </span>
    </div>
  </div>
)}
```

**Data Model Reference:**
From [`database.py`](../../app/backend/database.py), tasker-specific fields:
- `skills: String` (nullable)
- `hourly_rate: Float` (nullable)
- `bio: Text` (nullable)

**Formatting Helpers:**
```javascript
// Hourly rate formatter
const formatRate = (rate) => {
  if (!rate || rate === 0) return 'Not provided';
  return `$${parseFloat(rate).toFixed(2)}`;
};

// Bio formatter (preserve line breaks)
const formatBio = (bio) => {
  if (!bio || bio.trim() === '') return 'Not provided';
  return bio;
};
```

**Visual Design Considerations:**
- Use consistent styling with Account Information section
- Consider adding an icon or badge to indicate professional information
- Ensure proper spacing between sections
- Consider using a different background color or border for visual separation

---

### Story v0.0.2-2-3: Read-Only Profile Display

**User Story:**
As a user  
I want a clear, read-only view of my profile  
So that I can review my information without accidentally modifying it

**Acceptance Criteria (Gherkin Format):**

**Scenario 1: All fields displayed as read-only**
**Given** I am viewing my profile page  
**When** I look at any profile field  
**Then** the field should be displayed as plain text  
**And** there should be no input fields, textareas, or editable elements

**Scenario 2: No edit controls present**
**Given** I am viewing my profile page  
**When** I review the entire page  
**Then** there should be no "Edit" buttons  
**And** there should be no "Save" buttons  
**And** there should be no form controls

**Scenario 3: Clear visual indication of read-only status**
**Given** I am viewing my profile page  
**When** the page is displayed  
**Then** the styling should clearly indicate this is informational only  
**And** the layout should emphasize readability over editability

**Detailed Acceptance Criteria:**
- All profile data must be displayed using non-editable elements (`<span>`, `<p>`, `<div>`)
- No `<input>`, `<textarea>`, or `<select>` elements should be present
- No edit, save, or cancel buttons should be displayed
- Visual design should emphasize information display (use of labels, clear hierarchy)
- Consider using definition list (`<dl>`, `<dt>`, `<dd>`) or similar semantic markup
- Fields should be clearly labeled with readable label text
- Text should have sufficient contrast and readability
- Layout should be scannable and easy to read
- Future edit functionality should be easily addable without major refactoring

**Definition of Done:**
- [ ] All profile fields rendered as read-only text elements
- [ ] No form controls or input elements present in component
- [ ] No edit/save/cancel buttons in the UI
- [ ] Labels clearly identify each field
- [ ] Visual design emphasizes information presentation
- [ ] Semantic HTML used for accessibility
- [ ] Manual inspection confirms no interactive elements except navigation
- [ ] Component structure allows for future edit mode addition
- [ ] Code reviewed and approved by at least one peer

**Technical Implementation Notes:**

**Display Pattern:**

Use label-value pairs with semantic HTML:

```jsx
<div className="profile-field">
  <label className="field-label">Email:</label>
  <span className="field-value">{user.email}</span>
</div>
```

**Alternative: Definition List (more semantic)**
```jsx
<dl className="profile-details">
  <dt>Email</dt>
  <dd>{user.email}</dd>
  
  <dt>Phone</dt>
  <dd>{user.phone || 'Not provided'}</dd>
  
  {/* ... more fields */}
</dl>
```

**CSS Styling for Read-Only Display:**
```css
.profile-field {
  display: flex;
  margin-bottom: 15px;
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.field-label {
  font-weight: 600;
  min-width: 150px;
  color: #555;
}

.field-value {
  color: #333;
  flex: 1;
}

.profile-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
```

**Design Principles:**
- Clear visual hierarchy (heading → section → fields)
- Generous whitespace for readability
- Consistent field spacing and alignment
- Subtle visual separation between sections
- Professional, clean appearance

**Future Extensibility:**
- Component structure should allow adding edit mode by:
  - Adding state for `editMode` boolean
  - Conditionally rendering input fields vs. text
  - Adding edit/save button handlers
- Consider separating display logic into a separate component if edit mode is added later

---

## Epic 3: User Experience Features

### Story v0.0.2-3-1: Dashboard Navigation from Profile

**User Story:**
As a user  
I want to easily navigate back to the dashboard from my profile page  
So that I can continue working on tasks without getting stuck

**Acceptance Criteria (Gherkin Format):**

**Scenario 1: Back to Dashboard button present**
**Given** I am viewing my profile page  
**When** I look at the page  
**Then** I should see a "Back to Dashboard" button or link  
**And** the button should be prominently placed and easy to find

**Scenario 2: Navigation to appropriate dashboard**
**Given** I am a customer viewing my profile  
**When** I click "Back to Dashboard"  
**Then** I should be navigated to `/customer-dashboard`

**Scenario 3: Tasker navigation to tasker dashboard**
**Given** I am a tasker viewing my profile  
**When** I click "Back to Dashboard"  
**Then** I should be navigated to `/tasker-dashboard`

**Scenario 4: Browser back button works**
**Given** I navigated to profile from a dashboard  
**When** I click the browser back button  
**Then** I should be returned to the dashboard I came from  
**And** the page state should be preserved

**Detailed Acceptance Criteria:**
- Profile page must include a navigation button/link to return to dashboard
- Navigation must be role-aware (customer → customer dashboard, tasker → tasker dashboard)
- Button should use React Router's `<Link>` or `useNavigate()` for client-side navigation
- Button placement should be intuitive (top of page, bottom of page, or both)
- Button styling should be consistent with other navigation elements
- Alternative: navbar remains visible, providing implicit navigation via existing links
- Browser back button should work correctly due to proper React Router usage
- Navigation should not disrupt user's authentication state
- Consider keyboard navigation support for accessibility

**Definition of Done:**
- [ ] "Back to Dashboard" button added to Profile component
- [ ] Navigation logic determines correct dashboard based on `user.role`
- [ ] Button uses React Router for navigation
- [ ] Button placement is user-friendly and intuitive
- [ ] Button styling matches application design system
- [ ] Manual testing confirms navigation works for both roles
- [ ] Browser back button functionality verified
- [ ] Keyboard navigation tested
- [ ] Code reviewed and approved by at least one peer

**Technical Implementation Notes:**

**Implementation Approach 1: Conditional Link**

```jsx
import { Link } from 'react-router-dom';

function Profile() {
  // ... existing code ...
  
  const dashboardPath = user.role === 'customer' 
    ? '/customer-dashboard' 
    : '/tasker-dashboard';
  
  return (
    <div className="profile-container">
      <h2>My Profile</h2>
      
      {/* Back button at top */}
      <Link to={dashboardPath} className="back-button">
        ← Back to Dashboard
      </Link>
      
      {/* Profile content */}
      
      {/* Optional: Back button at bottom too */}
      <Link to={dashboardPath} className="back-button">
        ← Back to Dashboard
      </Link>
    </div>
  );
}
```

**Implementation Approach 2: useNavigate Hook**

```jsx
import { useNavigate } from 'react-router-dom';

function Profile() {
  const navigate = useNavigate();
  // ... existing code ...
  
  const handleBackToDashboard = () => {
    const dashboardPath = user.role === 'customer' 
      ? '/customer-dashboard' 
      : '/tasker-dashboard';
    navigate(dashboardPath);
  };
  
  return (
    <div className="profile-container">
      <button onClick={handleBackToDashboard} className="back-button">
        ← Back to Dashboard
      </button>
      {/* ... profile content ... */}
    </div>
  );
}
```

**CSS Styling:**
```css
.back-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 5px;
  margin-bottom: 20px;
  cursor: pointer;
  border: none;
  font-size: 14px;
}

.back-button:hover {
  background-color: #0056b3;
  text-decoration: none;
}
```

**Placement Options:**
1. **Top only**: Good for quick exit, visible immediately
2. **Bottom only**: Good after user reviews all information
3. **Both top and bottom**: Best user experience, covers both use cases
4. **Relying on navbar**: If navbar is always visible, this may be sufficient

**Recommended:** Include button at top of page for immediate access, with navbar providing additional navigation options.

**Alternative Navigation:**
- Navbar remains visible on profile page, providing links to dashboards
- Consider adding breadcrumb navigation: Home > Dashboard > Profile
- Browser back button will work automatically with React Router (no page reload)

---

## Story Dependencies

### Critical Path

The stories must be completed in the following sequence for the feature to work:

1. **v0.0.2-1-1** (Clickable Username Navigation) → **v0.0.2-2-1** (Customer Profile View)
   - Navigation must be implemented before profile component, as it provides the entry point
   
2. **v0.0.2-2-1** (Customer Profile View) → **v0.0.2-2-2** (Tasker Profile View)
   - Basic customer profile provides foundation for tasker-specific enhancements
   
3. **v0.0.2-2-1** (Customer Profile View) → **v0.0.2-2-3** (Read-Only Profile Display)
   - Read-only display styling can be applied once base profile structure exists
   
4. **v0.0.2-2-1** (Customer Profile View) → **v0.0.2-3-1** (Dashboard Navigation)
   - Dashboard navigation requires profile page to exist

### Parallel Development Opportunities

The following stories can be developed concurrently after the base profile component is created:

- **Group 1** (After v0.0.2-2-1 is complete):
  - v0.0.2-2-2 (Tasker Professional Details) - can be developed in parallel with read-only styling
  - v0.0.2-2-3 (Read-Only Display) - can be developed in parallel with tasker features
  - v0.0.2-3-1 (Dashboard Navigation) - can be added independently

**Recommended Development Sequence:**

**Sprint 1 - Foundation (5 story points):**
1. v0.0.2-1-1: Clickable Username Navigation (3 points)
2. v0.0.2-3-1: Dashboard Navigation (2 points)

**Sprint 2 - Profile Display (16 story points):**
3. v0.0.2-2-1: Customer Profile View (5 points)
4. v0.0.2-2-2: Tasker Profile View (8 points) - can start in parallel with 2-1
5. v0.0.2-2-3: Read-Only Display (3 points) - polish pass after 2-1 and 2-2

**Total Estimated Effort:** 21 story points

**Risk Factors:**
- API dependency: Relies on existing `/users/me` endpoint - already implemented, low risk
- Route configuration: Adding profile route to App.js - straightforward, low risk
- Component complexity: Profile component is relatively simple with clear requirements - low risk
- Role-based rendering: Conditional logic for tasker fields - medium complexity, medium risk

**Testing Strategy:**
- Manual testing required for both customer and tasker user flows
- Test with users having complete profiles and incomplete profiles (null fields)
- Browser compatibility testing for navigation
- Accessibility testing for keyboard navigation and screen readers
- Responsive design testing for mobile and tablet layouts

**Future Enhancements (Not in v0.0.2):**
- Edit profile functionality (separate feature)
- Profile picture upload
- Password change option
- Email verification status indicator
- Two-factor authentication setup