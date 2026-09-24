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


def test_extract_cli_option_facts_emits_explicit_argument_types():
    sample_help = """Usage: tool

  --name <string>     Set a name
  --count <number>    Set a count
  --quality <float>   Set quality
  --output <filename> Set destination file
"""

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_types",
        subject="tool",
    )

    type_facts = [
        fact for fact in facts
        if fact.predicate is SemanticPredicate.ACCEPTS_TYPE
    ]

    assert [(fact.subject, fact.value) for fact in type_facts] == [
        ("--name", "string"),
        ("--count", "number"),
        ("--quality", "float"),
        ("--output", "filename"),
    ]

    assert all(
        fact.provenance.line_start == fact.provenance.line_end
        for fact in type_facts
    )


def test_extract_cli_option_facts_preserves_existing_enum_and_support_facts():
    sample_help = """Usage: tool

  --format <string> Format:
      alpha
      beta
"""

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_enum_type",
        subject="tool",
    )

    supports = [
        fact for fact in facts
        if fact.predicate is SemanticPredicate.SUPPORTS
    ]
    enums = [
        fact for fact in facts
        if fact.predicate is SemanticPredicate.ENUMERATES
    ]
    types = [
        fact for fact in facts
        if fact.predicate is SemanticPredicate.ACCEPTS_TYPE
    ]

    assert [(fact.subject, fact.value) for fact in supports] == [
        ("tool", "--format"),
    ]
    assert [(fact.subject, fact.value) for fact in enums] == [
        ("--format", "alpha"),
        ("--format", "beta"),
    ]
    assert [(fact.subject, fact.value) for fact in types] == [
        ("--format", "string"),
    ]


def test_extract_cli_option_facts_emits_explicit_implied_option_dependency():
    sample_help = """Usage: tool

  --raw-output0    implies -r and output NUL after each output;
  -r               raw output
"""

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_requires",
        subject="tool",
    )

    requires = [
        fact
        for fact in facts
        if fact.predicate is SemanticPredicate.REQUIRES
    ]

    assert [(fact.subject, fact.value) for fact in requires] == [
        ("--raw-output0", "-r"),
    ]
    assert requires[0].provenance.line_start == 3
    assert requires[0].provenance.line_end == 3
    assert requires[0].provenance.raw_snippet == (
        "  --raw-output0    implies -r and output NUL after each output;"
    )


def test_extract_cli_option_facts_emits_multiple_explicit_implied_dependencies():
    sample_help = """Usage: tool

  --raw-output0    implies -r and output NUL after each output;
  --join-output    implies -r and output without newline;
  --stream-errors  implies --stream and report parse errors;
"""

    facts = extract_cli_option_facts(
        content=sample_help,
        doc_id="doc_multiple_requires",
        subject="tool",
    )

    requires = [
        fact
        for fact in facts
        if fact.predicate is SemanticPredicate.REQUIRES
    ]

    assert [(fact.subject, fact.value) for fact in requires] == [
        ("--raw-output0", "-r"),
        ("--join-output", "-r"),
        ("--stream-errors", "--stream"),
    ]
