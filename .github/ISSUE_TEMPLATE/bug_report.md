name: Bug Report
description: Report a bug or issue
title: "[BUG] "
labels: ["bug"]

body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting a bug! Please fill out the form below to help us understand and fix the issue.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Clear description of the bug
      placeholder: What is the bug about?
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Reproduction Steps
      description: Steps to reproduce the issue
      placeholder: |
        1. First step
        2. Second step
        3. The bug occurs
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen
      placeholder: Describe the expected behavior
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happens
      placeholder: Describe the actual behavior
    validations:
      required: true

  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: Relevant environment details
      value: |
        - Python version:
        - OS:
        - AIConexus version:
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Error Logs
      description: Relevant error logs or stack traces
      render: python

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Any other relevant information
