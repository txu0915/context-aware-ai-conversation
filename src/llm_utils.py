# src/llm_utils.py
import os
import json
import datetime
import requests
import google.generativeai as genai
from pydantic import ValidationError
from schema_utils import ErrorAnalysis
from prompt_utils import create_error_analysis_prompt, create_evaluation_prompt
from configs import ERROR_CATEGORIES
from schema_utils import ConversationEvaluation # Add this to imports


# Initialize the Gemini model once
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    VISION_MODEL = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    VISION_MODEL = None


def analyze_student_work_structured(problem_text: str, image_url: str) -> ErrorAnalysis | None:
    """
    Analyzes student work and returns a structured Pydantic object or None on failure.
    """
    if not VISION_MODEL:
        print("Vision model is not initialized.")
        return None

    try:
        # 1. Fetch the image data
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_data = {'mime_type': response.headers['Content-Type'], 'data': response.content}
    except requests.RequestException as e:
        print(f"Error fetching image {image_url}: {e}")
        return None

    # 2. Create the prompt
    prompt = create_error_analysis_prompt(problem_text, ERROR_CATEGORIES)

    try:
        # 3. Call the LLM
        llm_response = VISION_MODEL.generate_content([prompt, image_data])
        
        # 4. Clean and parse the response
        # The model can sometimes wrap the JSON in markdown, so we strip it.
        cleaned_response = llm_response.text.strip().replace("```json", "").replace("```", "")
        
        # 5. Validate with Pydantic
        analysis = ErrorAnalysis.model_validate_json(cleaned_response)
        return analysis

    except ValidationError as e:
        print(f"Pydantic validation failed for URL {image_url}: {e}")
        print(f"LLM Raw Output: {llm_response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during LLM call for URL {image_url}: {e}")
        return None
    

try:
    # Use a fast and capable model for conversation
    TEXT_MODEL = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Error configuring Gemini Text API: {e}")
    TEXT_MODEL = None


def is_student_rude(message: str) -> bool:
    """
    A simple filter to detect rude or demanding language for early stopping.
    """
    rude_keywords = [
        "stupid", "dumb", "idiot", "hate", "useless", 
        "just give me the answer", "tell me the answer", "don't care"
    ]
    message_lower = message.lower()
    for keyword in rude_keywords:
        if keyword in message_lower:
            return True
    return False


def log_conversation(log_path: str, conversation_history: list):
    """
    Saves the entire conversation history to a JSON file, creating parent directories if needed.
    """
    try:
        # --- ADD THIS LINE ---
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error logging conversation to {log_path}: {e}")


# src/llm_utils.py

def evaluate_conversation(conversation_history: list, ground_truth_analysis: dict) -> ConversationEvaluation | None:
    """
    Uses an LLM to evaluate a conversation log against a ground truth analysis.
    """
    if not TEXT_MODEL:
        print("Text model is not initialized.")
        return None

    try:
        log_str = json.dumps([msg for msg in conversation_history if msg['role'] != 'system'], indent=2)
        ground_truth_str = json.dumps(ground_truth_analysis, indent=2)
        
        # Pass both arguments to the refined prompt function
        prompt = create_evaluation_prompt(log_str, ground_truth_str)
        
        response = TEXT_MODEL.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
        
        evaluation = ConversationEvaluation.model_validate_json(cleaned_response)
        return evaluation

    except ValidationError as e:
        print(f"Pydantic validation failed during evaluation: {e}\nLLM Raw Output: {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during evaluation: {e}")
        return None
