"""Backend adapters for CAMEL.Bridge generation."""

from __future__ import annotations

import http.client
import json
import logging
import os
import socket
import ssl
import time
from typing import Any, Protocol
from urllib import error as urllib_error
from urllib import request as urllib_request

LOGGER = logging.getLogger(__name__)


class AgentTextBackend(Protocol):
    def generate(self, system_message: str, user_message: str) -> str: ...


class CamelChatBackend:
    """Lazy CAMEL backend that only imports CAMEL at runtime."""

    def __init__(
        self,
        model_platform: str | None = None,
        model_type: str | None = None,
        model_config: dict | None = None,
    ):
        self.model_platform = (
            model_platform or os.getenv("CAMEL_MODEL_PLATFORM") or "OPENAI"
        ).upper()
        self.model_type = (
            model_type or os.getenv("CAMEL_MODEL_TYPE") or "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
        )
        self.model_url = (
            os.getenv("CAMEL_MODEL_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or (
                "https://openrouter.ai/api/v1"
                if self.model_platform == "OPENROUTER"
                else (
                    "http://localhost:1234/v1"
                    if self.model_platform in {"LM_STUDIO", "LMLINK"}
                    else None
                )
            )
        )
        self.model_config = model_config or self._build_model_config()
        self._request_timeout = int(
            os.getenv("CAMEL_BRIDGE_REQUEST_TIMEOUT_SECONDS", "300")
        )

    def generate(self, system_message: str, user_message: str) -> str:
        self._validate_environment()
        if self.model_platform in {"OPENROUTER", "LM_STUDIO", "LMLINK"}:
            return self._generate_via_openai_compatible_http(
                system_message, user_message, request_timeout=self._request_timeout
            )
        try:
            from camel.agents import ChatAgent
            from camel.models import ModelFactory
            from camel.types import ModelPlatformType, ModelType
        except ImportError:
            if self._supports_openai_compatible_http():
                return self._generate_via_openai_compatible_http(
                    system_message, user_message, request_timeout=self._request_timeout
                )
            raise

        model = ModelFactory.create(
            model_platform=getattr(
                ModelPlatformType, self.model_platform, self.model_platform
            ),
            model_type=getattr(ModelType, self.model_type, self.model_type),
            model_config_dict=self.model_config,
            api_key=self._get_api_key(),
            url=self.model_url,
        )
        agent = ChatAgent(model=model)
        response = agent.step(
            f"System instruction:\n{system_message}\n\nUser request:\n{user_message}"
        )
        if hasattr(response, "msgs") and response.msgs:
            return response.msgs[-1].content
        return str(response)

    def _build_model_config(self) -> dict:
        config = {"temperature": float(os.getenv("CAMEL_MODEL_TEMPERATURE", "0.8"))}
        if os.getenv("CAMEL_MODEL_MAX_TOKENS"):
            config["max_tokens"] = int(os.getenv("CAMEL_MODEL_MAX_TOKENS", "0"))
        return config

    def _supports_openai_compatible_http(self) -> bool:
        return self.model_platform in {"OPENAI", "OPENROUTER", "LM_STUDIO", "LMLINK"}

    def _validate_environment(self) -> None:
        # Skip validation for localhost and docker host connections (LM Studio, local servers)
        if self.model_url and any(
            host in self.model_url for host in ("127.0.0.1", "localhost", "::1", "host.docker.internal")
        ):
            return
        if self.model_platform in {"LM_STUDIO", "LMLINK"}:
            return
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        if required_key and not os.getenv(required_key):
            raise RuntimeError(
                f"Missing required environment variable for CAMEL bridge: {required_key}"
            )

    def _get_api_key(self) -> str | None:
        required_key = {
            "OPENAI": "OPENAI_API_KEY",
            "ANTHROPIC": "ANTHROPIC_API_KEY",
            "GEMINI": "GOOGLE_API_KEY",
            "GOOGLE": "GOOGLE_API_KEY",
            "GROQ": "GROQ_API_KEY",
            "MISTRAL": "MISTRAL_API_KEY",
            "OPENROUTER": "OPENROUTER_API_KEY",
        }.get(self.model_platform)
        return os.getenv(required_key) if required_key else None

    def _generate_via_openai_compatible_http(
        self, system_message: str, user_message: str, request_timeout: int = 300
    ) -> str:
        if not self.model_url:
            raise RuntimeError(
                "CAMEL bridge needs CAMEL_MODEL_BASE_URL or OPENAI_BASE_URL for HTTP generation"
            )
        payload: dict[str, Any] = {
            "model": self.model_type,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        }
        payload.update(self.model_config)
        reasoning_effort = os.getenv("CAMEL_MODEL_REASONING_EFFORT")
        if reasoning_effort:
            payload["reasoning"] = {"effort": reasoning_effort}
        base_url = self.model_url.rstrip("/")
        base_url = base_url.rpartition("/v1")[0] if "/v1" in base_url else base_url
        request = urllib_request.Request(
            f"{base_url}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._build_openai_compatible_headers(),
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(1, self._http_retry_attempts() + 1):
            try:
                with urllib_request.urlopen(
                    request, timeout=request_timeout
                ) as response:
                    body = response.read().decode("utf-8")
                break
            except urllib_error.HTTPError as exc:
                details = exc.read().decode("utf-8", errors="replace")
                if (
                    self._should_retry_http_status(exc.code)
                    and attempt < self._http_retry_attempts()
                ):
                    last_error = RuntimeError(
                        f"CAMEL bridge HTTP generation failed with status {exc.code}: {details}"
                    )
                    self._sleep_before_retry(attempt)
                    continue
                raise RuntimeError(
                    f"CAMEL bridge HTTP generation failed with status {exc.code}: {details}"
                ) from exc
            except Exception as exc:
                if (
                    self._is_retryable_http_exception(exc)
                    and attempt < self._http_retry_attempts()
                ):
                    last_error = exc
                    self._sleep_before_retry(attempt)
                    continue
                reason = getattr(exc, "reason", exc)
                raise RuntimeError(
                    f"CAMEL bridge HTTP generation failed: {reason}"
                ) from exc
        else:
            reason = getattr(last_error, "reason", last_error)
            raise RuntimeError(
                f"CAMEL bridge HTTP generation failed after retries: {reason}"
            )

        parsed = json.loads(body)
        content = ((parsed.get("choices") or [{}])[0].get("message") or {}).get(
            "content"
        )
        if isinstance(content, str) and content.strip():
            # Extract JSON from markdown blocks or messy text.
            # Use raw_decode to find the first valid JSON object/array
            # by scanning for '{' or '[' — handles nested objects correctly.
            text = content.strip()
            decoder = json.JSONDecoder()
            for start, ch in enumerate(text):
                if ch in ('{', '['):
                    try:
                        obj, _ = decoder.raw_decode(text, start)
                        return json.dumps(obj, ensure_ascii=False)
                    except json.JSONDecodeError:
                        continue
            return text
        if isinstance(content, list):
            fragments = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") in {None, "text"}
            ]
            merged = "".join(fragment for fragment in fragments if fragment)
            if merged.strip():
                return merged
        raise RuntimeError("CAMEL bridge HTTP generation returned no assistant content")

    def _build_openai_compatible_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        # Skip Authorization header for localhost, docker host, and LM Studio / LM Link
        is_local = self.model_url and any(
            host in self.model_url for host in ("127.0.0.1", "localhost", "::1", "host.docker.internal")
        )
        is_lm = self.model_platform in {"LM_STUDIO", "LMLINK"}
        if not (is_local or is_lm):
            api_key = self._get_api_key()
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
        if self.model_platform == "OPENROUTER":
            headers["HTTP-Referer"] = (
                os.getenv("OPENROUTER_HTTP_REFERER")
                or "https://github.com/bivex/loreSystem"
            )
            headers["X-Title"] = (
                os.getenv("OPENROUTER_X_TITLE") or "loreSystem CAMEL.Bridge"
            )
        return headers

    def _http_retry_attempts(self) -> int:
        raw = os.getenv("CAMEL_HTTP_RETRY_ATTEMPTS")
        try:
            return max(1, int(raw)) if raw else 3
        except ValueError:
            return 3

    def _http_retry_base_delay_seconds(self) -> float:
        raw = os.getenv("CAMEL_HTTP_RETRY_BASE_DELAY_SECONDS")
        try:
            return max(0.0, float(raw)) if raw else 1.0
        except ValueError:
            return 1.0

    def _sleep_before_retry(self, attempt: int) -> None:
        delay = self._http_retry_base_delay_seconds() * (2 ** max(0, attempt - 1))
        if delay > 0:
            time.sleep(delay)

    def _should_retry_http_status(self, status_code: int) -> bool:
        return status_code in {408, 409, 425, 429, 500, 502, 503, 504}

    def _is_retryable_http_exception(self, exc: Exception) -> bool:
        if isinstance(
            exc,
            (
                TimeoutError,
                socket.timeout,
                ConnectionError,
                ConnectionResetError,
                ConnectionAbortedError,
                http.client.RemoteDisconnected,
                ssl.SSLEOFError,
            ),
        ):
            return True
        if isinstance(exc, urllib_error.URLError):
            return (
                self._is_retryable_http_exception(exc.reason)
                if isinstance(exc.reason, Exception)
                else False
            )
        if isinstance(exc, ssl.SSLError):
            return True
        return False
