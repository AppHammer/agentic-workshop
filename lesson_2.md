# Lesson 2: Adding Features to our App

In this lesson we will learn about commands and use them to help the AI do its job as we expect. 

## What are we building?

- Adding a profile feature to our app. We will do this two different ways. Vibe coded and then using our AI command toolset.

PROMPT: 
Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/models.py


## Steps 

1. Good AI prompts for Coding:

    - Provide context about the project. The models have no context.
    - Clear with details instructions about what you want done.
    - Specific to the task, scoping it appropriately.
    - Outline what should and should not be included in the implementation.

2. Let's generate project documentation to set the context for the AI. This will help the AI understand the project structure and technical requirements better.
3. Your first commands. Execute these using the `architect` mode with `Sonnet 4.5` model.
    - `/generate-project-structure` command to generate project structure document. Impotant to set naming conventions, import patterns, code structure patterns, and code organization principles for the AI.
    - `/generate-project-tech-stack` command to generate tech stack document. Important to set the technology stack, frameworks, libraries, and tools to be used in the project for the AI.
4. commit working directory before proceeding. `git add . && git commit -m "Generated project structure and tech stack documentation"`
5. Implement the "Profile" feature using vibe code with the following prompt in roo `code` mode and `Sonnet 4.5` model:

    - Review the @docs/project_structure.md and @docs/project_tech_stack.md to understand the conventions and technologies to be used in this project.
      Write a feature to allow users to view their profile when logged in. Make their user name clickable and display user information from the User class in @backend/models.py
      This feature only needs to support the current logged in user viewing their own  profile, not editing it.  
      Also the user does not need to view other users profiles.
6. Reset the working directory to before the profile feature was added. `git reset --hard HEAD`
7. Now let's implement the same feature using our AI command methodology.
    1. Using roo `Architect` with `Sonnet 4.5` model, run the `/generate-feature-requirement` command.
       Write a feature to allow users to view their profile when logged  Make their user name clickable and display user information from the User class in @backend/models.py.
       This feature only needs to support the current logged in user viewing their own  profile, not editing it. Also the user does not need to view other users profiles.
    2. Review the feature requirements document generated in `docs/v0.0.1/feature_requirements.md` and make any necessary edits.
    3. Using roo `Architect` with `Sonnet 4.5` model, run the `/generate-user-stories v0.0.1` command. This breaks down the feature requirements into user stories.
    4. Review the generated user stories generated in `docs/v0.0.1/user_stories.md` and make any necessary edits.
    5. Using roo `Architect` with `Sonnet 4.5` model, run the `/generate-technical-requirements v0.0.1` command. This creates a github issue for each user story with technical requirements. Instead of github the command makes an issue in the `docs/v0.0.1/issues/` folder.
    6. Review each generated issue in `docs/v0.0.1/issues/` and make any necessary edits. These will be coded next.
    7. For each issue:
        1. Implement the issue using roo `code` mode with `Sonnet 4.5` model. `/implement-issue <issue_number`
    8. All issues done, test the app with a final review. Is the feature acceptable?



## Takeaways:

- ??
