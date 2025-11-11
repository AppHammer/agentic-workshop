---
argument-hint: <issue-number>
description: Complete end-to-end implementation of a issue with testing and validation
sub-agent: orchestrator
---

FIRST SWITCH TO ORCHESTRATOR MODE

## Description

This command orchestrates a comprehensive workflow to implement, test, and validate an issue. It manages the entire development lifecycle from requirement analysis to pull request creation. The issues can be found in the issues directory ..docs/<version>/issues/<issue-number>.md

Here is the workflow definition in YAML:

```yaml
---
workflow_name: Resolve and Deploy Issue
input_issue: .docs/<version>/issues/<issue-number>.md

agents:
  - id: arch
    name: architect
  - id: dev
    name: code
  - id: qa
    name: qa-engineer

artifacts:
  - name: project_structure
    desctiption: "The structure of the project"
    location: ./project_structure.md
  - name: tech_stack
    desctiption: "The tech stack of the current application"
    location: ./tech_stack.md
  - name: design_doc
    description: "A comprehensive design doc for the feature"
    location: .docs/<version>/design.md
  - name: code_summary
    description: "The summary of the code and what changed, including unit tests written and how to execute"
  - name: qa_report
    description: "A structured report with status ('PASS' or 'FAIL') and a list of required fixes. and a deployment recommendation"
    template: .roo/templates/qa-summary-template.md

steps:
  - step_name: GATHER_REQUIREMENTS
    agent_id: arch
    input:
      - input_issue
    action: |
      Analyze the INPUT_ISSUE. 
      Consult the software architect persona for architectural constraints, data models, and API contracts.
      review the project_stucture, tech_stack, and design_doc to ensure the INPUT_ISSUE instructions align with the feature requirements and follows the proper coding practices in the code base.
      Produce a succinct 'specs_doc' with all information and clear acceptance criteria needed for a developer to begin work.
    output:
      - specs_doc

  - step_name: INITIAL_DEVELOPMENT
    agent_id: dev
    input:
      - specs_doc
    action: |
      Write the complete code, including all necessary functions, classes, and unit tests, 
      to satisfy 100% of the requirements and acceptance criteria in the 'specs_doc'.
    output:
      - code_summary

  - step_name: QA_LOOP
    type: loop
    condition: "artifacts.qa_report.status != 'PASS'"
    # This loop will continue as long as the QA report is not 'PASS'
    # It assumes the first run will have no qa_report, so the loop executes at least once.
    sub_steps:
      - step_name: PERFORM_QA
        agent_id: qa
        input:
          - code_bundle
          - specs_doc
        action: |
          review the artifacts.qa_report.template, and ensure you have all the infomration required to fill it out.

          You MUST use the playwright mcp server for all ux testing and validation.

          Customer Login: customer1 password123
          Tasker Login: tasker1 password123

          The backend and frontend will need to be run together for testing

          Perform a full analysis:
          1. Review 'code_bundle' for quality, maintainability, and security.
          2. Run all unit tests.
          3. Analyze the code against the 'specs_doc' to ensure all requirements are met.
          4. Perform functional and interface QA.
          5. Produce a 'qa_report' with a binary status: 'PASS' or 'FAIL'.
          6. If 'FAIL', provide a clear, actionable list of 'required_fixes'.
        output:
          - qa_report

      - step_name: CONDITIONAL_FIX
        type: conditional
        if: "artifacts.qa_report.status == 'FAIL'"
        then:
          agent_id: dev
          input:
            - code_bundle
            - "artifacts.qa_report.required_fixes"
          action: |
            Implement all fixes listed in the 'required_fixes' report. 
            Do not add new features. Return the updated code.
          output:
            - code_bundle # This updates the code_bundle for the next loop iteration

  - step_name: FINAL_REPORT
    agent_id: "orchestrator" # Or just a final reporting step
    input:
      - code_summary
      - qa_report
    action: |
      save the summary and qa_report to .docs/<version>/implementation/<issue-number>-summary.md
      Report to the user: 'QA_LOOP has passed. The following artifacts are ready for deployment.'
```