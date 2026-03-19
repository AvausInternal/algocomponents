# Contributing to Algocomponents

First of all, thank you for considering contributing to Algocomponents! This repository contains the algo components that aim to make writing code faster, easier, and more fun.

## Commit Customs

### Size

Commits should be large enough so that they can easily be described as a single, impactful change.

Commits should also be small enough so that you can easily get an overview of what the change is.

### Formatting

The 50/72 standard introduced by Tim Pope is used for the commit messages:

[A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)

### CI/CD Artifact Registry

When you merge code to the `master` branch, the CI/CD pipeline will try to create a new version in the artifact registry.

Remember to change the version number every time you want to push something to master. Otherwise, the creation of an artifact will fail.

## How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes following our commit customs (above)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup

To run tests:
```bash
pytest
```
