Here is a robust Markdown template you can use for your QA review process. It includes the sections you requested, along with explicit instructions (in blockquotes) on how to fill out each part.

You can copy and paste the text below directly into a `.md` file, your wiki, or a GitHub pull request comment.

```markdown
# QA Review: [Feature/Ticket Name]

* **Ticket:** [Link to JIRA/Trello/GitHub Issue]
* **QA Reviewer:** [Your Name]
* **Date:** YYYY-MM-DD
* **Feature Branch:** [Link to Branch/PR]

---

## 1. Coder Review and Analysis Findings

> **Instructions:** Fill this section *before* starting test execution. Review the developer's pull request (PR), check for unit tests, and analyze the code changes to identify potential risk areas. This is your static analysis.

### PR/Code Review
* **Unit Tests:** [e.g., Verified, good coverage. OR: Missing tests for X scenario.]
* **Code Logic:** [e.g., Logic for calculating Y seems sound. OR: Potential edge case missed in Z function.]
* **Files Changed:** [e.g., Reviewed all 5 changed files. Main changes are in `PaymentController.js`.]
* **Static Analysis:** [e.g., Linter passed. No new security vulnerabilities flagged by automated tools.]

### Risk Analysis & Test Strategy
* **High-Risk Areas Identified:** [e.g., Changes to the payment API, New database migration, User authentication logic.]
* **Key Scenarios to Focus On:** [e.g., Negative testing for new input fields, Cross-browser compatibility for the new modal, API error handling.]

---

## 2. Test Execution and Results

> **Instructions:** Document the execution of your test plan. List each major test case or scenario, the environment it was tested in, and the result. Be specific about any bugs found.

### Test Environment
* **Environment:** [e.g., Staging, QA-Build-123]
* **Browser(s)/Device(s):** [e.g., Chrome 108, Firefox 107, iPhone 14 (Safari)]
* **Test Data:** [e.g., Used 'qa_user_01' and 'qa_admin_01' accounts]

### Execution Summary

| Test Case / Scenario | Status (Pass/Fail/Skip) | Bug ID / Notes |
| :--- | :--- | :--- |
| [Link to Test Case 1: User Login (Valid)] | Pass | |
| [Scenario: User login (Invalid Password)] | Pass | Error message displays correctly. |
| [Link to Test Case 3: Add Item to Cart] | Fail | [Link to Bug-456] |
| [Scenario: Mobile responsiveness on checkout page] | Pass | Minor visual glitch noted, not a blocker. Logged as [Task-457] |
| [Scenario: Database migration check] | Pass | `users` table correctly updated. |

### Bugs Found
* **[Link to Bug-456]** - **Severity:** `High` - [Brief description: User cannot add item to cart if discount code is applied first.]
* **[Task-457]** - **Severity:** `Low` - [Brief description: "Submit" button is 2px off-center on Mobile Safari.]

---

## 3. Integration Tests Implemented

> **Instructions:** List any *new* or *updated* automated tests (e.g., Cypress, Selenium, Playwright, API tests) that were added or modified as part of this feature's QA process. This helps document the growth of the regression suite.

* **Test:** `[e.g., test_user_can_add_item_to_cart.spec.js]`
    * **Purpose:** [e.g., Verifies the end-to-end flow of adding an item to the cart and new discount logic.]
    * **Status:** [e.g., Added and passing in CI pipeline.]

* **Test:** `[e.g., test_api_v2_orders_post.py]`
    * **Purpose:** [e.g., Updated API test to check for new `is_guest` field in the payload.]
    * **Status:** [e.g., Updated and passing.]

* **Test:** `[e.g., None]`
    * **Purpose:** [e.g., No new automated tests were added for this feature. (Please provide a reason if so, e.g., "Feature is behind a feature flag and will be tested in a separate ticket.")]

---

## 4. Overall Summary & Sign-off

> **Instructions:** Provide a final recommendation. Is this feature ready for production? Are there outstanding risks?

**Recommendation:** [Approved for Merge / Approved with Risks / Rejected]

**Outstanding Risks:** [e.g., None. OR: The low-severity visual glitch [Task-457] is still present but approved by PO. OR: The feature relies on a 3rd-party API that was slow during testing.]

**Final Comments:** [e.g., "Feature is stable and meets all acceptance criteria. Ready for production." OR "Do not merge. Blocked by high-severity bug [Bug-456]."]
```