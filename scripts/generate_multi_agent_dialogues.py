"""Generate paired tutorial dialogues with separate tutor and student agents.

This script performs a real turn-by-turn simulation. Each teacher turn and each
student turn is produced by a separate model call with a role-specific prompt.
The student profile is held constant within each aware/unaware pair; only the
tutor's access to structured error context changes.

Example:
    python scripts/generate_multi_agent_dialogues.py \
        --provider Google --model gemini-3.8-flash
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from live_demo import DEFAULT_MODELS, KEY_NAMES, call_provider  # noqa: E402


SESSION_SPECS = (
    {"pair_id": "short", "case_id": "draft_case", "rounds": 4},
    {"pair_id": "medium", "case_id": "answer_case", "rounds": 8},
    {"pair_id": "long", "case_id": "both_case", "rounds": 12},
)

STUDENT_PERSONA = """You are a K–12 student, not a tutor or evaluator.
Use concise, age-appropriate language. Begin with the supplied misconception.
Answer only what the tutor's latest question reasonably elicits. Do not become
correct merely because the hidden answer is visible in your private state.
Revise your thinking only after sufficient guidance. If you understand, show it
in your own words instead of simply saying 'I understand'."""

TUTOR_PERSONA = """You are a patient K–12 Socratic tutor.
Ask exactly one focused question per turn. Do not reveal hidden labels or give
the complete solution. Adapt to the student's latest response, preserve useful
student reasoning, and verify learning through an independent explanation."""


def _load_key(provider: str) -> str:
    key_name = KEY_NAMES[provider]
    key = os.getenv(key_name) or _read_local_env(key_name)
    if not key:
        raise RuntimeError(f"Set {key_name} in the environment or local .env file.")
    return str(key)


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


def _agent_turn(
    *, provider: str, api_key: str, model: str, prompt: str, field: str
) -> str:
    result = call_provider(provider, api_key, model, prompt)
    value = str(result[field]).strip()
    if not value:
        raise ValueError(f"Agent returned an empty {field}.")
    return value


def _tutor_prompt(case: dict[str, Any], tutor_type: str, history: list[dict[str, Any]]) -> str:
    public_case = {
        "problem": case["question_content"],
        "correct_answer": case["correct_answer"],
        "student_answer": case["student_answer"],
        "learning_objective": case["knowledge_name"],
    }
    context: Any = "No structured diagnosis is available; infer cautiously from dialogue evidence."
    if tutor_type == "context_aware":
        context = {
            "error_id": case["identified_error_id"],
            "major_category": case["identified_major_category"],
            "minor_category": case["identified_minor_category"],
            "rationale": case["rationale"],
            "evidence_policy": case["evidence_policy"],
            "draft_quality": case["draft_quality"],
        }
    return f"""{TUTOR_PERSONA}

Return JSON only: {{"teacher_response":"..."}}.

PUBLIC CASE
{json.dumps(public_case, ensure_ascii=False, indent=2)}

PRIVATE TUTOR CONTEXT
{json.dumps(context, ensure_ascii=False, indent=2)}

VISIBLE DIALOGUE HISTORY
{json.dumps(history, ensure_ascii=False, indent=2)}

Produce only the next teacher turn."""


def _student_prompt(case: dict[str, Any], history: list[dict[str, Any]]) -> str:
    private_state = {
        "original_answer": case["student_answer"],
        "misconception": case["rationale"],
        "draft_evidence": case["draft_transcription"],
        "response_style": "brief, cooperative, initially uncertain",
    }
    return f"""{STUDENT_PERSONA}

Return JSON only: {{"student_response":"..."}}.

PRIVATE STUDENT STATE
{json.dumps(private_state, ensure_ascii=False, indent=2)}

VISIBLE DIALOGUE HISTORY
{json.dumps(history, ensure_ascii=False, indent=2)}

Produce only the next student turn."""


def simulate_session(
    *,
    case: dict[str, Any],
    pair_id: str,
    tutor_type: str,
    rounds: int,
    provider: str,
    model: str,
    api_key: str,
) -> dict[str, Any]:
    history: list[dict[str, Any]] = []
    for round_number in range(1, rounds + 1):
        teacher_text = _agent_turn(
            provider=provider,
            api_key=api_key,
            model=model,
            prompt=_tutor_prompt(case, tutor_type, history),
            field="teacher_response",
        )
        history.append({"round": round_number, "speaker": "teacher", "text": teacher_text})
        student_text = _agent_turn(
            provider=provider,
            api_key=api_key,
            model=model,
            prompt=_student_prompt(case, history),
            field="student_response",
        )
        history.append({"round": round_number, "speaker": "student", "text": student_text})

    suffix = "aware" if tutor_type == "context_aware" else "unaware"
    return {
        "session_id": f"{pair_id}_{suffix}",
        "pair_id": pair_id,
        "source_case_id": case["case_id"],
        "length": pair_id,
        "tutor_type": tutor_type,
        "dialogue_scene": "error_aware_socratic",
        "lo_name": case["knowledge_name"],
        "generation": {
            "method": "turn_by_turn_multi_agent_simulation",
            "provider": provider,
            "model": model,
            "student_agent": "student_persona_v1",
            "tutor_agent": f"{tutor_type}_socratic_tutor_v1",
            "student_profile_held_constant_within_pair": True,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "dialogue_messages": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("OpenAI", "Google"), default="Google")
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/dialogue_sessions_agent_generated.json",
    )
    args = parser.parse_args()

    model = args.model or DEFAULT_MODELS[args.provider]
    api_key = _load_key(args.provider)
    cases = pd.read_csv(ROOT / "data/error_cases_tutorial.csv").fillna("")
    cases_by_id = {row["case_id"]: row.to_dict() for _, row in cases.iterrows()}
    sessions: list[dict[str, Any]] = []

    for spec in SESSION_SPECS:
        case = cases_by_id[spec["case_id"]]
        for tutor_type in ("context_aware", "non_context_aware"):
            print(f"Generating {spec['pair_id']} / {tutor_type} ...", flush=True)
            sessions.append(
                simulate_session(
                    case=case,
                    pair_id=spec["pair_id"],
                    tutor_type=tutor_type,
                    rounds=spec["rounds"],
                    provider=args.provider,
                    model=model,
                    api_key=api_key,
                )
            )
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(sessions, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    print(f"Wrote {len(sessions)} sessions to {args.output}")


if __name__ == "__main__":
    main()
