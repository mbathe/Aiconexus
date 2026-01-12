name: Pull Request
description: Submit a pull request
title: "[PR] "

body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing! Please fill out the form below.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Clear description of the changes
      placeholder: What changes does this PR make?
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation and Context
      description: Why is this change needed
      placeholder: Link to issue or explain the context
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: How have you tested these changes?
      placeholder: |
        - Unit tests added
        - Integration tests passed
        - Manual testing completed
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: Code follows project style guidelines
          required: true
        - label: Tests added/updated
          required: true
        - label: Documentation updated
          required: true
        - label: No breaking changes
          required: false
        - label: PR title is descriptive
          required: true

  - type: textarea
    id: breaking-changes
    attributes:
      label: Breaking Changes
      description: List any breaking changes
      placeholder: None
