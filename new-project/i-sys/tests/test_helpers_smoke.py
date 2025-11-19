"""Simple smoke runner for i_sys.helpers (no pytest required).

Run with: python3 tests/test_helpers_smoke.py
"""

from i_sys.helpers import check_aider, check_ollama


def main():
    ok, msg = check_ollama(base_url="http://invalid.local:12345")
    print("Ollama check ->", ok, msg)
    ok2, msg2 = check_aider(endpoint="http://invalid.local:12345")
    print("Aider check ->", ok2, msg2)


if __name__ == "__main__":
    main()
