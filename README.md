# Grounded Commands

A deterministic evidence-processing and validation pipeline for generating and evaluating structured command-line training examples.

The project separates **documented evidence**, **deterministic parsing and validation**, and **LLM-based candidate generation**. The LLM generates candidates; it does not determine whether a candidate is valid.

## Design Principles

* **Evidence-grounded:** generated candidates are based on facts extracted from documented source material.
* **Deterministic validation:** acceptance and rejection are determined by code and normalized evidence, not by the LLM.
* **Traceable:** normalized facts retain source provenance, and identifiers are derived deterministically.
* **Model-independent boundary:** the generation layer uses an `LLMClient` interface rather than embedding a specific model implementation.
* **No invented evidence:** the pipeline does not infer undocumented values simply to increase coverage.

## Information Flow

1. A source artifact is selected.
2. A registered evidence loader parses the source into a normalized evidence document.
3. The document contains normalized facts with provenance.
4. Constraint extraction can derive structured constraints from those facts.
5. The generator selects evidence and builds a prompt.
6. An LLM produces a candidate.
7. The validator checks the candidate against the documented evidence.
The deterministic pipeline ends at validation. LLM generation itself is not deterministic.

## Getting Started

### Prerequisites

* Python `>= 3.11`
* `uv` package manager
* A running OpenAI-compatible local API endpoint, such as a `llama.cpp` server, for generation workflows

### Installation

```bash
uv sync
```

### Quickstart

1. **Normalize source evidence:**

   ```bash
   uv run python scripts/normalize_evidence.py \
     --input data/evidence/handbrakecli-help.txt \
     --output /tmp/normalized-handbrake.json
   ```

2. **Run the test suite:**

   ```bash
   uv run pytest
   ```

## Evidence Loading

Evidence loaders are evaluated in a fixed registry order. The registry returns the first loader whose `supports()` method accepts the target path.

| Priority | Loader | Matching rule |
| -------- | ------ | ------------- |
| 1 | `CLIHelpLoader(tool_name="HandBrakeCLI", filename="handbrakecli-help.txt")` | Exact filename `handbrakecli-help.txt` |
| 2 | `FFmpegLoader` | Filename contains `ffmpeg`, case-insensitive |
| 3 | `CLIHelpLoader` | `.txt` or `.help` source containing CLI usage/option syntax |
| 4 | `MarkdownEvidenceLoader` | `.md` or `.markdown` |
| 5 | `ManPageLoader` | `.man.` filename, `.1` suffix, or recognized man-page content |

Because matching is first-match, earlier loaders take precedence when multiple loaders support the same path.

The repository currently contains source evidence for HandBrakeCLI, FFmpeg, jq, and a sample man page under `data/evidence/`.

## Normalized Evidence

Evidence is represented by `NormalizedEvidenceDocument` and `NormalizedEvidenceFact` models.

A normalized document contains:

* `document_id`
* `artifact`
* `metadata`
* `facts`

`artifact` identifies the source with:

* `source_id`
* `source_sha256`
* optional `path_or_uri`

`metadata` describes source-level information separately from semantic evidence:

* `format`
* optional `tool`
* optional `role`

Facts contain:

* `fact_id`
* `document_id`
* `subject`
* `predicate`
* `value`
* `provenance`

The semantic predicate vocabulary includes assertions such as `supports`, `enumerates`, `accepts_type`, `has_minimum`, `has_maximum`, `requires`, and `conflicts_with`.

Provenance records source location information such as line range, section, and raw snippet when available. The source artifact identity and SHA-256 are held by the document rather than duplicated on every fact.

Document, fact, and constraint identifiers are deterministic SHA-256 identifiers. They are produced from deterministically serialized JSON representations of their input components. Fact IDs therefore depend on the document ID, fact fields, and provenance rather than on an arbitrary generated identifier.

## Constraints

The evidence layer supports derived constraint models for:

* enum values
* types
* ranges
* dependencies
* mutual exclusion

`extract_constraints()` currently derives constraints from normalized evidence, including enum constraints when documented values are explicitly represented in the evidence. The HandBrakeCLI evidence currently produces 21 extracted enum constraints.

The validator currently enforces enum-value constraints. The other constraint model types exist in the schema but are not currently enforcement mechanisms.

