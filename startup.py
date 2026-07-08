from config import GEMINI_API_KEY, GEMINI_MODEL


def validate_configuration():
    """
    Validate mandatory application configuration.

    """

    missing = []

    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")

    if not GEMINI_MODEL:
        missing.append("GEMINI_MODEL")

    if missing:
        return (
            False,
            "Application configuration is incomplete.\n\n"
            f"Missing configuration:\n• {'• '.join(missing)}\n\n"
            "Please update your .env file and restart the application."
        )

    return True, None