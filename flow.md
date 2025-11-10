# Walkthbough


## 1.0 start with initial commit just an idea in the docs/tasker.md

- asked roo to read the tasker.md and generate the application with a launch.json
- Vibe code the entire thing

### Problem with that approach

#### First Problem: User Registration Fails (Auth)

- Cannot register user - error with `auth.py` get password hash.
- Asked to fix - it could not. going in circles.
- Hey write some test. tests fail.
- GOOGLE SEARCH: doesn't use the right version of the CryptContext compared to what it vibe coded
- https://stackoverflow.com/questions/79776559/passlib-bcrypt-not-working-when-deployed-to-render-valueerror-password-cannot
- pip freeze to show passlib is "too new" downgrade to 4.3.0 of bcrypt
- Boom Tests pass. Problem solved.

## 2.0 Leveraging Roo Commands 

First let's generate some project documentation to set the context for the AI.

- `/generate-project-structure` command to generate project structure document. Impotant to set naming conventions, import patterns, code structure patterns, and code organization principles for the AI.
- `/generate-project-tech-stack` command to generate tech stack document. Important to set the technology stack, frameworks, libraries, and tools to be used in the project for the AI.

## 2.1 Implement a "Profile" Feature

### With tech stack

You might vibe code a prompt like this:

- Review the @project_structure.md and @project_tech_stack.md to understand the conventions and technologies to be used in this project. 
  Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/database.py.
 
**Questions**

- Did it work?
- What code changes were made to the backend to support the profile page feature?
- What code changes to the frontend components were created or modified to implement the profile page?
- Is this how YOU would have implemented it?


## 2.2 Repeat, but with AI Methodology

Process in a nutshell:

You have a "feature" you want to implement. Instead of asking the AI to just code it, you break it down into a series of steps that mimic a human software development workflow.

1. generate feature requirements document from your feature
2. Review / edit the feature requirements document
3. Generate user stories from feature requirements document for version 
4. Review / edit the user stories
5. Generate technical requirements for version (reads user stories.... creates a github issue for each user story with technical requirements) 
6. Review / edit each issue
7. for each issue:
    1. implement issue (this actually codes it with AI)
    2. review code / test / adjust code
8. Final review and testing of feature... it is acceptable?


**Procedure**

- `/generate-feature-requirement` 
  Write a feature to allow users to view their profile when logged  Make their user name clickable and display user information from the User class in @backend/database.py.
  This feature only needs to support the current logged in user viewing their own  profile, not editing it. Also the user does not need to view other users profiles.
- USER: review and edit the generated feature requirements document in `docs/v0.0.2/feature_requirements.md`
- `/generate-user-stories v0.0.2` 
- `/generate-technical-requirements v0.0.2`
- For each user story in `docs/v0.0.2/user_stories.md`:
  - `/implement-user-story <user_story_id>` 
  - Review code, run tests, adjust code as needed.

**This is better because:**

- It mimics the human software development workflow... but with far greater detail.
- Instructions are very explicit... AI Needs explicit instructions and detailed steps or else it will make assumptions.
- Human in the loop for review and adjustments at every step. Still keeping yourself accountable for the final product.
- Coding expectations are clear, concise and well defined. Easy to review and adjust.
- Project change log is preserved in the docs - clear history of changes.
- Git commit for each user story - tracked with precision.

## 3.0 The need for agents.

Agents adopt a persona to perform specific tasks.  Think of common software development roles:

- Product Manager - defines features, prioritizes backlog, writes user stories.
- Technical Lead - defines technical requirements, reviews architecture, ensures best practices.
- Developer - implements user stories, writes code.
- QA Tester - writes and runs tests, ensures quality.


From the agent side, from  our previous example:

- we don't need a coding agent for user story generation. 
- We do need a coding agent issue generation because we want the AI to be implementation aware.
- We definitely need a coding agent for implementation of user stories. But this coding agent doesn't need to be a "thinker" agent that does everything. It just needs to code.
- What about reviewing code? Maybe a "code reviewer" agent that reviews code for best practices, security, and performance?
- What about QA testing? A "QA tester" agent that writes and runs tests against the code?

Custom agents help us to:

- Specialize tasks - each agent has a specific role and expertise.
- Improve quality - specialized agents can focus on best practices in their domain.
- Reduce costs - specialized agents can be more efficient and cost-effective using the right models for their tasks.

