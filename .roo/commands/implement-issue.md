---
argument-hint: <issue-number>
description: Complete end-to-end implementation of a GitHub issue with testing and validation
---

## Description

This command orchestrates a comprehensive workflow to implement, test, and validate an issue. It manages the entire development lifecycle from requirement analysis to pull request creation. The issues can be found in the issues directory ../docs/<version>/issues/<issue-number>.md

## Workflow Phases

### Phase 1: Requirement Analysis & Implementation

1. **Issue Analysis**:
   - Reviews the issue contents thoroughly
   - Extracts requirements, deliverables, and acceptance criteria
   - Understands technical scope and dependencies

2. **Create a new branch**
   - Create a new branch with the issue number using `git checkout -b <issue_number>-descriptive-name`
   - Commit current uncommitted files into the new branch

3. **Implementation**:
   - Use a coding agent specialized in the relevant technology stack if available
   - Understand the Existing Codebase: Before starting, take the time to understand the relevant parts of the existing application. Pay attention to the current models, views, forms, URLs, templates, installed modules, and any existing tests.
   - Adhere to Best Practices: * DRY (Don't Repeat Yourself): Avoid duplicating code. Identify and reuse existing components or create new reusable ones. * SOLID: Follow the SOLID (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion) principals * Modularity: Ensure your changes are well-organized and don't tightly couple new code with unrelated parts of the application. * Secure Ensure all endpoints are properly protected with authentication if required.
   - Implement the Task: Write the necessary code to implement the specified task. This might involve modifying existing files or creating new ones (e.g., new views, forms, tests).
   - Integration: Ensure your changes seamlessly integrate with the existing application. This includes: * Properly connecting new views through URLs. * Modifying templates to display new data or functionality. * Ensuring forms correctly handle new or modified data.

4. **Summary**:
   - Create an implementation summary document including:
     - Overview of changes made
     - Files created/modified
     - Deployment notes
     - Rollback plan
     - Future enhancement suggestions
   - add the summary to `docs/<version>/<issue-number>-summary.md`


### Phase 2: Test Plan Creation

1. **Test Documentation**:
   - Uses test-coverage-engineer agent
   - Creates comprehensive test document including:
     - Feature summary and acceptance criteria
     - Positive test cases for core functionality
     - Negative test cases for error handling
     - Edge case scenarios
     - Clear test steps and expected results
   


## Success Criteria

- All issue requirements implemented and tested
- Comprehensive test coverage with passing results
- Clean pull request ready for code review
- Proper linking and documentation of all changes