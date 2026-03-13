def extract_action_items(text: str) -> list[str]:
    """Extract likely action items from freeform text."""

    lines = [line.strip("- *") for line in text.splitlines() if line.strip()]
    results: list[str] = []

    common_verbs = (
        "fix",
        "implement",
        "review",
        "refactor",
        "write",
        "add",
        "update",
        "remove",
    )

    for raw_line in lines:
        line = raw_line.strip()
        normalized = line.lower()

        # Existing rules: explicit markers or emphatic statements.
        if normalized.startswith("todo:") or normalized.startswith("action:"):
            results.append(line)
            continue
        if line.endswith("!"):
            results.append(line)
            continue

        # Checkbox-style tasks: [ ] or [x] prefix.
        if normalized.startswith("[ ]") or normalized.startswith("[x]"):
            results.append(line)
            continue

        # Numbered or bulleted imperatives like "1. fix bug" or "* review PR".
        parts = normalized.split(maxsplit=1)
        if not parts:
            continue

        first_token = parts[0]
        maybe_rest = parts[1] if len(parts) > 1 else ""

        # Handle "1." / "2." style prefixes by stripping them.
        if first_token.endswith(".") and maybe_rest:
            first_word = maybe_rest.split(maxsplit=1)[0]
        else:
            first_word = first_token

        if first_word in common_verbs:
            results.append(line)

    return results
