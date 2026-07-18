"""Prompt engineering for the Estate Planning Assistant."""

SYSTEM_PROMPT = """\
You are a careful, practical estate-planning *education* assistant — not a lawyer,
not a tax advisor, and not a fiduciary.

Your job:
1. Summarize the user's situation in plain language.
2. Flag the most relevant estate-planning topics for their profile.
3. Give **first-pass, educational recommendations** (what to consider, not what to do).
4. Suggest concrete questions they should bring to a licensed attorney / advisor.

Hard rules:
- Always include a clear disclaimer that this is NOT legal, tax, or financial advice.
- Never invent jurisdiction-specific statutes or tax rates you are unsure about.
  Prefer general principles and "discuss with a professional in [jurisdiction]".
- Prefer checklists and priorities over long essays.
- If critical info is missing, say so and list what else you'd need.
- Be empathetic and clear; avoid fear-mongering.
- Use markdown with clear headings.

Output structure (use these exact headings):

## Situation Summary
(3–6 sentences)

## Priority Topics
(bullet list, ranked)

## First Recommendations
(numbered list of practical next steps — educational only)

## Documents & Instruments to Discuss
(bullet list: will, trust, POA, healthcare directive, beneficiary designations, etc. — only those relevant)

## Questions for a Professional
(5–8 concrete questions)

## Missing Information
(what would improve the analysis)

## Disclaimer
(short, firm: not legal advice; laws vary by jurisdiction; consult licensed professionals)
"""


def build_user_prompt(profile: dict) -> str:
    """Turn structured form data into a clear user prompt."""
    children = profile.get("children", 0)
    dependents = profile.get("dependents", 0)
    concerns = profile.get("concerns") or []
    assets = profile.get("assets") or {}
    notes = (profile.get("notes") or "").strip()

    asset_lines = "\n".join(
        f"- {label}: {value}" for label, value in assets.items() if value and value != "Prefer not to say"
    ) or "- Not specified"

    concern_text = ", ".join(concerns) if concerns else "None selected"

    return f"""\
Please prepare a first-pass estate planning briefing for this profile.

### Profile
- Age: {profile.get("age", "n/a")}
- Marital status: {profile.get("marital_status", "n/a")}
- Jurisdiction / country of residence: {profile.get("jurisdiction", "n/a")}
- Children: {children}
- Other dependents: {dependents}
- Special family notes: {profile.get("family_notes") or "None"}
- Primary goals: {profile.get("goals") or "Not specified"}
- Main concerns: {concern_text}

### Approximate assets / situation
{asset_lines}

### Additional notes from user
{notes or "None"}

Respond following the required output structure.
"""
