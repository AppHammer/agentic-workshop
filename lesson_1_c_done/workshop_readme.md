# Lesson 1: Lets vibecode an app!

What are we building?

- Consult the @docs/tasker.md for the project requirements.

The problem:

- On signup: `ValueError: password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])`
- Ask Roo to fix, goes in circles.
-  Write tests, the tests don't work.
    PROMPT: write tests for the functions in  @/backend/auth.py 

The Fix:
need to update requirements.txt to use `bcrypt==4.3.0`

https://stackoverflow.com/questions/79776559/passlib-bcrypt-not-working-when-deployed-to-render-valueerror-password-cannot

Take aways:

- Hit or miss coding with AI not specific enough.
- Errors - not specifc == not consistent.
