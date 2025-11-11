# Lesson 3: Making the user profile editable

Using our agent team to build a full featureset for out app. 

## What are we building?

Using the agents individually to build the feature.


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
    - you have access to context7, the passlib library is causing issues, what is a good replacement?
4. create new issue
5. Allow team to fix new issue
    - /implement-issue docs/v0.0.2/issues/v0.0.2-2-1-1.md
6. Should work!

## Steps D

1. Install playwright mcp
    - Add to qa agent rules 
      * **6. E2E Testing:**

      * Use the Playwright MCP server to fully test ux from End 2 End for a feature that requires it.
      * Record screenshots when testing is desktop mode
      * Provide feedback and links to screenshots in testing summary.
    - add to orchestrator

          You MUST use the playwright mcp server for all ux testing and validation.

          Customer Login: customer1 password123
          Tasker Login: tasker1 password123

          The backend and frontend will need to be run together for testing

2. Test that playwright is setup:
    - Switch to QA Engineer mode and test playwright.
    - test that playwright works by navigating and takeing a screenshot of apphammer.co
    - IF NOT: you may need to run npx playwright install chromium --with-deps
3. Rinse and repeat for issues
    - /implement-issue docs/v0.0.2/issues/v0.0.2-1-2.md
    - /implement-issue docs/v0.0.2/issues/v0.0.2-1-3.md

4. Does it work? Lets Check
    - /generate-qa-summary v0.0.2


## Takeaways:

- MCP Servers are awesome! They supply funtionality that are not built in to agents
- Other MCP servers to play with.
    - Figma
    - Github
    - sequentialthinking
    - serena