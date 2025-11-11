# Feature Request: User Profile: Self-View for Logged-in Users

**Date:** 2025-11-10
**Status:** Draft

---

## 1. Summary

This feature enables logged-in users to view their own profile information by clicking their username in the navigation bar. Users will be able to see basic account details including username, email, account type, registration date, and tasker-specific fields (skills and hourly rate) when applicable.

## 2. The Why (Problem Statement)

Currently, users face the following challenges:

* **No Access to Own Profile:** Users cannot view their own profile information once logged in. While the username is displayed in the navigation bar, it provides no interactivity or access to account details.
* **Limited Account Visibility:** Users have no way to verify their account information (email, user type, skills, hourly rate) without navigating through account settings or external tools.
* **Inconsistent User Experience:** Most modern web applications provide easy access to profile information through clickable usernames or avatars, creating an expectation that the Tasker platform currently doesn't meet.

This leads to reduced user confidence in their account information and a less intuitive user experience compared to industry standards.

## 3. Proposed Solution

We propose implementing a User Profile View feature. This feature will allow users to:

* **User Story 1:** As a logged-in user, I want to click my username in the navigation bar, so that I can view my profile page.
* **User Story 2:** As a customer, I want to see my basic account information (username, email, user type, join date), so that I can verify my account details.
* **User Story 3:** As a tasker, I want to view my profile including my skills and hourly rate, so that I can confirm the information potential customers see when considering my bids.

**Functional Details:**
* The username displayed in the [`Navigation`](frontend/src/components/Navigation.jsx) component will become a clickable link
* Clicking the username navigates to a new `/profile` route
* A new `Profile.jsx` page component will display user information from the [`User`](backend/models.py:22) model
* The profile page will show:
  - Username
  - Email address
  - User type (customer or tasker)
  - Account creation date
  - For taskers only: Skills and hourly rate fields
* The page will follow the existing application styling patterns established in the current pages
* This is a view-only feature - no editing capabilities are included in this version

## 4. User Value

This feature will provide value to our users by:

* **Improving Usability:** Makes the application more intuitive by providing standard profile access functionality that users expect from modern web applications.
* **Increasing Transparency:** Users can easily verify their account information is correct, particularly important for taskers who want to ensure their skills and rates are properly displayed.
* **Providing New Capabilities:** Enables users to quickly access their account details without navigating through settings or external administrative interfaces.
* **Reducing Support Burden:** Users can self-serve basic account information verification, reducing support inquiries about account details.

## 5. Business Value

This feature supports our business goals in the following ways:

* **Customer Retention:** Improves user satisfaction by meeting basic user expectations for profile access, helping reduce churn from users frustrated by missing standard features.
* **Operational Efficiency:** Reduces support ticket volume related to "How do I view my account information?" queries by providing self-service access. Expected reduction of 5-10% in account-related support tickets.
* **Foundation for Future Features:** Establishes the profile page infrastructure that can be extended in future releases to support profile editing, statistics, and reputation features.
* **Competitive Advantage:** Brings the platform in line with competitor offerings, ensuring we don't lose users due to missing basic functionality.

## 6. Impact on Existing Features

### Enhances:
* **[`Navigation`](frontend/src/components/Navigation.jsx):** The username display will be enhanced with clickable functionality, improving the overall user experience of the navigation component.
* **[`AuthContext`](frontend/src/AuthContext.jsx):** The existing user data provided by the authentication context will be leveraged to populate the profile page without additional API calls.

### Changes:
* **[`Navigation`](frontend/src/components/Navigation.jsx):** The username display (currently line 30-32) will need to be converted from a plain `<span>` to a clickable `<Link>` component that navigates to `/profile`.
* **[`App.jsx`](frontend/src/App.jsx):** Will require a new route definition for the `/profile` path to render the Profile component.
* **[`api.js`](frontend/src/api.js):** May need a new API endpoint to fetch complete user profile data if the current user object doesn't include all required fields.
* **[`backend/main.py`](backend/main.py):** May require a new GET endpoint `/users/me/profile` to return complete user profile data including tasker-specific fields.

### Deprecates:
* None

## 7. Metrics for Success

We will measure the success of this feature through the following metrics:

**Quantitative Metrics:**
* **Profile Page Views:** Track the number of times users navigate to their profile page within 30 days of launch. Target: 60% of active users view their profile at least once.
* **Click-Through Rate:** Measure the percentage of users who click the username link in the navigation. Target: 40% of users click within their first 5 sessions.
* **Support Ticket Reduction:** Monitor decrease in support tickets related to viewing account information. Target: 10% reduction in account-related support requests.
* **Time on Profile Page:** Average session duration on the profile page. Baseline to be established post-launch.

**Qualitative Metrics:**
* **User Satisfaction:** Post-feature user survey asking about ease of accessing profile information. Target: 80% satisfaction rating.
* **Feature Discoverability:** Track how many users discover the feature without assistance. Target: 70% discovery rate within first week.

**Technical Metrics:**
* **Page Load Time:** Profile page should load within 200ms (excluding network latency).
* **Error Rate:** Less than 0.1% error rate on profile page loads.

## 8. Mockups / Design Links (Optional)

To be created.

**Note:** The profile page should follow the existing styling patterns used in other pages like [`Dashboard`](frontend/src/pages/Dashboard.jsx), [`TaskList`](frontend/src/pages/TaskList.jsx), and [`CreateTask`](frontend/src/pages/CreateTask.jsx) to maintain visual consistency across the application.