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
- Configuration over hardcoded behavior

The objective is to make new data sources, exporters and execution profiles easy to integrate without modifying the rest of the system.

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

Each scraper should operate independently from the others.

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

Responsible for transforming normalized information into output formats.

Examples:

- Excel
- CSV
- JSON

Exporters never perform data extraction.

---

### Utilities

Reusable helper functions shared across the project.

Examples:

- Logging
- Text normalization
- Validation
- Common utilities

---

## Execution Flow

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
Exporter
       │
       ▼
Structured Output
```

---

## Project Structure

The project is organized into independent modules.

```text
src/

├── config/
├── scraper/
├── models/
├── exporters/
├── utils/
└── main.py
```

User-defined execution profiles are stored separately from the application source code.

```text
configs/

default.yml
custom.yml
...
```

This separation keeps configuration independent from implementation and allows reusable execution profiles.

---

## Extensibility

The project is designed so that adding a new capability only requires implementing a new module within its corresponding layer.

Typical extension points include:

- New scrapers
- New exporters
- New configuration profiles
- New validation strategies

The remaining architecture should remain unchanged.

This allows the engine to evolve incrementally while keeping components isolated and maintainable.

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

These capabilities should be implemented by external platforms that consume this engine.