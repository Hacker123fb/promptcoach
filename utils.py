"""
utils.py — Helper utilities for configuration, secrets fallback, and PII detection.
"""

import os
import re
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Regular expressions for sensitive personal information (PII)
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")


def detect_pii(text: str) -> List[str]:
    """
    Check if the input text contains sensitive information like email or phone numbers.
    Returns a list of detected PII type labels.
    """
    if not text:
        return []
    
    findings = []
    if EMAIL_PATTERN.search(text):
        findings.append("email address")
    if PHONE_PATTERN.search(text):
        findings.append("phone number")
    return findings


def get_api_key() -> str:
    """
    Retrieve Gemini API key from Streamlit secrets (for cloud deployment)
    with fallback to environment variables (for local development).
    """
    # 1. Check Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
            if key:
                return key
    except Exception:
        pass

    # 2. Fallback to OS environment variable / .env
    return os.getenv("GEMINI_API_KEY", "").strip()


def get_model_name() -> str:
    """
    Retrieve Gemini model name from Streamlit secrets, then environment variable,
    falling back to 'gemini-2.5-flash'.
    """
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "MODEL_NAME" in st.secrets:
            val = str(st.secrets["MODEL_NAME"]).strip()
            if val:
                return val
    except Exception:
        pass

    return os.getenv("MODEL_NAME", "gemini-2.5-flash").strip()
