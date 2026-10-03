"""Portable V5.2 tutorial helpers based on the production methodology."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


VALID_EVIDENCE_POLICIES = {"both", "both_required", "draft_primary", "answer_primary"}


def load_tutorial_taxonomy(path: str | Path) -> pd.DataFrame:
    taxonomy = pd.read_csv(path).fillna("")
    required = {"id", "major_category", "minor_category", "evidence_policy", "definition", "exclude"}
    missing = required - set(taxonomy.columns)
    if missing:
        raise ValueError(f"taxonomy missing columns: {sorted(missing)}")
    if taxonomy["id"].duplicated().any():
        raise ValueError("taxonomy IDs must be unique")
    if not set(taxonomy["evidence_policy"]).issubset(VALID_EVIDENCE_POLICIES):
        raise ValueError("unknown evidence policy")
    return taxonomy


def compact_taxonomy(taxonomy: pd.DataFrame) -> str:
    return "\n".join(
        f"{r.id}|{r.evidence_policy}|{r.minor_category}|{r.definition}|exclude:{r.exclude}"
        for r in taxonomy.itertuples()
    )


def validate_v52_output(result: dict[str, Any], taxonomy: pd.DataFrame) -> list[str]:
    errors: list[str] = []
    known = taxonomy.set_index("id").to_dict("index")
    hits = result.get("hits")
    quality = result.get("draft_quality")
    if not isinstance(hits, list) or len(hits) > 4:
        errors.append("hits must be a list with at most four entries")
        hits = []
    if quality not in {"ok", "poor"}:
        errors.append("draft_quality must be ok or poor")
    seen = set()
    for hit in hits:
        error_id = hit.get("id")
        if error_id not in known:
            errors.append(f"unknown id: {error_id}")
            continue
        if error_id in seen:
            errors.append(f"duplicate id: {error_id}")
        seen.add(error_id)
        if hit.get("confidence") not in {"strong", "fair"}:
            errors.append(f"invalid confidence: {error_id}")
        if quality == "poor" and known[error_id]["evidence_policy"] == "both_required":
            errors.append(f"poor draft cannot support both-required class {error_id}")
    if hits and not str(result.get("rationale", "")).strip():
        errors.append("rationale is required when hits are present")
    return errors


def parse_hits(value: str) -> list[dict[str, str]]:
    return json.loads(value)
