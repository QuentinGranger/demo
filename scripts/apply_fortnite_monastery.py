#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
DETECTED_AT = "2026-08-22T20:18:37Z"
UID = "fortnite-lego-odyssey-monastery-portal-20260827@openai"
CANDIDATE_ID = "fortnite-lego-odyssey-monastery-portal-20260827"
CHANGE_ID = "chg_0f6de9cd0cf986bde06d38a1"
SUBJECT_SCOPE_KEY = "sub_f6490fede4f25f92255d0a19f8feaae540e7d157ce214402b050e5ea0e22d317"
SOURCE_URL = "https://www.fortnite.com/@epic/lego-fortnite-odyssey?lang=fr"


def write_json(path, obj, *, pretty=False):
    if pretty:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    else:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def apply_ledger():
    path = CAL / "fortnite-change-ledger.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if any(c.get("change_id") == CHANGE_ID for c in data.get("changes", [])):
        return
    # Reject an unexpected prior occurrence instead of fabricating a revision chain.
    if any(c.get("subject_scope_key") == SUBJECT_SCOPE_KEY for c in data.get("changes", [])):
        raise RuntimeError("Monastery subject already has a different change head; manual reconciliation required")
    data["changes"].append({
        "change_id": CHANGE_ID,
        "domain": "WATCHLIST",
        "subject_scope_key": SUBJECT_SCOPE_KEY,
        "subject_key": CANDIDATE_ID,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": "CALENDAR_PROMOTED",
        "materiality": "CALENDAR",
        "state_fingerprint": "6b8800605eff28d74309c2d0b684d56ecf861620939cc96ba3aff4da363b1f2c",
        "transition_fingerprint": "e32908e0a0a636f904d3a9f2c3871a51666689b50c7011df043f246113006447",
        "detected_at": DETECTED_AT,
        "source_refs": [SOURCE_URL],
        "notification_disposition": "SILENT_POLICY",
        "scope_key": None,
        "material_before": {"state": "READY"},
        "material_after": {
            "candidate_id": CANDIDATE_ID,
            "state": "CALENDAR_ADDED",
            "event_uid": UID,
            "mode": "LEGO_FORTNITE_ODYSSEY",
            "start_at": "2026-08-27T08:00:00Z",
            "end_at": "2026-09-02T08:00:00Z",
            "rewards": ["Nunchucks of LIGHTNING", "Scythe of QUAKES", "Shurikens of ICE", "Sword of FIRE"],
            "action": "PLAY"
        },
        "material_evidence_state": "FORTNITE_OFFICIAL_EXACT_EVENT_WINDOW",
        "projection_targets": ["calendars/fortnite-updates-france.ics", "calendars/fortnite-paris.ics"],
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
        "notes": "Official time-bounded LEGO Fortnite Odyssey gameplay event. Immediate chat alert suppressed; calendar J-1 reminder is the selected user effect."
    })
    data.setdefault("history", []).append({
        "at": DETECTED_AT,
        "type": "MATERIAL_LEGO_FORTNITE_EVENT_PROMOTED",
        "note": "Official Monastery portal window promoted to updates/global; the J-1 calendar alarm covers actionable timing without an immediate chat alert."
    })
    data["updated_at"] = DETECTED_AT
    write_json(path, data)


def apply_watchlist():
    path = CAL / "fortnite-watchlist-france.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    found = False
    for c in data.get("candidates", []):
        if c.get("candidate_id") == CANDIDATE_ID:
            found = True
            c["state"] = "CALENDAR_ADDED"
            c["source_ids"] = ["fortnite_news"]
            c["missing_for_calendar"] = []
            c["related_calendar_uid"] = UID
            c["promoted_at"] = DETECTED_AT
            c["promotion_rule"] = "Déjà promu depuis une publication Fortnite officielle datée et actionnable. Conserver le même UID si la fenêtre ou les récompenses sont corrigées officiellement."
    if not found:
        raise RuntimeError("Monastery candidate missing")
    data["updated_at"] = DETECTED_AT
    write_json(path, data, pretty=True)


