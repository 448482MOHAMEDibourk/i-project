"""Minimal Aider HTTP client wrapper.
This wrapper will attempt to POST to a reasonable endpoint under AIDER_ENDPOINT
and return a tuple `(ok: bool, message: str)` where `message` is the response text
on success or an error string prefixed with "[error]" on failure.
"""

import json
import os
from typing import Tuple

import requests


DEFAULT_AIDER_ENDPOINT = "http://localhost:8000"


class AiderClient:
    def __init__(self, endpoint: str | None = None, headers: dict | None = None):
        # Read environment at construction time (not import time) so callers
        # can inject `endpoint` during tests or orchestration.
        self.endpoint = endpoint or os.getenv("AIDER_ENDPOINT", DEFAULT_AIDER_ENDPOINT)
        self.headers = headers or {}

    def ask(self, prompt: str, timeout: int = 5) -> Tuple[bool, str]:
        """Try a few common paths and return (ok, message).

        Returns:
            Tuple[bool, str]: `(True, text)` on success or `(False, "[error] ...")` on failure.
        """
        paths = ["/ask", "/v1/ask", "/api/ask", "/generate"]
        payload = {"prompt": prompt}

        last_err = None
        for p in paths:
            url = self.endpoint.rstrip("/") + p
            try:
                resp = requests.post(
                    url, json=payload, timeout=timeout, headers=self.headers
                )
                if 200 <= resp.status_code < 300:
                    # prefer plain text, fall back to json->text
                    ct = resp.headers.get("Content-Type", "")
                    if "application/json" in ct:
                        try:
                            j = resp.json()
                            text = j.get("text") or j.get("output") or json.dumps(j, ensure_ascii=False)
                        except Exception:
                            text = resp.text
                        return True, text
                    return True, resp.text
                # non-2xx -> record and try next path
                try:
                    body = resp.text
                except Exception:
                    body = "<no-body>"
                last_err = f"HTTP {resp.status_code}: {body[:200]}"
            except Exception as e:
                # record exception and try next path
                last_err = e

        # After trying all paths, return a clear error tuple
        if last_err is None:
            return False, "[error] Aider request failed: no response and no exception"
        return False, f"[error] Aider request failed: {last_err}"
