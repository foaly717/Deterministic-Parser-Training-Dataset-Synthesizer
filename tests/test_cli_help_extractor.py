from dataset_tools.evidence.loaders.cli_help import extract_cli_option_facts
from dataset_tools.evidence.schema import SemanticPredicate


def test_extract_cli_option_facts_synthetic():
    sample_help = """Usage: tool [-v]

  -h      show help
  -r      raw output
"""
    doc_id = "doc_test_123"

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id=doc_id,
        subject="tool",
    )

    assert len(facts) == 3
    assert [fact.value for fact in facts] == ["-v", "-h", "-r"]

    assert facts[0].provenance.line_start == 1
    assert facts[0].provenance.line_end == 1
    assert facts[0].provenance.raw_snippet == "Usage: tool [-v]"
    assert facts[1].provenance.line_start == 3
    assert facts[2].provenance.line_start == 4

    first_fact = facts[0]
    assert first_fact.document_id == doc_id
    assert first_fact.subject == "tool"
    assert first_fact.predicate is SemanticPredicate.SUPPORTS
    assert first_fact.value == "-v"


def test_extract_cli_option_facts_line_numbers():
    sample_help = "header line\n  -v    verbose output"

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_456",
    )

    assert len(facts) == 1
    fact = facts[0]
    assert fact.value == "-v"
    assert fact.predicate is SemanticPredicate.SUPPORTS
    assert fact.provenance.line_start == 2
    assert fact.provenance.line_end == 2
    assert fact.provenance.raw_snippet == "  -v    verbose output"