def apply_updates_ics():
    path = CAL / "fortnite-updates-france.ics"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if f"UID:{UID}" in text:
        return
    event_lines = [
        "BEGIN:VEVENT",
        f"UID:{UID}",
        "DTSTAMP:20260822T201837Z",
        "LAST-MODIFIED:20260822T201837Z",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "PRIORITY:5",
        "X-FORTNITE-PRIORITY:IMPORTANT",
        "X-FORTNITE-ACTION:PLAY",
        "X-FORTNITE-EVENT-TYPE:LIMITED_TIME_EVENT",
        "X-FORTNITE-MODE:LEGO_FORTNITE_ODYSSEY",
        "X-FORTNITE-EVIDENCE-GRADE:A",
        "X-FORTNITE-SOURCE-ID:fortnite_news",
        "X-FORTNITE-SOURCE-TIMEZONE:America/New_York",
        "X-FORTNITE-TIME-PRECISION:EXACT",
        "X-FORTNITE-FIRST-ADDED-AT:20260822T201837Z",
        "X-FORTNITE-NEW-UNTIL:20260827T201837Z",
        "DTSTART;TZID=Europe/Paris:20260827T100000",
        "DTEND;TZID=Europe/Paris:20260902T100000",
        "SUMMARY:⭐ ✅ 🆕 🧱 LEGO Fortnite Odyssey — Portail du Monastère",
        "DESCRIPTION:Priorité : ⭐ Important — événement limité officiellement daté dans LEGO Fortnite Odyssey.\\nDu 27 août 2026 à 10h00 au 2 septembre 2026 à 10h00 (heure de Paris), le portail du Monastère rouvre.\\nObjectif : vaincre le Shatter Spawn.\\nRécompenses dorées annoncées : Sword of FIRE, Scythe of QUAKES, Nunchucks of LIGHTNING et Shurikens of ICE.\\nLa fenêtre source est publiée comme 27 août 04:00 ET → 2 septembre 04:00 ET ; la conversion Europe/Paris est exacte pour ces dates.\\nSource : https://www.fortnite.com/@epic/lego-fortnite-odyssey?lang=fr",
        f"URL:{SOURCE_URL}",
        "CATEGORIES:Fortnite,LEGO Fortnite Odyssey,Événement limité,Récompenses",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        "DESCRIPTION:🧱 Le portail du Monastère ouvre demain dans LEGO Fortnite Odyssey",
        "END:VALARM",
        "END:VEVENT",
    ]
    marker = "\nEND:VCALENDAR"
    if marker not in text:
        raise RuntimeError("updates ICS missing END:VCALENDAR")
    text = text.replace(marker, "\n" + "\n".join(event_lines) + marker, 1)
    path.write_bytes((text.rstrip("\n") + "\n").encode("utf-8"))


def rebuild_index():
    ledger = json.loads((CAL / "fortnite-change-ledger.json").read_text(encoding="utf-8"))
    outbox = json.loads((CAL / "fortnite-notification-outbox-france.json").read_text(encoding="utf-8"))
    path = CAL / "fortnite-change-index-france.json"
    idx = json.loads(path.read_text(encoding="utf-8"))
    changes = ledger.get("changes", [])
    heads, by_domain, by_type, open_by = {}, {}, {}, {}
    for c in changes:
        sk, rev, cid = c["subject_scope_key"], c["subject_revision"], c["change_id"]
        if sk not in heads or rev > heads[sk]["revision"]:
            heads[sk] = {"revision": rev, "change_id": cid}
        by_domain.setdefault(c["domain"], []).append(cid)
        by_type.setdefault(c["change_type"], []).append(cid)
        if c.get("state", "OPEN") == "OPEN":
            open_by.setdefault(sk, []).append(cid)
    for d in (by_domain, by_type, open_by):
        for k in d:
            d[k] = sorted(d[k])

    intents = {i["intent_id"]: i for i in outbox.get("intents", [])}
    events_by = {}
    for e in outbox.get("delivery_events", []):
        events_by.setdefault(e["intent_id"], []).append(e)
    consumed = {}
    for iid, evs in events_by.items():
        reserved, latest = False, None
        for e in sorted(evs, key=lambda x: x.get("at", "")):
            st = e.get("state")
            if st == "RESERVED":
                reserved, latest = True, e
            elif st in {"SENT", "UNKNOWN_DELIVERY"} and reserved:
                latest = e
        if latest and iid in intents:
            consumed[intents[iid]["notification_key"]] = latest["state"]
    consumed_keys = sorted(consumed)
    unknown = sorted(k for k, v in consumed.items() if v == "UNKNOWN_DELIVERY")

    idx["updated_at"] = DETECTED_AT
    idx["subject_heads"] = {k: heads[k] for k in sorted(heads)}
    idx["by_domain"] = {k: by_domain[k] for k in sorted(by_domain)}
    idx["by_change_type"] = {k: by_type[k] for k in sorted(by_type)}
    idx["open_changes_by_subject"] = {k: open_by[k] for k in sorted(open_by)}
    idx["consumed_notification_keys"] = consumed_keys
    idx["unknown_delivery_keys"] = unknown
    idx.setdefault("pending_reconciliation", [])
    idx["stats"] = {
        "changes": len(changes),
        "subjects": len(heads),
        "notification_intents": len(outbox.get("intents", [])),
        "consumed_notification_keys": len(consumed_keys),
        "unknown_delivery": len(unknown),
        "pending_reconciliation": len(idx.get("pending_reconciliation", [])),
    }
    write_json(path, idx)


def main():
    apply_ledger()
    apply_watchlist()
    apply_updates_ics()
    rebuild_index()
    print("Applied idempotent Monastery promotion patch")


if __name__ == "__main__":
    main()
