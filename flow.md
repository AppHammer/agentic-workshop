# Walkthbough


### start with initial commit just an idea in the docs/tasker.md

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

#### Second Problem: User Registration still does not work


