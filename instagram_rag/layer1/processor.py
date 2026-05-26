"""Calls the OpenAI model per row and saves structured JSON output."""

import json
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from layer1.config import Config
from layer1.prompts import FULL_SYSTEM_PROMPT

DELAY_SECONDS: float = 0.3


def process_rows(rows: list[dict[str, Any]], config: Config) -> tuple[int, int]:
    """Process each CSV row through the model and save output JSON files.

    Args:
        rows: List of clean row dicts from loader.py.
        config: Loaded Config instance.

    Returns:
        Tuple of (success_count, error_count).
    """
    client = OpenAI(api_key=config.openai_api_key)
    total = len(rows)
    all_results: list[dict[str, Any]] = []
    success_count = 0
    error_count = 0

    for i, row in enumerate(rows, start=1):
        post_id = str(row.get("post_id", f"unknown_{i}"))
        print(f"Processing row {i}/{total} — post_id: {post_id}", end=" ", flush=True)

        try:
            result = _call_model(client, config, row, post_id)
            _save_json(config.output_dir / f"{post_id}.json", result)
            all_results.append(result)
            success_count += 1
            print("✓")
        except Exception as exc:
            error_count += 1
            error_payload = {
                "post_id": post_id,
                "error": str(exc),
                "raw_row": row,
            }
            _save_json(config.output_dir / f"{post_id}_error.json", error_payload)
            print(f"✗  ERROR: {exc}")

        if i < total:
            time.sleep(DELAY_SECONDS)

    _save_json(config.output_dir / "all_results.json", all_results)
    return success_count, error_count


def _call_model(
    client: OpenAI,
    config: Config,
    row: dict[str, Any],
    post_id: str,
) -> dict[str, Any]:
    """Send one row to the model and return the parsed JSON response."""
    user_message = json.dumps(row, default=str)

    response = client.chat.completions.create(
        model=config.openai_model,
        messages=[
            {"role": "system", "content": FULL_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    raw = response.choices[0].message.content
    parsed: dict[str, Any] = json.loads(raw)
    return parsed


def _save_json(path: Path, data: Any) -> None:
    """Write data to a JSON file at the given path."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
