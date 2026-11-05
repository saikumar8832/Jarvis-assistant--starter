# Jarvis-style personal assistant - starter

A new sample created by Sai's AI assistant in November 2026 for Sai to review and learn from. It is not a recovered copy of Sai's lost project, and should not be presented as code he previously wrote. Nothing is published yet.

## What it does

A Python command-line assistant that responds to basic local text commands. Optional microphone input uses SpeechRecognition and Google's online speech recognition. Optional AI questions use an explicitly configured OpenAI-compatible chat completions endpoint. The starter does not execute arbitrary shell commands, control a computer, speak aloud, remember conversations, or include a graphical interface.

## Run text mode (Python 3.10+)

```sh
python jarvis.py
# Type help, time, date, hello, or quit
python -m unittest discover -s tests -v
```

## Optional microphone input

Install `SpeechRecognition` and `PyAudio` in a virtual environment following their current installation instructions, connect a working microphone, and run `python jarvis.py --voice`. Audio is sent to Google's speech recognition service; this requires internet and may be subject to its availability and terms. If the microphone or service fails, use text mode. The microphone integration has not been tested with a real device here.

## Optional AI

Use only a provider and HTTPS endpoint you trust. API use can cost money under your own provider's terms. It sends each `ai` question to that endpoint. Never commit keys to GitHub. Set these environment variables in your terminal using your provider's secure instructions:

- `JARVIS_AI_ENDPOINT`: full HTTPS chat completions endpoint, for a trusted provider.
- `JARVIS_MODEL`: a model supported by that provider.
- `JARVIS_API_KEY`: your provider key. Treat this as a secret.

Run `python jarvis.py --enable-ai`, then type `ai` followed by a question. The program sends no AI requests unless that flag is supplied and a question is entered. Requests time out after 20 seconds. The API integration is tested with a mock, not a real provider; compatibility and pricing depend on the chosen provider. AI responses may be wrong. Do not submit confidential data or secrets in questions.

## Privacy and limits

The program does not write conversation logs, but your terminal and external providers may retain data. Local time/date is determined by the machine's timezone. Voice recognition is optional and uses an external service; AI is optional and sends prompts to the endpoint you choose. No actual API keys are included.
