from dataset_tools.evidence.schema import NormalizedEvidenceFact


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
13. Generate a different CLI task each time.
14. Prefer different documented options when multiple options are available.
15. Do not reuse the same command pattern unless no alternatives exist.
16. Select options from different parts of the evidence when possible.
"""


def format_evidence_context(facts: list[NormalizedEvidenceFact]) -> str:
    """Render structured evidence without discarding provenance."""
    sections: list[str] = []

    for fact in facts:
        aliases_list = fact.metadata.get("aliases") or []
        aliases = ", ".join(aliases_list) if aliases_list else "none"
        argument = fact.metadata.get("argument") or "none"
        raw_description = fact.metadata.get("description")
        description = raw_description.replace("\n", " ") if raw_description else "No description"
        line_start = fact.metadata.get("source_line_start")
        line_end = fact.metadata.get("source_line_end")

        lines = [
            f"tool: {fact.subject or 'none'}",
            f"name: {fact.value}",
            f"aliases: {aliases}",
            f"argument: {argument}",
            f"description: {description}",
            f"source lines: {line_start}-{line_end}",
        ]
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def build_single_fact_prompt(
    fact: NormalizedEvidenceFact,
) -> str:
    """Build a generation prompt for exactly one deterministic evidence fact."""
    context = format_evidence_context([fact])

    return f"""{GENERATOR_SYSTEM_PROMPT}

Target CLI evidence:

{context}

Generate exactly ONE terminal instruction-response training pair
demonstrating this documented capability.

The response field must be exactly one terminal command that the user can run.
It must begin with the exact documented tool name from the evidence.

Output exactly ONE JSON object with these fields:
"instruction", "context", "response".

Do not output additional JSON objects, arrays, Markdown fences, or explanatory
text outside the JSON object.
"""
