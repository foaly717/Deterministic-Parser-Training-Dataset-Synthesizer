import hashlib

from dataset_tools.evidence.loaders.cli_help import extract_cli_option_facts
from dataset_tools.evidence.schema import FactCategory


def test_extract_cli_option_facts_synthetic():
    sample_help = """Usage: tool [-v]

  -h      show help
  -r      raw output
"""
    doc_id = "doc_test_123"
    source_id = "synthetic_tool"
    source_sha256 = hashlib.sha256(sample_help.encode("utf-8")).hexdigest()

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id=doc_id,
        source_id=source_id,
        source_sha256=source_sha256,
        subject="tool",
    )

    # 1. Assert exact fact count (1 usage fact + 2 option facts)
    assert len(facts) == 3

    values = [fact.value for fact in facts]
    assert values == ["-v", "-h", "-r"]

    # 3. Assert usage line provenance vs option lines
    assert facts[0].provenance.line_start == 1
    assert facts[0].metadata["description"] == "Referenced in usage syntax"
    assert facts[1].provenance.line_start == 3
    assert facts[2].provenance.line_start == 4

    first_fact = facts[0]
    assert first_fact.document_id == doc_id
    assert first_fact.category == FactCategory.CLI_OPTION
    assert first_fact.subject == "tool"
    assert first_fact.predicate == "supports"
    assert first_fact.provenance.source_id == source_id
    assert first_fact.provenance.source_sha256 == source_sha256


def test_extract_cli_option_facts_line_numbers():
    sample_help = "header line\n  -v    verbose output"
    source_id = "verbose_tool"
    source_sha256 = hashlib.sha256(sample_help.encode("utf-8")).hexdigest()

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_456",
        source_id=source_id,
        source_sha256=source_sha256,
    )

    assert len(facts) == 1
    fact = facts[0]
    assert fact.value == "-v"
    assert fact.provenance.line_start == 2
    assert fact.provenance.line_end == 2
    assert fact.provenance.raw_snippet == "  -v    verbose output"
