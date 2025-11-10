**Instructions:**

Before starting to code, review the design docs provided in the **docs/[VERSION]** folder within the repository, it includes import documentation about system design specification, data models, ui design, and other important information that will be required to perform any coding task. Specifications should ALWAYS be followed.

review the tech_stack.md file for the relevant technologies and instructions on how to use them
review the project_structure.md for relevant information about the project structure and the structure you should follow when updating the codebase

1.  **Understand Requirements & User Stories:**
    * Thoroughly analyze all provided user stories, wireframes, and design mockups.
    * When provided a github link, use the Github mcp server do gather and analyze all information provided in the github issue.
    * When a figma link is found use the the Figma MCP server to gather all designs required for the task
    * Clarify any ambiguities with the product owner or design team.

2.  **Understand the Existing Codebase:** Before starting, take the time to understand the relevant parts of the existing application. Pay attention to the current models, views, forms, URLs, templates, installed modules, and any existing tests.

2.  **Adhere to Best Practices:**
    * **DRY (Don't Repeat Yourself):** Avoid duplicating code. Identify and reuse existing components or create new reusable ones.
    * **SOLID:** Follow the SOLID (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion) principals
    * **Modularity:** Ensure your changes are well-organized and don't tightly couple new code with unrelated parts of the application.
    * **Secure** Ensure all endpoints are properly protected with authentication if required.

3.  **Implement the Task:** Write the necessary code to implement the specified task. This might involve modifying existing files or creating new ones (e.g., new views, forms, tests).

4.  **Testing:**
    * Write new unit tests to cover the changes you've made. Ensure that your tests adequately verify the functionality and prevent regressions.
    * Run the existing test suite to ensure that your changes haven't introduced any unintended side effects.
    * Unit Tests: Test models, forms, serializers, utility functions, and individual components in isolation. Use mocking where necessary.
    * Integration Tests: Test interactions between different components (e.g., view rendering, form processing, signal handling).
    * Coverage: Aim for high test coverage and use coverage reports (coverage run, coverage report) to identify untested code.

5.  **Integration:** Ensure your changes seamlessly integrate with the existing application. This includes:
    * Properly connecting new views through URLs.
    * Modifying templates to display new data or functionality.
    * Ensuring forms correctly handle new or modified data.

**Expected Output:**

Provide the code changes you have made, clearly indicating which files have been modified or created. If necessary, provide instructions on how to integrate these changes into the existing application (e.g., running migrations, updating URLs). Include the new unit tests you have written.

**Documentation:**

Write clear docstrings for functions, classes, and methods.
Add comments to explain complex logic.
Consider using Sphinx to auto-generate project documentation from docstrings.
For the API, DRF's browsable API provides basic documentation. USe drf-spectacular for generating OpenAPI/Swagger documentation.

**Success Criteria:**

* The specified task is successfully implemented.
* All code adheres to Python and Django best practices and is consistent with the existing codebase.
* The code is DRY and well-organized.
* Comprehensive unit tests are provided for the new or modified code.
* The changes integrate seamlessly with the existing application without introducing regressions.