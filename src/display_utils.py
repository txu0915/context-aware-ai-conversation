"""Projection-friendly HTML and plotting helpers for the tutorial notebooks."""

from __future__ import annotations

import html
import re
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, Image, SVG, display


NOTEBOOK_CSS = """
<style>
.jp-OutputArea-output, .output_subarea {max-width: 100% !important;}
.jp-RenderedText pre, .jp-OutputArea pre, .output_subarea pre {white-space:pre-wrap !important;
  overflow-wrap:anywhere !important; max-width:100% !important; overflow-x:hidden !important;}
table.dataframe {width: 100% !important; table-layout: fixed; border-collapse: collapse;}
table.dataframe th, table.dataframe td {white-space: normal !important; overflow-wrap: anywhere;
  vertical-align: top !important; padding: 9px 11px !important; line-height: 1.35;}
.tutorial-card {border:1px solid #d9e2f2; border-left:6px solid #315b96; border-radius:8px;
  padding:14px 18px; margin:10px 0 18px; background:#f8fbff; line-height:1.5; overflow-wrap:anywhere;}
.tutorial-grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px;}
.speaker {font-weight:700; min-width:76px; display:inline-block;}
.teacher {color:#174a8b;} .student {color:#8a3b12;} .system {color:#6a3d9a;}
.turn {padding:9px 12px; margin:6px 0; border-radius:7px; background:#f6f7f9;}
.context-aware {border-left:5px solid #173f73;} .context-unaware {border-left:5px solid #9ec3e6;}
.flag {background:#ffe6e6; color:#9a1b1b; font-weight:700; padding:1px 4px; border-radius:3px;}
.strategy {background:#e4f3e8; color:#176b34; font-weight:700; padding:1px 4px; border-radius:3px;}
.keyword {background:#fff1a8; color:#533f00; font-weight:700; padding:1px 4px; border-radius:3px;}
.dict-viewer {width:100%; max-width:100%; border:1px solid #d9e2f2; border-radius:8px;
  margin:10px 0 18px; background:#fbfdff; overflow:hidden;}
.dict-viewer summary {cursor:pointer; padding:12px 16px; font-weight:700; color:#173f73;
  background:#eef5fc; user-select:none;}
.dict-row {display:grid; grid-template-columns:minmax(150px,22%) minmax(0,78%); gap:12px;
  padding:9px 14px; border-top:1px solid #e7edf4; align-items:start;}
.dict-key {font-weight:700; color:#34495e; overflow-wrap:anywhere;}
.dict-value {white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; min-width:0;}
@media (max-width:800px) {.dict-row {grid-template-columns:1fr; gap:3px;}}
pre.prompt {white-space:pre-wrap; overflow-wrap:anywhere; background:#101827; color:#edf3ff;
  padding:16px; border-radius:9px; max-height:520px; overflow-y:auto; line-height:1.45;}
</style>
"""


