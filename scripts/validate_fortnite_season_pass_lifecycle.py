#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
LEDGER_PATH = CAL / "fortnite-season-pass-lifecycle-france.json"
ENGINE_PATH = CAL / "fortnite-season-pass-engine-france.json"
INDEX_PATH = CAL / "fortnite-season-pass-index-france.json"

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
    "COLLAB_WITHIN_SEASON", "SAME_CAMPAIGN", "REPLACED_BY", "SHARES_WINDOW_WITH", "SUCCESSOR_OF"
}
WINDOW_TYPES = {
    "PURCHASE", "PREMIUM_UPGRADE", "PROGRESSION", "QUEST_COMPLETION", "REWARD_CLAIM",
    "BONUS_REWARD_CLAIM", "RANKED_PLAY", "RANKED_PLACEMENT", "EVENT_ACCESS"
}
WINDOW_STATES = {"UNKNOWN", "ANNOUNCED", "NOT_STARTED", "OPEN", "CLOSING", "CLOSED", "EXTENDED", "CANCELLED"}
CLOSURE_STATES = {
    "UNKNOWN", "PRELAUNCH", "FULLY_OPEN", "CLOSING", "PROGRESSION_CLOSED", "CLAIM_ONLY",
    "PURCHASE_CLOSED_BUT_PLAYABLE", "FULLY_CLOSED", "TRANSITIONING", "CANCELLED"
}
NEXT_ACTIONS = {
    "CLAIM_REWARDS", "FINISH_QUESTS", "EARN_PROGRESS", "BUY_OR_UPGRADE", "PLAY_RANKED",
    "PREPARE_FOR_RESET", "WAIT_FOR_DOWNTIME", "START_NEXT_TRACK", "WAIT_FOR_ANNOUNCEMENT", "NONE"
}
RANKED_SCOPES = {"BATTLE_ROYALE", "ZERO_BUILD", "RELOAD", "FORTNITE_OG", "GLOBAL_SHARED", "UNKNOWN"}


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


def date_ok(value):
    if value is None:
        return True
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except Exception:
        return False


