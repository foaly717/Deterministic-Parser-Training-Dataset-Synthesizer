from dataset_tools.schema import EvidenceFact


GENERATOR_SYSTEM_PROMPT = """You are an automated training data generation engine.

Generate terminal-assistant training examples using ONLY the supplied CLI
documentation evidence.

Rules:
1. Use only options explicitly present in the evidence.
2. Do not invent option names, arguments, presets, values, or capabilities.
3. Positive examples must be directly supported by the evidence.
4. Negative examples may ask about unsupported functionality. Respond with
   "NOT SPECIFIED in target documentation" when the supplied evidence does
   not establish that functionality.
5. Preserve exact option spelling from the evidence.
6. Output valid JSON with exactly these fields:
   "instruction", "context", "response".
7. Do not output Markdown fences or explanatory text outside the JSON.
8. Use the exact documented tool name shown in the evidence as the executable.
9. Never invent, substitute, abbreviate, or generalize the executable name.
10. The "response" field must be exactly one terminal command.
11. The command must begin with the documented tool name.
12. Do not include explanatory prose, Markdown, or additional commands.
"""


def format_evidence_context(facts: list[EvidenceFact]) -> str:
    """Render structured evidence without discarding provenance."""
    sections: list[str] = []

    for fact in facts:
        aliases = ", ".join(fact.aliases) if fact.aliases else "none"
        argument = fact.argument or "none"
        description = (
            fact.description.replace("\n", " ")
            if fact.description
            else "No description"
        )
        lines = [
            f"tool: {fact.tool or 'none'}",
            f"name: {fact.name}",
            f"aliases: {aliases}",
            f"argument: {argument}",
            f"description: {description}",
            f"source lines: {fact.line_start}-{fact.line_end}",
        ]
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def build_candidate_prompt(
    facts: list[EvidenceFact],
    sample_size: int = 10,
) -> str:
    """Build a deterministic grounded prompt for single-example generation."""
    if sample_size < 1:
        raise ValueError("sample_size must be >= 1")

    selected = facts[:sample_size]

    if not selected:
        raise ValueError("At least one evidence fact is required")

    context = format_evidence_context(selected)

    return f"""{GENERATOR_SYSTEM_PROMPT}

Target CLI evidence:

{context}

Generate exactly ONE high-quality terminal instruction-response training pair
grounded exclusively in the evidence above.

The "response" field must be exactly one terminal command that the user can
run. It must begin with the exact documented tool name from the evidence.

Output exactly ONE JSON object with these fields:
"instruction", "context", "response".

Do not output additional JSON objects, arrays, Markdown fences, or explanatory
text outside the JSON object.
"""
