# Feature Request: User Profile: Self-Service Profile Viewing

**Date:** 2025-11-10
**Status:** Draft

---

## 1. Summary

This feature enables logged-in users to view their own profile information by making their username clickable in the navigation bar, which navigates to a dedicated profile page displaying all relevant user account details from the User model.

## 2. The Why (Problem Statement)

Currently, users face the following challenges:

* **No Profile Visibility:** Users cannot view their own profile information after registration and login, making it impossible to verify what information is stored in the system about them.
* **Limited Account Awareness:** Users have no way to see their account details such as email, phone number, location, role, and creation date without contacting support or re-registering.
* **Tasker Information Opacity:** Taskers cannot review their professional information (skills, hourly rate, bio) that is displayed to potential customers, preventing them from ensuring accuracy before engaging with the marketplace.
* **Poor User Experience:** The username display in the navigation bar (current implementation: `{user.full_name} ({user.role})`) is static text with no interactivity, missing an opportunity for intuitive profile access.

This leads to user confusion about their stored information, reduced trust in the platform, increased support requests for basic account information queries, and missed opportunities for users to verify and understand their profile data.

## 3. Proposed Solution

We propose implementing a User Profile viewing feature that allows users to view their own profile information. This feature will allow users to:

* **User Story 1:** As a logged-in user, I want to click on my username in the navigation bar, so that I can navigate to my profile page.

* **User Story 2:** As a customer, I want to view my profile information (email, full name, role, phone, location, account creation date), so that I can verify my account details are correct.

* **User Story 3:** As a tasker, I want to view my complete profile including my professional details (skills, hourly rate, bio) in addition to basic account information, so that I can see what customers will see about me.

* **User Story 4:** As a user, I want a clear, read-only view of my profile, so that I can review my information without accidentally modifying it.

* **User Story 5:** As a user, I want to easily navigate back to the dashboard from my profile page, so that I can continue working on tasks without getting stuck.

**Functional Details:**

* **Clickable Username:** Transform the username display in [`Navbar.js`](app/frontend/src/components/Navbar.js:13-15) from static text to a clickable link that navigates to `/profile`.

* **Profile Route:** Add a new route `/profile` in [`App.js`](app/frontend/src/App.js) that renders a new `Profile` component, protected by authentication.

* **Profile Component:** Create a new React component `Profile.js` that displays user information in a clean, organized layout.

* **Field Display Logic:**
  - **Common Fields (All Users):** Display `full_name`, `email`, `role`, `phone`, `location`, `created_at`
  - **Tasker-Specific Fields:** Display `skills`, `hourly_rate`, `bio` only for users with `role === "tasker"`
  - **Hidden Fields:** Never display `id`, `hashed_password`
  
* **Data Formatting:**
  - Format `created_at` date as a human-readable string
  - Display "Not provided" or "N/A" for null/empty optional fields
  - Show role as capitalized text (e.g., "Customer" or "Tasker")
  
* **View-Only Mode:** All fields are displayed as read-only text (no input fields or edit buttons in this version).

* **Navigation:** Include a "Back to Dashboard" button or link for easy navigation.

## 4. User Value

This feature will provide value to our users by:

* **Saving Time:** Users can instantly view their profile information without navigating through multiple pages or contacting support, reducing the average time to find account information from several minutes to seconds.

* **Reducing Errors:** Users can verify their contact information (phone, email, location) is accurate before customers or taskers attempt to reach them, preventing communication failures and missed opportunities.

* **Providing New Capabilities:** 
  - Users gain transparency into what information the platform stores about them
  - Taskers can review their professional presentation (skills, rate, bio) before engaging in the marketplace
  - Users can confirm their account creation date for verification purposes

* **Improving Usability:** 
  - Intuitive username click interaction matches common web patterns users expect
  - Single-page view of all profile information eliminates the need to navigate multiple screens
  - Clear, organized layout makes profile information easy to scan and understand

## 5. Business Value

This feature supports our business goals in the following ways:

