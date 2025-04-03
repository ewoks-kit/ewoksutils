# CHANGELOG.md

## 1.3.0

New features:

- Add decorator `@deprecated` to mark deprecated functions/method.

## 1.2.0

New features:

- Context manager `ewoksutils.logging_utils.cleanup.protect_logging_state` to support
  thread-safe and fork-safe access to global logging data structures.

- Support for Python 3.13.

## 1.1.0

New features:

- `ewoksutils.task_utils.task_inputs` create ewoks task inputs from a dictionary

## 1.0.0

Breaking changes:

- Rename `binding` to `engine` in events.

## 0.1.2

Changes:

- Optional module reloading when importing.

## 0.1.1

Changes:

- Ensure importing from the working directory.

## 0.1.0

Added:

- sqlite3 utilities
- ewoks event definition
- import utilities
