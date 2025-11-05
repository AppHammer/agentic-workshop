---
description: Generate a detailed tech stack document for user with agents
---

# Instructions

Switch to the correct subagent

IF a tech_stack.md document exists in the root of the folder, stop and ask the user if they want to update it before continuing.

Generate a detailed project structure document.

YOU MUST FIRST OPEN AND ANALYZE THE .roo/templates/tech-stack-template.md TEMPLATE AND INSTRUCTIONS.
IF YOU CAN'T FIND THE TEMPLATE FILE STOP AND ASK THE USER FOR THE LOCATION

IF YOU ANALYZED THE TEMPLATE YOU CAN CONTINUE, further instructions will refer to the template as <TEMPLATE>

For each phase below, do NOT continue to the next phase until all steps are completed, you are not to skip any steps and they must be completed in order

## Phase 1: Information Gathering

1. Using the tools available to you, review the codebase and gather all techinical information required to fill out the <TEMPLATE>
2. Ask the user relevant questions to fill out any of the information not found in the codebase, or if your are not 100% certain of the information

## Phase 2: Create the project structure document

1. create or update a tech_stack.md document based the <TEMPLATE> as save it in the root of the project as tech_stack.md

## Phase 3: Validate the document

1. Compare the new tech_stack.md document to the <TEMPLATE>
2. Take time to think about it, review if the document has all the required information for a new user of the codebase to understand it.
3. Validate that the structure is inline with the <TEMPLATE> instructions

## Phase 4: User Review

1. Once completed, ask the user to review the document to ensure everything is complete.
2. Stop and wait for user response.
3. If the user requests changes, update the document, then repeat step 2
4. If the user says it's complete or something similar finish the task and provide the user with a summary
