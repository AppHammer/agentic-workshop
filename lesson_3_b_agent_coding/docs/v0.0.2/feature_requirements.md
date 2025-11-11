# Feature Request: Profile: Editable Profile View

**Date:** 2025-11-11
**Status:** Draft

---

## 1. Summary

This feature enhances the existing user profile page by adding the ability for users to edit and update their own account information directly.

## 2. The Why (Problem Statement)

Currently, users face the following challenges:

*   **Static Information:** The profile page is view-only, preventing users from correcting or updating their own data.
*   **Dependency on Support:** To make any changes to their profile (e.g., update email, change skills), users must contact support, creating a slow and inefficient process.
*   **Data Inaccuracy:** Outdated information, such as an old email address or incorrect hourly rate for taskers, can lead to missed communications and lost business opportunities.

This leads to user frustration, inaccurate data in our system, and an unnecessary burden on customer support.

## 3. Proposed Solution

We propose implementing an "Edit Profile" functionality. This feature will allow users to:

*   **User Story 1:** As a logged-in user, I want to edit my profile fields, so that I can keep my account information accurate and up-to-date.
*   **User Story 2:** As a tasker, I want to easily update my skills and hourly rate, so that my profile correctly reflects my current service offerings.
*   **User Story 3:** As a user, I want to save my changes and see them reflected immediately on my profile, so that I have confidence the update was successful.

**Functional Details:**
*   The profile page will include an "Edit" button.
*   When a user clicks "Edit", the following fields will become editable input fields:
    *   Email
    *   Password (will likely require a separate "Change Password" flow for security)
    *   Skills (for taskers)
    *   Hourly Rate (for taskers)
*   The "Edit" button will be replaced by "Save" and "Cancel" buttons.
*   **Validation:**
    *   The email field must validate for correct email format.
    *   The hourly rate must be a positive number.
*   Clicking "Save" will send the updated data to the backend and, upon success, display the updated information.
*   Clicking "Cancel" will discard any changes and return the page to its view-only state.

## 4. User Value

This feature will provide value to our users by:

*   **Empowerment & Control:** Gives users direct control over their own account information.
*   **Accuracy:** Ensures users can maintain accurate and current profile data, which is critical for taskers.
*   **Efficiency:** Eliminates the need to contact support for simple data changes, saving users time.

## 5. Business Value

This feature supports our business goals in the following ways:

*   **Operational Efficiency:** Significantly reduces the volume of support tickets related to profile information updates, freeing up support staff for more complex issues.
*   **Improved Data Integrity:** Leads to more accurate and reliable user data, which is valuable for communication, marketing, and analytics.
*   **Increased User Satisfaction & Retention:** Providing essential self-service functionality improves the user experience and reduces a key point of friction, contributing to higher user retention.

## 6. Impact on Existing Features

### Enhances:
*   **[`Profile Page`](frontend/src/pages/Profile.jsx):** Evolves the page from a static view into an interactive and functional component of the user's account management.

### Changes:
*   **[`Profile Page`](frontend/src/pages/Profile.jsx):** Will require significant changes to manage state (view vs. edit mode), handle user input, and trigger API calls.
*   **[`api.js`](frontend/src/api.js):** A new function will be needed to handle the `PUT` or `PATCH` request to update the user's profile data.
*   **[`backend/main.py`](backend/main.py):** A new endpoint (e.g., `PUT /api/users/me`) will be required to accept and process profile update requests.
*   **[`backend/schemas.py`](backend/schemas.py):** A new Pydantic schema will be needed to define the expected data structure for profile updates.
*   **[`backend/auth.py`](backend/auth.py):** The logic for updating user information, especially sensitive fields like email or password, will need to be carefully implemented.

### Deprecates:
*   None

## 7. Metrics for Success

Metrics will be defined in a future iteration.

## 8. Mockups / Design Links (Optional)

To be created.