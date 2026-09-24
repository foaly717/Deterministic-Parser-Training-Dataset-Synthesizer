# Current State

## Completed

- Validation pipeline with staged candidate validation.
- Deterministic evidence-seeded generation.
- Dataset diversity reporting.
- Option coverage reporting.
- Canonical normalized evidence document and fact schema.
- Canonical documentation-ingestion boundary with registered evidence loaders.
- Documentation ingestion separated from command parsing and `ParsedCommand` command IR.
- Legacy `CLIOption` and `ManEntry` documentation contracts removed.

## Current generation and validation state

- The generator selects documented evidence and produces an LLM-generated candidate.
- Candidates are parsed and validated deterministically against prepared evidence.
- Generation results can be represented as canonical RunRecords containing evidence identity, model/prompt metadata, candidate data, and validation results.
- No finalized problem:answer training dataset has been produced, curated, or accepted for final use.
- There is currently no dataset-promotion or export step that turns accepted generation records into a final training dataset.

## Next work

- Expand canonical evidence coverage with additional source-specific loaders and semantic extractors.
- Continue keeping generation and validation independent of source format and model.
