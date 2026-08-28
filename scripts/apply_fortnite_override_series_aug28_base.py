#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
DELTA = CAL / "fortnite-competitive-ingest-delta-20260828.json"
LEDGER = CAL / "fortnite-competitive-ledger-france.json"
CINDEX = CAL / "fortnite-competitive-index-france.json"
CHANGE = CAL / "fortnite-change-ledger.json"
CHINDEX = CAL / "fortnite-change-index-france.json"
ENGINE = CAL / "fortnite-competitive-engine-france.json"
CID = "override-series-eu-20260828"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, obj, compact=False):
    if compact:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value):
    if not isinstance(value, str):
        value = canonical(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def blob_sha(path: Path):
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def sorted_add(mapping, key, value):
    values = list(mapping.get(key, []))
    values.append(value)
    mapping[key] = sorted(set(values))


def competition_from_delta(delta):
    s = delta["sessions"][0]
    session_id = f"{CID}:base:EU:20260828T1700:session1"
    phase_id = f"{CID}:base"
    return {
        "competition_id": CID,
        "official_event_id": s.get("official_event_id"),
        "official_event_slug": s.get("official_event_slug"),
        "series_id": s.get("series", "OVERRIDE_SERIES"),
        "season_id": "C7S4",
        "name": "Override Series — EU — 28 août 2026",
        "competition_class": s.get("competition_class", "OTHER"),
        "status": "SCHEDULED",
        "regions": ["EU"],
        "ruleset": s.get("ruleset", "BUILD"),
        "team_format": s.get("team_format", "DUOS"),
        "platform_scope": s.get("platform_scope", "ALL_SUPPORTED"),
        "physical_event": False,
        "venue": None,
        "date_window": {"start_date": s["event_date"], "end_date": s["event_date"], "time_precision": s.get("time_precision", "EXACT")},
        "registration": None,
        "eligibility": s.get("eligibility", {"status": "UNKNOWN"}),
        "prize_pool": None,
        "qualification": None,
        "visibility": "LEDGER_ONLY",
        "calendar_uid": None,
        "source_ids": [delta.get("source_id", "fortnite_competitive")],
        "source_urls": [s["source_url"], s.get("schedule_evidence_url")],
        "phases": [{
            "phase_id": phase_id,
            "name": "Base session",
            "phase_type": "OTHER",
            "order": 1,
            "status": "SCHEDULED",
            "registration": None,
            "eligibility_override": None,
            "qualification_override": None,
            "sessions": [{
                "session_id": session_id,
                "official_session_id": s.get("official_event_id"),
                "name": s.get("name", "Override Series"),
                "session_number": 1,
                "round_number": 1,
                "round_label": "BASE",
                "status": "SCHEDULED",
                "region": "EU",
                "ruleset": s.get("ruleset", "BUILD"),
                "team_format": s.get("team_format", "DUOS"),
                "platform_scope": s.get("platform_scope", "ALL_SUPPORTED"),
                "start_at": s["start_at"],
                "end_at": s["end_at"],
                "source_timezone": "Europe/Paris",
                "display_timezone": "Europe/Paris",
                "time_precision": s.get("time_precision", "EXACT"),
                "registration_deadline_at": None,
                "check_in_at": None,
                "max_matches": None,
                "qualification": None,
                "prize": None,
                "source_url": s["source_url"],
                "visibility": "LEDGER_ONLY",
                "calendar_uid": None,
                "related_service_event_ids": []
            }],
            "schedule_completeness": "EXACT"
        }],
        "history": [{"at": NOW, "type": "COMPETITION_CREATED", "source_id": delta.get("source_id", "fortnite_competitive"), "note": "Canonical merge of previously staged official EU Override Series base session. Routine session remains LEDGER_ONLY and SILENT_POLICY."}]
    }


def add_competition(delta):
    ledger = load(LEDGER)
    if any(c.get("competition_id") == CID for c in ledger.get("competitions", [])):
        return False
    ledger.setdefault("competitions", []).append(competition_from_delta(delta))
    ledger["updated_at"] = NOW
    dump(LEDGER, ledger)
    return True


def add_change(delta):
    obj = load(CHANGE)
    existing = next((c for c in obj.get("changes", []) if c.get("domain") == "COMPETITIVE" and c.get("subject_key") == CID), None)
    if existing:
        return existing["change_id"]
    s = delta["sessions"][0]
    material_after = {
        "competition_id": CID,
        "status": "SCHEDULED",
        "visibility": "LEDGER_ONLY",
        "region": "EU",
        "ruleset": s.get("ruleset", "BUILD"),
        "team_format": s.get("team_format", "DUOS"),
        "start_at": s["start_at"],
        "end_at": s["end_at"]
    }
    evidence = "FORTNITE_COMPETITIVE_OFFICIAL_EU_EXACT"
    tfp = sha256({"change_type": "ENTITY_CREATED", "material_before": None, "material_after": material_after, "material_evidence_state": evidence})
    sfp = sha256(material_after)
    subject_scope_key = "sub_" + sha256(f"COMPETITIVE|{CID}|")
    change_id = "chg_" + sha256(f"COMPETITIVE|{CID}||1||{tfp}")[:24]
    rec = {
        "change_id": change_id,
        "domain": "COMPETITIVE",
        "subject_scope_key": subject_scope_key,
        "subject_key": CID,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": "ENTITY_CREATED",
        "materiality": "LEDGER_ONLY",
        "state_fingerprint": sfp,
        "transition_fingerprint": tfp,
        "detected_at": NOW,
        "source_refs": [s["source_url"], s.get("schedule_evidence_url")],
        "notification_disposition": "SILENT_POLICY",
        "scope_key": None,
        "material_before": None,
        "material_after": material_after,
        "material_evidence_state": evidence,
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
        "notes": "Routine official EU Override Series base session; exhaustive competitive ledger ingestion only, no visible calendar projection or outbox intent."
    }
    obj.setdefault("changes", []).append(rec)
    obj["updated_at"] = NOW
    obj.setdefault("history", []).append({"at": NOW, "type": "SILENT_COMPETITIVE_ENTITY_CREATED", "note": "Merged staged Aug 28 Override Series base EU session into canonical competitive ledger; visible calendars unchanged."})
    dump(CHANGE, obj, compact=True)

    idx = load(CHINDEX)
    idx["updated_at"] = NOW
    idx.setdefault("subject_heads", {})[subject_scope_key] = {"revision": 1, "change_id": change_id}
    sorted_add(idx.setdefault("by_domain", {}), "COMPETITIVE", change_id)
    sorted_add(idx.setdefault("by_change_type", {}), "ENTITY_CREATED", change_id)
    idx.setdefault("open_changes_by_subject", {})[subject_scope_key] = [change_id]
    stats = idx.setdefault("stats", {})
    stats["changes"] = len(obj.get("changes", []))
    stats["subjects"] = len(idx.get("subject_heads", {}))
    dump(CHINDEX, idx, compact=True)
    return change_id


def rebuild_competitive_index():
    ledger = load(LEDGER)
    engine = load(ENGINE)
    old = load(CINDEX)
    idx = {
        "version": "FORTNITE_COMPETITIVE_INDEX_EU_V1",
        "generated_at": NOW,
        "derived_only": True,
        "authority": "NONE — rebuild from competitive ledger + competitive engine when inconsistent.",
        "source": {"ledger": "calendars/fortnite-competitive-ledger-france.json", "ledger_version": ledger.get("version"), "ledger_sha": blob_sha(LEDGER), "engine": "calendars/fortnite-competitive-engine-france.json", "engine_version": engine.get("version"), "engine_sha": blob_sha(ENGINE)},
        "principles": old.get("principles", {}),
        "competition_ids": [], "by_visibility": {}, "by_status": {}, "by_region": {}, "by_series_id": {}, "by_competition_class": {}, "by_ruleset": {}, "by_team_format": {}, "by_platform_scope": {}, "by_phase_type": {}, "by_date": {},
        "sessions": {"all_ids": [], "by_exact_date": {}, "by_status": {}, "by_start_at": {}},
        "actionable": {"ATTEND": [], "WATCH": [], "REGISTER": [], "CHECK_IN": [], "PLAY": [], "FOLLOW": []},
        "deadlines": old.get("deadlines", {"LAST_REGISTRATION_AT": [], "LAST_CHECK_IN_AT": [], "LAST_QUALIFIER_AT": []}),
        "qualification_graph": old.get("qualification_graph", {"edges": [], "unresolved_candidates": []}),
        "projection": {}, "conflicts": old.get("conflicts", []),
        "watch_targets": sorted({w.get("watch_id") for w in ledger.get("watch_targets", []) if isinstance(w, dict) and w.get("watch_id")}),
        "rebuild_triggers": old.get("rebuild_triggers", [])
    }
    def add(section, key, value):
        if key is not None:
            sorted_add(section, str(key), value)
    old_actionable = old.get("actionable", {})
    for comp in ledger.get("competitions", []):
        cid = comp["competition_id"]
        idx["competition_ids"].append(cid)
        for section, key in ((idx["by_visibility"], comp.get("visibility")), (idx["by_status"], comp.get("status")), (idx["by_series_id"], comp.get("series_id")), (idx["by_competition_class"], comp.get("competition_class")), (idx["by_ruleset"], comp.get("ruleset")), (idx["by_team_format"], comp.get("team_format")), (idx["by_platform_scope"], comp.get("platform_scope"))): add(section, key, cid)
        for region in comp.get("regions", []): add(idx["by_region"], region, cid)
        dw = comp.get("date_window") or {}
        if dw.get("start_date"): add(idx["by_date"], dw["start_date"], cid)
        if dw.get("end_date") and dw.get("end_date") != dw.get("start_date"): add(idx["by_date"], dw["end_date"], cid)
        for phase in comp.get("phases", []):
            if phase.get("phase_id") and phase.get("phase_type"): add(idx["by_phase_type"], phase["phase_type"], phase["phase_id"])
            for sess in phase.get("sessions", []):
                sid = sess["session_id"]
                idx["sessions"]["all_ids"].append(sid)
                if sess.get("start_at"):
                    add(idx["sessions"]["by_exact_date"], sess["start_at"][:10], sid)
                    add(idx["sessions"]["by_start_at"], sess["start_at"], sid)
                    add(idx["by_date"], sess["start_at"][:10], cid)
                add(idx["sessions"]["by_status"], sess.get("status"), sid)
        idx["projection"][cid] = {"initial_level": comp.get("visibility"), "v2_score_status": "NOT_MATERIALIZED", "calendar_uid": comp.get("calendar_uid")}
        for action, values in old_actionable.items():
            if action in idx["actionable"] and cid in values: idx["actionable"][action].append(cid)
    idx["competition_ids"] = sorted(set(idx["competition_ids"]))
    idx["sessions"]["all_ids"] = sorted(set(idx["sessions"]["all_ids"]))
    for mapping in [idx["by_visibility"], idx["by_status"], idx["by_region"], idx["by_series_id"], idx["by_competition_class"], idx["by_ruleset"], idx["by_team_format"], idx["by_platform_scope"], idx["by_phase_type"], idx["by_date"], idx["sessions"]["by_exact_date"], idx["sessions"]["by_status"], idx["sessions"]["by_start_at"]]:
        for k in list(mapping): mapping[k] = sorted(set(mapping[k]))
    for k in idx["actionable"]: idx["actionable"][k] = sorted(set(idx["actionable"][k]))
    dump(CINDEX, idx)


def mark_delta_merged():
    delta = load(DELTA)
    delta["status"] = "MERGED_CANONICAL"
    delta["merged_at"] = NOW
    delta["notification_disposition"] = "SILENT_POLICY"
    dump(DELTA, delta)


def main():
    delta = load(DELTA)
    if delta.get("version") != "FORTNITE_COMPETITIVE_INGEST_DELTA_EU_V1":
        raise SystemExit("unexpected delta version")
    add_competition(delta)
    add_change(delta)
    rebuild_competitive_index()
    mark_delta_merged()
    print("OK", CID, "merged canonical; visible calendars/outbox unchanged")


if __name__ == "__main__":
    main()
