"""
Estate Planning Assistant
A simple LLM-powered Streamlit app that turns a family/asset profile into
a first-pass estate planning briefing.

Educational use only — not legal or financial advice.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from estate_assistant.llm import PROVIDERS, LLMConfig, generate_report

load_dotenv()

st.set_page_config(
    page_title="Estate Planning Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.5rem; max-width: 1100px; }
      .hero {
        background: linear-gradient(135deg, #0f2744 0%, #1a4a6e 55%, #2d6a8f 100%);
        color: #f5f8fc;
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
      }
      .hero h1 { margin: 0 0 0.35rem 0; font-size: 1.75rem; color: #fff; }
      .hero p { margin: 0; opacity: 0.92; font-size: 1.02rem; }
      .disclaimer {
        background: #fff8e6;
        border-left: 4px solid #e6a817;
        padding: 0.85rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0 1.2rem 0;
        color: #3d3200;
        font-size: 0.95rem;
      }
      .stButton > button {
        background: #1a4a6e;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
      }
      .stButton > button:hover { background: #0f2744; color: white; border: none; }
      div[data-testid="stMetric"] {
        background: #f4f7fb;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def sidebar_config() -> LLMConfig:
    st.sidebar.header("⚙️ Settings")
    provider = st.sidebar.selectbox("LLM provider", list(PROVIDERS.keys()), index=0)
    models = PROVIDERS[provider]["models"]
    model = st.sidebar.selectbox("Model", models, index=0)

    env_key_name = PROVIDERS[provider]["env_key"]
    env_present = bool(os.getenv(env_key_name))
    if env_present:
        st.sidebar.success(f"`{env_key_name}` loaded from environment")
    else:
        st.sidebar.info(f"Optional: set `{env_key_name}` in `.env`")

    api_key = st.sidebar.text_input(
        "API key (optional if set in .env)",
        type="password",
        placeholder=f"{env_key_name}",
        help="Keys stay in this session only and are never written to disk.",
    )

    demo_mode = st.sidebar.toggle(
        "Demo mode (no API call)",
        value=not env_present and not api_key,
        help="Generates a realistic sample report without calling an LLM.",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Built for portfolio / educational use. "
        "Default provider: **xAI Grok** via OpenAI-compatible API."
    )
    return LLMConfig(provider=provider, model=model, api_key=api_key or None, demo_mode=demo_mode)


def collect_profile() -> dict:
    st.subheader("1. Your situation")
    c1, c2, c3 = st.columns(3)
    with c1:
        age = st.number_input("Age", min_value=18, max_value=110, value=38, step=1)
        marital_status = st.selectbox(
            "Marital status",
            ["Single", "Married", "Domestic partnership", "Divorced", "Widowed", "Other"],
        )
    with c2:
        jurisdiction = st.selectbox(
            "Jurisdiction / residence",
            [
                "United States (general)",
                "California, USA",
                "New York, USA",
                "Texas, USA",
                "Florida, USA",
                "Germany",
                "Switzerland",
                "United Kingdom",
                "Other / multi-jurisdiction",
            ],
        )
        children = st.number_input("Number of children", min_value=0, max_value=20, value=1, step=1)
    with c3:
        dependents = st.number_input("Other dependents", min_value=0, max_value=20, value=0, step=1)
        goals = st.selectbox(
            "Primary goal",
            [
                "Protect family / provide for loved ones",
                "Avoid probate / simplify transfer",
                "Minimize taxes (educational overview)",
                "Plan for incapacity",
                "Charitable giving",
                "Business succession",
                "General first overview",
            ],
        )

    family_notes = st.text_input(
        "Family notes (optional)",
        placeholder="e.g. blended family, special-needs child, aging parents…",
    )

    st.subheader("2. Assets (approximate ranges)")
    a1, a2, a3 = st.columns(3)
    ranges = [
        "Prefer not to say",
        "None / N/A",
        "Under $100k",
        "$100k – $500k",
        "$500k – $1M",
        "$1M – $5M",
        "Over $5M",
    ]
    with a1:
        home = st.selectbox("Primary residence equity", ranges, index=3)
        investments = st.selectbox("Investments / brokerage", ranges, index=2)
    with a2:
        retirement = st.selectbox("Retirement accounts", ranges, index=3)
        business = st.selectbox("Business ownership", ranges, index=1)
    with a3:
        life_insurance = st.selectbox("Life insurance (face value)", ranges, index=2)
        other = st.selectbox("Other significant assets", ranges, index=0)

    st.subheader("3. Concerns & free notes")
    concerns = st.multiselect(
        "What are you most concerned about?",
        [
            "No will / outdated documents",
            "Guardianship for minor children",
            "Blended family / second marriage",
            "Probate cost & delay",
            "Estate / inheritance taxes",
            "Incapacity (who decides if I can't)",
            "Business succession",
            "Charitable legacy",
            "Digital assets / crypto",
            "International / multi-state issues",
        ],
        default=["No will / outdated documents", "Guardianship for minor children"],
    )
    notes = st.text_area(
        "Anything else the assistant should know?",
        placeholder="Existing documents, specific people you want to protect, recent life events…",
        height=100,
    )

    return {
        "age": age,
        "marital_status": marital_status,
        "jurisdiction": jurisdiction,
        "children": int(children),
        "dependents": int(dependents),
        "family_notes": family_notes,
        "goals": goals,
        "assets": {
            "Primary residence equity": home,
            "Investments / brokerage": investments,
            "Retirement accounts": retirement,
            "Business ownership": business,
            "Life insurance": life_insurance,
            "Other significant assets": other,
        },
        "concerns": concerns,
        "notes": notes,
    }


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
          <h1>🏛️ Estate Planning Assistant</h1>
          <p>Structured profile in → clear first-pass briefing out.
          Built with prompt engineering + an LLM (Grok / OpenAI). Educational only.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="disclaimer">
          <strong>Disclaimer:</strong> This tool is for education and portfolio demonstration only.
          It does <em>not</em> provide legal, tax, or financial advice. Always consult a licensed
          professional in your jurisdiction before acting.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    config = sidebar_config()
    render_hero()

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        profile = collect_profile()
        generate = st.button("✨ Generate briefing", type="primary", use_container_width=True)

    with right:
        st.subheader("Briefing")
        if generate:
            with st.spinner("Preparing your first-pass estate planning briefing…"):
                try:
                    report = generate_report(profile, config)
                    st.session_state["report"] = report
                    st.session_state["report_ts"] = datetime.now().isoformat(timespec="seconds")
                    st.session_state["report_profile"] = profile
                except Exception as exc:  # noqa: BLE001 — show clean UX error
                    st.error(str(exc))
                    st.stop()

        report = st.session_state.get("report")
        if report:
            mode = "Demo" if config.demo_mode else f"{config.provider} · {config.model}"
            m1, m2 = st.columns(2)
            m1.metric("Mode", mode)
            m2.metric("Generated", st.session_state.get("report_ts", "—")[:16].replace("T", " "))

            st.markdown(report)

            fname = f"estate-briefing-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
            st.download_button(
                "⬇️ Download Markdown",
                data=report,
                file_name=fname,
                mime="text/markdown",
                use_container_width=True,
            )
        else:
            st.info(
                "Fill in your situation on the left, then click **Generate briefing**. "
                "Enable **Demo mode** in the sidebar to try without an API key."
            )
            st.markdown(
                """
                **What you'll get**
                - Situation summary in plain language  
                - Ranked priority topics  
                - First educational recommendations  
                - Documents to discuss with a professional  
                - Concrete questions for an attorney / advisor  
                """
            )

    st.markdown("---")
    st.caption(
        "Estate Planning Assistant · portfolio project · "
        f"source: `{Path(__file__).parent.name}/` · not legal advice"
    )


if __name__ == "__main__":
    main()
