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
8. Experimental generation runs record the candidate and validation result under `data/raw/`.

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

2. **Run experimental generation and validation:**

   ```bash
   uv run python scripts/live_generate_20.py \
     --model Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf \
     --output data/raw/experimental_run.jsonl
   ```

3. **Run the test suite:**

   ```bash
   uv run pytest
   ```

## Evidence Loading

Evidence loaders are evaluated in a fixed registry order. The registry returns the first loader whose `supports()` method accepts the target path.

| Priority | Loader                   | Actual matching rule                         |
| -------- | ------------------------ | -------------------------------------------- |
| 1        | `HandBrakeCliLoader`     | Exact filename `handbrakecli-help.txt`       |
| 2        | `FFmpegLoader`           | Filename contains `ffmpeg`, case-insensitive |
| 3        | `CLIHelpLoader`          | Filename suffix is `.txt` or `.help`         |
| 4        | `MarkdownEvidenceLoader` | Filename suffix is `.md` or `.markdown`      |
| 5        | `TextEvidenceLoader`     | Filename suffix is `.txt` or `.md`           |
| 6        | `ManPageLoader`          | Filename contains `.man.` or has suffix `.1` |

Because matching is first-match, earlier loaders take precedence when multiple loaders support the same path.

The repository currently contains source evidence for HandBrakeCLI, FFmpeg, jq, and a sample man page under `data/evidence/`.

## Normalized Evidence

Evidence is represented by `NormalizedEvidenceDocument` and `NormalizedEvidenceFact` models.

A normalized document contains:

* `document_id`
* `source_id`
* `source_type`
* `source_sha256`
* `facts`
* `metadata`

Facts contain:

* `fact_id`
* `document_id`
* `category`
* `subject`
* `predicate`
* `value`
* `provenance`
* `metadata`

Provenance records the source identifier and hash together with source location information such as line range, section, and raw snippet when available.

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

The current configuration is supplied through environment variables. No `.env` file loading is implemented.

| Variable         | Default                                     |
| ---------------- | ------------------------------------------- |
| `MODEL_PROVIDER` | `openai_compatible`                         |
| `MODEL_NAME`     | `default`                                   |
| `MODEL_ENDPOINT` | `http://127.0.0.1:8080/v1/chat/completions` |
| `HELP_FILE`      | `data/evidence/handbrakecli-help.txt`       |
| `OUTPUT_FILE`    | `data/raw/livefire_20.jsonl`                |

For example:

```bash
export MODEL_PROVIDER=openai_compatible
export MODEL_NAME=Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf
export MODEL_ENDPOINT=http://127.0.0.1:8080/v1/chat/completions
```

`MODEL_NAME=default` is a configuration default, not an actual model selection. It indicates that no explicit model name was supplied; it does not identify usable model weights.

The live-generation script also accepts `--provider`, `--model`, `--endpoint`, `--help-file`, and `--output`, which override the corresponding runtime settings for that invocation.

The default endpoint is a local OpenAI-compatible HTTP endpoint suitable for a locally running `llama.cpp` server. No authentication is configured by the current runtime settings.

The current generation configuration uses temperature `0`. The live generation path has been exercised with Qwen models; generation is still an experimental part of the pipeline.

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

The live-generation script also records parse/request failures separately, including invalid JSON and invalid JSON shape. Validation is deterministic for a given candidate and evidence index.

## Repository Layout

```text
data/
  evidence/       source evidence artifacts
  normalized/     normalized evidence artifacts
  raw/             experimental generation and validation run output

docs/
  current-state.md
  notes/           historical architecture notes, benchmarks, and blueprints

scripts/           operational and analysis scripts

src/
  dataset_tools/
    config/        runtime configuration
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

## Experimental Live Generation

`live_generate_20.py` exercises the generation and validation boundary against an evidence source.

A run records, for each attempt:

* attempt number
* source SHA-256
* generator provider
* generator model
* raw model response
* parsed candidate
* validation result

The live generator currently builds an evidence index directly from the loaded document. Constraint extraction is available separately through the evidence layer; the live-generation script does not currently perform a separate `extract_constraints()` call before building its index.

## Run Records

Run records are useful for evaluating generation and validation behavior but are not currently a durable dataset contract.

In particular:

* generated outputs may be overwritten when the same output path is reused;
* candidate-to-fact relationships are not currently stored as a dedicated final dataset schema.

## Dataset Analysis

The repository includes scripts and tests for analyzing experimental data, including dataset diversity and CLI option coverage.

These tools support evaluation of the generation pipeline. They do not imply that the analyzed records constitute a finalized training dataset.

## Current Generation State

The repository contains experimental generation and validation runs used to exercise the pipeline.

Files under `data/raw/` are run artifacts. They contain generation attempts, model/provider information, raw and parsed responses, and validation results. They are **not** a finalized training dataset.

There is currently no implemented dataset-promotion or export step that turns accepted generation records into a final problem:answer dataset. The project therefore does **not** currently contain a finalized generated training dataset.

## Current Scope and Known Limitations

The current implementation is focused on deterministic evidence normalization, fact/constraint extraction, candidate generation, and validation.

Known limitations include:

* generation is still experimental;
* there is no finalized problem:answer dataset or dataset-promotion workflow;
* only currently documented evidence can establish accepted values;
* enum constraints are enforced, while other constraint types are modeled but not yet enforced;
* the current HandBrakeCLI evidence does not derive preset-name enum values;
* some live-generation edge cases remain, including shell-syntax cases and `--flag=value` handling;
* parse/request failures are recorded as run-level validation failures;
* the declared SQL/tree-sitter dependencies are not currently part of the evidence/validation implementation.

Future work explicitly discussed for the project includes expanding evidence ingestion with additional loaders and continuing to separate generation from source-format-specific implementation. These are future directions, not claims about the current implementation.

