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

Whenever possible, scraper implementations delegate reusable execution behavior to shared engines instead of implementing infrastructure directly.

This allows every public source to optimize its extraction strategy without affecting the global architecture.

### Architectural Rule

Reusable behavior should exist in only one place.

If the same execution logic is required by multiple scrapers, it belongs in an engine.

If the same helper function is required by multiple modules, it belongs in a utility.

Scrapers should remain focused exclusively on implementing the extraction workflow specific to their target source.

---

## Dependency Principles

Prospector CLI follows a unidirectional dependency model.

Reusable infrastructure must never depend on scraper implementations.

Instead, scraper implementations depend on reusable engines and shared modules.

The dependency flow is intentionally organized as follows:

```text
CLI

↓

Configuration

↓

Scraper

↓

Engines

↓

External Libraries
```

This architecture allows reusable infrastructure to evolve independently from individual scrapers while minimizing coupling across the project.

Whenever reusable behavior is identified, it should be extracted into an engine instead of being duplicated across scraper implementations.

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

### Engines

Engines encapsulate reusable execution behavior shared across multiple scrapers.

Unlike utilities, which provide isolated helper functions, engines coordinate reusable execution workflows and infrastructure shared throughout the engine.

Typical responsibilities include:

- Selector resolution
- DOM synchronization
- Validation
- Normalization
- Deduplication
- Website inspection
- Future reusable execution workflows

Scrapers delegate reusable behavior to engines instead of implementing it directly.

This separation allows infrastructure to evolve independently from scraper implementations while keeping extraction logic focused on source-specific behavior.

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
- File naming
- Text parsing
- Performance helpers
- Common helper functions

Utilities should remain stateless whenever possible.

Reusable execution behavior belongs in engines rather than utilities.

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

## Engine Architecture

Reusable execution behavior is organized into specialized engines.

Each engine owns a single infrastructure responsibility and may be reused by multiple scrapers.

Engines expose reusable interfaces while remaining independent from scraper implementations.

This approach reduces duplicated logic, minimizes coupling and improves long-term maintainability as additional data sources are introduced.

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

Every execution stage should enrich the information produced by previous stages without degrading it.

A stage may complete missing fields or replace existing values only when a more accurate representation is available.

No stage should overwrite valid data with missing or lower-quality information.

---

## Project Structure

The project is organized into independent modules.

```text
src/

├── config/
├── engines/
│   └── selector/
├── exporters/
├── models/
├── scraper/
├── services/
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
...
```

This separation keeps the global architecture independent from scraper-specific implementation details.

---

## Extensibility

The project is designed so that new capabilities can be added without modifying existing architectural layers.

Typical extension points include:

- New scrapers
- New engines
- New exporters
- New configuration profiles
- New validation modules
- New normalization modules
- New website enrichment modules

Whenever new reusable behavior is introduced, it should be implemented as an engine rather than embedded inside scraper implementations.

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