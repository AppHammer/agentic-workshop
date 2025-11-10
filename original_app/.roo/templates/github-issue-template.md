# Title: {VERSION}-{EPIC NUMBER}-{USER STORY NUMBER}-{TASK NUMBER} - [Brief Title of Task]

## Summary: 
[Brief, descirption of the task]

### Acceptance Criteria:
[Provide a list of Acceptance Criteria required to test the code changes for completeness]

### Test Strategy:

[Provide a Test Strategy, including required tools, types of tests, and what to test]

---

[ For all the sections below, only use the ones that are relevant to the task ]

## 📝 Code Changes
**Description:**
[Describe the logic and reason for the code changes.]

**File:** `path/to/modified/file.js`
```diff
- old code line
+ new code line
````

---

-----

## ✨ New Files (If Applicable)

  - `path/to/new/file1.ts`
  - `path/to/new/service/file2.py`

-----

## 📄 JSON Contracts (If Applicable)

**Contract Name:** `User.json`

```json
{
  "user": {
    "id": "string",
    "name": "string",
    "email": "string"
  }
}
```

-----

## 📡 API Specs (If Applicable)

```yaml
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Returns a list of users.
      responses:
        '200':
          description: A JSON array of user objects
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
```

-----

## 🖥️ Front End Components (If Applicable)

**Component Name:** `UserProfileCard.vue`

**Description:**
[Brief description of the component's purpose, props, and appearance.]

**Code:**

```jsx
import React from 'react';

const UserProfileCard = ({ user }) => {
    return (
        <div className="card">
            <h3>{user.name}</h3>
            <p>{user.email}</p>
        </div>
    );
};

export default UserProfileCard;
```

-----

## 📦 Dependencies (If Applicable)

**Package Manager:** `npm`

  - `axios@^1.4.0`
  - `lodash@^4.17.21`

**Package Manager:** `pip`

  - `requests==2.31.0`

-----

## 🎨 Figma Links (If Provided)

  - **High-Fidelity Mockup:** [Link to Figma Frame]
  - **Component Design:** [Link to Figma Component]
  - **User Flow Prototype:** [Link to Figma Prototype]

## Issue Dependencies

[ Link other issues that this issue is dependent on]

## Related Issues

[ Link other issues that this issue is related to]