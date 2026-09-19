# Current State

## Completed

- Validation pipeline with staged candidate validation.
- Deterministic evidence-seeded generation.
- Dataset diversity reporting.
- Option coverage reporting.
- Normalized evidence document schema.

## Current generation and validation state

- The repository contains experimental generation and validation runs used to exercise the pipeline.
- Run outputs under `data/raw/` are experimental artifacts, not finalized training data.
- No finalized problem:answer training dataset has been produced, curated, or accepted for final use.
- There is currently no dataset-promotion or export step that turns accepted generation records into a final training dataset.

## Next work

- Expand evidence ingestion with additional loaders.
- Keep generation pipeline independent of source format and model.
