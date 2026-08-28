#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import apply_crash_bandicoot_override_20260828 as competitive_helper

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-28T22:06:02Z"
OFFICIAL_SCHEDULE = "https://www.fortnite.com/competitive/events/S39_RankedCupDuos/schedule?lang=en-US&region=EU"
PS_INCIDENT = "https://status.epicgames.com/incidents/tsz8bfd4nyql"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    if not isinstance(value, str):
        value = canonical(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, obj, *, compact=False):
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(obj, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def sorted_add(mapping, key, value):
    values = list(mapping.get(key, []))
    values.append(value)
    mapping[key] = sorted(set(values))


def add_service_incident():
    service_path = CAL / "fortnite-service-events-france.json"
    service = load(service_path)
    service_id = "epic-fortnite-ps-login-20260828"
    if not any(e.get("service_event_id") == service_id for e in service.get("entries", [])):
        entry = {
            "service_event_id": service_id,
            "epic_incident_id": "tsz8bfd4nyql",
            "external_alias_ids": [],
            "calendar_uid": None,
            "fingerprint": "epic:tsz8bfd4nyql",
            "kind": "UNPLANNED_INCIDENT",
            "state": "RESOLVED",
            "source_id": "epic_status",
            "canonical_source_url": PS_INCIDENT,
            "first_seen_at": AT,
            "last_changed_at": "2026-08-28T14:32:00Z",
            "provider_phase": "RESOLVED",
            "provider_impact": "PARTIAL",
            "provider_title": "Fortnite Login Issues on PlayStation 4 and PlayStation 5",
            "provider_message_hash": sha("PS4 PS5 Fortnite login issue investigated 13:55 UTC and resolved 14:32 UTC on 2026-08-28"),
            "announced_at": "2026-08-28T13:55:00Z",
            "scheduled_start_at": None,
            "actual_start_at": "2026-08-28T13:55:00Z",
            "expected_end_at": None,
            "expected_end_updated_at": None,
            "recovery_started_at": None,
            "actual_end_at": "2026-08-28T14:32:00Z",
            "source_timezone": "UTC",
            "timing_precision": "EXACT",
            "component_states": [
                {
                    "component_id": "LOGIN",
                    "status": "OPERATIONAL",
                    "provider_component_name": "Fortnite (Login)",
                    "impact_note": "Epic reported that some PS4/PS5 players could not log into Fortnite; service returned to normal at 14:32 UTC.",
                    "source_id": "epic_status",
                    "source_url": PS_INCIDENT,
                    "observed_at": AT
                }
            ],
            "affected_regions": ["GLOBAL"],
            "affected_platforms": ["PLAYSTATION"],
            "internal_actionability": "NONE",
            "internal_priority_score": 15,
            "relation_type": "UNRELATED_OR_UNKNOWN",
            "relation_confidence": "UNKNOWN",
            "related_event_uid": None,
            "related_candidate_id": None,
            "group_id": None,
            "patch_version": None,
            "season_id": None,
            "relation_source_id": None,
            "relation_source_url": None,
            "calendar_status": "LEDGER_ONLY",
            "calendar_promoted_at": None,
            "calendar_last_synced_at": None,
            "previous_state": "STARTED",
            "evidence_grade": "A",
            "confidence": "OFFICIAL_EXACT",
            "last_verified_at": AT,
            "extension_count": 0,
            "notified_transition_keys": [],
            "history": [
                {"at":"2026-08-28T13:55:00Z","event_type":"CREATED","source_id":"epic_status","source_url":PS_INCIDENT,"note":"Epic began investigating Fortnite login failures affecting PlayStation 4 and PlayStation 5."},
                {"at":"2026-08-28T14:32:00Z","event_type":"STATE_TRANSITION","source_id":"epic_status","source_url":PS_INCIDENT,"from":"STARTED","to":"RESOLVED","note":"Epic confirmed PS4/PS5 Fortnite login services returned to normal."}
            ]
        }
        service.setdefault("entries", []).append(entry)
        service["updated_at"] = AT
        dump(service_path, service)
    return service_id


def comp(cid, name, klass, ruleset, team, platform, start, end, sessions=None, series=None):
    if sessions is None:
        sessions = [("session1", name, start, end)]
    session_records = []
    for i, (suffix, sname, sstart, send) in enumerate(sessions, start=1):
        session_records.append({
            "session_id": f"{cid}:main:EU:{sstart[0:10].replace('-', '')}T{sstart[11:16].replace(':', '')}:{suffix}",
            "official_session_id": None,
            "name": sname,
            "session_number": i,
            "round_number": i,
            "round_label": suffix.upper(),
            "status": "SCHEDULED",
            "region": "EU",
            "ruleset": ruleset,
            "team_format": team,
            "platform_scope": platform,
            "start_at": sstart,
            "end_at": send,
            "source_timezone": "Europe/Paris",
            "display_timezone": "Europe/Paris",
            "time_precision": "EXACT",
            "registration_deadline_at": None,
            "check_in_at": None,
            "max_matches": None,
            "qualification": None,
            "prize": None,
            "source_url": OFFICIAL_SCHEDULE,
            "visibility": "LEDGER_ONLY",
            "calendar_uid": None,
            "related_service_event_ids": []
        })
    return {
        "competition_id": cid,
        "official_event_id": None,
        "official_event_slug": None,
        "series_id": series,
        "season_id": "C7S4",
        "name": name,
        "competition_class": klass,
        "status": "SCHEDULED",
        "regions": ["EU"],
        "ruleset": ruleset,
        "team_format": team,
        "platform_scope": platform,
        "physical_event": False,
        "venue": None,
        "date_window": {"start_date": session_records[0]["start_at"][:10], "end_date": session_records[-1]["end_at"][:10], "time_precision": "EXACT"},
        "registration": None,
        "eligibility": {"status": "UNKNOWN"},
        "prize_pool": None,
        "qualification": None,
        "visibility": "LEDGER_ONLY",
        "calendar_uid": None,
        "source_ids": ["fortnite_competitive"],
        "source_urls": [OFFICIAL_SCHEDULE],
        "phases": [{
            "phase_id": f"{cid}:main",
            "name": "Official EU session",
            "phase_type": "OTHER",
            "order": 1,
            "status": "SCHEDULED",
            "registration": None,
            "eligibility_override": None,
            "qualification_override": None,
            "sessions": session_records,
            "schedule_completeness": "EXACT"
        }],
        "history": [{"at": AT, "type": "COMPETITION_CREATED", "source_id": "fortnite_competitive", "note": "Official EU schedule session ingested exhaustively under LEDGER_ONLY anti-bazar policy."}]
    }


def add_competitive_sessions():
    path = CAL / "fortnite-competitive-ledger-france.json"
    ledger = load(path)
    records = [
        comp(
            "console-zb-solo-victory-eu-20260829",
            "Console Zero Build Solo Victory Cup — EU — 29 août 2026",
            "VICTORY_CUP", "ZERO_BUILD", "SOLOS", "CONSOLE",
            "2026-08-29T17:00:00+02:00", "2026-08-29T21:00:00+02:00",
            sessions=[
                ("round1", "Console Zero Build Solo Victory Cup", "2026-08-29T17:00:00+02:00", "2026-08-29T19:00:00+02:00"),
                ("round2", "Console Zero Build Solo Victory Cup", "2026-08-29T20:00:00+02:00", "2026-08-29T21:00:00+02:00")
            ], series="CONSOLE_VICTORY_CUP"
        ),
        comp("fncs-div1-practice-eu-20260829", "FNCS Division 1 Practice — EU — 29 août 2026", "FNCS", "BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-29T17:00:00+02:00", "2026-08-29T19:40:00+02:00", series="FNCS_DIVISION_1_PRACTICE"),
        comp("duos-ranked-br-eu-20260829", "Duos Ranked Cup (Battle Royale) — EU — 29 août 2026", "RANKED_CUP", "BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-29T17:00:00+02:00", "2026-08-29T20:00:00+02:00", series="RANKED_CUP"),
        comp("duos-ranked-zb-eu-20260829", "Duos Ranked Cup (Zero Build) — EU — 29 août 2026", "RANKED_CUP", "ZERO_BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-29T17:00:00+02:00", "2026-08-29T20:00:00+02:00", series="RANKED_CUP"),
        comp("arenas-test-eu-20260830", "Arenas Test Cup — EU — 30 août 2026", "TEST_CUP", "UNKNOWN", "UNKNOWN", "ALL_SUPPORTED", "2026-08-30T17:00:00+02:00", "2026-08-30T19:00:00+02:00", series="ARENAS_TEST"),
        comp("duos-reload-ranked-zb-eu-20260830", "Duos Reload Ranked Cup (Zero Build) — EU — 30 août 2026", "RANKED_CUP", "ZERO_BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-30T17:00:00+02:00", "2026-08-30T20:00:00+02:00", series="RANKED_RELOAD"),
        comp("duos-reload-ranked-br-eu-20260830", "Duos Reload Ranked Cup (Battle Royale) — EU — 30 août 2026", "RANKED_CUP", "RELOAD", "DUOS", "ALL_SUPPORTED", "2026-08-30T17:00:00+02:00", "2026-08-30T20:00:00+02:00", series="RANKED_RELOAD"),
        comp("reload-zb-duos-cash-eu-20260830", "Reload ZB Duos Cash Cup — EU — 30 août 2026", "CASH_CUP", "ZERO_BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-30T17:00:00+02:00", "2026-08-30T19:30:00+02:00", series="RELOAD_CASH_CUP"),
        comp("fncs-div1-practice-eu-20260831", "FNCS Division 1 Practice — EU — 31 août 2026", "FNCS", "BUILD", "DUOS", "ALL_SUPPORTED", "2026-08-31T17:00:00+02:00", "2026-08-31T20:00:00+02:00", series="FNCS_DIVISION_1_PRACTICE")
    ]
    existing = {c.get("competition_id") for c in ledger.get("competitions", [])}
    added = []
    for record in records:
        if record["competition_id"] not in existing:
            ledger.setdefault("competitions", []).append(record)
            added.append(record)
    if added:
        ledger["updated_at"] = AT
        dump(path, ledger)
    return added


def add_change_record(change, idx, *, domain, subject, change_type, materiality, disposition, source_refs, material_after, evidence):
    existing = next((c for c in change.get("changes", []) if c.get("domain") == domain and c.get("subject_key") == subject and c.get("subject_revision") == 1), None)
    if existing:
        return existing["change_id"]
    scope = ""
    transition_fp = sha({"change_type": change_type, "material_before": None, "material_after": material_after, "material_evidence_state": evidence})
    state_fp = sha(material_after)
    subject_scope_key = "sub_" + sha(f"{domain}|{subject}|{scope}")
    change_id = "chg_" + sha(f"{domain}|{subject}|{scope}|1||{transition_fp}")[:24]
    rec = {
        "change_id": change_id,
        "domain": domain,
        "subject_scope_key": subject_scope_key,
        "subject_key": subject,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": change_type,
        "materiality": materiality,
        "state_fingerprint": state_fp,
        "transition_fingerprint": transition_fp,
        "detected_at": AT,
        "source_refs": source_refs,
        "notification_disposition": disposition,
        "scope_key": None,
        "material_before": None,
        "material_after": material_after,
        "material_evidence_state": evidence,
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2"
    }
    change.setdefault("changes", []).append(rec)
    idx.setdefault("subject_heads", {})[subject_scope_key] = {"revision": 1, "change_id": change_id}
    sorted_add(idx.setdefault("by_domain", {}), domain, change_id)
    sorted_add(idx.setdefault("by_change_type", {}), change_type, change_id)
    idx.setdefault("open_changes_by_subject", {})[subject_scope_key] = [change_id]
    return change_id


def update_change_ledgers(service_id, added_competitions):
    change_path = CAL / "fortnite-change-ledger.json"
    index_path = CAL / "fortnite-change-index-france.json"
    change = load(change_path)
    idx = load(index_path)

    add_change_record(
        change, idx,
        domain="SERVICE",
        subject=service_id,
        change_type="ENTITY_CREATED",
        materiality="LEDGER_ONLY",
        disposition="STALE",
        source_refs=[PS_INCIDENT],
        material_after={"state":"RESOLVED","provider_phase":"RESOLVED","affected_components":["LOGIN"],"affected_platforms":["PLAYSTATION"],"actual_start_at":"2026-08-28T13:55:00Z","actual_end_at":"2026-08-28T14:32:00Z"},
        evidence="EPIC_STATUS_OFFICIAL_EXACT"
    )

    for record in added_competitions:
        sessions = []
        for phase in record.get("phases", []):
            for session in phase.get("sessions", []):
                sessions.append({"name":session.get("name"),"start_at":session.get("start_at"),"end_at":session.get("end_at"),"ruleset":session.get("ruleset"),"team_format":session.get("team_format")})
        add_change_record(
            change, idx,
            domain="COMPETITIVE",
            subject=record["competition_id"],
            change_type="ENTITY_CREATED",
            materiality="LEDGER_ONLY",
            disposition="SILENT_POLICY",
            source_refs=[OFFICIAL_SCHEDULE],
            material_after={"status":"SCHEDULED","visibility":"LEDGER_ONLY","sessions":sessions},
            evidence="FORTNITE_COMPETITIVE_OFFICIAL_EU_EXACT"
        )

    change["updated_at"] = AT
    idx["updated_at"] = AT
    stats = idx.setdefault("stats", {})
    stats["changes"] = len(change.get("changes", []))
    stats["subjects"] = len(idx.get("subject_heads", {}))
    dump(change_path, change, compact=True)
    dump(index_path, idx, compact=True)


def main():
    service_id = add_service_incident()
    added = add_competitive_sessions()
    update_change_ledgers(service_id, added)
    competitive_helper.AT = AT
    competitive_helper.rebuild_competitive_index()
    print(f"Applied Fortnite sweep: {len(added)} competitive records; service incident {service_id} reconciled.")


if __name__ == "__main__":
    main()
