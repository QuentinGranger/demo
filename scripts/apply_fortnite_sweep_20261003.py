#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import apply_crash_bandicoot_override_20260828 as competitive_helper
import apply_fortnite_sweep_20260829 as base


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-10-03T10:44:54Z"


def make(spec):
    base.OFFICIAL_SCHEDULE = spec["source"]
    record = base.comp(
        spec["competition_id"],
        spec["name"],
        spec["competition_class"],
        spec["ruleset"],
        spec["team_format"],
        spec["platform_scope"],
        spec["sessions"][0][2],
        spec["sessions"][-1][3],
        sessions=spec["sessions"],
        series=spec["series_id"],
    )
    record["official_event_id"] = spec.get("official_event_id")
    record["official_event_slug"] = spec.get("official_event_id")
    record["eligibility"] = spec.get("eligibility", {"status": "UNKNOWN"})
    record["qualification"] = spec.get("qualification")
    record["prize_pool"] = spec.get("prize_pool")
    record["history"][0]["at"] = AT
    for phase in record["phases"]:
        for session in phase["sessions"]:
            session["source_url"] = spec["source"]
    for patch in spec.get("session_patches", []):
        record["phases"][0]["sessions"][patch["index"]].update(patch["values"])
    return record


SPECS = [
    {
        "competition_id": "console-zb-solo-victory-eu-20261003",
        "official_event_id": "S42_ConsoleVCC_SolosZB",
        "series_id": "CONSOLE_VICTORY_CUP",
        "name": "Console Zero Build Solo Victory Cup — Europe — 3 octobre 2026",
        "competition_class": "VICTORY_CUP",
        "ruleset": "ZERO_BUILD",
        "team_format": "SOLOS",
        "platform_scope": "CONSOLE",
        "source": "https://www.fortnite.com/competitive/events/S42_ConsoleVCC_SolosZB/?lang=fr&region=EU",
        "sessions": [
            ("round1", "Console Zero Build Solo Victory Cup — round 1", "2026-10-03T12:00:00+02:00", "2026-10-03T14:00:00+02:00"),
            ("round2", "Console Zero Build Solo Victory Cup — round 2", "2026-10-03T15:00:00+02:00", "2026-10-03T16:00:00+02:00"),
        ],
        "eligibility": {
            "status": "CONFIRMED",
            "minimum_rank": "Gold or higher in Combined Ranked in the previous or current season",
            "age_min": 13,
            "two_factor_required": True,
            "region_lock": "EU",
            "platform_requirements": "CONSOLE",
            "team_requirements": "SOLOS",
        },
        "qualification": {"round1_eu_to_round2": 2000},
        "prize_pool": {"round_2_victory_royale_usd": 100},
        "session_patches": [
            {"index": 0, "values": {"qualification": {"advances_to": "round 2", "eu_slots": 2000}}},
            {"index": 1, "values": {"prize": {"type": "VICTORY_ROYALE", "amount_usd": 100}}},
        ],
    },
    {
        "competition_id": "mobile-reload-mini-venture-victory-eu-20261003",
        "official_event_id": "S42_MobileVictoryCup",
        "series_id": "MOBILE_VICTORY_CUP",
        "name": "Mobile Reload (Mini Venture) Victory Cup — Europe — 3 octobre 2026",
        "competition_class": "VICTORY_CUP",
        "ruleset": "RELOAD",
        "team_format": "SOLOS",
        "platform_scope": "MOBILE",
        "source": "https://www.fortnite.com/competitive/events/S42_MobileVictoryCup/?lang=fr&region=EU",
        "sessions": [
            ("round1", "Mobile Reload (Mini Venture) Victory Cup — round 1", "2026-10-03T16:00:00+02:00", "2026-10-03T17:15:00+02:00"),
            ("round2", "Mobile Reload (Mini Venture) Victory Cup — round 2", "2026-10-03T18:00:00+02:00", "2026-10-03T19:10:00+02:00"),
        ],
        "eligibility": {
            "status": "CONFIRMED",
            "minimum_rank": "Platinum or higher in Reload Ranked in the previous or current season",
            "age_min": 13,
            "two_factor_required": True,
            "region_lock": "EU",
            "platform_requirements": "MOBILE",
            "team_requirements": "SOLOS",
        },
        "qualification": {"round1_eu_to_round2": 176},
        "prize_pool": {"round_2_victory_royale_usd": 50},
        "session_patches": [
            {"index": 0, "values": {"qualification": {"advances_to": "round 2", "eu_slots": 176}}},
            {"index": 1, "values": {"prize": {"type": "VICTORY_ROYALE", "amount_usd": 50}}},
        ],
    },
    {
        "competition_id": "duos-ranked-br-eu-20261003",
        "series_id": "RANKED_CUP",
        "name": "Duos Ranked Cup (Battle Royale) — Europe — 3 octobre 2026",
        "competition_class": "RANKED_CUP",
        "ruleset": "BUILD",
        "team_format": "DUOS",
        "platform_scope": "ALL_SUPPORTED",
        "source": "https://www.fortnite.com/competitive/?lang=fr&region=EU",
        "sessions": [("session1", "Duos Ranked Cup (Battle Royale)", "2026-10-03T17:00:00+02:00", "2026-10-03T20:00:00+02:00")],
    },
    {
        "competition_id": "duos-ranked-zb-eu-20261003",
        "series_id": "RANKED_CUP",
        "name": "Duos Ranked Cup (Zero Build) — Europe — 3 octobre 2026",
        "competition_class": "RANKED_CUP",
        "ruleset": "ZERO_BUILD",
        "team_format": "DUOS",
        "platform_scope": "ALL_SUPPORTED",
        "source": "https://www.fortnite.com/competitive/?lang=fr&region=EU",
        "sessions": [("session1", "Duos Ranked Cup (Zero Build)", "2026-10-03T17:00:00+02:00", "2026-10-03T20:00:00+02:00")],
    },
    {
        "competition_id": "arenas-test-eu-20261004",
        "official_event_id": "S42_ArenaTestCup",
        "series_id": "ARENAS_TEST",
        "name": "Arenas Test Cup — Europe — 4 octobre 2026",
        "competition_class": "TEST_CUP",
        "ruleset": "UNKNOWN",
        "team_format": "UNKNOWN",
        "platform_scope": "ALL_SUPPORTED",
        "source": "https://www.fortnite.com/competitive/events/S42_ArenaTestCup/?lang=fr&region=EU",
        "sessions": [("session1", "Arenas Test Cup", "2026-10-04T13:00:00+02:00", "2026-10-04T15:00:00+02:00")],
    },
    {
        "competition_id": "reload-zb-duos-cash-eu-20261004",
        "official_event_id": "S42_ReloadCashCup_DuosZB",
        "series_id": "RELOAD_CASH_CUP",
        "name": "Reload ZB Duos Cash Cup — Europe — 4 octobre 2026",
        "competition_class": "CASH_CUP",
        "ruleset": "ZERO_BUILD",
        "team_format": "DUOS",
        "platform_scope": "ALL_SUPPORTED",
        "source": "https://www.fortnite.com/competitive/events/S42_ReloadCashCup_DuosZB/?lang=fr&region=EU",
        "sessions": [("round1", "Reload ZB Duos Cash Cup — round 1", "2026-10-04T13:00:00+02:00", "2026-10-04T15:30:00+02:00")],
    },
]


