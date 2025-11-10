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

## 2.0 Leveraging Roo Commands to generate project structure and user stories

- `/generate-project-structure` command to generate project structure document. Impotant to set naming conventions, import patterns, code structure patterns, and code organization principles for the AI.
- `/generate-project-tech-stack` command to generate tech stack document. Important to set the technology stack, frameworks, libraries, and tools to be used in the project for the AI.

### Profile Feature

#### With tech stack

- Review the @project_structure.md and @project_tech_stack.md to understand the conventions and technologies to be used in this project. 
  Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/database.py.
  
**Questions**

- What changes were made to the backend to support the profile page feature?
- What frontend components were created or modified to implement the profile page?
- Is this how you would have implemented it?

#### AI Methodology

1. generate feature requirements document from text
2. Review
3. Generate user stories from feature requirements document for version 
4. Review
5. Generate technical requirements for version (reads user stories)
6. Review
7. for each user story:
    1. implement issue
    2. review code / test / adjust code
8. Final review and testing of feature


**Procedure**

- `/generate-feature-requirement` 
  Write a feature to allow users to view their profile when logged  Make their user name clickable and display user information from the User class in @backend/database.py.
  This feature only needs to support the current logged in user viewing their own  profile, not editing it. Also the user does not need to view other users profiles.
- USER: review and edit the generated feature requirements document in `docs/v0.0.2/feature_requirements.md`
- `/generate-user-stories v0.0.2` 
- `/generate-technical-requirements v0.0.2`




**This is better because:**

- To some degree it mimics the human software development workflow
- Instructions are very explicit... AI Needs explicit instructions and detailed steps
- Human in the loop for review and adjustments at every step
- Coding expectations are clear, concise and well defined
- Project change log is preserved in the docs
- Git commit for each user story
