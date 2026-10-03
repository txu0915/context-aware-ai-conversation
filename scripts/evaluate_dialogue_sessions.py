"""Evaluate generated dialogue sessions with an independent judge model."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluation_v2 import DialogueEvaluationV2, render_evaluation_prompt  # noqa: E402
from live_demo import DEFAULT_MODELS, KEY_NAMES, call_provider  # noqa: E402


def _read_local_env(key_name: str) -> str | None:
    """Read one key without depending on shell-style dotenv parsing."""
    path = ROOT / ".env"
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == key_name:
            return value.strip().strip("'\"")
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("OpenAI", "Google"), default="Google")
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data/dialogue_sessions_agent_generated.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/dialogue_evaluations_agent_generated.json",
    )
    args = parser.parse_args()

    model = args.model or DEFAULT_MODELS[args.provider]
    key_name = KEY_NAMES[args.provider]
    api_key = os.getenv(key_name) or _read_local_env(key_name)
    if not api_key:
        raise RuntimeError(f"Set {key_name} in the environment or local .env file.")

    sessions = json.loads(args.input.read_text(encoding="utf-8"))
    template = (ROOT / "prompts/eval_prompt_en.md").read_text(encoding="utf-8")
    records: list[dict] = []

    for session in sessions:
        print(f"Evaluating {session['session_id']} ...", flush=True)
        result = call_provider(
            args.provider,
            str(api_key),
            model,
            render_evaluation_prompt(template, session),
        )
        # Identity and pairing fields come from the source record, never from
        # model output. The judge is responsible only for evaluation fields.
        result["session_id"] = session["session_id"]
        result["dialogue_scene"] = session["dialogue_scene"]
        result["pair_id"] = session["pair_id"]
        result["tutor_type"] = session["tutor_type"]
        result.setdefault("false_completion", False)
        record = DialogueEvaluationV2.model_validate(result).model_dump()
        records.append(record)
        args.output.write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"Wrote {len(records)} evaluations to {args.output}")


if __name__ == "__main__":
    main()
