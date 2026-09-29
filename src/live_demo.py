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
    api_key = widgets.Password(description="API key:", placeholder="Key is saved only to local .env", layout=widgets.Layout(width="520px"))
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
            if not api_key.value.strip():
                print("Enter an API key, or skip this optional cell.")
                return
            try:
                env_path = _save_key(root, provider.value, api_key.value.strip())
                row = cases.loc[case_id.value].to_dict()
                table = "\n".join(
                    f"{r.id}|{r.modality}|{r.minor_category}|{r.definition}|exclude:{r.exclude}"
                    for r in taxonomy.itertuples()
                )
                prompt = f"""Analyze one K–12 math error. Use only IDs in the taxonomy.
Return JSON only: {{"hits":[{{"id":"ID","confidence":"strong|fair"}}],"rationale":"...","draft_quality":"ok|poor"}}.
Maximum four non-duplicate hits. Respect answer, draft_preferred, draft_required, and cross evidence policies.

CASE
{json.dumps(row, ensure_ascii=False, indent=2)}

TAXONOMY
{table}"""
                image_url = row.get("draft_image_url", "")
                result = call_provider(provider.value, api_key.value.strip(), model.value.strip(), prompt, image_url)
                print(f"Saved {KEY_NAMES[provider.value]} to {env_path} (git-ignored).")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as exc:
                print(f"Live call failed: {type(exc).__name__}: {exc}")

    run.on_click(execute)
    display(widgets.VBox([widgets.HTML("<b>Optional live error analysis</b> — safe to skip."), case_id, provider, model, api_key, run, output]))


def dialogue_simulation_widget(root: str | Path):
    """Generate one complete simulated student–tutor session."""
    import pandas as pd
    from IPython.display import display

    root = Path(root)
    widgets, provider, model, api_key, run, output = _base_controls(root)
    cases = pd.read_csv(root / "data/error_cases_tutorial.csv").fillna("").set_index("case_id")
    case_id = widgets.Dropdown(options=list(cases.index), description="Case:")
    tutor_type = widgets.Dropdown(options=["context_aware", "non_context_aware"], description="Tutor:")
    rounds = widgets.IntSlider(value=6, min=3, max=12, step=1, description="Rounds:")

    def execute(_):
        with output:
            output.clear_output()
            if not api_key.value.strip():
                print("Enter an API key, or skip this optional cell.")
                return
            try:
                env_path = _save_key(root, provider.value, api_key.value.strip())
                row = cases.loc[case_id.value].to_dict()
                diagnosis = ({"error_id": row["identified_error_id"], "rationale": row["rationale"], "draft_quality": row["draft_quality"]}
                             if tutor_type.value == "context_aware" else "hidden from tutor")
                prompt = f"""Simulate a {rounds.value}-round K–12 tutoring session as JSON only.
Return {{"session_id":"live_demo","tutor_type":"{tutor_type.value}","dialogue_messages":[{{"round":1,"speaker":"teacher|student","text":"..."}}]}}.
The tutor is Socratic, asks one focused question per turn, never reveals hidden labels, and verifies learning.
The student keeps the same misconception until sufficient guidance and uses concise age-appropriate language.

CASE
{json.dumps(row, ensure_ascii=False, indent=2)}

TUTOR DIAGNOSIS
{json.dumps(diagnosis, ensure_ascii=False, indent=2)}"""
                result = call_provider(provider.value, api_key.value.strip(), model.value.strip(), prompt)
                print(f"Saved {KEY_NAMES[provider.value]} to {env_path} (git-ignored).")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as exc:
                print(f"Live call failed: {type(exc).__name__}: {exc}")

    run.on_click(execute)
    display(widgets.VBox([widgets.HTML("<b>Optional live dialogue simulation</b> — safe to skip."), case_id, tutor_type, rounds, provider, model, api_key, run, output]))


def dialogue_evaluation_widget(root: str | Path):
    """Evaluate one existing dialogue using the English production rubric."""
    from IPython.display import display

    root = Path(root)
    widgets, provider, model, api_key, run, output = _base_controls(root)
    sessions = json.loads((root / "data/dialogue_sessions_tutorial.json").read_text(encoding="utf-8"))
    by_id = {item["session_id"]: item for item in sessions}
    session_id = widgets.Dropdown(options=list(by_id), description="Session:", layout=widgets.Layout(width="520px"))

    def execute(_):
        with output:
            output.clear_output()
            if not api_key.value.strip():
                print("Enter an API key, or skip this optional cell.")
                return
            try:
                env_path = _save_key(root, provider.value, api_key.value.strip())
                session = by_id[session_id.value]
                template = (root / "prompts/eval_prompt_en.md").read_text(encoding="utf-8")
                prompt = (template
                          .replace("{dialogue_scene}", session["dialogue_scene"])
                          .replace("{lo_name}", session["lo_name"])
                          .replace("{dialogue_messages}", json.dumps(session["dialogue_messages"], indent=2)))
                result = call_provider(provider.value, api_key.value.strip(), model.value.strip(), prompt)
                print(f"Saved {KEY_NAMES[provider.value]} to {env_path} (git-ignored).")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as exc:
                print(f"Live call failed: {type(exc).__name__}: {exc}")

    run.on_click(execute)
    display(widgets.VBox([widgets.HTML("<b>Optional live dialogue evaluation</b> — safe to skip."), session_id, provider, model, api_key, run, output]))
