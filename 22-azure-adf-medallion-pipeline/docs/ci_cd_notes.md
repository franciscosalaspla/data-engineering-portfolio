# CI/CD Notes

This project is designed to be versioned and reviewed through Git, even though it runs locally and does not deploy Azure resources.

## Versioning

Pipeline changes should be tracked in branches and reviewed through pull requests. A practical branch strategy could be:

- `main` for reviewed portfolio-ready code;
- feature branches for new pipelines or fixes;
- draft pull requests while validation is still in progress.

## Pull Request Validation

A PR for this project should validate:

- Python syntax with `py_compile`;
- dependency installation;
- full pipeline execution;
- final pipeline status;
- data quality summary;
- ignored generated outputs.

## DEV / QA / PROD Conceptual Flow

In a real Azure setup, promotion could follow:

1. DEV: develop and run with sample data.
2. QA: validate with controlled data and automated checks.
3. PROD: deploy approved pipeline definitions and notebooks.

This local project does not deploy to any environment, but the same review discipline applies.

## What to Automate

Useful automated checks would include:

- linting and formatting;
- unit tests for transformation logic;
- pipeline smoke test with small data volumes;
- schema checks for Bronze, Silver, and Gold outputs;
- validation that no secrets or generated data are committed;
- documentation checks for required README sections.
