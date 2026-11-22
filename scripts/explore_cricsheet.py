"""Week 1: explore Cricsheet ball-by-ball JSON before writing the Week 2 importer.

Usage:  python scripts/explore_cricsheet.py data/cricsheet
Download JSON files from https://cricsheet.org/downloads/ (e.g. ipl_json.zip,
t20s_json.zip) and unzip them into data/cricsheet/.
"""
import json, sys
from collections import defaultdict
from pathlib import Path


def phase(over, match_type):
    if match_type == "T20":
        return "powerplay" if over < 6 else "middle" if over < 16 else "death"
    return "other"


def main(folder):
    files = sorted(Path(folder).glob("*.json"))
    if not files:
        sys.exit(f"No .json files in {folder}. Download from cricsheet.org first.")

    matches = deliveries = wickets = 0
    types = defaultdict(int)
    bowl = defaultdict(lambda: {"balls": 0, "runs": 0, "wkts": 0, "dots": 0})
    phases = defaultdict(lambda: {"balls": 0, "runs": 0})

    for f in files:
        data = json.loads(f.read_text())
        info = data["info"]
        mtype = info.get("match_type", "?")
        types[mtype] += 1
        matches += 1
        for inn in data.get("innings", []):
            for ov in inn.get("overs", []):
                for d in ov["deliveries"]:
                    deliveries += 1
                    extras = d.get("extras", {})
                    legal = not ("wides" in extras or "noballs" in extras)
                    runs = d["runs"]["total"] - extras.get("byes", 0) - extras.get("legbyes", 0)
                    b = bowl[d["bowler"]]
                    if legal:
                        b["balls"] += 1
                    b["runs"] += runs
                    if legal and runs == 0:
                        b["dots"] += 1
                    for w in d.get("wickets", []):
                        wickets += 1
                        if w["kind"] not in ("run out", "retired hurt", "retired out"):
                            b["wkts"] += 1
                    p = phases[phase(ov["over"], mtype)]
                    p["balls"] += 1 if legal else 0
                    p["runs"] += runs

    print(f"Matches: {matches}   Deliveries: {deliveries}   Wicket events: {wickets}")
    print("Match types:", dict(types))
    print("\nTop 10 bowlers by wickets (min 60 balls):")
    rows = [(n, s) for n, s in bowl.items() if s["balls"] >= 60]
    for n, s in sorted(rows, key=lambda x: -x[1]["wkts"])[:10]:
        econ = s["runs"] / (s["balls"] / 6)
        print(f"  {n:<22} wkts={s['wkts']:<4} econ={econ:5.2f} dot%={100*s['dots']/s['balls']:4.1f}")
    print("\nRuns per over by phase:")
    for k, p in phases.items():
        if p["balls"]:
            print(f"  {k:<10} {6*p['runs']/p['balls']:.2f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/cricsheet")
