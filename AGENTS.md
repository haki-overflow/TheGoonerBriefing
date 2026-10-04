# The Gooner Briefing: agent brief

A weekly ~4 minute Premier League audio recap built for ONE real friend who supports Arsenal.
Code finds the facts. Gemma writes the narration. A voice model reads it aloud. Everything runs locally on open models.

Deadline: Mon 5 Oct 2026, 12:29 PM IST (DEV Hacktoberfest Weekend Challenge, "Build for a Friend").
Priority order if time runs short: one full working episode > mood dial > demo clips in 3 moods > fact-checker > the rest.

## Who does what

| Who | Job | Model |
| --- | --- | --- |
| Product narrator | Writes the weekly script inside script.py | Gemma 4 12B QAT, `google/gemma-4-12b-qat` via LM Studio. NEVER change this. |
| OpenCode | Builds and fixes the code, one task at a time | Big Pickle (free, hosted via OpenCode Zen). Not part of the product. |
| OpenClaw | Tests, debugs, reports. Does NOT edit code | Whatever model the user configures. Not part of the product. |

- Only ONE agent edits files at a time.
- OpenClaw writes findings to ISSUES.md. OpenCode applies the fixes.
- Big Pickle is hosted in the cloud, so it does not use the GPU. Keep Gemma loaded in LM Studio the whole time, because the pipeline needs it.
- PRIVACY: during its free period, Big Pickle may collect data to improve the model, and anything the agent reads or prints is sent to OpenCode's servers. So never read or print `.env`, and never paste secrets or personal data (such as the friend's private messages) into the session. The PRODUCT itself (Gemma + Kokoro) still runs fully locally.
- Free models can rotate or be rate limited. If Big Pickle stops responding, switch with `/models` and carry on.

## Pipeline

```
facts.py  ->  episodes/facts.json
script.py ->  episodes/script.txt      (Gemma, with mood)
factcheck.py (checks script against facts.json)
tts.py    ->  episodes/episode.mp3     (Kokoro)
run.py    ->  runs all of the above in one command
```

## Hard rules (never break)

1. NEVER open, print, log, copy or commit `.env`. It holds a secret API key. Read it only through `os.environ` after the existing `load_env` helper runs.
2. Gemma must use ONLY facts in `episodes/facts.json`. No invented players, scores, minutes, quotes, injuries or reasons. No "colour" such as "a quiet game" or "chaotic" unless the facts support it.
3. Mood changes tone, NEVER facts. Mood is picked by code from the data, not by the LLM.
4. Do not add dependencies without telling the user. Use `uv add`. Run everything with `uv run`.
5. Keep code simple, with short plain comments. The user is a beginner and must be able to explain it.
6. Never overwrite `episodes/script.txt` with empty text.
7. `models/`, `.env`, `.venv/` and `episodes/*.wav` stay out of git.
8. Ask before doing anything outside the assigned task.

## Environment

- Linux (Omarchy/Arch). Project folder: `~/TheGoonerBriefing`. Package manager: `uv`.
- Python is pinned to 3.12 (`pyproject.toml` says `requires-python = ">=3.12"`). Check with `uv run python --version`.
- Installed: requests, pyyaml, openai (only as a client for LM Studio), kokoro-onnx, soundfile.
- LM Studio server: `http://localhost:1234/v1`, API key `"lm-studio"`, model `"google/gemma-4-12b-qat"`.
- Gemma 4 "thinks" before answering. It needs `max_tokens=12000` and LM Studio Context Length 16384 with Parallel 1. An empty `content` with `finish_reason: "length"` means it ran out of room while thinking: retry, never save empty text.
- Voice files are in `models/` (`kokoro-v1.0.onnx`, `voices-v1.0.bin`). Default voice `bm_george`, `lang="en-gb"`.

## Data sources

- FPL API (`https://fantasy.premierleague.com/api`), no key. Used for results, scorers, hat-tricks, red cards.
- football-data.org, key in `.env` as `FOOTBALL_DATA_KEY`. The FREE tier has NO scorers, minutes or cards, so use it ONLY for the league table and fixtures.
- There are no goal minutes anywhere, so late winners and comebacks are out of scope. Say so honestly in the README.

## Current status (update HANDOFF.md as this changes)

- DONE: `facts.py` works and writes `episodes/facts.json` (latest finished gameweek, Arsenal result, hat-tricks, red cards, big margins, next fixture).
- PARTLY: `script.py` produced a good 526-word script once, then returned empty replies several times (Gemma ran out of room while thinking).
- WRITTEN, NOT YET RUN: `tts.py` (splits the script into chunks, speaks with Kokoro, writes `episodes/episode.wav` then `episode.mp3` with ffmpeg).
- NOT STARTED: moods, mood.py, factcheck.py, league table, run.py, config.yaml, tests, README.

## Mood spec

Code computes the score from `facts.json["arsenal"]`:

- result: win +5, draw 0, loss -5
- goal difference clamped to -3..+3, added
- label: `smug` if score >= 5, `gutted` if score <= -4, else `neutral`
- env var `MOOD` (or CLI flag `--mood`) overrides it

Each mood is a YAML file in `moods/` with: `name`, `prompt` (tone instructions only), `opener` (fixed first line), `voice`, `speed`. Example:

```yaml
name: gutted
prompt: >
  You are devastated but still loyal. Short, flat sentences. Dark humour.
  Never make up an excuse that is not in the facts.
opener: "Right. Sit down. We need to talk about the weekend."
voice: bm_george
speed: 0.92
```

Check which Kokoro voices actually exist before choosing others (e.g. `bm_lewis`, `bf_emma`). If a voice name does not exist, fall back to `bm_george` and print a warning.

## Fact-check spec

- Split the script into sentences.
- For each sentence, every capitalised name (player, team) and every number or number-word must be traceable to `facts.json`. Allow common words and the speakable forms of scores ("three-zero").
- If a sentence fails, ask Gemma to rewrite ONLY that sentence using the facts (max 3 tries). If it still fails, drop the sentence.
- Log every rejection to `episodes/rejections.log` with: the sentence, what was wrong, the attempt number.
- `run.py --no-factcheck` skips this step. It exists so we can compare invented-fact counts with the check off and on.

## Handoff protocol

- `HANDOFF.md`: OpenCode appends after each task: task name, files changed, the exact command to test it, what the expected result is.
- `ISSUES.md`: OpenClaw writes newest first. Each issue: command run, exact output (trimmed), likely cause (say if guessing), suggested fix. OpenCode marks fixed issues with `[x]`.
- OpenCode starts every session by reading `ISSUES.md` and `HANDOFF.md`.

## Definition of done

- `uv run run.py --mood gutted` produces `episodes/episode.mp3` of about 3 to 5 minutes with no errors.
- All three moods work and sound different.
- `uv run pytest` passes.
- README explains setup, how it works, and what is out of scope.
