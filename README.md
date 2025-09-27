# Advancing Human-Machine Systems in Education: Socratic AI Tutoring for Personalized Math Education
### Official Repository for the IEEE SMC 2025 Tutorial

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Conference](https://img.shields.io/badge/IEEE%20SMC-2025-blueviolet)](https://ieeesmc2025.org/)

Welcome! This repository contains all the code, data, and interactive notebooks for our tutorial on building a context-aware Socratic AI tutor for K-12 math education.

---

### 📖 Tutorial Abstract

As AI-driven educational systems advance, the challenge lies in designing human-machine interactions that are pedagogically effective and adaptive. This tutorial introduces Socratic AI Tutoring, a structured framework that engages students in interactive, step-by-step guidance to understand and correct their own mistakes. By leveraging multimodal AI to pre-analyze a student's work, our tutor is context-aware from the first interaction, enabling personalized and highly effective learning dialogues.

### ✨ What You'll Learn & Build

By the end of this 2-hour tutorial, you will have built and evaluated a complete Socratic tutoring system. You will:

1.  🧠 **Perform Multimodal Error Analysis:** Use Google Gemini's vision capabilities to analyze a student's handwritten work, identify their specific mistake, and categorize it into a structured format.
2.  💬 **Build a Dual-Chat Interface:** Create and compare two AI tutors side-by-side—one that is context-aware and one that is not—to vividly demonstrate the UX benefits of context.
3.  ⚖️ **Create an Automated Evaluation Framework:** Use an LLM as an impartial judge to score conversation quality against a 6-point pedagogical rubric, turning qualitative interactions into quantitative data.

### 📂 Project Structure

The repository is organized to be clean and modular:
├── notebooks/ # The interactive Jupyter notebooks for the tutorial
│ ├── 01_Error_Aware_Retrieval.ipynb
│ ├── 02_Context_Aware_Dialogue.ipynb
│ └── 03_Conversational_Evaluation.ipynb
│
├── src/ # Reusable Python utility modules
│ ├── configs.py
│ ├── llm_utils.py
│ ├── prompt_utils.py
│ └── schema_utils.py
│
├── data/ # Sample data for the tutorial
│ └── student_drafts.csv
│
├── logs/ # Directory where conversation logs are saved
│ ├── context_aware/
│ └── non_context_aware/
│
├── results/ # Output from the analysis notebook
│ └── student_drafts_with_analysis.csv
│
├── setup.sh # Automated setup script for macOS/Linux
├── setup.bat # Automated setup script for Windows
├── requirements.txt # List of Python dependencies
└── README.md # You are here!
code
Code
---

### 🚀 Getting Started: From Zero to Ready in 5 Steps

Follow these steps to set up your environment.

#### Step 0: Prerequisites (For Absolute Beginners)

If you don't have Python or Git installed, you'll need to set them up first.

1.  **Install Git:** Git is a version control system used to download this repository.
    *   **Check if it's installed:** Open a terminal (Terminal on macOS/Linux, PowerShell or Command Prompt on Windows) and type `git --version`. If you see a version number, you're all set.
    *   **How to install:** Download it from the [official Git website](https://git-scm.com/downloads).

2.  **Install Python:** You'll need Python version 3.9 or newer.
    *   **Check if it's installed:** In your terminal, type `python --version` or `python3 --version`.
    *   **How to install:** Download it from the [official Python website](https://www.python.org/downloads/). **Important:** On Windows, make sure to check the box that says "Add Python to PATH" during installation.

#### Step 1: Clone the Repository

Open your terminal, navigate to where you want to store the project, and run:
```bash
git clone https://github.com/txu0915/context-aware-ai-conversation.git
cd context-aware-ai-conversation
Step 2: Get Your Google Gemini API Key
This project uses the Google Gemini API. It has a generous free tier that is perfect for this tutorial.
Go to Google AI Studio.
Sign in with your Google account.
Click on "Get API key" and then "Create API key in new project".
Copy the generated key. You will need it in the next step.
Step 3: Run the Automated Setup Script
We've created a script that handles everything for you: it creates a virtual environment, installs all required packages, and prepares your configuration file.
For macOS and Linux:
```
bash setup.sh
```

For Windows:
```
cmd
setup.bat
```

Step 4: Add Your API Key
The setup script created a file named .env in your project directory.
Open the .env file with any text editor.
Replace the placeholder 'YOUR_API_KEY_HERE' with the Gemini API key you copied earlier.
Save and close the file.
Step 5: Activate Your Environment & Launch
Activate the virtual environment in your terminal:
macOS/Linux: source venv/bin/activate
Windows: venv\Scripts\activate
You'll know it's active when you see (venv) at the beginning of your terminal prompt.
Launch Jupyter Lab:
```
jupyter lab
This will open a new tab in your browser with the Jupyter Lab interface.
💻 Running the Tutorial Notebooks
Navigate to the notebooks directory in the Jupyter Lab file browser. Run the notebooks in the following order:
01_Error_Aware_Retrieval.ipynb: Analyze student drafts with a multimodal AI and generate a structured analysis file.
02_Context_Aware_Dialogue.ipynb: Launch the side-by-side chat interface and interact with the two different AI tutors.
03_Conversational_Evaluation.ipynb: Automatically evaluate your saved conversation logs and visualize the performance comparison.
🔧 Troubleshooting
Problem: The chat widgets in Notebook 02 are not appearing or are stuck loading.
Solution: Your Jupyter Lab may be missing the required frontend extension. Stop Jupyter Lab (Ctrl+C in terminal), make sure your (venv) is active, and run:
```
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```
Then, restart jupyter lab.
👥 Organizers
Tianlong Xu - Squirrel Ai Learning (tianlongxu@squirrelai.com)
Aoxiao Zhong - Squirrel Ai Learning (aoxiaozhong@squirrelai.com)
Joleen Liang - Squirrel Ai Learning (joleenliang@squirrelai.com)
Qingsong Wen - Squirrel Ai Learning (qingsongwen@squirrelai.com)
📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
