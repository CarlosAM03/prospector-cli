# Scripting Pipeline

## Purpose

This document describes the execution flow of Prospector CLI from user input to structured output.

The pipeline is designed so every stage has a single responsibility.

---

# Overview

```
User
 │
 ▼
CLI
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
Output
```

---

# Pipeline Stages

## 1. Input

The execution starts from one of three sources:

- Interactive CLI
- Configuration profile
- Command-line arguments

The engine builds a unified search request regardless of the origin.

---

## 2. Configuration

Configuration files define reusable execution profiles.

Example responsibilities:

- Search query
- Maximum results
- Export format
- Output location

Interactive input always overrides missing values.

---

## 3. Query Builder

Transforms user input into a normalized internal query.

Example:

Input:

```
maquila tijuana
```

Normalized query:

```
SearchQuery(
    source="google_maps",
    location="Tijuana",
    keyword="maquila"
)
```

---

## 4. Scraper

Responsible for interacting with a public source.

Responsibilities:

- Navigate
- Search
- Scroll
- Extract
- Return raw information

---

## 5. Normalization

Converts raw information into internal models.

Example:

```
Business

name

category

address

phone

website
```

---

## 6. Validation

Ensures extracted information is usable.

Examples:

- Required fields
- Empty values
- Invalid formats

---

## 7. Deduplication

Removes duplicated businesses before export.

The deduplication strategy may evolve over time.

---

## 8. Export

Transforms validated information into supported formats.

Examples:

- Excel
- CSV
- JSON

Future exporters can be added without modifying previous stages.

---

# Design Principles

Every stage should:

- Receive one input.
- Perform one responsibility.
- Produce one output.

This keeps the pipeline modular, testable and extensible.

---

# Future Evolution

The pipeline has been intentionally designed to support:

- Multiple data sources
- Parallel execution
- Configuration profiles
- Plugin-based scrapers
- Future API integration

without changing the overall architecture.
