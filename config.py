import os
import streamlit as st


def get_secret(name, default=None):
    """
    Read a Streamlit secret first, then environment variable.
    """
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name, default)


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")

TEXT_MODEL = get_secret(
    "TEXT_MODEL",
    "gpt-5.6-luna"
)

TTS_MODEL = get_secret(
    "TTS_MODEL",
    "gpt-4o-mini-tts"
)

VEO_MODEL = get_secret(
    "VEO_MODEL",
    "veo-3.1-generate-preview"
)

OUTPUT_DIR = "outputs"
