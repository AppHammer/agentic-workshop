# [Project Name] - Project Structure Guidelines

## Directory Organization
[Define your project's directory structure here. Explain the purpose of each top-level directory. Adapt the example below to project type and technology stack. If the project contains directorys for both backend and frontend application, ensure to separate and provide details for each. Base on the template below]

```

[project-root]/
├── app/                    \# Primary source code for the application/library.
│   ├── frontend/           \# NodeJS / React frontend for the application.
│   └── backend/            \# Python / FastAPI backend for the application.
├── tests/                  \# All test files (unit, integration, e2e).
└── docs/                   \# Project documentation.

```

## Naming Conventions
[Establish clear and consistent naming conventions for files and code constructs.]

### Files
- **Components**: `[e.g., PascalCase.jsx, kebab-case.vue]`
- **Services**: `[e.g., useApiService.ts, user.service.js]`
- **Utilities**: `[e.g., dateUtils.js, string-helpers.ts]`
- **Tests**: `[e.g., ComponentName.test.js, service-name.spec.ts]`

### Code
- **Classes/Types/Interfaces**: `[e.g., PascalCase]`
- **Functions/Methods**: `[e.g., camelCase]`
- **Constants/Enums**: `[e.g., UPPER_SNAKE_CASE]`
- **Variables**: `[e.g., camelCase]`

## Import Patterns
[Define rules for how modules are imported to maintain consistency and avoid circular dependencies.]

### Import Order
[Define a consistent order for import statements.]
1.  External dependencies (e.g., `import React from 'react'`)
2.  Internal absolute imports (e.g., `import { UserService } from 'src/services/user'`)
3.  Internal relative imports (e.g., `import { helper } from './utils'`)
4.  Style imports (e.g., `import './styles.css'`)

### Import Style
- **Rule**: `[e.g., Use absolute imports from the 'src' directory for all cross-feature communication.]`
- **Rule**: `[e.g., Relative imports should only be used within the same feature module.]`

## Code Structure Patterns
[Define common patterns for organizing code *within* files.]

### Module/File Organization
[Define the standard order of code blocks within a file.]
1.  Imports
2.  Constants
3.  Type Definitions
4.  Main Component/Class/Function Implementation
5.  Helper Functions
6.  Exports

### Guiding Principles
- **Clarity**: Code should be organized to be read from top to bottom like a story.
- **Consistency**: The structure of similar files (e.g., all service files) should be consistent.
- **Single Responsibility**: Each file should have one primary purpose.

## Code Organization Principles
[State the high-level principles that guide the project's architecture and organization.]

1.  **Modularity**: Code is organized into independent, reusable modules with clear boundaries.
2.  **Separation of Concerns**: UI, business logic, and data access are kept separate.
3.  **Testability**: The structure is designed to make unit and integration testing straightforward.
4.  **Consistency**: Follow the established patterns in this document and the existing codebase.

## Module Boundaries
[Define the rules for how different parts of your project can interact.]

- **Public API vs. Internal Implementation**: `[e.g., Modules should only expose functionality through a designated index file. All other files are considered internal.]`
- **Dependency Direction**: `[e.g., 'features' can depend on 'services' and 'utils', but 'services' cannot depend on 'features'.]`
- **Cross-Feature Communication**: `[e.g., One feature should not directly import from another feature's internal files. Use shared services or state management instead.]`

## Code Size Guidelines
[Set reasonable limits to prevent files from becoming overly complex and difficult to maintain.]

- **File Size**: `[e.g., < 400 lines]`
- **Function/Method Size**: `[e.g., < 50 lines]`
- **Class Complexity**: `[e.g., < 5 methods]`
- **Nesting Depth**: `[e.g., Maximum of 3 levels of nesting]`

## Documentation Standards
[Outline the requirements for documenting the code.]

- **Public APIs**: `[e.g., All exported functions, classes, and components must have JSDoc/TSDoc/Docstrings comments.]`
- **Complex Logic**: `[e.g., Any complex algorithms or business logic must include inline comments explaining the 'why', not just the 'what'.]`
- **Module READMEs**: `[e.g., Each top-level directory (e.g., 'services') must have a README.md explaining its purpose and usage.]`
