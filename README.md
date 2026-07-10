# Prospector CLI

Prospector CLI is an open-source command-line engine for extracting structured business data from publicly available sources.

The project transforms raw public information into reusable datasets that can be consumed by CRM, ERP, marketing automation or custom business platforms.

---

*Public data in. Structured business data out.*

---

## Philosophy

Prospector CLI is intentionally designed as a lightweight extraction engine.

Its responsibility is to transform public information into structured data through a modular and reusable pipeline.

The engine focuses exclusively on:

* Searching public data sources.
* Extracting business information.
* Normalizing collected data.
* Validating extracted information.
* Exporting structured results.

Business logic such as CRM management, customer administration, marketing workflows, dashboards and analytics belongs to external applications that consume this engine.

---

## Design Principles

The engine is built around a small set of architectural principles that remain constant regardless of the supported data source.

* Single responsibility for every module.
* Configuration over hardcoded behavior.
* Source-independent architecture.
* Normalized internal data model.
* Scraper-specific internal pipelines.
* Incremental enrichment of business data.
* Reusable extraction components.

Each data source may require a different extraction strategy, but all sources must produce a consistent internal representation.

---

## Technology Stack

* Python 3.11
* Playwright
* Pandas
* OpenPyXL

---

## Project Structure

```text
prospector-cli/

├── configs/
│
├── docs/
│   ├── architecture.md
│   ├── contributing.md
│   ├── roadmap.md
│   └── scripting-pipeline.md
│
├── src/
│   ├── config/
│   ├── exporters/
│   ├── models/
│   ├── scraper/
│   ├── utils/
│   └── main.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Getting Started

Clone the repository:

```bash
git clone <repository-url>
cd prospector-cli
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install chromium
```

Run the application:

```bash
python src/main.py
```

---

## Documentation

Technical documentation is available in the `docs/` directory.

Available documentation:

* Architecture overview.
* Internal execution pipeline.
* Project roadmap.
* Contribution guidelines.

---

## Project Scope

Prospector CLI is responsible only for obtaining structured business information from public sources.

The following responsibilities are intentionally outside the scope of this repository:

* CRM systems.
* ERP systems.
* Customer management.
* User management.
* Marketing automation.
* Sales workflows.
* Dashboards.
* Analytics.
* Business process management.
* Data persistence.

These responsibilities belong to external platforms built on top of this engine.

---

## Contributing

Contributions are welcome.

Before submitting changes, please review the documentation available in:

```text
docs/contributing.md
```

All contributions should follow the project's architectural principles and maintain the modular design of the engine.

---

## License

License information will be added before the first stable public release.
