#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-29T09:13:36Z"
AT_ICS = "20260829T091336Z"
CID = "fortnite-og-final-showdown-return-20260829"
UID = "fortnite-og-final-showdown-return-20260829@openai"
SOURCE = "https://communities.epicgames.com/thread/the-final-showdown-event-returns-to-fortnite-og/Ull5"
FORTNITE_PAGE = "https://www.fortnite.com/@epic/fortnite-og"
NOTICE_KIND = "FORTNITE_OG_FINAL_SHOWDOWN_RETURN_TODAY"
PAYLOAD = "🔥 Fortnite OG — The Final Showdown revient aujourd’hui à 20h00 (Paris) pour 10 minutes. Epic recommande d’entrer dans une partie OG avant 19h55. Les dégâts et la tempête seront désactivés 10 minutes avant l’événement et un Jetpack permettra de choisir un point d’observation."


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


def add_watchlist():
    path = CAL / "fortnite-watchlist-france.json"
    data = load(path)
    existing = next((c for c in data.get("candidates", []) if c.get("candidate_id") == CID), None)
    if existing:
        return False
    data.setdefault("candidates", []).append({
        "candidate_id": CID,
        "state": "CALENDAR_ADDED",
        "topic": "Fortnite OG — The Final Showdown — retour le 29 août 2026",
        "source_ids": ["fortnite_news"],
        "known": "Epic confirme le retour de The Final Showdown dans Fortnite OG le 29 août 2026 à 18:00 UTC, soit 20:00 à Paris. L'événement dure 10 minutes. Epic recommande d'entrer dans une partie OG avant 17:55 UTC, soit 19:55 à Paris. Les dégâts et la tempête sont désactivés 10 minutes avant et un Jetpack est fourni pour choisir un point d'observation.",
        "missing_for_calendar": [],
        "promotion_rule": "Déjà promu depuis une publication Epic Communities directe mise en avant sur la page Fortnite OG officielle. Conserver un UID stable ; aucune identité du 'monstrous threat' ni relation lore n'est inférée sans source officielle explicite.",
        "official_event_url": SOURCE,
        "related_calendar_uid": UID,
        "promoted_at": AT
    })
    data["updated_at"] = AT
    dump(path, data)
    return True


def add_change():
    path = CAL / "fortnite-change-ledger.json"
    data = load(path)
    subject = f"calendars/fortnite-updates-france.ics|{UID}"
    existing = next((c for c in data.get("changes", []) if c.get("domain") == "CALENDAR_PROJECTION" and c.get("subject_key") == subject), None)
    if existing:
        return existing["change_id"], existing.get("notification_disposition")
    material_after = {
        "uid": UID,
        "status": "CONFIRMED",
        "mode": "FORTNITE_OG",
        "action": "PLAY",
        "event_type": "LIVE_EVENT",
        "theme": "FINAL_SHOWDOWN",
        "start_at": "2026-08-29T20:00:00+02:00",
        "end_at": "2026-08-29T20:10:00+02:00",
        "join_by": "2026-08-29T19:55:00+02:00",
        "pre_event_rules": {
            "damage_disabled": True,
            "storm_paused": True,
            "starts_minutes_before_event": 10,
            "jetpack_viewing": True
        },
        "projection_targets": ["calendars/fortnite-updates-france.ics", "calendars/fortnite-paris.ics"]
    }
    evidence = "EPIC_COMMUNITIES_DIRECT_EXACT_UTC_PLUS_OFFICIAL_FORTNITE_OG_HIGHLIGHT"
    transition_fp = sha({"change_type":"CALENDAR_PROMOTED","material_before":None,"material_after":material_after,"material_evidence_state":evidence})
    state_fp = sha(material_after)
    scope = "calendars/fortnite-paris.ics"
    subject_scope_key = "sub_" + sha(f"CALENDAR_PROJECTION|{subject}|{scope}")
    change_id = "chg_" + sha(f"CALENDAR_PROJECTION|{subject}|{scope}|1||{transition_fp}")[:24]
    rec = {
        "change_id": change_id,
        "domain": "CALENDAR_PROJECTION",
        "subject_scope_key": subject_scope_key,
        "subject_key": subject,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": "CALENDAR_PROMOTED",
        "materiality": "NOTIFY",
        "state_fingerprint": state_fp,
        "transition_fingerprint": transition_fp,
        "detected_at": AT,
        "source_refs": [SOURCE, FORTNITE_PAGE],
        "notification_disposition": "ELIGIBLE_NOW",
        "scope_key": scope,
        "material_before": None,
        "material_after": material_after,
        "material_evidence_state": evidence,
        "projection_targets": ["calendars/fortnite-updates-france.ics", "calendars/fortnite-paris.ics"],
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
        "notes": "Same-day official 10-minute Fortnite OG live event. No lore identity/causation is materialized from the generic 'monstrous threat' wording."
    }
    data.setdefault("changes", []).append(rec)
    data["updated_at"] = AT
    data.setdefault("history", []).append({"at":AT,"type":"MATERIAL_CALENDAR_PROMOTION","note":"Official Fortnite OG Final Showdown return projected into updates + global with exact start, 10-minute duration and join-by time."})
    dump(path, data, compact=True)

    idx_path = CAL / "fortnite-change-index-france.json"
    idx = load(idx_path)
    idx["updated_at"] = AT
    idx.setdefault("subject_heads", {})[subject_scope_key] = {"revision":1,"change_id":change_id}
    sorted_add(idx.setdefault("by_domain", {}), "CALENDAR_PROJECTION", change_id)
    sorted_add(idx.setdefault("by_change_type", {}), "CALENDAR_PROMOTED", change_id)
    idx.setdefault("open_changes_by_subject", {})[subject_scope_key] = [change_id]
    stats = idx.setdefault("stats", {})
    stats["changes"] = len(data.get("changes", []))
    stats["subjects"] = len(idx.get("subject_heads", {}))
    dump(idx_path, idx, compact=True)
    return change_id, "ELIGIBLE_NOW"


