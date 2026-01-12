name: Feature Request
description: Suggest a new feature
title: "[FEATURE] "
labels: ["enhancement"]

body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a feature! Please fill out the form below.

  - type: textarea
    id: description
    attributes:
      label: Feature Description
      description: Clear description of the requested feature
      placeholder: What feature would you like to see?
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation
      description: Why this feature would be useful
      placeholder: Describe the problem it solves or value it adds
    validations:
      required: true

  - type: textarea
    id: proposed-solution
    attributes:
      label: Proposed Solution
      description: Your suggested implementation approach
      placeholder: How would you implement this?

  - type: textarea
    id: alternatives
    attributes:
      label: Alternative Solutions
      description: Other approaches you've considered
      placeholder: What other solutions exist?

  - type: textarea
    id: additional
    attributes:
      label: Additional Context
      description: Any other relevant information
