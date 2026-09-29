"""Rule-based safety and pedagogical stopping controls for tutorial demos.

The rules are intentionally transparent: participants can inspect why a turn is
continued, redirected, escalated, or stopped. Production systems should combine
these checks with a trained classifier and human escalation policy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import re
from typing import Any

from pydantic import BaseModel, Field


class Action(str, Enum):
    CONTINUE = "continue"
    REDIRECT = "redirect"
    SUPPORT = "support"
    VERIFY = "verify_learning"
    STOP = "stop"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class StopDecision:
    action: Action
    reason: str
    response: str
    terminal: bool = False
    severity: int = 0

    def model_dump(self) -> dict:
        return asdict(self)


PATTERNS = {
    "unsafe": re.compile(r"\b(kill myself|suicide|self[- ]harm|hurt myself|do not want to live)\b", re.I),
    "abuse": re.compile(r"\b(fuck|idiot|stupid|shut up|get lost)\b", re.I),
    "answer_demand": re.compile(r"\b(just (give|tell) me the answer|only want the answer)\b", re.I),
    "emotion": re.compile(r"\b(I('m| am) (sad|scared|frustrated|anxious)|I can never do this)\b|😭|😢", re.I),
    "off_topic": re.compile(r"\b(change the subject|talk about games|talk about dating)\b", re.I),
    "claimed_mastery": re.compile(r"\b(I (get|understand) it|I know how now|got it)\b", re.I),
}


class LLMGuardrailDecision(BaseModel):
    """Structured semantic classification returned by a guardrail LLM."""

    action: Action
    reason: str
    confidence: float = Field(ge=0, le=1)
    response: str
    terminal: bool = False
    severity: int = Field(default=0, ge=0, le=3)


GUARDRAIL_LLM_PROMPT = """You are a K-12 tutoring guardrail classifier.
Classify the latest student turn using exactly one action:
continue, verify_learning, support, redirect, stop, or escalate.

Priority order:
1. escalate: credible immediate safety risk or self-harm signal;
2. stop: abuse, threats, or a boundary violation that should end the session;
3. support: distress that needs a brief empathetic response before instruction;
4. verify_learning: an unverified claim of mastery;
5. redirect: answer-seeking, off-topic behavior, repeated non-progress, or a
   learning request beyond the configured grade-level objective;
6. continue: relevant and safe learning dialogue.

Return JSON only with action, reason, confidence, response, terminal, severity.
Do not diagnose the student. Keep the response brief, neutral, and age-appropriate.
Distinguish an off-topic diversion from an academically relevant but out-of-scope
question. For an out-of-scope question, preserve curiosity, state the boundary,
bridge to a prerequisite in the current objective, and suggest teacher support
for the advanced topic when appropriate.
"""


def decide_next_action(
    message: str,
    *,
    round_index: int,
    max_rounds: int = 10,
    repeated_non_progress: int = 0,
    out_of_scope: bool = False,
) -> StopDecision:
    """Return a deterministic control decision for one student turn."""
    text = (message or "").strip()
    if PATTERNS["unsafe"].search(text):
        return StopDecision(
            Action.ESCALATE,
            "potential_self_harm",
            "Thank you for telling me. Your safety matters most. Please contact a trusted adult or local emergency support now; we will pause the math problem.",
            True,
            3,
        )
    if PATTERNS["abuse"].search(text):
        return StopDecision(
            Action.STOP,
            "abusive_language",
            "I want to help, but we need to keep the conversation respectful. We will pause here and can continue when you are ready.",
            True,
            2,
        )
    if round_index >= max_rounds:
        return StopDecision(
            Action.STOP,
            "round_limit",
            "Let us pause here. I will record the current blocker so the next session can continue from this step instead of pretending it is resolved.",
            True,
            1,
        )
    if repeated_non_progress >= 2:
        return StopDecision(
            Action.REDIRECT,
            "repeated_non_progress",
            "The previous approach did not help. Let us try a smaller question: should this step use addition or subtraction?",
            False,
            1,
        )
    if out_of_scope:
        return StopDecision(
            Action.REDIRECT,
            "out_of_scope_learning_request",
            "That is an interesting question, but it is beyond our current learning objective. Let us connect it to what you know now, and you can explore the advanced topic with your teacher afterward.",
            False,
            1,
        )
    if PATTERNS["emotion"].search(text):
        return StopDecision(
            Action.SUPPORT,
            "student_distress",
            "Feeling stuck can be frustrating. We can slow down and look at just one small step.",
        )
    if PATTERNS["answer_demand"].search(text):
        return StopDecision(
            Action.REDIRECT,
            "answer_seeking",
            "I will not give the final answer yet, but I can make the task smaller. Which quantity should we calculate first?",
        )
    if PATTERNS["off_topic"].search(text):
        return StopDecision(
            Action.REDIRECT,
            "off_topic",
            "Let us finish this step first. Which operation appears in the expression?",
        )
    if PATTERNS["claimed_mastery"].search(text):
        return StopDecision(
            Action.VERIFY,
            "unverified_mastery",
            "Great. Without repeating the answer, explain in your own words why that step works.",
        )
    return StopDecision(Action.CONTINUE, "on_task", "Continue with one focused tutoring step based on the student's latest response.")


_PRIORITY = {
    Action.CONTINUE: 0,
    Action.VERIFY: 1,
    Action.REDIRECT: 2,
    Action.SUPPORT: 3,
    Action.STOP: 4,
    Action.ESCALATE: 5,
}


def combine_guardrail_decisions(
    rule_decision: StopDecision,
    llm_decision: LLMGuardrailDecision | dict[str, Any] | None,
    *,
    min_llm_confidence: float = 0.70,
) -> StopDecision:
    """Conservatively arbitrate deterministic rules and semantic LLM judgment.

    High-severity rule matches are hard overrides. Otherwise, a confident LLM
    decision can raise the intervention level, but cannot downgrade a stricter
    rule decision. This makes the LLM useful for paraphrases without allowing it
    to bypass deterministic safety boundaries.
    """
    if rule_decision.severity >= 2:
        return rule_decision
    if llm_decision is None:
        return rule_decision
    if isinstance(llm_decision, dict):
        llm_decision = LLMGuardrailDecision.model_validate(llm_decision)
    if llm_decision.confidence < min_llm_confidence:
        return rule_decision
    if _PRIORITY[llm_decision.action] <= _PRIORITY[rule_decision.action]:
        return rule_decision
    return StopDecision(
        llm_decision.action,
        f"llm:{llm_decision.reason}",
        llm_decision.response,
        llm_decision.terminal,
        llm_decision.severity,
    )
