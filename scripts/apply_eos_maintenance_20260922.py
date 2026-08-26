#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-26T16:08:18Z"
AT_ICS = "20260826T160818Z"
SOURCE = "https://status.epicgames.com/incidents/djsq84vjvp45"
SERVICE_ID = "epic-eos-maintenance-20260922"
UID = "fortnite-service-epic-eos-maintenance-20260922@openai"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(value):
    if not isinstance(value, str):
        value = canonical(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, obj, compact=False):
    if compact:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def fold_line(line):
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return [line]
    out = []
    first = True
    rest = line
    while rest:
        limit = 75 if first else 74
        used = 0
        chars = []
        for ch in rest:
            b = len(ch.encode("utf-8"))
            if chars and used + b > limit:
                break
            if not chars and b > limit:
                chars.append(ch)
                used += b
                break
            chars.append(ch)
            used += b
        part = "".join(chars)
        out.append(("" if first else " ") + part)
        rest = rest[len(part):]
        first = False
    return out


def insert_event(path):
    raw = path.read_text(encoding="utf-8-sig")
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    if f"UID:{UID}" in normalized:
        return False
    lines = [
        "BEGIN:VEVENT",
        f"UID:{UID}",
        f"DTSTAMP:{AT_ICS}",
        f"LAST-MODIFIED:{AT_ICS}",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "PRIORITY:9",
        "X-FORTNITE-PRIORITY:INFO",
        "X-FORTNITE-ACTION:PLAN",
        "X-FORTNITE-EVENT-TYPE:SERVICE_DOWNTIME",
        f"X-FORTNITE-SERVICE-EVENT-ID:{SERVICE_ID}",
        "X-FORTNITE-SERVICE-KIND:SCHEDULED_MAINTENANCE",
        "X-FORTNITE-SERVICE-STATE:DOWNTIME_ANNOUNCED",
        "X-FORTNITE-SERVICE-PROVIDER-PHASE:SCHEDULED",
        "X-FORTNITE-SERVICE-IMPACT:PARTIAL",
        "X-FORTNITE-SERVICE-ACTIONABILITY:MEDIUM",
        "X-FORTNITE-AFFECTED-SERVICE:EOS Sessions,Lobbies,Matchmaking,Invites",
        "X-FORTNITE-SERVICE-SOURCE-ID:epic_status",
        "X-FORTNITE-SERVICE-RELATION-TYPE:PLATFORM_MAINTENANCE",
        "X-FORTNITE-TIME-PRECISION:EXACT",
        f"X-FORTNITE-FIRST-ADDED-AT:{AT_ICS}",
        "X-FORTNITE-NEW-UNTIL:20260831T160818Z",
        "DTSTART;TZID=Europe/Paris:20260922T080000",
        "DTEND;TZID=Europe/Paris:20260922T093000",
        "SUMMARY:ℹ️ ✅ 🆕 🛠️ Maintenance Epic Online Services — sessions et matchmaking",
        "DESCRIPTION:Priorité : ℹ️ Info — maintenance Epic Online Services planifiée.\\nEpic annonce une maintenance EOS le 22 septembre 2026 de 06:00 à 07:30 UTC, soit 08:00 à 09:30 heure de Paris.\\nLes services Sessions et Lobbies auront une disponibilité dégradée jusqu’à 90 minutes : les sessions existantes pourront expirer et déconnecter les clients ; la création de nouvelles sessions, les invitations, la recherche et le matchmaking pourront être temporairement indisponibles.\\n⚠️ Il ne s’agit pas d’une panne Fortnite en cours ni d’une maintenance de patch Fortnite explicitement annoncée. Fortnite est actuellement opérationnel ; ce créneau concerne l’infrastructure Epic Online Services.\\nSource : https://status.epicgames.com/incidents/djsq84vjvp45",
        f"URL:{SOURCE}",
        "CATEGORIES:Fortnite,Maintenance,Epic Online Services,Matchmaking,Services",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        "DESCRIPTION:🛠️ Maintenance EOS demain 08h00–09h30 — sessions et matchmaking pourront être perturbés",
        "END:VALARM",
        "BEGIN:VALARM",
        "TRIGGER:-PT1H",
        "ACTION:DISPLAY",
        "DESCRIPTION:🛠️ Maintenance EOS dans 1 h — sessions et matchmaking pourront être perturbés",
        "END:VALARM",
        "END:VEVENT",
    ]
    folded = []
    for line in lines:
        folded.extend(fold_line(line))
    marker = "END:VCALENDAR"
    if marker not in normalized:
        raise RuntimeError(f"{path} missing END:VCALENDAR")
    event_text = "\n".join(folded) + "\n"
    normalized = normalized.replace(marker, event_text + marker, 1)
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))
    return True


