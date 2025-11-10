---
argument-hint: <feature-request>
description: Comprehensive workflow for gathering, documenting, and implementing product requirements
---

# Instructions

Generate a detailed project structure document.

YOU MUST FIRST OPEN AND ANALYZE THE .roo/templates/feature-requirements-template.md TEMPLATE AND INSTRUCTIONS.
IF YOU CAN'T FIND THE TEMPLATE FILE STOP AND ASK THE USER FOR THE LOCATION

IF YOU ANALYZED THE TEMPLATE YOU CAN CONTINUE, further instructions will refer to the template as <TEMPLATE>

For each phase below, do NOT continue to the next phase until all steps are completed, you are not to skip any steps and they must be completed in order

## Phase 1: Information Gathering

1. Review the <feature-request>
2. Using the tools available to you, review the ./project_structure.md
3. Using the tools avaialble to you, review the ./docs/**/feature_requirements.md for all previous versions, make sure you understand how they features relate to each other if applicable
4. Ask the user relevant questions to fill out any of the information not found in the documents provided, or if your are not 100% certain of the information
5. Review the <TEMPLATE> and make ensure you have all of the information required to fill out the <TEMPLATE>

## Phase 2: Create the project structure document

1. Determine the next version number based on the folder stucture inside of the .docs/ it should contain versions such as v1.0.1, v2.0.1, etc. set the <VERSION> to the next appropriate version for example: v1.0.1 if the last folder is v1.0.0. If it does not contain any versions then start the <VERSION> is v0.0.1
1. create or update a feature_requirements.md document based the <TEMPLATE> as save it in of ./docs/<VERSION>/feature_requirements.md

## Phase 3: Validate the document

1. Compare the new ./docs/<VERSION>/feature_requirements.md document to the <TEMPLATE>
2. Take time to think about it, review if the document has all the required information.
3. Validate that the structure is inline with the <TEMPLATE> instructions

## Phase 4: User Review

1. Once completed, ask the user to review the document to ensure everything is complete.
2. top and wait for user response. 
3. If the user requests changes, update the document, then repeat step 2
4. If the user says it's complete or something similar finish the task and provide the user with a summary