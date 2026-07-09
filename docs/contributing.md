# Contributing

Thank you for your interest in contributing to Prospector CLI.

The goal of this project is to provide a lightweight, modular and reusable engine for extracting business information from public sources.

---

## Project Philosophy

Before contributing, keep the following principles in mind:

- Keep components small and focused.
- Avoid introducing business logic into the engine.
- Favor reusable modules over source-specific implementations.
- Prioritize readability over clever code.

---

## Project Structure

```text
src/

├── scraper/
├── exporters/
├── models/
├── utils/
└── main.py
```

Each directory has a single responsibility.

---

## Branch Strategy

Create a new branch for every feature or fix.

Examples:

```text
feature/google-maps-parser

feature/excel-export

fix/google-selectors

docs/update-roadmap
```

---

## Commit Convention

The project follows Conventional Commits.

Examples:

```text
feat: implement Google Maps search

feat: export businesses to Excel

fix: update Playwright selectors

refactor: simplify scraper pipeline

docs: improve architecture documentation
```

---

## Pull Requests

Before submitting a Pull Request:

- Keep changes focused on a single purpose.
- Update documentation when necessary.
- Verify that existing functionality is not affected.
- Follow the project's architecture and philosophy.

---

## Code Style

General guidelines:

- Use descriptive names.
- Keep functions short.
- Avoid duplicated code.
- Prefer composition over large classes.
- Document non-obvious decisions.

---

## Reporting Issues

When reporting bugs, include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs or screenshots when available

---

## Thank You

Every contribution helps improve the project.

Whether it is code, documentation, bug reports or suggestions, your participation is appreciated.
