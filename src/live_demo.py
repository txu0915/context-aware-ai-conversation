"""Optional API-powered cells for Notebooks 01–03.

Nothing in this module is imported by the deterministic tutorial path. The
notebooks import it only in their final optional cell. Provider SDKs are loaded
inside request functions, so missing credentials never affect earlier cells.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_MODELS = {
    "OpenAI": "gpt-6-astra",
    "Google": "gemini-3.8-flash",
}
KEY_NAMES = {"OpenAI": "OPENAI_API_KEY", "Google": "GEMINI_API_KEY"}


def _save_key(root: Path, provider: str, api_key: str) -> Path:
    """Update one provider key in the local, git-ignored .env file."""
    key_name = KEY_NAMES[provider]
    env_path = root / ".env"
    existing = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    updated: list[str] = []
    replaced = False
    for line in existing:
        if line.strip().startswith(f"{key_name}="):
            updated.append(f"{key_name}={api_key}")
            replaced = True
        else:
            updated.append(line)
    if not replaced:
        updated.append(f"{key_name}={api_key}")
    env_path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")
    os.environ[key_name] = api_key
    return env_path


def _load_saved_key(root: Path, provider: str) -> str:
    """Load one provider key from the local .env without shell parsing."""
    env_path = root / ".env"
    if not env_path.exists():
        return ""
    key_name = KEY_NAMES[provider]
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == key_name:
            return value.strip().strip("'\"")
    return ""


def _resolve_key(root: Path, provider: str, entered_key: str) -> str:
    """Prefer a pasted key; otherwise reuse the provider key in local .env."""
    return entered_key.strip() or os.getenv(KEY_NAMES[provider], "") or _load_saved_key(root, provider)


def _extract_json(text: str) -> Any:
    value = text.strip()
    if value.startswith("```"):
        value = value.replace("```json", "", 1).replace("```", "").strip()
    return json.loads(value)


def _openai_text(api_key: str, model: str, prompt: str, image_url: str = "") -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the optional dependency with: pip install openai") from exc
    client = OpenAI(api_key=api_key)
    if image_url:
        content = [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": image_url},
        ]
        response = client.responses.create(model=model, input=[{"role": "user", "content": content}])
    else:
        response = client.responses.create(model=model, input=prompt)
    return response.output_text


def _google_text(api_key: str, model: str, prompt: str, image_url: str = "") -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError("Install the optional dependency with: pip install google-genai") from exc
    client = genai.Client(api_key=api_key)
    contents: list[Any] = [prompt]
    if image_url:
        import requests
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()
        mime_type = response.headers.get("Content-Type", "image/png").split(";")[0]
        contents.append(types.Part.from_bytes(data=response.content, mime_type=mime_type))
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return response.text


def call_provider(provider: str, api_key: str, model: str, prompt: str, image_url: str = "") -> Any:
    if provider == "OpenAI":
        text = _openai_text(api_key, model, prompt, image_url)
    elif provider == "Google":
        text = _google_text(api_key, model, prompt, image_url)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    return _extract_json(text)


def _base_controls(root: Path):
    import ipywidgets as widgets

    provider = widgets.Dropdown(options=list(DEFAULT_MODELS), value="OpenAI", description="Provider:")
    model = widgets.Text(value=DEFAULT_MODELS[provider.value], description="Model:", layout=widgets.Layout(width="520px"))
    api_key = widgets.Textarea(
        description="API key:",
        placeholder="Paste enabled — or leave blank to use local .env",
        continuous_update=False,
        rows=1,
        layout=widgets.Layout(width="620px", height="58px"),
    )
    run = widgets.Button(description="Save key and run", button_style="primary", icon="play")
    output = widgets.Output(layout={"border": "1px solid #d9e2f2", "padding": "10px", "width": "100%"})

    def update_model(change):
        if change["name"] == "value":
            model.value = DEFAULT_MODELS[change["new"]]

    provider.observe(update_model, names="value")
    return widgets, provider, model, api_key, run, output


def error_analysis_widget(root: str | Path):
    """Analyze one existing error case with an optional live multimodal call."""
    import pandas as pd
    from IPython.display import display

    root = Path(root)
    widgets, provider, model, api_key, run, output = _base_controls(root)
    cases = pd.read_csv(root / "data/error_cases_tutorial.csv").fillna("").set_index("case_id")
    taxonomy = pd.read_csv(root / "data/error_taxonomy_tutorial.csv").fillna("")
    case_id = widgets.Dropdown(options=list(cases.index), description="Case:")

    def execute(_):
        with output:
            output.clear_output()
            key = _resolve_key(root, provider.value, api_key.value)
            if not key:
                print("Paste an API key or configure it in local .env; otherwise skip this optional cell.")
                return
            try:
                env_path = _save_key(root, provider.value, key)
                api_key.value = ""
                row = cases.loc[case_id.value].to_dict()
                table = "\n".join(
                    f"{r.id}|{r.evidence_policy}|{r.minor_category}|{r.definition}|exclude:{r.exclude}"
                    for r in taxonomy.itertuples()
                )
                prompt = f"""Analyze one K–12 math error. Use only IDs in the taxonomy.
