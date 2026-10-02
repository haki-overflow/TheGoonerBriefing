import json
from pathlib import Path

from openai import OpenAI

MOOD = "neutral"  # try: smug, gutted, neutral

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
facts = json.loads(Path("episodes/facts.json").read_text())

system = """You write a short weekly Premier League audio recap for one friend who supports Arsenal.
You sound like a mate chatting, not a stats feed.

HARD RULES:
- Use ONLY the facts in the JSON. Never invent players, scores, quotes, minutes, injuries or reasons.
- If something is not in the facts, do not mention it.
- Write for the ear: short sentences, no lists, no brackets, no emojis, no headings.
- Say scores in words, like "two-one".
- About 450 to 550 words.

STRUCTURE:
1. Start with Arsenal's result and who scored.
2. Then the notable moments from around the league (hat-tricks and red cards first).
3. End with Arsenal's next fixture.

Output only the words to be spoken."""

user = f"Mood for this episode: {MOOD}\n\nFACTS:\n{json.dumps(facts, indent=2)}"

resp = client.chat.completions.create(
    model="google/gemma-4-12b-qat",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    temperature=0.6,
    max_tokens=6000,
)

print(resp.model_dump_json(indent=2)[:3000])

text = (resp.choices[0].message.content or "").strip()
Path("episodes/script.txt").write_text(text)
print("\nWords:", len(text.split()))
