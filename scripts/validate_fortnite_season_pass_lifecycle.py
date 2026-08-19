#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
LEDGER_PATH = CAL / "fortnite-season-pass-lifecycle-france.json"
ENGINE_PATH = CAL / "fortnite-season-pass-engine-france.json"

TRACK_TYPES = {
    "BR_SEASON", "BATTLE_PASS", "OG_PASS", "FESTIVAL_SEASON", "FESTIVAL_PASS",
    "LEGO_PASS", "MINI_PASS", "COLLAB_PASS", "RANKED_SEASON", "RANKED_RESET"
}
PRECISIONS = {"EXACT", "DATE_ONLY", "DATE_RANGE", "WINDOW_ONLY", "UNPUBLISHED"}
MILESTONE_TYPES = {
    "ANNOUNCED_AT", "START_AT", "END_AT", "LAST_EARN_AT", "LAST_CLAIM_AT",
    "RANKED_END_AT", "RANK_RESET_AT", "DOWNTIME_START_AT", "DOWNTIME_END_AT", "NEXT_START_AT"
}
RELATIONS = {
    "PASS_FOR_SEASON", "RANKED_FOR_SEASON", "NEXT_TRACK", "TRANSITION_DOWNTIME",
    "COLLAB_WITHIN_SEASON", "SAME_CAMPAIGN", "REPLACED_BY"
}


def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def iso_ok(value):
    if value is None:
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def main():
    errors = []
    for path in (LEDGER_PATH, ENGINE_PATH):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    ledger = load(LEDGER_PATH)
    engine = load(ENGINE_PATH)
    if ledger.get("version") != "FORTNITE_SEASON_PASS_INTELLIGENCE_FR_V1":
        errors.append("unexpected season/pass ledger version")
    if engine.get("version") != "FORTNITE_SEASON_PASS_ENGINE_FR_V1":
        errors.append("unexpected season/pass engine version")
    if engine.get("base_ledger") != LEDGER_PATH.name:
        errors.append("engine base_ledger mismatch")

    tracks = {}
    milestones = {}
    for track in ledger.get("tracks", []):
        tid = track.get("track_id")
        ttype = track.get("track_type")
        if not tid:
            errors.append("track without track_id")
            continue
        if tid in tracks:
            errors.append(f"duplicate track_id: {tid}")
        tracks[tid] = track
        if ttype not in TRACK_TYPES:
            errors.append(f"invalid track_type {ttype} on {tid}")
        if not track.get("source_ids"):
            errors.append(f"track {tid} has no source_ids")
        for h in track.get("history", []):
            if not iso_ok(h.get("at")):
                errors.append(f"invalid history timestamp on {tid}: {h.get('at')}")
        for m in track.get("milestones", []):
            mid = m.get("milestone_id")
            if not mid:
                errors.append(f"milestone without id on {tid}")
                continue
            if mid in milestones:
                errors.append(f"duplicate milestone_id: {mid}")
            milestones[mid] = (tid, m)
            if m.get("type") not in MILESTONE_TYPES:
                errors.append(f"invalid milestone type {m.get('type')} on {mid}")
            precision = m.get("time_precision")
            if precision not in PRECISIONS:
                errors.append(f"invalid time_precision {precision} on {mid}")
            if m.get("at") and not iso_ok(m.get("at")):
                errors.append(f"invalid milestone at on {mid}: {m.get('at')}")
            if precision == "EXACT" and not m.get("at"):
                errors.append(f"EXACT milestone without at: {mid}")
            if precision == "DATE_ONLY" and not m.get("date"):
                errors.append(f"DATE_ONLY milestone without date: {mid}")
            if m.get("type") in {"START_AT", "END_AT", "LAST_EARN_AT", "LAST_CLAIM_AT", "RANK_RESET_AT", "NEXT_START_AT"} and not m.get("source_id"):
                errors.append(f"material milestone without source_id: {mid}")
            if m.get("type") == "RANK_RESET_AT" and ttype not in {"RANKED_SEASON", "RANKED_RESET"}:
                errors.append(f"RANK_RESET_AT on non-ranked track: {mid}")

    watch_ids = {f"watch:{w.get('watch_id')}" for w in ledger.get("watch_tracks", []) if w.get("watch_id")}
    for tid, track in tracks.items():
        for rel in track.get("relations", []):
            rtype = rel.get("type")
            target = rel.get("target_id")
            if rtype not in RELATIONS:
                errors.append(f"invalid relation type {rtype} on {tid}")
            if not target:
                errors.append(f"relation without target on {tid}")
                continue
            if rtype in {"PASS_FOR_SEASON", "RANKED_FOR_SEASON", "NEXT_TRACK", "COLLAB_WITHIN_SEASON", "SAME_CAMPAIGN", "REPLACED_BY"}:
                if target not in tracks and target not in watch_ids:
                    errors.append(f"relation on {tid} references unknown target {target}")

    # Strong anti-inference guard: if a pass END_AT and another track NEXT_START_AT are
    # identical, require independent source evidence instead of treating adjacency as proof.
    pass_end_values = []
    for tid, track in tracks.items():
        if track.get("track_type") in {"BATTLE_PASS", "OG_PASS", "FESTIVAL_PASS", "LEGO_PASS", "MINI_PASS", "COLLAB_PASS"}:
            for m in track.get("milestones", []):
                if m.get("type") == "END_AT":
                    pass_end_values.append((tid, m.get("at"), m.get("date"), m.get("source_id")))
    for tid, track in tracks.items():
        for m in track.get("milestones", []):
            if m.get("type") != "NEXT_START_AT":
                continue
            for pass_tid, at, date, source_id in pass_end_values:
                same_value = (m.get("at") and m.get("at") == at) or (m.get("date") and m.get("date") == date)
                if same_value and m.get("source_id") == source_id:
                    errors.append(
                        f"possible inferred next start: {tid}/{m.get('milestone_id')} copies {pass_tid} pass end from same source without independent evidence"
                    )

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(f"OK: season/pass lifecycle validated — {len(tracks)} tracks, {len(milestones)} milestones")
    return 0


if __name__ == "__main__":
    sys.exit(main())