Return JSON only: {{"hits":[{{"id":"ID","confidence":"strong|fair"}}],"rationale":"...","draft_quality":"ok|poor"}}.
Maximum four non-duplicate hits. The taxonomy defines one policy per class:
both, both_required, draft_primary, or answer_primary. Inspect both sources by
default; never choose a policy from the observed case outcome.

CASE
{json.dumps(row, ensure_ascii=False, indent=2)}

TAXONOMY
{table}"""
                image_url = row.get("draft_image_url", "")
                result = call_provider(provider.value, key, model.value.strip(), prompt, image_url)
                print(f"Saved {KEY_NAMES[provider.value]} to {env_path} (git-ignored).")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as exc:
                print(f"Live call failed: {type(exc).__name__}: {exc}")

    run.on_click(execute)
    display(widgets.VBox([widgets.HTML("<b>Optional live error analysis</b> — safe to skip."), case_id, provider, model, api_key, run, output]))


def dialogue_simulation_widget(root: str | Path):
    """Run a live session where the participant is the student and the LLM is the tutor."""
    import pandas as pd
    from html import escape
    from IPython.display import display

    root = Path(root)
    widgets, provider, model, api_key, run, output = _base_controls(root)
    cases = pd.read_csv(root / "data/error_cases_tutorial.csv").fillna("").set_index("case_id")
    case_id = widgets.Dropdown(options=list(cases.index), description="Case:")
    tutor_type = widgets.Dropdown(options=["context_aware", "non_context_aware"], description="Tutor:")
    max_rounds = widgets.IntSlider(value=8, min=3, max=12, step=1, description="Max rounds:")
    student_input = widgets.Textarea(
        description="You:",
        placeholder="Respond as the student, then click Send.",
        layout=widgets.Layout(width="100%", height="90px"),
        disabled=True,
    )
    send = widgets.Button(description="Send", button_style="success", icon="paper-plane", disabled=True)
    reset = widgets.Button(description="Reset", icon="refresh", disabled=True)
    run.description = "Start tutoring"
    history: list[dict[str, Any]] = []

    def render_history(status: str = ""):
        blocks: list[str] = []
        for message in history:
            color = "#174a8b" if message["speaker"] == "teacher" else "#8a3b12"
            label = "AI Tutor" if message["speaker"] == "teacher" else "Student"
            blocks.append(
                f"<div style='padding:9px 12px;margin:6px 0;border-left:5px solid {color};"
                f"background:#f6f7f9;border-radius:6px'><b style='color:{color}'>{label}</b><br>"
                f"{escape(message['text'])}</div>"
            )
        if status:
            blocks.append(f"<div style='color:#5b6472;margin-top:8px'>{escape(status)}</div>")
        rendered = "".join(blocks)
        output.outputs = ({
            "output_type": "display_data",
            "data": {"text/html": rendered, "text/plain": "Live tutoring dialogue"},
            "metadata": {},
        },)

    def tutor_turn() -> str:
        row = cases.loc[case_id.value].to_dict()
        diagnosis = (
            {
                "error_id": row["identified_error_id"],
                "rationale": row["rationale"],
                "evidence_policy": row["evidence_policy"],
                "draft_quality": row["draft_quality"],
            }
            if tutor_type.value == "context_aware"
            else "No structured error diagnosis is available. Infer cautiously from the conversation."
        )
        prompt = f"""You are the AI tutor in a live K–12 Socratic tutoring session.
The human participant is playing the student. Return JSON only: {{"teacher_response":"...","resolved":false}}.

