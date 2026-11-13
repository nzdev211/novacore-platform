"""Check whether the environment is prepared for a live Google ADK run.

This performs local checks only. It does not make network calls or validate that
a credential is accepted by Google.
"""
from __future__ import annotations

import importlib.metadata
import os
import sys


def main() -> int:
    problems: list[str] = []
    try:
        version = importlib.metadata.version("google-adk")
        print(f"google-adk: installed ({version})")
    except importlib.metadata.PackageNotFoundError:
        problems.append("google-adk is not installed; install the adapter extra.")

    try:
        import google.adk  # noqa: F401
        import google.genai  # noqa: F401
        print("Google ADK / GenAI imports: available")
    except ImportError as exc:
        problems.append(f"Google ADK imports failed: {exc}")

    model = os.getenv("NOVACORE_GEMINI_MODEL", "gemini-flash-latest")
    print(f"Model: {model}")

    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in {
        "1", "true", "yes"
    }
    if use_vertex:
        missing = [
            name for name in ("GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")
            if not os.getenv(name)
        ]
        if missing:
            problems.append(
                "Vertex AI mode is enabled but missing: " + ", ".join(missing)
            )
        else:
            print("Vertex AI configuration: project and location are set")
            print("Credentials: expected through Application Default Credentials")
    elif os.getenv("GOOGLE_API_KEY"):
        print("Google AI Studio API key: present (value not displayed)")
    else:
        problems.append(
            "No GOOGLE_API_KEY found. Set it for Google AI Studio, or enable "
            "Vertex AI with GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_CLOUD_PROJECT, "
            "GOOGLE_CLOUD_LOCATION, and Application Default Credentials."
        )

    if problems:
        for problem in problems:
            print(f"NOT READY: {problem}", file=sys.stderr)
        return 1

    print("Local preflight passed. This does not prove network access or credential validity.")
    print("Next: python examples/creative_studio_e2e/run_storyboard.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

