"""A small, local-first assistant. New sample, not a recovery of lost code."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_RESPONSE_BYTES = 1_000_000


def ask_ai(prompt: str, endpoint: str, model: str, api_key: str) -> str:
    """Send the prompt only after the user explicitly enables the AI mode."""
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("AI endpoint must be an HTTPS URL without embedded credentials")
    if not model or not api_key:
        raise ValueError("Set JARVIS_MODEL and JARVIS_API_KEY before using AI mode")
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode()
    request = urllib.request.Request(endpoint, data=payload, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {api_key}"
    }, method="POST")
    try:
        # Refuse redirects: credentials must not be sent to a different destination.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=20) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("AI response was too large")
        result = json.loads(raw)
        answer = result["choices"][0]["message"]["content"]
        if not isinstance(answer, str):
            raise ValueError("AI response did not contain text")
        return answer.strip()
    except (urllib.error.URLError, OSError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("AI request failed or returned an unsupported response") from exc


def respond(text: str, now: dt.datetime | None = None) -> str:
    command = text.strip().lower()
    current = now or dt.datetime.now().astimezone()
    if command in {"help", "?"}:
        return "Commands: time, date, hello, help, quit. Optional AI: ai <question>."
    if command in {"hello", "hi"}:
        return "Hello! How can I help?"
    if command in {"time", "what time is it", "what time is it?"}:
        return "Local time: " + current.strftime("%H:%M %Z")
    if command in {"date", "what is the date", "what is the date?"}:
        return "Local date: " + current.strftime("%Y-%m-%d")
    return "I don't know that command. Type help for the available commands."


def listen() -> str:
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise RuntimeError("Install SpeechRecognition and PyAudio to use microphone mode.") from exc
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening (speech is sent to Google's speech recognition service)...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)
        return recognizer.recognize_google(audio)
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        print("I couldn't understand that audio.")
        return ""
    except (sr.RequestError, OSError) as exc:
        raise RuntimeError("Microphone or speech recognition service failed.") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local-first Jarvis-style command assistant")
    parser.add_argument("--voice", action="store_true", help="Use microphone and Google's online speech recognition")
    parser.add_argument("--enable-ai", action="store_true", help="Allow ai commands to send text to a configured API")
    args = parser.parse_args(argv)
    print("Jarvis starter - type help; type quit to exit.")
    if args.voice:
        print("Voice mode sends recorded speech to Google. Stop with Ctrl+C.")
    while True:
        try:
            text = listen() if args.voice else input("> ")
            text = text.strip()
            if not text:
                continue
            if text.lower() in {"quit", "exit"}:
                print("Goodbye.")
                return 0
            if re.match(r"^ai\s+", text, re.IGNORECASE):
                if not args.enable_ai:
                    print("AI is disabled. Restart with --enable-ai to permit API requests.")
                    continue
                endpoint = os.environ.get("JARVIS_AI_ENDPOINT", "")
                try:
                    answer = ask_ai(text.split(None, 1)[1], endpoint, os.environ.get("JARVIS_MODEL", ""), os.environ.get("JARVIS_API_KEY", ""))
                    print(answer)
                except (ValueError, RuntimeError) as exc:
                    print(f"AI error: {exc}")
            else:
                print(respond(text))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
