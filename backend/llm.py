"""
Thin client for a locally running Ollama server. Streams tokens as they're
generated so the frontend can show them live, ChatGPT-style. Also exposes
model listing/switching and a one-shot vision call used for OCR.
"""
import base64
import json
import logging
from typing import Generator, List, Optional

import requests

import config
import runtime_state

logger = logging.getLogger("llm")


def list_installed_models() -> List[str]:
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except requests.exceptions.RequestException as e:
        logger.warning("Could not list Ollama models: %s", e)
        return []


def check_ollama_available():
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
    except requests.exceptions.RequestException as e:
        return False, f"Cannot reach Ollama at {config.OLLAMA_HOST}. Is 'ollama serve' running? ({e})"

    chat_model = runtime_state.get_chat_model()
    if chat_model not in models:
        return False, f"Model '{chat_model}' isn't pulled yet. Run: ollama pull {chat_model}"
    return True, "ok"


def stream_generate(prompt: str, system: str = "", model: Optional[str] = None) -> Generator[str, None, None]:
    payload = {
        "model": model or runtime_state.get_chat_model(),
        "prompt": prompt,
        "system": system,
        "stream": True,
        "options": {
            "temperature": config.LLM_TEMPERATURE,
            "num_ctx": config.LLM_NUM_CTX,
            "num_predict": config.LLM_MAX_TOKENS,
        },
    }
    try:
        with requests.post(
            f"{config.OLLAMA_HOST}/api/generate", json=payload, stream=True, timeout=300
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    yield data["response"]
                if data.get("done"):
                    break
    except requests.exceptions.RequestException as e:
        logger.error("Ollama generation failed: %s", e)
        yield f"\n\n[Error contacting local LLM: {e}]"


def vision_extract_text(image_bytes: bytes, prompt: Optional[str] = None, model: Optional[str] = None) -> str:
    """One-shot (non-streaming) call to a vision model. Used for OCR of
    scanned PDF pages, and reusable for general image/screenshot questions."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "model": model or runtime_state.get_vision_model(),
        "prompt": prompt or (
            "Transcribe all readable text from this image exactly as it appears, "
            "preserving line breaks and reading order. Output only the transcribed "
            "text, no commentary."
        ),
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0.0},
    }
    resp = requests.post(
        f"{config.OLLAMA_HOST}/api/generate",
        json=payload,
        timeout=config.OCR_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()
