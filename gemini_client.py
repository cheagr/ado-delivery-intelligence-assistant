"""
Gemini Client

Handles all communication with Google's Gemini API.

Responsibilities:
- Configure Gemini client
- Build prompt
- Call Gemini
- Handle failures gracefully
"""

from google import genai
from schemas import AI_SUMMARY_SCHEMA
import json

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    TEMPERATURE,
    MAX_OUTPUT_TOKENS
)

from prompt_builder import build_summary_prompt


def generate_ai_summary(feature_report: dict) -> str:
    print("Generating AI summary...")
    """
    Generate AI summary for delivery report.

    Parameters
    ----------
    feature_report : dict

    Returns
    -------
    str
        Markdown response.
    """

    # ----------------------------
    # API Key Validation
    # ----------------------------

    if not GEMINI_API_KEY:
        return False, {"error": "Gemini API Key not found.\n\nPlease configure GEMINI_API_KEY before using AI Summary."}

    try:

        # Configure Gemini
        # genai.configure(api_key=GEMINI_API_KEY)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # model = genai.GenerativeModel(GEMINI_MODEL)

        prompt = build_summary_prompt(feature_report)
        # print(prompt)
        print(f"Max Token config: {MAX_OUTPUT_TOKENS}")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": TEMPERATURE,
                "response_mime_type": "application/json",
                "response_schema": AI_SUMMARY_SCHEMA,
            }
        )
        # response = model.generate_content(
        #     prompt,
        #     generation_config={
        #         "temperature": TEMPERATURE,
        #         # "max_output_tokens": MAX_OUTPUT_TOKENS,
        #     }
        # )
        # print("Generated content REPR: ", repr(response.text))
        # print(f"Resonse Candidate: {response.candidates}")
        # print(f"Prompt feedback: {response.prompt_feedback}")
        # print(f"Finish reason : {response.candidates[0].finish_reason}")
        if not response.text:
            return False, {"error": "No response received from Gemini."}

        ai_result = response.parsed #json.loads(response.text)
        print (ai_result)
        return True, ai_result

    except Exception as ex:
        print(f"Error in gemini_client: {ex}")
        return False, {
            "error": f"AI Summary unavailable.\n\nReason:\n{ex}"
        }
