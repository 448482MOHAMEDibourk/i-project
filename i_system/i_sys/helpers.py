from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Tuple

import requests
from src.config.settings import settings

"""Helpers to check local AI services (Ollama, Aider) for i_system.

Reads optional header config from env (AIDER_HEADERS, OLLAMA_HEADERS) as JSON
and falls back to `ai-sources.yaml` for URLs and default models.
"""


def _read_ai_sources_fallback() -> dict:
    root = Path(__file__).parent
    f = root / "../ai-sources.yaml"
    out = {}
    if not f.exists():
        return out
    section = None
    with f.open("r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.endswith(":"):
                section = s[:-1].strip()
                continue
            if ":" in s and section:
                k, v = s.split(":", 1)
                k = k.strip()
                v = v.strip().strip('"')
                out.setdefault(section, {})[k] = v
    return out


def _headers_from_env(name: str) -> Dict[str, str]:
    s = os.getenv(name, "")
    if not s:
        return {}
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        # try simple KEY=VAL;KEY2=VAL2 format
        out = {}
        for part in s.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                out[k.strip()] = v.strip()
        return out
    return {}


def check_ollama(
    base_url: str | None = None, model: str | None = None, timeout: int = 5
) -> Tuple[bool, str]:
    ai = _read_ai_sources_fallback()
    base_url = (
        base_url
        or settings.get("OLLAMA_URL")
        or ai.get("ollama", {}).get("url")
        or "http://localhost:11434"
    )
    model = (
        model
        or settings.get("OLLAMA_MODEL")
        or ai.get("ollama", {}).get("default_model")
        or "mistral"
    )
    headers = _headers_from_env("OLLAMA_HEADERS")

    # 1) Quick GET / root check
    try:
        url = f"{base_url.rstrip('/')}/"
        resp = requests.get(url, timeout=timeout, headers=headers)
        if 200 <= resp.status_code < 300:
            # return short body or JSON
            ct = resp.headers.get("Content-Type", "")
            if "application/json" in ct:
                try:
                    j = resp.json()
                    return True, json.dumps(j, ensure_ascii=False)[:400]
                except Exception:
                    return True, resp.text[:400]
            return True, resp.text[:400]
    except Exception:
        # proceed to additional probes
        pass

    # 2) Try listing models via /api/tags (common Ollama endpoint)
    first_model = None
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        resp = requests.get(url, timeout=timeout, headers=headers)
        if 200 <= resp.status_code < 300:
            try:
                j = resp.json()
                # confirm structure
                if isinstance(j, dict) and "models" in j:
                    models = j.get("models") or []
                    if isinstance(models, list) and len(models) > 0:
                        # extract model name if available
                        m0 = models[0]
                        if isinstance(m0, dict) and "model" in m0:
                            first_model = m0.get("model") or m0.get("name")
                        elif isinstance(m0, str):
                            first_model = m0
                    return True, json.dumps(j, ensure_ascii=False)[:400]
            except Exception:
                return True, resp.text[:400]
    except Exception:
        pass

    # 3) If we have (or were given) a model name, attempt a lightweight POST to a generate endpoint
    # to validate generation works. Use model from args/settings or first_model found above.
    chosen_model = model or first_model
    if chosen_model:
        paths = [
            "/api/generate",
            "/api/completions",
            "/v1/generate",
            "/v1/completions",
        ]
        payload = {"model": chosen_model, "prompt": "i_system health check: اختبار"}
        last_err = None
        for p in paths:
            url = f"{base_url.rstrip('/')}{p}"
            try:
                resp = requests.post(url, json=payload, timeout=timeout, headers=headers)
                if 200 <= resp.status_code < 300:
                    try:
                        j = resp.json()
                        return True, json.dumps(j, ensure_ascii=False)[:400]
                    except Exception:
                        return True, resp.text[:400]
                try:
                    body = resp.text
                except Exception:
                    body = "<no-body>"
                last_err = f"HTTP {resp.status_code}: {body[:200]} (path {p})"
            except Exception as e:
                last_err = e

        if last_err is None:
            return False, "[error] Ollama generate request failed: no response and no exception"
        return False, f"[error] Ollama generate request failed: {last_err}"

    return False, "[error] Ollama health check failed: no reachable endpoint or model discovered"


def check_aider(endpoint: str | None = None, timeout: int = 5) -> Tuple[bool, str]:
    ai = _read_ai_sources_fallback()
    endpoint = (
        endpoint
        or settings.get("AIDER_ENDPOINT")
        or ai.get("aider", {}).get("endpoint")
        or "http://localhost:8000"
    )
    headers = _headers_from_env("AIDER_HEADERS")
    paths = ["/ask", "/v1/ask", "/api/ask", "/generate"]

    last_err = None
    for p in paths:
        url = endpoint.rstrip("/") + p
        try:
            resp = requests.post(
                url,
                json={"prompt": "i_system health check: اختبار"},
                timeout=timeout,
                headers=headers,
            )
            if 200 <= resp.status_code < 300:
                ct = resp.headers.get("Content-Type", "")
                if "application/json" in ct:
                    try:
                        j = resp.json()
                        return True, json.dumps(j, ensure_ascii=False)[:400]
                    except Exception:
                        return True, resp.text[:400]
                return True, resp.text[:400]
            try:
                body = resp.text
            except Exception:
                body = "<no-body>"
            last_err = f"HTTP {resp.status_code}: {body[:200]}"
        except Exception as e:
            last_err = e

    if last_err is None:
        return False, "[error] Aider request failed: no response and no exception"
    return False, f"[error] Aider request failed: {last_err}"


if __name__ == "__main__":
    ok, msg = check_ollama()
    print("Ollama:", "OK" if ok else "FAIL", msg)
    ok, msg = check_aider()
    print("Aider:", "OK" if ok else "FAIL", msg)