def fold_line(line: str):
    if len(line.encode("utf-8")) <= 75:
        return [line]
    out, rest, first = [], line, True
    while rest:
        limit = 75 if first else 74
        used, chars = 0, []
        for ch in rest:
            b = len(ch.encode("utf-8"))
            if chars and used + b > limit:
                break
            chars.append(ch)
            used += b
        part = "".join(chars)
        out.append(("" if first else " ") + part)
        rest = rest[len(part):]
        first = False
    return out


def add_calendar_event(change_id):
    path = CAL / "fortnite-updates-france.ics"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if f"UID:{UID}" in text:
        return False
    lines = [
        "BEGIN:VEVENT", f"UID:{UID}", f"DTSTAMP:{AT_ICS}", f"LAST-MODIFIED:{AT_ICS}",
        "SEQUENCE:0", "STATUS:CONFIRMED", "PRIORITY:1", "X-FORTNITE-PRIORITY:CRITICAL",
        "X-FORTNITE-ACTION:PLAY", "X-FORTNITE-EVENT-TYPE:LIVE_EVENT", "X-FORTNITE-MODE:FORTNITE_OG",
        "X-FORTNITE-THEME:FINAL_SHOWDOWN", "X-FORTNITE-EVIDENCE-GRADE:A", "X-FORTNITE-SOURCE-ID:fortnite_news",
        "X-FORTNITE-SOURCE-TIMEZONE:UTC", "X-FORTNITE-TIME-PRECISION:EXACT", f"X-FORTNITE-CANDIDATE-ID:{CID}",
        f"X-FORTNITE-LAST-CHANGE-ID:{change_id}", f"X-FORTNITE-FIRST-ADDED-AT:{AT_ICS}", "X-FORTNITE-NEW-UNTIL:20260903T091336Z",
        "X-FORTNITE-JOIN-BY;TZID=Europe/Paris:20260829T195500",
        "DTSTART;TZID=Europe/Paris:20260829T200000", "DTEND;TZID=Europe/Paris:20260829T201000",
        "SUMMARY:🔥 ✅ 🆕 🎬 Fortnite OG — The Final Showdown",
        "DESCRIPTION:Priorité : 🔥 Critique — live event Fortnite OG officiel de 10 minutes.\\nDébut : samedi 29 août à 20h00 à Paris (18:00 UTC).\\n⚠️ Epic recommande d’entrer dans une partie Fortnite OG avant 19h55 à Paris.\\nDix minutes avant l’événement, les dégâts sont désactivés et la tempête mise en pause ; un Jetpack est fourni pour choisir un point d’observation. Après l’événement, dégâts et tempête sont réactivés.\\nEpic décrit une menace monstrueuse près de la côte au nord de Lazy Lagoon ; aucune identité, relation ou causalité lore supplémentaire n’est déduite.\\nSource : https://communities.epicgames.com/thread/the-final-showdown-event-returns-to-fortnite-og/Ull5",
        f"URL:{SOURCE}", "CATEGORIES:Fortnite,Fortnite OG,Live Event,The Final Showdown",
        "BEGIN:VALARM", "TRIGGER:-PT1H", "ACTION:DISPLAY", "DESCRIPTION:🎬 The Final Showdown dans 1 h — Fortnite OG à 20h", "END:VALARM",
        "BEGIN:VALARM", "TRIGGER:-PT15M", "ACTION:DISPLAY", "DESCRIPTION:🔥 The Final Showdown dans 15 min — entre dans une partie OG avant 19h55", "END:VALARM",
        "END:VEVENT"
    ]
    folded = []
    for line in lines:
        folded.extend(fold_line(line))
    event = "\n".join(folded) + "\n"
    if "END:VCALENDAR" not in text:
        raise RuntimeError("updates calendar missing END:VCALENDAR")
    text = text.replace("END:VCALENDAR", event + "END:VCALENDAR", 1)
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    return True


