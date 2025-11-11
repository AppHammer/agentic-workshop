# Lesson 4: Memory

Bigger tasks, bigger codebases. 

## What are we building?

Lets add memory to the orchestrator agent, so it knows what was done and what the status are.


## Steps A

1. Switch to product manager mode, run command /generate-feature-requirements 
    - make the profile view editable on when the user clicks the their name in the menu. The user should be able to update their information and save.
    - the subagent should ask some clarifing questions
2. Once the feature requirements are complete, generate user stories, and technical requiremnts using the following commands
    - /generate-user-stories v0.0.2
    - /generate-designs v0.0.2
    - /generate-technical-requirements v0.0.2

## Steps B

1. Switch to orchestrator mode.
    - /implement-issue docs/v0.0.2/issues/v0.0.2-1-1.md
2. Review updates
3. Code looks ok, but now having dependency issues becuase of python3.13

## Steps C

1. Into to MCP servers!
2. Install context 7
3. Use context 7 and the architect subagent to create a new issue
    - you have access to context7, the passlib library is causing dependency issues with python 3.13, what is a good replacement?
4. create new issue
    - /generate-technical-requirements v0.0.2 Add a new issue based on the recommended approach for our code subagent
5. Allow team to fix new issue
    - /implement-issue docs/v0.0.2/issues/v0.0.2-2-1-1.md

## Steps D

1. Install playwright mcp
2. provide the qa agent more context and instructions
    - Add login instructions etc
3. Rinse and repeat for issues
    - /implement-issue docs/v0.0.2/issues/v0.0.2-1-1.md
    - /implement-issue docs/v0.0.2/issues/v0.0.2-1-1.md
4. Does it work?


## Takeaways:

- 