* **Customer Retention:** Providing profile visibility increases platform transparency and trust, expected to reduce early-stage churn by 10-15% as users feel more confident about their account information and the platform's professionalism.

* **Increased Revenue:** Taskers who can verify their professional information accuracy are more likely to engage actively in bidding, potentially increasing tasker participation by 5-10% and subsequently increasing marketplace liquidity.

* **Operational Efficiency:** 
  - Reduces support ticket volume related to "what email do I have registered" and "what information does my profile show" queries by an estimated 20-25%
  - Provides foundation for future self-service profile editing, reducing manual account update requests
  - Decreases onboarding friction as new users can immediately confirm their registration details

* **Competitive Advantage:** Most freelance/task marketplace platforms provide profile viewing as a baseline feature. Implementing this brings the Tasker Platform to feature parity with competitors like TaskRabbit and Thumbtack, removing a significant gap in user experience.

## 6. Impact on Existing Features

### Enhances:

* **[`Navbar.js`](app/frontend/src/components/Navbar.js):** Transform the static username display into an interactive link, improving navigation and making the navbar more functional without adding visual clutter.

* **User Authentication Flow:** Strengthens the post-login experience by giving users immediate access to verify their account information, building confidence in the platform.

* **Onboarding Experience:** New users can immediately verify their registration details after first login, providing peace of mind and catching any registration errors early.

### Changes:

* **[`Navbar.js`](app/frontend/src/components/Navbar.js):** Line 13-15 needs modification to convert the `<span>` element displaying `{user.full_name} ({user.role})` into a clickable `<Link to="/profile">` element.

* **[`App.js`](app/frontend/src/App.js):** Add a new protected route for `/profile` that renders the new `Profile` component, following the existing authentication pattern used for other routes.

* **API Usage:** The profile page will utilize the existing `/users/me` endpoint (already used in [`getCurrentUser()`](app/frontend/src/api.js)) to fetch complete user data, requiring no backend changes.

### Deprecates:

* None - This feature adds new functionality without removing or replacing any existing features.

## 7. Metrics for Success

We will measure the success of this profile viewing feature through the following metrics:

**Adoption Metrics:**
* **Profile View Rate:** Percentage of daily active users who view their profile at least once → Target: 60% within first week, 30% steady-state
* **New User Profile Views:** Percentage of new users who view profile within first session → Target: 75%
* **Time to First Profile View:** Average time from login to first profile view for new users → Target: <2 minutes

**Engagement Metrics:**
* **Profile Views per User per Week:** Average number of profile page views per active user → Target: 1-2 views
* **Navigation Pattern:** Percentage of profile views accessed via navbar username click vs. direct URL → Track for usability insights

**Business Impact Metrics:**
* **Support Ticket Reduction:** Decrease in account information inquiry tickets → Target: 20-25% reduction
* **Tasker Activation Rate:** Percentage of taskers who view profile before placing first bid → Track for 15%+ increase
* **User Retention Impact:** Difference in 7-day retention between users who viewed profile vs. those who didn't → Track for positive correlation

**User Satisfaction Metrics:**
* **Feature Satisfaction Score:** User rating of profile viewing usefulness → Target: 4.2+ out of 5.0
* **Information Accuracy Confidence:** Post-feature survey question "I am confident my profile information is accurate" → Target: 85%+ agreement

**Technical Metrics:**
* **Page Load Time:** Profile page load time from route navigation → Target: <500ms
* **Error Rate:** Failed profile data loads → Target: <0.5%
* **Mobile Responsiveness:** Profile page usability score on mobile devices → Target: 90%+ usability

## 8. Mockups / Design Links (Optional)

To be created - recommend wireframes showing:

1. Updated Navbar with clickable username (visual indication of link, e.g., underline on hover)
2. Profile page layout with sections for:
   - Account Information (common fields)
   - Professional Information (tasker-specific fields, conditionally rendered)
   - Account metadata (creation date)
3. Mobile-responsive profile layout
4. Empty state handling for null/optional fields
5. Navigation back to dashboard