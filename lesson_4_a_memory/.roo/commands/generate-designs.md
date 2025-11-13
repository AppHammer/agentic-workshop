---
argument-hint: [version]
description: Generate design specifications based on features and user stories
subagent: architect
---

# Instructions

Switch to the architect mode

Generate design specifications based on features and user stories

YOU MUST FIRST OPEN AND ANALYZE THE /home/apphammer/.claude/templates/design_template.md TEMPLATE AND INSTRUCTIONS.
IF YOU CAN'T FIND THE TEMPLATE FILE STOP AND ASK THE USER FOR THE LOCATION

IF YOU ANALYZED THE TEMPLATE YOU CAN CONTINUE, further instructions will refer to the template as <TEMPLATE>

For each phase below, do NOT continue to the next phase until all steps are completed, you are not to skip any steps and they must be completed in order

## Phase 1: Information Gathering
1. Review the instructions
2. Using the tools available to you, review the ./project_structure.md
3. Using the tools available to you, review the ./tech_stack.md
4. Using the tools avaialble to you, review the ./docs/[version]/user_stories.md
5. Review the gathered information and ensure you have a complete understanding about the requirements required to complete the design document
4. Ask the user relevant questions to fill out any of the information not found in the documents provided, or if your are not 100% certain of the information
5. Review the <TEMPLATE> and make ensure you have all of the information required to fill out the <TEMPLATE> for each required task.

## Phase 2: Create the technical requirements and github issues
YOU MUST FOLLOW THESE RULES EXPLICITLY
1. For each user story based on the information gathered, create an design.md based on the <TEMPLATE>
2. The design.md should contain all the information based on the the <TEMPLATE> required to generate robust technical requirements and github issues.
3. The document should contain ALL relevant information to complete the task, included mermaid diagrams, data models, json stucture and contracts etc.
6. Save the document in it's own file in ./docs/[version]/design.md.
7. Compare the new ./docs/[version]/design.md document to the <TEMPLATE>
8. Take time to think about it, review if the document has all the required information.
9. Validate that the structure is inline with the <TEMPLATE> instructions

## Phase 3: User Review
1. Once completed, ask the user to review the document to ensure everything is complete.
2. top and wait for user response. 
3. If the user requests changes, update the document, then repeat step 2
4. If the user says it's complete or something similar, Finish the task and provide the user with a summary