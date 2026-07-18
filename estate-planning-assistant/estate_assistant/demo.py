"""Offline demo report so the app is usable without an API key (screenshots / demos)."""


def demo_report(profile: dict) -> str:
    age = profile.get("age", "—")
    status = profile.get("marital_status", "—")
    jurisdiction = profile.get("jurisdiction", "—")
    children = profile.get("children", 0)
    concerns = profile.get("concerns") or []
    concern_text = ", ".join(concerns) if concerns else "general planning"

    return f"""\
## Situation Summary
You are approximately **{age}** years old, **{status}**, and primarily focused on
estate planning under **{jurisdiction}** rules. You reported **{children}** child(ren)
and highlighted concerns around: **{concern_text}**.

This is a **demo report** generated without calling a live LLM. It shows the structure
and quality of output you can expect when an API key is configured.

## Priority Topics
1. **Core documents** — Will and/or trust aligned with your family structure
2. **Decision-makers** — Durable power of attorney and healthcare proxy
3. **Beneficiary designations** — Retirement accounts and life insurance often bypass the will
4. **Guardianship** — Naming guardians if minor children are involved
5. **Tax & probate basics** — High-level awareness for your jurisdiction (not personalized tax advice)

## First Recommendations
1. List your major assets, debts, and account types in one simple inventory.
2. Confirm who currently appears as beneficiary on retirement plans and life insurance.
3. Draft (or update) a simple will; if your situation is more complex, ask whether a revocable living trust makes sense.
4. Appoint a durable financial power of attorney and a healthcare decision-maker.
5. If you have minor children, name a guardian and a backup guardian.
6. Schedule a short consult with a licensed estate attorney in **{jurisdiction}**.

## Documents & Instruments to Discuss
- Last will and testament
- Revocable living trust (if appropriate)
- Durable power of attorney (financial)
- Healthcare proxy / advance directive
- Beneficiary designation forms (401(k), IRA, life insurance)
- Guardianship nominations (if applicable)

## Questions for a Professional
1. Given my marital status and family setup, do I need a will only or also a trust?
2. How should we handle guardianship and backup decision-makers?
3. Are my beneficiary designations currently aligned with my will/trust?
4. What probate process applies in my jurisdiction, and can we simplify it?
5. Are there any tax-efficient gifts or transfers I should understand *before* acting?
6. How often should we review this plan (life events, moves, new children, divorce, etc.)?
7. Who should serve as executor / trustee, and what are the practical responsibilities?

## Missing Information
- Exact asset values and ownership titles (joint vs. individual)
- Existing documents (will, trust, POA)
- Citizenship / multi-jurisdiction issues
- Business ownership details
- Special-needs or blended-family arrangements

## Disclaimer
**This is educational content only — not legal, tax, or financial advice.** Estate laws and
tax rules vary by jurisdiction and change over time. Consult a licensed attorney and/or
qualified advisor before making decisions. Demo mode does not call a live model.
"""
