"""
Application configuration.

All application-wide configuration values should be defined here.
This keeps AI model settings, environment variables and future
configuration in one place.
"""

import os


# ----------------------------
# Gemini Configuration
# ----------------------------

# Read API key from environment variable.
# Never hardcode API keys in source code.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Model to use
GEMINI_MODEL = "gemini-2.5-flash"


# Generation settings
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 800


# ----------------------------
# Application Settings
# ----------------------------

APP_NAME = "ADO Delivery Intelligence Assistant"

APP_VERSION = "0.1.0"


# ----------------------------
# Logging
# ----------------------------

ENABLE_AI_LOGGING = True