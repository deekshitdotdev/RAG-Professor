"""
Holds the currently-active chat and vision models in memory so they can be
switched from the UI (via /api/models + /api/model) without restarting the
server.

Features:
- Falls back to config.py defaults on startup
- Thread-safe updates
- Prevents empty model names
- Supports resetting to defaults
"""

from threading import Lock
import RAG_Professor.backend.config as config

_lock = Lock()

_DEFAULT_CHAT_MODEL = config.LLM_MODEL
_DEFAULT_VISION_MODEL = config.VISION_MODEL

_state = {
    "chat_model": _DEFAULT_CHAT_MODEL,
    "vision_model": _DEFAULT_VISION_MODEL,
}


def get_chat_model() -> str:
    with _lock:
        return _state["chat_model"]


def set_chat_model(name: str) -> None:
    if not name or not isinstance(name, str):
        raise ValueError("Invalid chat model name")

    with _lock:
        _state["chat_model"] = name.strip()


def get_vision_model() -> str:
    with _lock:
        return _state["vision_model"]


def set_vision_model(name: str) -> None:
    if not name or not isinstance(name, str):
        raise ValueError("Invalid vision model name")

    with _lock:
        _state["vision_model"] = name.strip()


def get_models() -> dict:
    with _lock:
        return {
            "chat_model": _state["chat_model"],
            "vision_model": _state["vision_model"],
        }


def reset_models() -> None:
    with _lock:
        _state["chat_model"] = _DEFAULT_CHAT_MODEL
        _state["vision_model"] = _DEFAULT_VISION_MODEL