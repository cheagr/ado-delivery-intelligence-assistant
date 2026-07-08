"""
Prompt Builder

Converts structured business rule output into
a well-engineered prompt for Gemini.
"""


def build_summary_prompt(feature_report: dict) -> str:
    """
    Builds the prompt sent to Gemini.

    Parameters
    ----------
    feature_report : dict
        Structured output generated from the business rule engine.

    Returns
    -------
    str
        Prompt ready for Gemini.
    """

    prompt = f"""
        You are an experienced Technical Product Manager working in enterprise banking technology.

        You are reviewing delivery progress for a software feature.

        The information below has ALREADY been validated by deterministic business rules.

        IMPORTANT RULES

        1. Do NOT recalculate percentages.
        2. Do NOT invent missing information.
        3. Do NOT assume reasons unless explicitly provided.
        4. Base every statement ONLY on the structured data.
        5. If information is unavailable, clearly state it.

        Your tasks are:

        1. Write an Executive Summary - should be 2 liner
        2. Highlight Delivery Risks. - 3 bullets
        3. Recommend PM Actions. - 3 bullets
        4. Mention any Manual Review items. - 3 bullets
        5. Keep response concise and professional. - 80 words

        Do not include markdown.
        Do not include code fences.
        Do not include explanations outside JSON.

        Structured Feature Report

        {feature_report}
    """
    # print(f"Prompt from builder: {prompt}")
    return prompt.strip()