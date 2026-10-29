import logging
from typing import Any, List, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger("app.core.llm_fallback")

DEFAULT_FALLBACK_CHAIN = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]


def get_gemini_model_candidates(
    primary_model: Optional[str] = None,
    is_stt: bool = False,
) -> List[str]:
    """
    Returns an ordered, deduplicated list of Gemini models to try:
    1. Explicitly passed primary_model (if any)
    2. Configured GEMINI_STT_MODEL_NAME (if is_stt=True) or GEMINI_MODEL_NAME
    3. Configured GEMINI_FALLBACK_MODELS from .env
    4. Built-in supported Gemini fallback chain
    """
    candidates: List[str] = []

    if primary_model and primary_model.strip():
        candidates.append(primary_model.strip())

    configured_primary = (
        settings.GEMINI_STT_MODEL_NAME if is_stt else settings.GEMINI_MODEL_NAME
    )
    if configured_primary and configured_primary.strip():
        candidates.append(configured_primary.strip())

    raw_fallbacks = getattr(settings, "GEMINI_FALLBACK_MODELS", "") or ""
    for item in raw_fallbacks.split(","):
        model_id = item.strip()
        if model_id:
            candidates.append(model_id)

    for default_model in DEFAULT_FALLBACK_CHAIN:
        candidates.append(default_model)

    # Deduplicate while preserving order
    unique_candidates: List[str] = []
    seen = set()
    for m in candidates:
        if m not in seen:
            seen.add(m)
            unique_candidates.append(m)

    return unique_candidates


def generate_content_with_fallback(
    client: Any,
    contents: Any,
    config: Optional[Any] = None,
    primary_model: Optional[str] = None,
    is_stt: bool = False,
) -> Tuple[Any, str]:
    """
    Executes `client.models.generate_content` with automatic fallback across
    supported Gemini models if the primary model fails (e.g., 404, 429 quota, 503).
    Returns a tuple of (response, model_used).
    """
    candidates = get_gemini_model_candidates(primary_model=primary_model, is_stt=is_stt)
    last_error: Optional[Exception] = None

    for idx, model_name in enumerate(candidates):
        try:
            kwargs: dict = {
                "model": model_name,
                "contents": contents,
            }
            if config is not None:
                kwargs["config"] = config

            response = client.models.generate_content(**kwargs)
            if idx > 0:
                logger.info(
                    "Gemini fallback succeeded using model '%s' (after %d failed attempt(s)).",
                    model_name,
                    idx,
                )
            return response, model_name
        except Exception as exc:
            last_error = exc
            next_model = candidates[idx + 1] if idx + 1 < len(candidates) else None
            if next_model:
                logger.warning(
                    "Gemini model '%s' failed (%s). Falling back to '%s'...",
                    model_name,
                    exc,
                    next_model,
                )
            else:
                logger.error(
                    "All Gemini model candidates %s failed. Last error: %s",
                    candidates,
                    exc,
                )

    if last_error:
        raise last_error
    raise RuntimeError("No Gemini model candidates available.")


def invoke_langchain_gemini_with_fallback(
    messages: List[Any],
    api_key: str,
    primary_model: Optional[str] = None,
    temperature: float = 0.2,
) -> Tuple[Any, str]:
    """
    Invokes LangChain `ChatGoogleGenerativeAI` with automatic fallback across
    supported Gemini models. Returns (response, model_used).
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    candidates = get_gemini_model_candidates(primary_model=primary_model, is_stt=False)
    last_error: Optional[Exception] = None

    for idx, model_name in enumerate(candidates):
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
            )
            response = llm.invoke(messages)
            if idx > 0:
                logger.info(
                    "LangChain Gemini fallback succeeded using model '%s' (after %d failed attempt(s)).",
                    model_name,
                    idx,
                )
            return response, model_name
        except Exception as exc:
            last_error = exc
            next_model = candidates[idx + 1] if idx + 1 < len(candidates) else None
            if next_model:
                logger.warning(
                    "LangChain Gemini model '%s' failed (%s). Falling back to '%s'...",
                    model_name,
                    exc,
                    next_model,
                )
            else:
                logger.error(
                    "All LangChain Gemini model candidates %s failed. Last error: %s",
                    candidates,
                    exc,
                )

    if last_error:
        raise last_error
    raise RuntimeError("No Gemini model candidates available.")

