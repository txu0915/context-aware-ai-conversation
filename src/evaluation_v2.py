"""Utilities for the SMC 2026 T1-T9 / S1-S6 dialogue evaluation rubric."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


TEACHER_FIELDS = [f"T{i}_{name}" for i, name in enumerate([
    "corrective_anti_misleading", "guidance_encouragement", "calculation_precision",
    "emotional_support", "detail_appropriateness", "learning_evidence",
    "personalization", "safety_boundary_control", "concise_appropriate_detail",
], 1)]
STUDENT_FIELDS = [f"S{i}_{name}" for i, name in enumerate([
    "student_engagement_persistence", "student_learning_evidence",
    "student_affect_cooperation", "student_response_clarity",
    "student_high_quality_question", "student_focus_relevance",
], 1)]


class DialogueEvaluationV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    pair_id: str | None = None
    tutor_type: str | None = None
    dialogue_scene: str
    T1_corrective_anti_misleading: int = Field(ge=1, le=5)
    T2_guidance_encouragement: int = Field(ge=1, le=5)
    T3_calculation_precision: int = Field(ge=1, le=5)
    T4_emotional_support: int = Field(ge=1, le=5)
    T5_detail_appropriateness: int = Field(ge=1, le=5)
    T6_learning_evidence: int = Field(ge=1, le=5)
    T7_personalization: int = Field(ge=1, le=5)
    T8_safety_boundary_control: int = Field(ge=1, le=5)
    T9_concise_appropriate_detail: int = Field(ge=1, le=5)
    S1_student_engagement_persistence: int = Field(ge=1, le=5)
    S2_student_learning_evidence: int = Field(ge=1, le=5)
    S3_student_affect_cooperation: int = Field(ge=1, le=5)
    S4_student_response_clarity: int = Field(ge=1, le=5)
    S5_student_high_quality_question: int = Field(ge=1, le=5)
    S6_student_focus_relevance: int = Field(ge=1, le=5)
    rounds_to_resolution: int | None = Field(default=None, ge=1, le=12)
    false_completion: bool = False
    major_safety_issue: bool
    judge_summary: str


def load_production_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def render_evaluation_prompt(template: str, session: dict[str, Any]) -> str:
    messages = json.dumps(session["dialogue_messages"], ensure_ascii=False, indent=2)
    return (template
            .replace("{dialogue_scene}", session.get("dialogue_scene", "unknown"))
            .replace("{lo_name}", session.get("lo_name", "unknown"))
            .replace("{dialogue_messages}", messages))


def score_frame(records: list[dict[str, Any]]):
    """Return tidy teacher/student score tables for visualization."""
    import pandas as pd
    frame = pd.DataFrame(records)
    teacher = frame.melt(id_vars=["session_id", "dialogue_scene"], value_vars=TEACHER_FIELDS,
                         var_name="dimension", value_name="score")
    student = frame.melt(id_vars=["session_id", "dialogue_scene"], value_vars=STUDENT_FIELDS,
                         var_name="dimension", value_name="score")
    return teacher, student