The project does not invent undocumented enum values. For example, the current HandBrakeCLI evidence documents `--preset` as an option but does not provide preset-name values, so no preset enum constraint is derived from that evidence.

## Candidate Generation and LLM Boundary

The generator currently selects a documented CLI option fact and uses it to construct a generation prompt.

The LLM boundary is represented by:

```text
LLMClient.generate(prompt, max_tokens)
```


## Validation

Candidate validation is staged across five sequential checkpoints:

| Stage | Check         | Description                                                     |
| ----- | ------------- | --------------------------------------------------------------- |
| 1     | `structure`   | Validates the candidate's required structure                    |
| 2     | `command`     | Confirms the target CLI executable matches the expected command |
| 3     | `options`     | Validates flags and arguments against normalized evidence facts |
| 4     | `constraints` | Enforces active constraints, such as supported enum values      |
| 5     | `complete`    | Marks a candidate accepted after all validation stages succeed  |

A `ValidationResult` records:

* `status`
* `stage`
* `reason_code`
* `validation_logs`

Current validation reason codes include:

* `INVALID_STRUCTURE`
* `UNEXPECTED_EXECUTABLE`
* `UNSUPPORTED_OPTION`
* `UNSUPPORTED_ENUM_VALUE`

Generation results can be assembled into canonical RunRecords containing the selected evidence fact, source identity, prompt metadata, raw model response, parsed candidate, and deterministic validation result.

## Repository Layout

```text
data/
  evidence/       source evidence artifacts
  normalized/     normalized evidence artifacts

docs/
  current-state.md
  notes/           historical architecture notes, benchmarks, and blueprints

scripts/           operational and analysis scripts

src/
  dataset_tools/
    evidence/      loaders, normalized models, IDs, indexes, constraints
    generator/     evidence selection and prompt construction
    llm/           LLM client abstraction and implementations
    validators/    candidate validation and result serialization

tests/              unit and integration coverage
```

`docs/notes/` contains historical project material and architectural planning. It is not the authoritative description of every current implementation detail.

## Development

The project uses `uv` for Python environment and dependency management.

Run the test suite with:

```bash
uv run pytest
```

Runtime configuration is provided through the project configuration layer rather than hard-coded model-specific paths.

## Evidence Normalization

`normalize_evidence.py` converts supported source evidence into the normalized document representation.

For example:

```bash
uv run python scripts/normalize_evidence.py \
  --input data/evidence/handbrakecli-help.txt \
  --output /tmp/normalized-handbrake.json
```

The resulting JSON contains the normalized document, facts, provenance, and associated metadata.

## Run Records

Run records are useful for evaluating generation and validation behavior but are not currently a durable dataset contract.

In particular:

* generated outputs may be overwritten when the same output path is reused;
* candidate-to-fact relationships are not currently stored as a dedicated final dataset schema.

## Dataset Analysis

The repository includes scripts and tests for analyzing generation and validation records, including dataset diversity and CLI option coverage.

These tools support evaluation of the generation pipeline. They do not imply that the analyzed records constitute a finalized training dataset.

## Current Generation State

The generator currently selects documented evidence and produces an LLM-generated candidate. The candidate is parsed, validated deterministically against the prepared evidence, and can be represented as a canonical RunRecord.

RunRecords are evaluation artifacts rather than the final training-dataset contract. There is currently no implemented dataset-promotion or export step that turns accepted records into a final problem:answer dataset. The project therefore does **not** currently contain a finalized generated training dataset.

## Current Scope and Known Limitations

The current implementation is focused on deterministic evidence normalization, fact/constraint extraction, candidate generation, and validation.

Known limitations include:

* generation is not yet a finalized dataset-production workflow;
* there is no finalized problem:answer dataset or dataset-promotion workflow;
* only currently documented evidence can establish accepted values;
* enum constraints are enforced, while other constraint types are modeled but not yet enforced;
* the current HandBrakeCLI evidence does not derive preset-name enum values;
* parse/request failures are recorded as run-level validation failures;
* the declared SQL/tree-sitter dependencies are not currently part of the evidence/validation implementation.

Future work explicitly discussed for the project includes expanding evidence ingestion with additional loaders and continuing to separate generation from source-format-specific implementation. These are future directions, not claims about the current implementation.