def main():
    service_path = CAL / "fortnite-service-events-france.json"
    service = load(service_path)
    if not any(e.get("service_event_id") == SERVICE_ID for e in service.get("entries", [])):
        entry = {
            "service_event_id": SERVICE_ID,
            "epic_incident_id": "djsq84vjvp45",
            "external_alias_ids": [],
            "calendar_uid": UID,
            "fingerprint": "epic:djsq84vjvp45",
            "kind": "SCHEDULED_MAINTENANCE",
            "state": "DOWNTIME_ANNOUNCED",
            "source_id": "epic_status",
            "canonical_source_url": SOURCE,
            "first_seen_at": AT,
            "last_changed_at": AT,
            "provider_phase": "SCHEDULED",
            "provider_impact": "PARTIAL",
            "provider_title": "EOS Maintenance",
            "provider_message_hash": sha("Epic Online Services Sessions and Lobbies maintenance 2026-09-22 06:00-07:30 UTC"),
            "announced_at": "2026-08-26T11:57:00Z",
            "scheduled_start_at": "2026-09-22T06:00:00Z",
            "actual_start_at": None,
            "expected_end_at": "2026-09-22T07:30:00Z",
            "expected_end_updated_at": "2026-08-26T11:57:00Z",
            "recovery_started_at": None,
            "actual_end_at": None,
            "source_timezone": "UTC",
            "timing_precision": "EXACT",
            "component_states": [
                {"component_id":"MATCHMAKING","status":"UNDER_MAINTENANCE","impact_note":"During the scheduled EOS window, searching and matchmaking may be temporarily unavailable.","source_id":"epic_status","source_url":SOURCE,"observed_at":AT},
                {"component_id":"PARTIES_FRIENDS","status":"UNDER_MAINTENANCE","impact_note":"EOS Lobbies/Sessions maintenance may disrupt session and lobby invites; existing sessions can time out and disconnect clients.","source_id":"epic_status","source_url":SOURCE,"observed_at":AT}
            ],
            "affected_regions": ["GLOBAL"],
            "affected_platforms": [],
            "internal_actionability": "MEDIUM",
            "internal_priority_score": 50,
            "relation_type": "PLATFORM_MAINTENANCE",
            "relation_confidence": "EXPLICIT",
            "related_event_uid": None,
            "related_candidate_id": None,
            "group_id": None,
            "patch_version": None,
            "season_id": None,
            "relation_source_id": "epic_status",
            "relation_source_url": SOURCE,
            "calendar_status": "PROMOTED",
            "calendar_promoted_at": AT,
            "calendar_last_synced_at": AT,
            "previous_state": None,
            "evidence_grade": "A",
            "confidence": "OFFICIAL_EXACT",
            "last_verified_at": AT,
            "extension_count": 0,
            "notified_transition_keys": [],
            "history": [
                {"at":AT,"event_type":"CREATED","source_id":"epic_status","source_url":SOURCE,"note":"Epic scheduled EOS Sessions/Lobbies maintenance for 22 September 2026, 06:00–07:30 UTC, with temporary disruption to sessions, invites, searching and matchmaking."},
                {"at":AT,"event_type":"RELATION_ADDED","source_id":"epic_status","source_url":SOURCE,"note":"Classified as PLATFORM_MAINTENANCE. No Fortnite patch, season, live-event or competitive linkage is inferred."},
                {"at":AT,"event_type":"CALENDAR_PROMOTED","source_id":"epic_status","source_url":SOURCE,"note":"Exact actionable global EOS maintenance window projected to Fortnite updates and global calendars."}
            ]
        }
        service.setdefault("entries", []).append(entry)
        service["updated_at"] = AT
        dump(service_path, service, compact=False)

    change_path = CAL / "fortnite-change-ledger.json"
    change = load(change_path)
    if not any(c.get("subject_key") == SERVICE_ID for c in change.get("changes", [])):
        material_after = {
            "state":"DOWNTIME_ANNOUNCED",
            "provider_phase":"SCHEDULED",
            "provider_impact":"PARTIAL",
            "scheduled_start_at":"2026-09-22T06:00:00Z",
            "expected_end_at":"2026-09-22T07:30:00Z",
            "affected_components":["MATCHMAKING","PARTIES_FRIENDS"],
            "relation_type":"PLATFORM_MAINTENANCE"
        }
        evidence = "EPIC_STATUS_OFFICIAL_EXACT"
        transition_obj = {"change_type":"ENTITY_CREATED","material_before":None,"material_after":material_after,"material_evidence_state":evidence}
        transition_fp = sha(transition_obj)
        state_fp = sha(material_after)
        scope = ""
        subject_scope_key = "sub_" + sha(f"SERVICE|{SERVICE_ID}|{scope}")
        revision = 1
        parent = None
        parent_s = "" if parent is None else parent
        change_id = "chg_" + sha(f"SERVICE|{SERVICE_ID}|{scope}|{revision}|{parent_s}|{transition_fp}")[:24]
        rec = {
            "change_id":change_id,
            "domain":"SERVICE",
            "subject_scope_key":subject_scope_key,
            "subject_key":SERVICE_ID,
            "subject_revision":revision,
            "causal_parent_change_id":parent,
            "change_type":"ENTITY_CREATED",
            "materiality":"CALENDAR",
            "state_fingerprint":state_fp,
            "transition_fingerprint":transition_fp,
            "detected_at":AT,
            "source_refs":[SOURCE],
            "notification_disposition":"ELIGIBLE_WHEN_DUE",
            "scope_key":None,
            "material_before":None,
            "material_after":material_after,
            "material_evidence_state":evidence,
            "projection_targets":["calendars/fortnite-updates-france.ics","calendars/fortnite-paris.ics"],
            "policy_version":"FORTNITE_CHANGE_ENGINE_FR_V2",
            "notes":"New exact EOS infrastructure maintenance window. Calendar-worthy now; no notification intent is created until a due reminder is revalidated."
        }
        change.setdefault("changes", []).append(rec)
        change["updated_at"] = AT
        dump(change_path, change, compact=True)

        idx_path = CAL / "fortnite-change-index-france.json"
        idx = load(idx_path)
        idx["updated_at"] = AT
        idx.setdefault("subject_heads", {})[subject_scope_key] = {"revision":1,"change_id":change_id}
        idx.setdefault("by_domain", {}).setdefault("SERVICE", []).append(change_id)
        idx["by_domain"]["SERVICE"] = sorted(set(idx["by_domain"]["SERVICE"]))
        idx.setdefault("by_change_type", {}).setdefault("ENTITY_CREATED", []).append(change_id)
        idx["by_change_type"]["ENTITY_CREATED"] = sorted(set(idx["by_change_type"]["ENTITY_CREATED"]))
        idx.setdefault("open_changes_by_subject", {})[subject_scope_key] = [change_id]
        stats = idx.setdefault("stats", {})
        stats["changes"] = len(change.get("changes", []))
        stats["subjects"] = len(idx.get("subject_heads", {}))
        dump(idx_path, idx, compact=True)

    insert_event(CAL / "fortnite-updates-france.ics")
    insert_event(CAL / "fortnite-paris.ics")


if __name__ == "__main__":
    main()
