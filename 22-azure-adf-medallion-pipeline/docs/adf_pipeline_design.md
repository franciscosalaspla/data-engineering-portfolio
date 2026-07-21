# ADF-Style Pipeline Design

This project models an Azure Data Factory-style pipeline with explicit activities, dependencies, monitoring metadata, and a final run summary.

## Activities

An activity is one executable step in the pipeline. In this project, activities are represented as Python function calls wrapped by `app/adf_orchestrator.py`.

The simulated activities are:

1. Extract source files
2. Bronze ingestion
3. Silver transformations
4. Data quality checks
5. Gold datamart build
6. Pipeline summary

Each activity records:

- activity name;
- status;
- input rows;
- output rows;
- duration in seconds;
- dependencies.

## Dependencies

Dependencies define the execution order. Bronze ingestion depends on source extraction. Silver depends on Bronze. Quality checks depend on Silver. Gold datamarts depend on successful quality checks.

This matters because a real ADF pipeline should not publish Gold outputs when upstream validation fails.

## Triggers

No real trigger is used in this local project. Conceptually, the pipeline could run from:

- a scheduled trigger;
- an event trigger when new files arrive;
- a manual trigger for backfills or controlled reprocessing.

## Parameters

The local pipeline generates a `pipeline_run_id` for each execution. In a real ADF pipeline, similar parameters could include:

- source path;
- processing date;
- environment name;
- target container;
- retry settings.

## Monitoring

The file `output/adf_pipeline_run_summary.json` acts as local monitoring evidence. It can be used to explain pipeline status, activity durations, row movement, and failed activity details if the pipeline stops.

## Retries

Retries are documented conceptually but not implemented to keep the project simple. In a real ADF pipeline, retry policies would be configured for transient failures such as storage throttling, temporary network errors, or notebook job startup delays.

## Why separate orchestration from transformation

The orchestrator should coordinate work, not contain all business logic. This project separates orchestration from transformation so each layer is easier to test, debug, and explain in an interview.
