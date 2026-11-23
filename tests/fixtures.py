def sample_cricsheet_match():
    def b(runs, extra_runs=0, **kw):
        d = {"batter": "Bat One", "bowler": "Bowl One", "non_striker": "Bat Two",
             "runs": {"batter": runs, "extras": extra_runs, "total": runs + extra_runs}}
        d.update(kw)
        return d

    return {
        "info": {
            "match_type": "T20", "dates": ["2026-01-05"], "teams": ["Team X", "Team Y"],
            "venue": "Test Ground", "event": {"name": "Test League"},
            "outcome": {"winner": "Team X"},
            "registry": {"people": {"Bat One": "b1", "Bat Two": "b2", "Bowl One": "w1"}},
        },
        "innings": [
            {"team": "Team X", "overs": [
                {"over": 0, "deliveries": [
                    b(1),
                    b(0, 1, extras={"wides": 1}),
                    b(0, wickets=[{"player_out": "Bat One", "kind": "bowled"}]),
                ]},
                {"over": 17, "deliveries": [b(6)]},
            ]},
            {"team": "Team Y", "overs": [{"over": 0, "deliveries": [b(4)]}]},
            {"team": "Team X", "super_over": True, "overs": [{"over": 0, "deliveries": [b(6)]}]},
        ],
    }
