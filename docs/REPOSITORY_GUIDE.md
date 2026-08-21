# Repository Guide

This guide explains the purpose of each intentional file in the Decision Readiness Platform and how the current ingestion flow works. It describes the repository at its initial data-discovery stage; several test and curated-data files are placeholders for upcoming work.

## Current data flow

```text
Shell environment variables
          ↓
config.py loads and validates settings
          ↓
NWSClient sends an HTTP request to api.weather.gov
          ↓
ingest_nws_alerts.py coordinates the ingestion run
          ↓
Unmodified API response is written under data/raw/nws_alerts/
```

The design separates configuration, external-system communication, and pipeline orchestration. These components change for different reasons and can therefore be developed and tested independently.

## Root files

### `README.md`

The public landing page for the project. It explains the problem, current project status, initial decision question, and information-safety boundaries. As the project matures, it should gain verified setup instructions, architecture, screenshots, results, and limitations.

### `LICENSE`

The MIT License for code authored specifically for this project. It permits others to use and modify the code while retaining the copyright and license notice. It does not automatically relicense public datasets or third-party assets; those retain their original terms.

### `.gitignore`

Defines local and generated content Git should not track. Important exclusions include:

- `.venv/`: the machine-specific Python virtual environment
- `__pycache__/` and `*.pyc`: generated Python bytecode
- `*.egg-info/`: generated package-installation metadata
- `.env`: local configuration that may contain contact details or secrets
- Runtime files under `data/raw/` and `data/curated/`
- Local databases, editor settings, and operating-system metadata

The `.gitkeep` exceptions allow otherwise-empty data directories to remain visible in Git.

### `.env.example`

A safe configuration template showing which environment variables the application expects:

- `NWS_USER_AGENT`: identifies this application to the National Weather Service
- `NWS_AREA`: two-letter state or territory area used to filter alerts
- `RAW_DATA_DIR`: location where raw responses are written

This file is documentation, not active configuration. Copy it to `.env`, replace placeholder values, and load those values into the shell before running the pipeline. The real `.env` is ignored by Git.

### `pyproject.toml`

The central Python project manifest. It currently defines:

- The build system (`setuptools`)
- Project name, version, description, and supported Python version
- Runtime dependency on `httpx`
- Development dependencies such as `pytest` and `ruff`
- The `src/` package-discovery layout
- Test and lint configuration
- The `ingest-nws-alerts` terminal command

The script declaration connects the terminal command to the Python function:

```text
ingest-nws-alerts
    → decision_readiness.pipelines.ingest_nws_alerts:main
```

Running `python -m pip install -e ".[dev]"` reads this file, installs the project in editable mode, installs its dependencies, and creates the command inside the active virtual environment.

## Data directories

### `data/raw/.gitkeep`

Preserves the empty raw-data directory in Git. Raw data should be an immutable representation of what the source returned. It allows later transformations to be reproduced and audited without repeatedly depending on the live API.

Files generated under `data/raw/nws_alerts/` are deliberately ignored because they are runtime outputs and can accumulate quickly.

### `data/curated/.gitkeep`

Preserves the empty curated-data directory in Git. This directory will eventually contain validated, normalized, decision-ready outputs such as Parquet files or a local DuckDB database.

The distinction is:

- **Raw:** what the source provided
- **Curated:** what the platform has validated, standardized, and modeled

### `.gitkeep`

`.gitkeep` has no special meaning to Git. It is a community convention: an empty placeholder file lets Git retain a directory, because Git tracks files rather than directories.

## Python package

### `src/decision_readiness/__init__.py`

Marks `decision_readiness` as a Python package. It is intentionally empty at this stage. Package-level exports or version information could be added later, but an empty file is normal.

### `src/decision_readiness/config.py`

Owns application configuration. It defines an immutable `Settings` dataclass and a `load_settings()` function that reads environment variables, validates the required NWS user agent, applies defaults, and converts the raw-data directory string into a `Path` object.

Centralizing settings prevents environment access from being scattered through the client and pipeline code. It also makes configuration behavior easier to test.

## External-service client

### `src/decision_readiness/clients/__init__.py`

Marks the `clients` directory as an importable subpackage. It is intentionally empty.

### `src/decision_readiness/clients/nws.py`

Contains `NWSClient`, the boundary between this project and the National Weather Service API. It:

- Configures the API base URL
- Sends the required identifying `User-Agent`
- Requests GeoJSON responses
- Applies a request timeout
- Retrieves active alerts for an area
- Raises an explicit exception for unsuccessful HTTP responses
- Manages the HTTP connection lifecycle

It does not write files, transform alerts, or make risk decisions. Keeping the client narrowly focused makes it easier to mock in tests and reuse from other pipelines.

## Pipeline

### `src/decision_readiness/pipelines/__init__.py`

Marks the `pipelines` directory as an importable subpackage. It is intentionally empty and is not a duplicate of the other `__init__.py` files; each package directory needs its own marker.

### `src/decision_readiness/pipelines/ingest_nws_alerts.py`

Coordinates a complete ingestion run. Its responsibilities are divided into small functions:

- `build_output_path()` creates a deterministic, UTC-timestamped raw-file path.
- `write_raw_response()` creates missing directories and writes formatted JSON.
- `main()` loads settings, retrieves alerts, writes the response, and reports the result.

The response is first written to a temporary file and then moved to its final name. This reduces the chance that an interrupted write leaves a partial JSON file that appears complete.

The module can run through either:

```bash
ingest-nws-alerts
```

or:

```bash
python -m decision_readiness.pipelines.ingest_nws_alerts
```

## Tests

### `tests/fixtures/nws_alerts.json`

Contains a small, stable example of an NWS response. The fixture lets tests exercise realistic data without depending on live network access or current weather.

### `tests/test_nws_clients.py`

Contains automated tests of `NWSClient`. A mocked HTTP transport verifies request construction, successful decoding, and error handling without calling the real NWS service.

## Local generated content

The following items may appear in the IDE but are not intentional repository source files:

| Path | Created by | Purpose |
|---|---|---|
| `.git/` | Git | Commit history, branches, and repository metadata |
| `.venv/` | `python -m venv` | Isolated Python interpreter and installed dependencies |
| `__pycache__/` | Python | Cached compiled bytecode |
| `*.egg-info/` | `pip`/`setuptools` | Generated package metadata for editable installation |
| `.pytest_cache/` | pytest | Test-run cache |
| `.ruff_cache/` | Ruff | Linting cache |
| `.DS_Store` | macOS | Finder display metadata |
| `data/raw/nws_alerts/*.json` | Ingestion pipeline | Timestamped live API responses |

These files are either ignored or intentionally kept out of Git. They can generally be recreated from the tracked project files.

## Current completion state

Completed:

- Python package structure
- Environment-based configuration
- NWS HTTP client
- Timestamped raw-response ingestion
- Editable command-line entry point
- Generated-file ignore rules
- Validated alert data model
- Raw-to-curated transformation
- DuckDB storage
- Synthetic logistics data
- Geographic joins and decision metrics
- Automated unit, transformation, filesystem, and end-to-end tests
- GitHub Actions quality workflow

Potential future extensions:

- Historical incremental loading rather than snapshot rebuilding
- Census population-exposure data
- Orchestration and operational monitoring
- An API and TypeScript dashboard
- Optimization and uncertainty analysis
