#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
INBOX = CAL / "fortnite-service-inbox.json"
SERVICE = CAL / "fortnite-service-events-france.json"
CHANGE = CAL / "fortnite-change-ledger.json"
INDEX = CAL / "fortnite-change-index-france.json"
OUTBOX = CAL / "fortnite-notification-outbox-france.json"
GLOBAL_ICS = CAL / "fortnite-paris.ics"
UPDATES_ICS = CAL / "fortnite-updates-france.ics"


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump(path, data, compact=False):
    text = json.dumps(data, ensure_ascii=False, sort_keys=False, separators=(",", ":") if compact else None, indent=None if compact else 2)
    path.write_text(text + ("" if compact else "\n"), encoding="utf-8")


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_stamp(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def paris_stamp(iso):
    # Dates ingested here are known Europe/Paris DST/standard instants; convert with zoneinfo.
    from zoneinfo import ZoneInfo
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Paris"))
    return dt.strftime("%Y%m%dT%H%M%S")


def fold_line(line):
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return [line]
    parts = []
    current = ""
    limit = 75
    for ch in line:
        candidate = current + ch
        if len(candidate.encode("utf-8")) > limit:
            parts.append(current)
            current = " " + ch
            limit = 75
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def esc(text):
    return str(text).replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")


def build_event(e, change_id):
    start = paris_stamp(e["scheduled_start_at"])
    end = paris_stamp(e["expected_end_at"])
    dtstamp = utc_stamp(e["detected_at"])
    lines = [
        "BEGIN:VEVENT",
        f"UID:{e['calendar_uid']}",
        f"DTSTAMP:{dtstamp}",
        f"LAST-MODIFIED:{dtstamp}",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        f"PRIORITY:{e.get('calendar_priority', 9)}",
        "X-FORTNITE-PRIORITY:INFO",
        f"X-FORTNITE-ACTION:{e.get('calendar_action', 'PLAN')}",
        "X-FORTNITE-EVENT-TYPE:SERVICE_DOWNTIME",
        f"X-FORTNITE-SERVICE-EVENT-ID:{e['service_event_id']}",
        f"X-FORTNITE-SERVICE-KIND:{e['kind']}",
        f"X-FORTNITE-SERVICE-STATE:{e['state']}",
        f"X-FORTNITE-SERVICE-PROVIDER-PHASE:{e['provider_phase']}",
        f"X-FORTNITE-SERVICE-IMPACT:{e['provider_impact']}",
        f"X-FORTNITE-SERVICE-ACTIONABILITY:{e['internal_actionability']}",
        "X-FORTNITE-AFFECTED-SERVICE:Epic Online Services Lobbies,Sessions,Matchmaking",
        f"X-FORTNITE-SERVICE-SOURCE-ID:{e['source_id']}",
        f"X-FORTNITE-SERVICE-RELATION-TYPE:{e['relation_type']}",
        "X-FORTNITE-TIME-PRECISION:EXACT",
        f"X-FORTNITE-LAST-CHANGE-ID:{change_id}",
        f"DTSTART;TZID=Europe/Paris:{start}",
        f"DTEND;TZID=Europe/Paris:{end}",
        "SUMMARY:ℹ️ ✅ 🛠️ Maintenance Epic Online Services — sessions/lobbies",
        "DESCRIPTION:" + esc(
            "Priorité : ℹ️ Info — maintenance Epic Online Services planifiée.\n"
            "Le 22 septembre 2026 de 08h00 à 09h30 heure de Paris, Epic prévoit une disponibilité dégradée des services Sessions et Lobbies.\n"
            "Epic indique que les sessions existantes expireront et que les clients seront déconnectés ; création de nouvelles sessions, invitations, recherche et matchmaking seront temporairement indisponibles pendant cette fenêtre.\n"
            "Aucun patch Fortnite, saison ou compétition n'est lié par inférence.\n"
            f"Source : {e['source_url']}"
        ),
        f"URL:{e['source_url']}",
        "CATEGORIES:Fortnite,Maintenance,Epic Online Services,Matchmaking",
        "BEGIN:VALARM",
        "TRIGGER:-PT1H",
        "ACTION:DISPLAY",
        "DESCRIPTION:🛠️ Maintenance EOS dans 1 h — sessions/lobbies et matchmaking potentiellement indisponibles",
        "END:VALARM",
        "END:VEVENT",
    ]
    folded = []
    for line in lines:
        folded.extend(fold_line(line))
    return "\r\n".join(folded) + "\r\n"


def add_ics(path, uid, event_text):
    raw = path.read_text(encoding="utf-8")
    normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
    if f"UID:{uid}" in normalized:
        return False
    marker = "END:VCALENDAR\n"
    if marker not in normalized:
        raise RuntimeError(f"{path} missing END:VCALENDAR")
    normalized = normalized.replace(marker, event_text.replace("\r\n", "\n") + "END:VCALENDAR\n")
    path.write_bytes(normalized.replace("\n", "\r\n").encode("utf-8"))
    return True


def rebuild_index(index, ledger, outbox, updated_at):
    changes = ledger.get("changes", [])
    heads = {}
    by_domain = {}
    by_type = {}
    open_by_subject = {}
    for c in changes:
        sk = c["subject_scope_key"]
        rev = c["subject_revision"]
        cur = heads.get(sk)
        if cur is None or rev > cur["revision"]:
            heads[sk] = {"revision": rev, "change_id": c["change_id"]}
        by_domain.setdefault(c["domain"], []).append(c["change_id"])
        by_type.setdefault(c["change_type"], []).append(c["change_id"])
        if c.get("state", "OPEN") == "OPEN":
            open_by_subject.setdefault(sk, []).append(c["change_id"])
    for d in (by_domain, by_type, open_by_subject):
        for key in d:
            d[key] = sorted(d[key])
    consumed = outbox.get("consumed_keys", {})
    unknown = sorted(k for k, v in consumed.items() if v.get("state") == "UNKNOWN_DELIVERY")
    index["updated_at"] = updated_at
    index["subject_heads"] = {k: heads[k] for k in sorted(heads)}
    index["by_domain"] = {k: by_domain[k] for k in sorted(by_domain)}
    index["by_change_type"] = {k: by_type[k] for k in sorted(by_type)}
    index["open_changes_by_subject"] = {k: open_by_subject[k] for k in sorted(open_by_subject)}
    index["consumed_notification_keys"] = sorted(consumed)
    index["unknown_delivery_keys"] = unknown
    index["stats"] = {
        "changes": len(changes),
        "subjects": len(heads),
        "notification_intents": len(outbox.get("intents", [])),
        "consumed_notification_keys": len(consumed),
        "unknown_delivery": len(unknown),
    }


def main():
    inbox = load(INBOX)
    service = load(SERVICE)
    ledger = load(CHANGE)
    index = load(INDEX)
    outbox = load(OUTBOX)
    changed = False

    for e in inbox.get("events", []):
        if any(x.get("service_event_id") == e["service_event_id"] for x in service.get("entries", [])):
            continue

        scope_key = None
        subject_key = e["service_event_id"]
        subject_scope = "sub_" + sha256(f"SERVICE|{subject_key}|")
        previous = [c for c in ledger.get("changes", []) if c.get("subject_scope_key") == subject_scope]
        revision = max([c.get("subject_revision", 0) for c in previous] or [0]) + 1
        parent = None
        if previous:
            parent = max(previous, key=lambda c: c.get("subject_revision", 0))["change_id"]

        material_after = {
            "state": e["state"],
            "provider_phase": e["provider_phase"],
            "scheduled_start_at": e["scheduled_start_at"],
            "expected_end_at": e["expected_end_at"],
            "affected_components": sorted([c["component_id"] for c in e["component_states"]]),
            "relation_type": e["relation_type"],
        }
        state_fp = sha256(canon(material_after))
        transition_obj = {
            "change_type": "MAINTENANCE_CHANGED",
            "material_before": None,
            "material_after": material_after,
            "material_evidence_state": "OFFICIAL_EXACT_SCHEDULED_MAINTENANCE",
        }
        transition_fp = sha256(canon(transition_obj))
        cid_seed = f"SERVICE|{subject_key}||{revision}|{parent or ''}|{transition_fp}"
        change_id = "chg_" + sha256(cid_seed)[:24]

        entry = {
            "service_event_id": e["service_event_id"],
            "epic_incident_id": e["epic_incident_id"],
            "external_alias_ids": [],
            "calendar_uid": e["calendar_uid"],
            "fingerprint": f"epic:{e['epic_incident_id']}",
            "kind": e["kind"],
            "state": e["state"],
            "source_id": e["source_id"],
            "canonical_source_url": e["source_url"],
            "first_seen_at": e["detected_at"],
            "last_changed_at": e["detected_at"],
            "provider_phase": e["provider_phase"],
            "provider_impact": e["provider_impact"],
            "provider_title": e["provider_title"],
            "provider_message_hash": None,
            "announced_at": e["announced_at"],
            "scheduled_start_at": e["scheduled_start_at"],
            "actual_start_at": None,
            "expected_end_at": e["expected_end_at"],
            "expected_end_updated_at": e["announced_at"],
            "recovery_started_at": None,
            "actual_end_at": None,
            "source_timezone": e["source_timezone"],
            "timing_precision": e["timing_precision"],
            "component_states": [
                {**c, "source_id": e["source_id"], "source_url": e["source_url"], "observed_at": e["detected_at"]}
                for c in e["component_states"]
            ],
            "affected_regions": e["affected_regions"],
            "affected_platforms": [],
            "internal_actionability": e["internal_actionability"],
            "internal_priority_score": e["internal_priority_score"],
            "relation_type": e["relation_type"],
            "relation_confidence": e["relation_confidence"],
            "related_event_uid": None,
            "related_candidate_id": None,
            "group_id": None,
            "patch_version": None,
            "season_id": None,
            "relation_source_id": e["source_id"],
            "relation_source_url": e["source_url"],
            "calendar_status": "PROMOTED",
            "calendar_promoted_at": e["detected_at"],
            "calendar_last_synced_at": e["detected_at"],
            "previous_state": None,
            "evidence_grade": "A",
            "confidence": "OFFICIAL_EXACT",
            "last_verified_at": e["detected_at"],
            "extension_count": 0,
            "notified_transition_keys": [],
            "history": [
                {
                    "at": e["detected_at"],
                    "event_type": "CREATED",
                    "source_id": e["source_id"],
                    "source_url": e["source_url"],
                    "note": e["note"],
                },
                {
                    "at": e["detected_at"],
                    "event_type": "CALENDAR_PROMOTED",
                    "source_id": e["source_id"],
                    "source_url": e["source_url"],
                    "note": "Official exact EOS maintenance window projected to Fortnite global and updates calendars because matchmaking/session availability is actionable.",
                },
            ],
        }
        service.setdefault("entries", []).append(entry)
        service["updated_at"] = e["detected_at"]

        change = {
            "change_id": change_id,
            "domain": "SERVICE",
            "subject_scope_key": subject_scope,
            "subject_key": subject_key,
            "subject_revision": revision,
            "causal_parent_change_id": parent,
            "change_type": "MAINTENANCE_CHANGED",
            "materiality": e["materiality"],
            "state_fingerprint": state_fp,
            "transition_fingerprint": transition_fp,
            "detected_at": e["detected_at"],
            "source_refs": [e["source_url"]],
            "notification_disposition": e["notification_disposition"],
            "scope_key": scope_key,
            "material_before": None,
            "material_after": material_after,
            "material_evidence_state": "OFFICIAL_EXACT_SCHEDULED_MAINTENANCE",
            "projection_targets": ["calendars/fortnite-paris.ics", "calendars/fortnite-updates-france.ics"],
            "policy_version": "FORTNITE_SERVICE_INTELLIGENCE_FR_V2",
            "notes": e["note"],
        }
        ledger.setdefault("changes", []).append(change)
        ledger["updated_at"] = e["detected_at"]

        event_text = build_event(e, change_id)
        add_ics(GLOBAL_ICS, e["calendar_uid"], event_text)
        add_ics(UPDATES_ICS, e["calendar_uid"], event_text)
        changed = True

    if not changed:
        print("NOOP: no new service events")
        return 0

    rebuild_index(index, ledger, outbox, ledger["updated_at"])
    dump(SERVICE, service, compact=False)
    dump(CHANGE, ledger, compact=True)
    dump(INDEX, index, compact=True)
    print("OK: Fortnite service inbox ingested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
