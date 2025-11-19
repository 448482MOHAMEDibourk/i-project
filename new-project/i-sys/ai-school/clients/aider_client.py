"""Minimal Aider HTTP client wrapper.
This wrapper will attempt to POST to a reasonable endpoint under AIDER_ENDPOINT
and return the text body or an error string prefixed with [error].
"""

import os

import requests

AIDER_ENDPOINT = os.getenv("AIDER_ENDPOINT", "http://localhost:8000")


class AiderClient:
    def __init__(self, endpoint: str | None = None, headers: dict | None = None):
        self.endpoint = endpoint or AIDER_ENDPOINT
        self.headers = headers or {}

    def ask(self, prompt: str, timeout: int = 5) -> str:
        """Try a few common paths and return response text or error string.

        Returns:
            str: response text on success or string starting with "[error]" on failure.
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
                        j = resp.json()
                        return j.get("text") or j.get("output") or str(j)
                    return resp.text
                # non-2xx -> record and try next path
                try:
                    body = resp.text
                except Exception:
                    body = "<no-body>"
                last_err = f"HTTP {resp.status_code}: {body[:200]}"
            except Exception as e:
                # record exception and try next path
                last_err = e

        # After trying all paths, return a clear error string
        if last_err is None:
            return "[error] Aider request failed: no response and no exception"
        return f"[error] Aider request failed: {last_err}"
