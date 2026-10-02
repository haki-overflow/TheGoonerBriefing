import os
import json
import requests


def load_env(path=".env"):
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ[key] = value


load_env()
headers = {"X-Auth-Token": os.environ["FOOTBALL_DATA_KEY"]}
base = "https://api.football-data.org/v4"

# 1. Get finished Premier League matches
r = requests.get(
    f"{base}/competitions/PL/matches",
    params={"status": "FINISHED"},
    headers=headers,
)
print("Status code:", r.status_code)
if r.status_code != 200:
    print(r.text)
    raise SystemExit

matches = r.json().get("matches", [])
print("Finished matches found:", len(matches))
last = matches[-1]
home = last["homeTeam"]["name"]
away = last["awayTeam"]["name"]
score = last["score"]["fullTime"]
print(f"Latest match: {home} {score['home']}-{score['away']} {away}")

# 2. Get that one match in detail
d = requests.get(f"{base}/matches/{last['id']}", headers=headers).json()
print("\nFields in match detail:", list(d.keys()))
print("\nGOALS:", json.dumps(d.get("goals"), indent=2)[:1500])
print("\nBOOKINGS:", json.dumps(d.get("bookings"), indent=2)[:800])