Rules:
- Produce only the next teacher turn, never a simulated student turn.
- Ask at most one focused question.
- Do not reveal hidden labels or the complete solution.
- Use the visible history and adapt to the student's actual response.
- Mark resolved true only after the student independently explains the key idea.
- Keep the response concise, supportive, and age-appropriate.

CASE
{json.dumps(row, ensure_ascii=False, indent=2)}

TUTOR CONTEXT
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}

HISTORY
{json.dumps(history, ensure_ascii=False, indent=2)}"""
        key = _resolve_key(root, provider.value, api_key.value)
        if not key:
            raise ValueError("Paste an API key or configure it in local .env.")
        result = call_provider(provider.value, key, model.value.strip(), prompt)
        response = str(result["teacher_response"]).strip()
        if not response:
            raise ValueError("The tutor returned an empty response.")
        return response

    def start_session(_):
        history.clear()
        key = _resolve_key(root, provider.value, api_key.value)
        if not key:
            render_history("Paste an API key or configure it in local .env; otherwise skip this optional live demo.")
            return
        try:
            _save_key(root, provider.value, key)
            api_key.value = ""
            history.append({"round": 1, "speaker": "teacher", "text": tutor_turn()})
            student_input.disabled = False
            send.disabled = False
            reset.disabled = False
            run.disabled = True
            case_id.disabled = tutor_type.disabled = provider.disabled = model.disabled = max_rounds.disabled = True
            render_history("Your turn: respond as the student.")
        except Exception as exc:
            render_history(f"Live call failed: {type(exc).__name__}: {exc}")

    def send_turn(_):
        text = student_input.value.strip()
        if not text:
            render_history("Enter a student response before clicking Send.")
            return
        round_number = 1 + sum(message["speaker"] == "student" for message in history)
        history.append({"round": round_number, "speaker": "student", "text": text})
        student_input.value = ""
        if round_number >= max_rounds.value:
            student_input.disabled = send.disabled = True
            render_history("Maximum rounds reached. Reset to start another session.")
            return
        try:
            history.append({"round": round_number + 1, "speaker": "teacher", "text": tutor_turn()})
            render_history("Your turn: respond as the student.")
        except Exception as exc:
            render_history(f"Live call failed: {type(exc).__name__}: {exc}")

    def reset_session(_):
        history.clear()
        student_input.value = ""
        student_input.disabled = send.disabled = reset.disabled = True
        run.disabled = False
        case_id.disabled = tutor_type.disabled = provider.disabled = model.disabled = max_rounds.disabled = False
        output.outputs = ()

    run.on_click(start_session)
    send.on_click(send_turn)
    reset.on_click(reset_session)
    display(widgets.VBox([
        widgets.HTML("<b>Optional live tutoring</b> — you are the student; the selected model is the AI tutor."),
        case_id, tutor_type, max_rounds, provider, model, api_key,
        widgets.HBox([run, send, reset]), student_input, output,
    ]))


def dialogue_evaluation_widget(root: str | Path):
    """Evaluate one existing dialogue using the English production rubric."""
    from IPython.display import display

    root = Path(root)
    widgets, provider, model, api_key, run, output = _base_controls(root)
    sessions = json.loads((root / "data/dialogue_sessions_agent_generated.json").read_text(encoding="utf-8"))
    by_id = {item["session_id"]: item for item in sessions}
    session_id = widgets.Dropdown(options=list(by_id), description="Session:", layout=widgets.Layout(width="520px"))

    def execute(_):
        with output:
            output.clear_output()
            key = _resolve_key(root, provider.value, api_key.value)
            if not key:
                print("Paste an API key or configure it in local .env; otherwise skip this optional cell.")
                return
            try:
                env_path = _save_key(root, provider.value, key)
                api_key.value = ""
                session = by_id[session_id.value]
                template = (root / "prompts/eval_prompt_en.md").read_text(encoding="utf-8")
                prompt = (template
                          .replace("{dialogue_scene}", session["dialogue_scene"])
                          .replace("{lo_name}", session["lo_name"])
                          .replace("{dialogue_messages}", json.dumps(session["dialogue_messages"], indent=2)))
                result = call_provider(provider.value, key, model.value.strip(), prompt)
                print(f"Saved {KEY_NAMES[provider.value]} to {env_path} (git-ignored).")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as exc:
                print(f"Live call failed: {type(exc).__name__}: {exc}")

    run.on_click(execute)
    display(widgets.VBox([widgets.HTML("<b>Optional live dialogue evaluation</b> — safe to skip."), session_id, provider, model, api_key, run, output]))