def reserve_notification(change_id):
    path = CAL / "fortnite-notification-outbox-france.json"
    data = load(path)
    key = "ntf_" + sha(f"{change_id}|{NOTICE_KIND}|user|chat")
    if key in data.get("consumed_keys", {}):
        return key, False
    intent_id = "nti_" + sha(key)[:24]
    if any(i.get("notification_key") == key for i in data.get("intents", [])):
        return key, False
    reservation_id = "nrs_" + sha(f"{key}|{AT}|final-showdown")[:24]
    delivery_id = "nde_" + sha(f"{intent_id}|RESERVED|1|{reservation_id}")[:24]
    data.setdefault("intents", []).append({
        "intent_id": intent_id,
        "notification_key": key,
        "change_ids": [change_id],
        "notice_kind": NOTICE_KIND,
        "audience_key": "user",
        "channel_key": "chat",
        "payload_fingerprint": sha(PAYLOAD),
        "render_version": "FORTNITE_ALERT_FR_V1",
        "created_at": AT,
        "subject_key": UID,
        "locale": "fr-FR",
        "payload_snapshot": PAYLOAD,
        "condition_snapshot": {
            "start_at": "2026-08-29T20:00:00+02:00",
            "end_at": "2026-08-29T20:10:00+02:00",
            "join_by": "2026-08-29T19:55:00+02:00",
            "event_future": True
        },
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2"
    })
    data.setdefault("delivery_events", []).append({
        "delivery_event_id": delivery_id,
        "intent_id": intent_id,
        "notification_key": key,
        "state": "RESERVED",
        "at": AT,
        "reservation_id": reservation_id,
        "note": "Reserved after canonical revalidation of the official same-day Fortnite OG Final Showdown live event. This consumes the key before user-visible emission."
    })
    data.setdefault("consumed_keys", {})[key] = {"intent_id": intent_id, "state": "RESERVED", "last_event_id": delivery_id}
    data.setdefault("history", []).append({"at":AT,"type":"NOTIFICATION_RESERVED","notification_key":key,"note":"One notification reserved for The Final Showdown official return in Fortnite OG."})
    data["updated_at"] = AT
    dump(path, data, compact=True)
    return key, True


def reconcile_outbox_index():
    outbox = load(CAL / "fortnite-notification-outbox-france.json")
    idx_path = CAL / "fortnite-change-index-france.json"
    idx = load(idx_path)
    consumed = sorted(outbox.get("consumed_keys", {}).keys())
    unknown = sorted(k for k, v in outbox.get("consumed_keys", {}).items() if v.get("state") == "UNKNOWN_DELIVERY")
    idx["consumed_notification_keys"] = consumed
    idx["unknown_delivery_keys"] = unknown
    idx["updated_at"] = AT
    idx.setdefault("stats", {})["notification_intents"] = len(outbox.get("intents", []))
    idx["stats"]["consumed_notification_keys"] = len(consumed)
    idx["stats"]["unknown_delivery"] = len(unknown)
    dump(idx_path, idx, compact=True)


def main():
    add_watchlist()
    change_id, disposition = add_change()
    add_calendar_event(change_id)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_fortnite_calendars.py")], cwd=ROOT, check=True)
    key, reserved = reserve_notification(change_id)
    reconcile_outbox_index()
    print("FINAL_SHOWDOWN_APPLIED", change_id, key, "RESERVED" if reserved else "ALREADY_CONSUMED", disposition)


if __name__ == "__main__":
    main()