def main():
    errors = []
    for path in (LEDGER_PATH, ENGINE_PATH, INDEX_PATH):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    ledger = load(LEDGER_PATH)
    engine = load(ENGINE_PATH)
    index = load(INDEX_PATH)

    if ledger.get("version") not in engine.get("base_versions_supported", []):
        errors.append("ledger version is not supported by V2 engine")
    if engine.get("version") != "FORTNITE_SEASON_PASS_ENGINE_FR_V2":
        errors.append("season/pass engine must be FORTNITE_SEASON_PASS_ENGINE_FR_V2")
    if engine.get("base_ledger") != LEDGER_PATH.name:
        errors.append("engine base_ledger mismatch")
    if engine.get("derived_index") != INDEX_PATH.name:
        errors.append("engine derived_index mismatch")
    if index.get("version") != "FORTNITE_SEASON_PASS_INDEX_FR_V1":
        errors.append("unexpected season/pass index version")

    tracks = {}
    milestones = {}
    windows = {}
    calendar_uids = {}

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
        if track.get("track_version") is not None and (not isinstance(track.get("track_version"), int) or track.get("track_version") < 1):
            errors.append(f"invalid track_version on {tid}")
        if track.get("closure_state") is not None and track.get("closure_state") not in CLOSURE_STATES:
            errors.append(f"invalid closure_state {track.get('closure_state')} on {tid}")
        if track.get("next_action") is not None and track.get("next_action") not in NEXT_ACTIONS:
            errors.append(f"invalid next_action {track.get('next_action')} on {tid}")
        if track.get("ranked_scope") is not None and track.get("ranked_scope") not in RANKED_SCOPES:
            errors.append(f"invalid ranked_scope {track.get('ranked_scope')} on {tid}")
        if ttype not in {"RANKED_SEASON", "RANKED_RESET"} and track.get("ranked_scope") not in {None, "UNKNOWN"}:
            errors.append(f"ranked_scope on non-ranked track {tid}")

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
            if m.get("date") and not date_ok(m.get("date")):
                errors.append(f"invalid milestone date on {mid}: {m.get('date')}")
            if precision == "EXACT" and not m.get("at"):
                errors.append(f"EXACT milestone without at: {mid}")
            if precision == "DATE_ONLY" and not m.get("date"):
                errors.append(f"DATE_ONLY milestone without date: {mid}")
            if m.get("type") in {"START_AT", "END_AT", "LAST_EARN_AT", "LAST_CLAIM_AT", "RANK_RESET_AT", "NEXT_START_AT"} and not m.get("source_id"):
                errors.append(f"material milestone without source_id: {mid}")
            if m.get("type") == "RANK_RESET_AT" and ttype not in {"RANKED_SEASON", "RANKED_RESET"}:
                errors.append(f"RANK_RESET_AT on non-ranked track: {mid}")
            uid = m.get("calendar_uid")
            if uid:
                if uid in calendar_uids and calendar_uids[uid] != tid:
                    errors.append(f"calendar_uid reused by different tracks: {uid}")
                calendar_uids[uid] = tid

        for w in track.get("windows", []):
            wid = w.get("window_id")
            if not wid:
                errors.append(f"window without window_id on {tid}")
                continue
            if wid in windows:
                errors.append(f"duplicate window_id: {wid}")
            windows[wid] = (tid, w)
            if w.get("window_type") not in WINDOW_TYPES:
                errors.append(f"invalid window_type {w.get('window_type')} on {wid}")
            if w.get("state") not in WINDOW_STATES:
                errors.append(f"invalid window state {w.get('state')} on {wid}")
            precision = w.get("time_precision")
            if precision is not None and precision not in PRECISIONS:
                errors.append(f"invalid window time_precision {precision} on {wid}")
            for field in ("opens_at", "closes_at"):
                if w.get(field) and not iso_ok(w.get(field)):
                    errors.append(f"invalid {field} on {wid}: {w.get(field)}")
            for field in ("opens_date", "closes_date"):
                if w.get(field) and not date_ok(w.get(field)):
                    errors.append(f"invalid {field} on {wid}: {w.get(field)}")
            if precision == "EXACT" and not any([w.get("opens_at"), w.get("closes_at")]):
                errors.append(f"EXACT window without exact boundary: {wid}")
            if any([w.get("opens_at"), w.get("closes_at"), w.get("opens_date"), w.get("closes_date")]) and not w.get("source_id"):
                errors.append(f"dated window without source_id: {wid}")
            if w.get("opens_at") and w.get("closes_at"):
                if datetime.fromisoformat(w["closes_at"].replace("Z", "+00:00")) < datetime.fromisoformat(w["opens_at"].replace("Z", "+00:00")):
                    errors.append(f"window closes before it opens: {wid}")

        # CLAIM_ONLY must be supported by actual window facts if materialized canonically.
        if track.get("closure_state") == "CLAIM_ONLY":
            progression_closed = any(w.get("window_type") in {"PROGRESSION", "RANKED_PLAY"} and w.get("state") == "CLOSED" for w in track.get("windows", []))
            claim_open = any(w.get("window_type") in {"REWARD_CLAIM", "BONUS_REWARD_CLAIM"} and w.get("state") in {"OPEN", "CLOSING", "EXTENDED"} for w in track.get("windows", []))
            if not (progression_closed and claim_open):
                errors.append(f"CLAIM_ONLY without closed progression + open claim window on {tid}")

    watch_ids_raw = [w.get("watch_id") for w in ledger.get("watch_tracks", []) if w.get("watch_id")]
    if len(watch_ids_raw) != len(set(watch_ids_raw)):
        errors.append("duplicate watch_id")
    watch_ids = {f"watch:{wid}" for wid in watch_ids_raw}

    for tid, track in tracks.items():
        for rel in track.get("relations", []):
            rtype = rel.get("type")
            target = rel.get("target_id")
            if rtype not in RELATIONS:
                errors.append(f"invalid relation type {rtype} on {tid}")
            if not target:
                errors.append(f"relation without target on {tid}")
                continue
            if rtype in {"PASS_FOR_SEASON", "RANKED_FOR_SEASON", "NEXT_TRACK", "COLLAB_WITHIN_SEASON", "SAME_CAMPAIGN", "REPLACED_BY", "SHARES_WINDOW_WITH", "SUCCESSOR_OF"}:
                if target not in tracks and target not in watch_ids:
                    errors.append(f"relation on {tid} references unknown target {target}")
            if rtype == "REPLACED_BY" and rel.get("confidence") in {"SIGNAL_ONLY", "UNKNOWN"}:
                errors.append(f"weak REPLACED_BY relation on {tid}")

    # Strong anti-inference guard: a pass close and a next-track start may coincide,
    # but copying the same value from the same source is not independent proof.
    close_values = []
    for tid, track in tracks.items():
        if track.get("track_type") in {"BATTLE_PASS", "OG_PASS", "FESTIVAL_PASS", "LEGO_PASS", "MINI_PASS", "COLLAB_PASS"}:
            for m in track.get("milestones", []):
                if m.get("type") in {"END_AT", "LAST_EARN_AT", "LAST_CLAIM_AT"}:
                    close_values.append((tid, m.get("at"), m.get("date"), m.get("source_id")))
            for w in track.get("windows", []):
                if w.get("closes_at") or w.get("closes_date"):
                    close_values.append((tid, w.get("closes_at"), w.get("closes_date"), w.get("source_id")))
    for tid, track in tracks.items():
        for m in track.get("milestones", []):
            if m.get("type") not in {"START_AT", "NEXT_START_AT", "RANK_RESET_AT"}:
                continue
            for close_tid, at, date, source_id in close_values:
                same_value = (m.get("at") and m.get("at") == at) or (m.get("date") and m.get("date") == date)
                if same_value and m.get("source_id") == source_id and tid != close_tid:
                    errors.append(
                        f"possible boundary inference: {tid}/{m.get('milestone_id')} copies {close_tid} close from same source without independent evidence"
                    )

    # Derived index validation.
    indexed_tracks = set()
    for facet in ("by_track_type", "by_state", "by_mode", "by_closing_date", "by_completeness", "by_next_action"):
        mapping = index.get(facet, {})
        for key, ids in mapping.items():
            if len(ids) != len(set(ids)):
                errors.append(f"duplicate IDs in index {facet}/{key}")
            for tid in ids:
                if tid not in tracks:
                    errors.append(f"index {facet}/{key} references unknown track {tid}")
                indexed_tracks.add(tid)
    for uid, tid in index.get("by_calendar_uid", {}).items():
        if tid not in tracks:
            errors.append(f"index calendar UID references unknown track {tid}")
        if uid not in calendar_uids or calendar_uids.get(uid) != tid:
            errors.append(f"index calendar UID mismatch: {uid} -> {tid}")
    ledger_watch = set(watch_ids_raw)
    for ids in index.get("watch_ids", {}).values():
        for wid in ids:
            if wid not in ledger_watch:
                errors.append(f"index references unknown watch_id {wid}")

    if index.get("derived_from", {}).get("engine_version") != engine.get("version"):
        errors.append("index engine_version mismatch")
    if index.get("derived_from", {}).get("ledger_version") != ledger.get("version"):
        errors.append("index ledger_version mismatch")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(
        "OK: season/pass lifecycle V2 validated — "
        f"{len(tracks)} tracks, {len(milestones)} milestones, {len(windows)} windows, "
        f"{len(watch_ids_raw)} watch targets"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
