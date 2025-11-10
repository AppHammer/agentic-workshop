---
argument-hint: <version>
description: Generate detailed user stories based on feature requirements
---

# Instructions

Generate user stories based on feature requirements

YOU MUST FIRST OPEN AND ANALYZE THE .roo/templates/user-stories-template.md TEMPLATE AND INSTRUCTIONS.
IF YOU CAN'T FIND THE TEMPLATE FILE STOP AND ASK THE USER FOR THE LOCATION

IF YOU ANALYZED THE TEMPLATE YOU CAN CONTINUE, further instructions will refer to the template as <TEMPLATE>

For each phase below, do NOT continue to the next phase until all steps are completed, you are not to skip any steps and they must be completed in order

## Phase 1: Information Gathering

1. Review the <version>
2. Using the tools available to you, review the ./project_structure.md
3. Using the tools available to you, review the ./tech_stack.md
4. Using the tools avaialble to you, review the ./docs/<version>/feature_requirements.md
5. Review the gathered information and ensure you have a complete understanding about the feature requirements required to generate the user stories based on the feature
4. Ask the user relevant questions to fill out any of the information not found in the documents provided, or if your are not 100% certain of the information
5. Review the <TEMPLATE> and make ensure you have all of the information required to fill out the <TEMPLATE> for each required task.

## Phase 2: Create the user stories

YOU MUST FOLLOW THESE RULES EXPLICITLY
1. For the feature generate the user stories base on <TEMPLATE>
2. Each user story should be small enough to complete and test, under 13 story points
3. Each issue should contain ALL relevant information to complete the task, included mermaid diagrams, data models, json stucture and contracts etc.
4. This issue title should use the user story version plus the task number: {VERSION}-{EPIC NUMBER}-{USER STORY NUMBER} {SHORT TITLE} For example "v1.0.1-2-1 User Login".
6. Save the user stories file in ./docs/$1/user_stories.md
7. Compare the new ./docs/$1/user_stories.md document to the <TEMPLATE>
8. Take time to <think> about it, review if the document has all the required information.
9. Validate that the structure is inline with the <TEMPLATE> instructions

## Phase 3: User Review
1. Once completed, ask the user to review the document to ensure everything is complete.
2. top and wait for user response. 
3. If the user requests changes, update the document, then repeat step 2
4. If the user says it's complete or something similar, Finish the task and provide the user with a summary