def main():
    base.AT = AT
    ledger_path = CAL / "fortnite-competitive-ledger-france.json"
    ledger = base.load(ledger_path)
    existing = {item.get("competition_id") for item in ledger.get("competitions", [])}
    records = [make(spec) for spec in SPECS]
    added = [record for record in records if record["competition_id"] not in existing]
    if not added:
        print("No-op: all October 3–4 routine EU sessions already exist.")
        return

    ledger.setdefault("competitions", []).extend(added)
    ledger["updated_at"] = AT
    base.dump(ledger_path, ledger)

    change_path = CAL / "fortnite-change-ledger.json"
    index_path = CAL / "fortnite-change-index-france.json"
    change = base.load(change_path)
    index = base.load(index_path)
    for record in added:
        sessions = [
            {
                "name": session.get("name"),
                "start_at": session.get("start_at"),
                "end_at": session.get("end_at"),
                "ruleset": session.get("ruleset"),
                "team_format": session.get("team_format"),
            }
            for phase in record.get("phases", [])
            for session in phase.get("sessions", [])
        ]
        base.add_change_record(
            change,
            index,
            domain="COMPETITIVE",
            subject=record["competition_id"],
            change_type="ENTITY_CREATED",
            materiality="LEDGER_ONLY",
            disposition="SILENT_POLICY",
            source_refs=record["source_urls"],
            material_after={"status": "SCHEDULED", "visibility": "LEDGER_ONLY", "sessions": sessions},
            evidence="FORTNITE_COMPETITIVE_OFFICIAL_EU_EXACT",
        )
    change["updated_at"] = AT
    change.setdefault("history", []).append({
        "at": AT,
        "type": "SILENT_COMPETITIVE_ENTITIES_CREATED",
        "note": "Six official EU competition instances for October 3–4 were ingested exhaustively as LEDGER_ONLY; visible calendars and notification outbox are unchanged.",
    })
    index["updated_at"] = AT
    index.setdefault("stats", {})["changes"] = len(change.get("changes", []))
    index["stats"]["subjects"] = len(index.get("subject_heads", {}))
    base.dump(change_path, change, compact=True)
    base.dump(index_path, index, compact=True)

    competitive_helper.AT = AT
    competitive_helper.rebuild_competitive_index()
    print(f"Applied silent Fortnite EU sweep: {len(added)} competition records.")


if __name__ == "__main__":
    main()
