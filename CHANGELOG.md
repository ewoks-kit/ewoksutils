# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `import_qualname`, `import_method`, `instantiate_class`, `import_module`: support importing
  from any python file not necessarily part of an installed package.

## [1.4.0] - 2025-06-10

### Changed

- Make `ConnectionHandler` abstract at import time instead of raising `NotImplementedError` at runtime.

### Fixed

- Fix `Sqlite3Handler` connection cleanup.

## [1.3.1] - 2025-05-09

### Fixed

- `cleanup_logger` should close all handlers.

## [1.3.0] - 2025-04-04

### Added

- Add decorator `@deprecated` to mark deprecated functions/method.

## [1.2.0] - 2025-01-24

### Added

- Context manager `ewoksutils.logging_utils.cleanup.protect_logging_state` to support
  thread-safe and fork-safe access to global logging data structures.
- Support for Python 3.13.

## [1.1.0] - 2025-01-13

### Added

- `ewoksutils.task_utils.task_inputs` create ewoks task inputs from a dictionary.

## [1.0.0] - 2024-12-22

### Changed

- Rename `binding` to `engine` in events.

## [0.1.2] - 2023-06-01

### Changed

- Optional module reloading when importing.

## [0.1.1] - 2023-03-21

### Changed

- Ensure importing from the working directory.

## [0.1.0] - 2022-08-31

### Added

- Sqlite3 utilities.
- Ewoks event definition.
- Import utilities.

[unreleased]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.4.0...HEAD
[1.4.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.3.1...v1.4.0
[1.3.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.3.0...v1.3.1
[1.3.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.2.0...v1.3.0
[1.2.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.1.0...v1.2.0
[1.1.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v1.0.0...v1.1.0
[1.0.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v0.1.2...v1.0.0
[0.1.2]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v0.1.1...v0.1.2
[0.1.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/compare/v0.1.0...v0.1.1
[0.1.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksutils/-/tags/v0.1.0
