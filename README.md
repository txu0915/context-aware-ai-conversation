# Error-Aware Socratic Tutoring at Scale

English-language materials for the IEEE SMC 2026 half-day tutorial on building context-aware, error-aware Socratic AI tutors for K–12 education.

The tutorial connects four ideas: structured error attribution, context-aware dialogue generation, dialogue evaluation, and hybrid guardrails. Every core notebook runs from small, de-identified, deterministic fixtures so it can be presented quickly and reproduced without network access. Notebooks 01–03 also include optional live API cells for participants who want to try the workflow with OpenAI or Google Gemini.

## Tutorial sequence

Run the notebooks in this order:

1. `00_Tutorial_Roadmap.ipynb` — tutorial narrative, methodology, and prepared/live learning paths.
2. `01_Error_Aware_Retrieval.ipynb` — multimodal error attribution, taxonomy evidence, evidence policies, and optional live case analysis.
3. `02_Context_Aware_Dialogue.ipynb` — matched context-aware and context-unaware sessions plus optional live simulation.
4. `03_Conversation_Evaluation.ipynb` — T1–T9 teacher evaluation, paired visualizations, failure definitions, and optional live evaluation.
5. `03_Early_Stopping_and_Guardrails.ipynb` — S1–S6 student outcomes, bad-case review, curriculum-scope monitoring, and rule-plus-LLM arbitration.

The two `03_` notebooks form one evaluation and safety section: evaluate the conversation first, then inspect stopping and guardrail decisions.

## What is included

- A stratified 20-class demonstration subset of the 41-class error taxonomy, with at least two minor classes per major category.
- Three complete error-attribution cases showing draft-preferred, answer-preferred, and mixed evidence policies.
- Six matched dialogue sessions covering short, medium, and long interactions with and without error context.
- An English presentation version of the production-inspired T1–T9 teacher and S1–S6 student rubrics.
- Guardrail examples for `continue`, `verify_learning`, `support`, `redirect`, `stop`, and `escalate`.
- Optional OpenAI and Google Gemini live demos that remain isolated from the offline tutorial path.

Prepared scores are tutorial fixtures, not production evaluation results. They make the presentation deterministic and easy to follow; the optional live cells let participants run the same workflow themselves.

## Repository structure

```text
data/       Small tutorial fixtures
notebooks/  Presentation-ready tutorial notebooks
prompts/    English prompt references
src/        Display, evaluation, guardrail, and live-demo utilities
logs/       Example context-aware and context-unaware conversations
reports/    Tutorial deck and overview exports
```

`ppt_assets_local/`, `.env`, virtual environments, notebook checkpoints, and Python caches are intentionally excluded from Git.

## Quick start

### Requirements

- Python 3.10 or later
- Git
- An OpenAI or Google API key only if you want to run the optional live cells

### macOS or Linux

```bash
git clone https://github.com/txu0915/context-aware-ai-conversation.git
cd context-aware-ai-conversation
bash setup.sh
source venv/bin/activate
jupyter lab
```

### Windows

```bat
git clone https://github.com/txu0915/context-aware-ai-conversation.git
cd context-aware-ai-conversation
setup.bat
venv\Scripts\activate
jupyter lab
```

You can also install manually:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter lab
```

## Optional live API configuration

All required cells run without credentials. For a live demo, enter a key in the final cell of Notebook 01, 02, or 03, or create a local `.env` file:

```text
OPENAI_API_KEY=
GEMINI_API_KEY=
```

The widget stores a submitted key only in the local `.env`, which is ignored by Git. The provider and model fields are editable because model availability changes over time.

## Guardrail design

The tutorial uses a conservative hybrid controller:

- Deterministic rules enforce explicit safety boundaries and product limits.
- An LLM detects semantic risks, indirect distress, intent, and contextual drift.
- Curriculum evidence distinguishes off-topic behavior from academically relevant but out-of-scope questions.
- A confident semantic judgment may raise intervention severity but cannot weaken a stricter rule decision.

## Validation

Before presenting, activate the environment and execute the notebooks in order. The offline path should complete without API keys. Live cells are optional and can be skipped.

## Organizers

- Tianlong Xu — Squirrel AI Learning
- Haoyang Li — Squirrel AI Learning
- Joleen Liang — Squirrel AI Learning
- Qingsong Wen — Squirrel AI Learning

## License

This project is licensed under the MIT License.
