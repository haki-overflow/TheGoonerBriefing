import json
from pathlib import Path

import requests

BASE = "https://fantasy.premierleague.com/api"
TEAM = "Arsenal"


def get(path):
    r = requests.get(f"{BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


boot = get("/bootstrap-static/")
players = {p["id"]: p["web_name"] for p in boot["elements"]}
teams = {t["id"]: t["name"] for t in boot["teams"]}
my_id = next(i for i, n in teams.items() if n == TEAM)

fixtures = get("/fixtures/")
by_gw = {}
for f in fixtures:
    if f["event"]:
        by_gw.setdefault(f["event"], []).append(f)

# latest gameweek where every match is finished
done = [g for g, fs in by_gw.items() if all(x["finished_provisional"] for x in fs)]
gw = max(done)
week = by_gw[gw]


def stat(f, ident):
    out = []
    for s in f["stats"]:
        if s["identifier"] == ident:
            for side in ("h", "a"):
                for item in s[side]:
                    out.append({"player": players[item["element"]], "n": item["value"], "side": side})
    return out


results, moments, arsenal = [], [], None
for f in week:
    h, a = teams[f["team_h"]], teams[f["team_a"]]
    hs, as_ = f["team_h_score"], f["team_a_score"]
    label = f"{h} {hs}-{as_} {a}"
    results.append({"home": h, "away": a, "home_score": hs, "away_score": as_})

    for g in stat(f, "goals_scored"):
        if g["n"] >= 3:
            team = h if g["side"] == "h" else a
            moments.append({"type": "hat_trick", "score": 10, "player": g["player"],
                            "team": team, "goals": g["n"], "match": label})
    for c in stat(f, "red_cards"):
        team = h if c["side"] == "h" else a
        moments.append({"type": "red_card", "score": 7, "player": c["player"],
                        "team": team, "match": label})
    if abs(hs - as_) >= 4:
        moments.append({"type": "big_margin", "score": 6, "match": label})

    if my_id in (f["team_h"], f["team_a"]):
        home = f["team_h"] == my_id
        mine, theirs = (hs, as_) if home else (as_, hs)
        side = "h" if home else "a"
        arsenal = {
            "opponent": a if home else h,
            "home": home,
            "goals_for": mine,
            "goals_against": theirs,
            "result": "W" if mine > theirs else "D" if mine == theirs else "L",
            "scorers": [{"player": g["player"], "goals": g["n"]}
                        for g in stat(f, "goals_scored") if g["side"] == side],
        }

upcoming = sorted(
    [f for f in fixtures
     if not f["finished_provisional"] and f["kickoff_time"] and my_id in (f["team_h"], f["team_a"])],
    key=lambda f: f["kickoff_time"],
)
next_fixture = None
if upcoming:
    n = upcoming[0]
    home = n["team_h"] == my_id
    next_fixture = {
        "opponent": teams[n["team_a"] if home else n["team_h"]],
        "home": home,
        "kickoff_utc": n["kickoff_time"],
    }

moments.sort(key=lambda m: -m["score"])
facts = {
    "team": TEAM,
    "gameweek": gw,
    "arsenal": arsenal,
    "results": results,
    "moments": moments[:6],
    "next_fixture": next_fixture,
}

Path("episodes").mkdir(exist_ok=True)
Path("episodes/facts.json").write_text(json.dumps(facts, indent=2))
print(json.dumps(facts, indent=2))