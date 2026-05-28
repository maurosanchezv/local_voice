# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **Windows-only**, fully offline speech-to-text desktop widget for accessibility (hands-free dictation, e.g. while gaming). It listens to the microphone, transcribes locally with Vosk, and types the result directly into whatever window has focus. UI text and code comments are in Spanish.

## Commands

```bash
# Install dependencies (use the local venv in env/ or your own)
pip install -r requirements.txt

# Run the app
python reconocimiento.py

# Type-check (mypy is the only quality tool configured; note the # type: ignore
# comments and types-* stubs in requirements.txt)
mypy reconocimiento.py

# Build a standalone Windows .exe into dist/TranscriptorVozLocal/
python build_exe.py
```

There is **no test suite** and no linter config. `env/` is a committed virtualenv (gitignored going forward); ignore everything under it.

## Vosk language models (required, not in the repo)

The app loads Vosk model folders by **hardcoded path** from the project root (`reconocimiento.py` `transcribe_audio`):
- Spanish → `vosk-model-small-es-0.42`
- Portuguese → `vosk-model-small-pt-0.3`
- English → `vosk-model-small-en` (i.e. `vosk-model-small-{lang}`)

These must be downloaded separately and placed in the root. If you change a model version, update the path string in `transcribe_audio`, the README, **and** the `--add-data` lines in `build_exe.py`. After building, the model folders must be manually copied into `dist/TranscriptorVozLocal/` (PyInstaller bundles them via `build_exe.py`, but verify they land there).

## Architecture

Everything lives in one file, `reconocimiento.py` (~430 lines). There are no classes — the CustomTkinter UI and all state are built at **module level** at the bottom of the file, and functions read/write module-global variables (`transcription_active`, `voice_control_active`, `is_new_sentence`, `loaded_models`, plus widget globals like `language_var`, `device_combobox`, `status_label`, `root`).

Key design points to understand before editing:

- **The audio loop runs on the Tkinter event loop, not in a worker thread.** `toggle_transcription` spawns a daemon thread only to call `transcribe_audio`, which opens the PyAudio stream and then drives transcription via `root.after(10, process_audio)`. `process_audio` reads a chunk, feeds Vosk, and **reschedules itself** with `root.after`. So all UI updates and audio polling happen on the main loop; `transcription_active = False` is the only stop signal, and it tears down the stream on the next tick.

- **Model caching for instant start/stop.** Loaded Vosk `Model` objects are kept in the `loaded_models` dict keyed by path, so toggling or switching language reuses an already-loaded model instead of paying the multi-second load again.

- **Output goes through `keyboard.write`, not the clipboard.** Transcribed text is typed into the focused window. `continuous_text_var` chooses the separator (space vs newline). `apply_formatting` handles capitalization state (`is_new_sentence`) and spoken-punctuation replacement (e.g. "punto" → ".") per language via regex tables.

- **Two input modes share the recognizer.** Final Vosk results are written out; partial results are only used for live feedback. When voice control is on (`voice_control_active`), `process_voice_command` intercepts *final* results matching command regexes (start/stop, change language, copy/clear) **before** they get typed.

- **Global F9 hotkey** toggles transcription regardless of focus (`keyboard.add_hotkey('f9', toggle_transcription)`), registered at import time.

- **Config** (selected mic + language) persists to `config.json` (gitignored). Device names are decoded with a `cp1252`→`utf-8` fixup in `get_audio_devices` to handle Windows accent characters.

## Known loose ends

- `clear_text` and `copy_text` are no-op placeholders, yet `process_voice_command` maps "copiar texto" / "limpiar texto" to them. The help dialog also says voice commands are disabled, while `voice_control_var` defaults to `True` — treat these as inconsistent and confirm intended behavior before relying on them.
