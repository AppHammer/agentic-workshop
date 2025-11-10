# Lesson 1: Lets vibecode an app!

In this lesson, we will be building a simple application while addressing some common issues that arise during AI development.

## What are we building?

- Consult the @docs/tasker.md for the project requirements.

## Steps

1. Roo window with `code` mode and `Sonnet 4.5`, PROMPT:
   Read in the @docs/tasker.md and implement the application based on the requirements specified.
2. Watch as a lot of code and "documentation" is generated.
3. Install the `requirements.txt` and install node dependencies.
4. Fix any issues that arise during the build process by asking roo to debug @terminal.
5. Encounter the following error on signup:
   ```
   ValueError: password cannot be longer than 72 bytes, truncate manually if necessary (e.g. my_password[:72])
   ```
6. Ask roo to to fix... goes in circles.
7. Ask roo to write unit tests for the functions in `@/backend/auth.py`.
8. Tests don't work due to the same issue. This outlays a prorblem with AI models - they are not "current" with current coding libraries and practices. MCP fixes this.
9. Update `requirements.txt` to use `bcrypt==4.3.0` as per [this StackOverflow solution](https://stackoverflow.com/questions/79776559/passlib-bcrypt-not-working-when-deployed-to-render-valueerror-password-cannot).
10. Check that the tests now work.
11. Run the app, register, login.

## Takeaways:

- Hit or miss coding with AI, inconsistent results:
  - when you are not specific enough
  - when you use different models or parameters on that model.
- Even the best AI models can produce errors and will not get complex applications right.
- Models training has a current cutoff date, and may not be aware of the latest libraries or best practices.
