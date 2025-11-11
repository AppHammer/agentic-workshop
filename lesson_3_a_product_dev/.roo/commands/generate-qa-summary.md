---
argument-hint: <version>
description: Perform testing, code review and qa.
subagent: qa-engineer
---

# Instructions

Switch to the correct subagent

Generate a detailed project structure document.

YOU MUST FIRST OPEN AND ANALYZE THE .roo/templates/qa-summary-template.md TEMPLATE AND INSTRUCTIONS.
IF YOU CAN'T FIND THE TEMPLATE FILE STOP AND ASK THE USER FOR THE LOCATION

IF YOU ANALYZED THE TEMPLATE YOU CAN CONTINUE, further instructions will refer to the template as <TEMPLATE>

For each phase below, do NOT continue to the next phase until all steps are completed, you are not to skip any steps and they must be completed in order

## Phase 1: Information Gathering

1. Review the users <version>
2. Using the tools available to you, review the ./project_structure.md
3. Using the tools available to you, review the ./tech_stack.md
4. Using the tools avaialble to you, review the ./docs/<version>/user_stories.md
5. Using the tools available to you, review the ./docs/<version>/design.md
5. Review the gathered information and ensure you have a complete understanding about the technical requirements required to complete the testing and qa of the current feature
4. Review the <TEMPLATE> and make ensure you have all of the information required to fill out the <TEMPLATE> for each required task.

## Phase 2: Test the application

1. For each user story in the application. delevlop a comprehensive test plan.
2. exectute that test plan utlizing the tools that you have available to you.
3. determine if the test pass and the feature is ready for deployment, if they do not create a comprehensive bug report to include in the summary and response back to the user.

## Phase 3: Results

1. complete the <TEMPLATE>
2. review and think to ensure the <TEMPLATE> is filled out properly and includes all the requested information
3. Return the the summary of results back to the user and include a bug report and recommended action for the user to review.