def setup_notebook_display() -> None:
    # Pandas truncates long strings before CSS is applied unless this is disabled.
    # These options affect representation only; they do not change the data.
    try:
        import pandas as pd
        pd.set_option("display.max_colwidth", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.expand_frame_repr", False)
    except ImportError:
        pass
    display(HTML(NOTEBOOK_CSS))


def field_cards(record: dict, fields: Iterable[tuple[str, str]]) -> None:
    cards = []
    for key, label in fields:
        value = record.get(key, "—")
        cards.append(f"<div class='tutorial-card'><b>{html.escape(label)}</b><br>{html.escape(str(value))}</div>")
    display(HTML("<div class='tutorial-grid'>" + "".join(cards) + "</div>"))


def draft_viewer(record: dict, root, *, width: int = 720) -> None:
    """Display a remote draft URL, with a local SVG fallback for simulations."""
    url = str(record.get("draft_image_url") or "").strip()
    local = str(record.get("draft_local_path") or "").strip()
    if url:
        display(HTML(
            f"<div class='tutorial-card'><b>Draft image URL</b><br>"
            f"<a href='{html.escape(url)}' target='_blank'>{html.escape(url)}</a><br><br>"
            f"<img src='{html.escape(url)}' style='max-width:{width}px;width:100%;height:auto;border:1px solid #ccd6e2;border-radius:6px'></div>"
        ))
        return
    if local:
        path = root / local
        display(HTML(f"<div class='tutorial-card'><b>Local tutorial draft</b><br>{html.escape(str(path))}</div>"))
        if path.suffix.lower() == ".svg":
            display(SVG(filename=str(path)))
        else:
            display(Image(filename=str(path), width=width))
        return
    display(HTML("<div class='tutorial-card'><b>No draft image is available.</b></div>"))


def dictionary_viewer(
    record: dict,
    *,
    title: str = "Case dictionary",
    collapsed: bool = False,
    preview_keys: Iterable[str] = (),
) -> None:
    """Render a wrapping dictionary with an optional compact preview and disclosure."""
    preview_keys = list(preview_keys)
    preview = {key: record.get(key, "") for key in preview_keys if key in record}
    remaining = {key: value for key, value in record.items() if key not in preview}

    def rows(values: dict) -> str:
        return "".join(
            f"<div class='dict-row'><div class='dict-key'>{html.escape(str(key))}</div>"
            f"<div class='dict-value'>{html.escape(str(value))}</div></div>"
            for key, value in values.items()
        )

    preview_html = rows(preview)
    open_attr = "" if collapsed else " open"
    detail_html = (
        f"<details{open_attr}><summary>{html.escape(title)} — click to "
        f"{'expand' if collapsed else 'collapse'}</summary>{rows(remaining)}</details>"
    )
    display(HTML(f"<div class='dict-viewer'>{preview_html}{detail_html}</div>"))


def _highlight(text: str, keywords: list[str] | None, css_class: str = "keyword") -> str:
    escaped = html.escape(text)
    for word in sorted(keywords or [], key=len, reverse=True):
        escaped = re.sub(re.escape(html.escape(word)), f"<span class='{css_class}'>\\g<0></span>", escaped, flags=re.I)
    return escaped


def dialogue_html(session: dict, *, title: str | None = None) -> HTML:
    aware = "context-aware" if session.get("tutor_type") == "context_aware" else "context-unaware"
    rows = [f"<h3>{html.escape(title or session['session_id'])}</h3><div class='{aware} tutorial-card'>"]
    for message in session["dialogue_messages"]:
        speaker = message["speaker"]
        label = speaker.title()
        css = "teacher" if speaker == "teacher" else "student"
        text = _highlight(message["text"], message.get("highlights"))
        rows.append(f"<div class='turn'><span class='speaker {css}'>R{message['round']} {label}</span>{text}</div>")
    rows.append("</div>")
    return HTML("".join(rows))


def paired_dialogue_html(aware: dict, unaware: dict, *, title: str) -> HTML:
    left = dialogue_html(aware, title="Context-aware").data
    right = dialogue_html(unaware, title="Context-unaware").data
    return HTML(f"<h2>{html.escape(title)}</h2><div class='tutorial-grid'>{left}{right}</div>")


def flagged_dialogue_html(case: dict) -> HTML:
    rows = [f"<h3>{html.escape(case['scenario'])}</h3><div class='tutorial-card'>"]
    for message in case["messages"]:
        css = "system" if message["speaker"] not in {"teacher", "student", "tutor"} else (
            "teacher" if message["speaker"] in {"teacher", "tutor"} else "student")
        text = html.escape(message["text"])
        for word in sorted(message.get("flags", []), key=len, reverse=True):
            text = re.sub(re.escape(html.escape(word)), f"<span class='flag'>\\g<0></span>", text, flags=re.I)
        for word in sorted(message.get("strategies", []), key=len, reverse=True):
            text = re.sub(re.escape(html.escape(word)), f"<span class='strategy'>\\g<0></span>", text, flags=re.I)
        rows.append(f"<div class='turn'><span class='speaker {css}'>{html.escape(message['speaker'].title())}</span>{text}</div>")
    rows.append(f"<b>Recommended outcome:</b> {html.escape(case['expected_outcome'])}</div>")
    return HTML("".join(rows))


def paired_radar(aware_scores: list[float], unaware_scores: list[float], labels: list[str], title: str):
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    aware = aware_scores + aware_scores[:1]
    unaware = unaware_scores + unaware_scores[:1]
    fig, ax = plt.subplots(figsize=(8, 7), subplot_kw={"polar": True})
    ax.plot(angles, unaware, color="#8fc1e3", linewidth=2, label="Context-unaware")
    ax.fill(angles, unaware, color="#b9d9ef", alpha=.42)
    ax.plot(angles, aware, color="#123c69", linewidth=2.6, label="Context-aware")
    ax.fill(angles, aware, color="#123c69", alpha=.30)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 5); ax.set_yticks([1, 2, 3, 4, 5]); ax.set_yticklabels(["1", "2", "3", "4", "5"])
    ax.set_title(title, pad=25, fontsize=14, fontweight="bold"); ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.12))
    return fig, ax


def prompt_block(text: str, highlights: list[str] | None = None) -> None:
    rendered = _highlight(text, highlights)
    display(HTML(f"<pre class='prompt'>{rendered}</pre>"))
