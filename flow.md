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
- '/generate-project-tech-stack` command to generate tech stack document. Important to set the technology stack, frameworks, libraries, and tools to be used in the project for the AI.

### Profile Feature

#### With tech stack

- Review the @project_structure.md and @project_tech_stack.md to understand the conventions and technologies to be used in this project. 
  Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/database.py.

#### As generated user story

- `/generate-user-stories`  
- Review the @project_structure.md and @project_tech_stack.md to understand the conventions and technologies to be used in this project. 
  Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/database.py.

This is better because:

- Instructions are explicit
- Project change log is preserved in the docs