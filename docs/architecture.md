# Architecture

## Purpose

Prospector CLI is an open-source command-line engine designed to extract structured business information from publicly available sources.

The project focuses exclusively on data extraction, normalization and export. It intentionally avoids implementing business logic such as CRM management, customer administration, marketing automation or sales workflows.

Those responsibilities belong to external applications that consume this engine.

---

## Architectural Philosophy

Prospector CLI follows a modular architecture where every component has a single responsibility.

The engine transforms user-defined search criteria into structured prospect data through a configurable extraction pipeline.

The architecture is designed around the following principles:

- Simplicity
- Extensibility
- Reusability
- Performance
- Configuration over hardcoded behavior

The objective is to make new data sources, exporters and execution profiles easy to integrate without modifying the rest of the system.

Each scraper exposes a common interface to the engine while remaining free to implement its own internal execution pipeline.

This allows every public source to optimize its extraction strategy without affecting the global architecture.

---

## Core Components

### CLI

Application entry point.

Responsible for:

- Receiving command-line arguments.
- Starting interactive mode.
- Selecting configuration profiles.
- Executing the extraction workflow.
- Coordinating the remaining modules.

---

### Configuration

Responsible for resolving the execution configuration.

Configuration may come from:

- Command-line arguments
- Configuration profiles
- Interactive user input

The configuration system provides a single normalized configuration object to the engine regardless of its origin.

---

### Scrapers

Responsible for interacting with a single public data source.

Examples:

- Google Maps
- Business directories
- Industrial directories
- Future integrations

Every scraper is isolated from the others.

Each scraper exposes the same public interface while internally implementing the extraction strategy that best fits its source.

The engine only depends on the normalized output produced by the scraper, never on its internal implementation.

---

### Models

Represent the internal data structures handled by the engine.

Examples:

- Business
- SearchQuery
- SearchResult

Models provide a common representation regardless of the original source.

---

### Exporters

Responsible for transforming normalized information into supported output formats.

Examples:

- Excel
- CSV
- JSON

Exporters never perform data extraction.

---

### Utilities

Reusable helper modules shared across the project.

Examples:

- Logging
- Validation
- Text normalization
- Performance measurement
- DOM helpers
- Selector helpers
- Common utilities

Utilities should remain independent from any specific scraper whenever possible.

---

## Global Execution Flow

The engine follows a single execution pipeline regardless of the selected data source.

```text
CLI Arguments
       │
Configuration Profile
       │
Interactive Input
       │
       ▼
Configuration
       │
       ▼
Query Builder
       │
       ▼
Scraper
       │
       ▼
Raw Data
       │
       ▼
Normalization
       │
       ▼
Validation
       │
       ▼
Deduplication
       │
       ▼
Exporter
       │
       ▼
Structured Output
```

This pipeline represents the public contract of the engine.

Individual scrapers may implement any internal workflow as long as they produce the expected normalized output.

---

## Internal Scraper Pipelines

Every scraper may define its own internal execution pipeline.

These implementation details are documented independently from the global architecture.

For example, the Google Maps scraper internally separates extraction into multiple phases:

```text
Result List

↓

Detail Panel

↓

Website Inspection

↓

Business[]
```

Another scraper may require a completely different workflow depending on the structure and behavior of its target platform.

Keeping these pipelines independent allows each scraper to evolve without impacting the rest of the engine.

---

## Performance Principles

Performance is considered a first-class architectural concern.

Whenever possible, scrapers should:

- Synchronize using state changes instead of fixed delays.
- Minimize browser round trips.
- Reduce DOM queries.
- Batch browser interactions.
- Measure execution performance.
- Prefer deterministic synchronization over timeout-based waits.

Performance optimizations should never compromise modularity, readability or maintainability.

---

## Project Structure

The project is organized into independent modules.

```text
src/

├── config/
├── exporters/
├── models/
├── scraper/
├── utils/
└── main.py
```

Execution profiles are stored independently from the application source code.

```text
configs/

default.yml
custom.yml
...
```

Project documentation is organized independently from the implementation.

```text
docs/

architecture.md
contributing.md
roadmap.md
scripting-pipeline.md

pipelines/

google-maps.md
yellow-pages.md
linkedin.md
...
```

This separation keeps the global architecture independent from scraper-specific implementation details.

---

## Extensibility

The project is designed so that new capabilities can be added without modifying existing architectural layers.

Typical extension points include:

- New scrapers
- New exporters
- New configuration profiles
- New validation strategies
- New selector strategies
- New website enrichment modules

Existing components should remain unchanged whenever possible.

This approach allows the engine to evolve incrementally while keeping modules isolated, reusable and maintainable.

---

## Scope

Prospector CLI is responsible only for obtaining structured prospect data from public sources.

The following responsibilities are explicitly outside the scope of this project:

- CRM features
- Customer management
- User authentication
- Dashboards
- Marketing campaigns
- Business analytics
- Sales workflows
- Business rules
- Data persistence

These capabilities belong to external platforms that consume the engine.