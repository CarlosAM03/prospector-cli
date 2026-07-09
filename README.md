# Prospector CLI

Prospector CLI is an open-source command-line engine for extracting structured business prospect data from publicly available sources.

The project focuses on transforming raw public information into reusable datasets that can be consumed by CRM, ERP, marketing automation or custom business platforms.

---

* Public data in. Structured prospects out.

---

## Philosophy

Prospector CLI is intentionally designed as a lightweight extraction engine.

Its responsibilities are limited to:

- Searching public data sources.
- Extracting business information.
- Normalizing collected data.
- Exporting structured results.

Business logic such as CRM management, customer administration, marketing workflows, dashboards and analytics belongs to external applications that consume this engine.

---

## Current Status

**Version:** v0.1.0

Current development focuses on validating the technical feasibility of the extraction engine through Google Maps before expanding to additional data sources.

### Completed

- Project structure.
- Python environment.
- Playwright integration.
- Google Maps navigation.
- Interactive CLI search.
- Initial DOM exploration.
- Browser automation validation.

---

## Planned Features

- Business name extraction.
- Business category extraction.
- Business address extraction.
- Phone number extraction.
- Excel export.
- CSV export.
- Automatic scrolling.
- Configuration profiles.
- Multiple public data sources.

---

## Technology Stack

- Python 3.11
- Playwright
- Pandas
- OpenPyXL

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

- Architecture
- Scripting Pipeline
- Project Roadmap
- Contributing Guide

---

## Project Scope

Prospector CLI is responsible only for obtaining structured prospect information from public sources.

The following capabilities are intentionally outside the scope of this repository:

- CRM
- ERP
- Customer management
- User management
- Marketing automation
- Sales workflows
- Dashboards
- Analytics

These responsibilities belong to external platforms built on top of this engine.

---

## Contributing

Contributions are welcome.

Please read the documentation available in `docs/contributing.md` before submitting changes.

---

## License

License information will be added before the first stable public release.
