"""LLM client for the Estate Planning Assistant (xAI Grok by default)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from .demo import demo_report
from .prompts import SYSTEM_PROMPT, build_user_prompt


PROVIDERS = {
    "xAI (Grok)": {
        "base_url": "https://api.x.ai/v1",
        "env_key": "XAI_API_KEY",
        "default_model": "grok-4.5",
        "models": ["grok-4.5", "grok-4.3"],
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o"],
    },
}


@dataclass
class LLMConfig:
    provider: str = "xAI (Grok)"
    model: str = "grok-4.5"
    api_key: Optional[str] = None
    demo_mode: bool = False


def resolve_api_key(provider: str, explicit_key: Optional[str] = None) -> Optional[str]:
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()
    env_name = PROVIDERS[provider]["env_key"]
    return os.getenv(env_name) or None


def generate_report(profile: dict, config: LLMConfig) -> str:
    """Generate an estate-planning briefing from a structured profile."""
    if config.demo_mode:
        return demo_report(profile)

    api_key = resolve_api_key(config.provider, config.api_key)
    if not api_key:
        raise ValueError(
            f"No API key found. Set {PROVIDERS[config.provider]['env_key']} "
            "in your environment / .env, enter a key in the sidebar, or enable Demo mode."
        )

    provider = PROVIDERS[config.provider]
    client = OpenAI(api_key=api_key, base_url=provider["base_url"])

    # Prefer Chat Completions for broad OpenAI-compatible provider support
    # (xAI supports both /responses and /chat/completions).
    response = client.chat.completions.create(
        model=config.model or provider["default_model"],
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(profile)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The model returned an empty response.")
    return content.strip()
