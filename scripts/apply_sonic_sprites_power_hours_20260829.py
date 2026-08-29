#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-29T02:00:55Z"
AT_ICS = "20260829T020055Z"
CID = "fortnite-sonic-sprites-power-hours-20260829"
UID = "fortnite-sonic-sprites-power-hours-20260829@openai"
SOURCE = "https://communities.epicgames.com/thread/power-hours-sonic-sprites-this-weekend-august-29/XvRq"
FORTNITE_PAGE = "https://www.fortnite.com/@epic/battle-royale"
NOTICE_KIND = "SONIC_SPRITES_POWER_HOURS_TODAY"
PAYLOAD = "💨 Fortnite Battle Royale — Power Hours: Sonic Sprites aujourd’hui. Deux fenêtres officielles : 20h–22h samedi 29 août puis 03h–05h dimanche 30 août (Paris). Le Storm Scout Sprite fait ses débuts ; Sonic, Tails et Shadow Sprites apparaissent plus souvent, les Sonic Power Sneakers ont un taux de drop accru dans les coffres, et des 1-Up Tokens / Portable Extractors peuvent aussi apparaître comme trouvailles rares."


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
        "topic": "Battle Royale — Power Hours: Sonic Sprites — 29/30 août 2026",
        "source_ids": ["fortnite_news"],
        "known": "Epic/Fortnite confirme deux fenêtres Power Hours : 29 août 18:00–20:00 UTC puis 30 août 01:00–03:00 UTC, soit 20:00–22:00 puis 03:00–05:00 à Paris. Storm Scout Sprite débute pendant l’événement ; Sonic/Tails/Shadow Sprites apparaissent plus souvent, Sonic Power Sneakers bénéficient d’un taux de drop accru dans les coffres et des 1-Up Tokens / Portable Extractors peuvent apparaître comme trouvailles rares.",
        "missing_for_calendar": [],
        "promotion_rule": "Déjà promu depuis une publication Epic Communities directe et une mise en avant sur la page Fortnite Battle Royale officielle. Conserver un seul UID logique avec deux sessions distinctes ; ne jamais traiter l’intervalle entre 22h et 03h comme une fenêtre active.",
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
        "mode": "BATTLE_ROYALE",
        "action": "PLAY",
        "event_type": "LIMITED_TIME_EVENT",
        "theme": "SONIC_SPRITES",
        "windows": [
            {"start_at": "2026-08-29T20:00:00+02:00", "end_at": "2026-08-29T22:00:00+02:00"},
            {"start_at": "2026-08-30T03:00:00+02:00", "end_at": "2026-08-30T05:00:00+02:00"}
        ],
        "storm_scout_sprite_debut": True,
        "boosted": ["SONIC_TAILS_SHADOW_SPRITE_APPEARANCE", "SONIC_POWER_SNEAKERS_CHEST_DROP_RATE"],
        "rare_chest_finds": ["1-UP_TOKENS", "PORTABLE_EXTRACTORS"],
        "projection_targets": ["calendars/fortnite-updates-france.ics", "calendars/fortnite-paris.ics"]
    }
    evidence = "EPIC_COMMUNITIES_DIRECT_EXACT_WINDOWS_PLUS_FORTNITE_OFFICIAL_HIGHLIGHT"
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
        "notes": "Same-day official limited event. Two exact sessions are represented separately; only the first window gets a calendar H-1 alarm to avoid a 02:00 overnight alarm."
    }
    data.setdefault("changes", []).append(rec)
    data["updated_at"] = AT
    data.setdefault("history", []).append({"at":AT,"type":"MATERIAL_CALENDAR_PROMOTION","note":"Official Sonic Sprites Power Hours projected into updates + global with two exact windows."})
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
            chars.append(ch); used += b
        part = "".join(chars)
        out.append(("" if first else " ") + part)
        rest = rest[len(part):]
        first = False
    return out


def add_calendar_event(change_id):
    path = CAL / "fortnite-updates-france.ics"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n","\n").replace("\r","\n")
    if f"UID:{UID}" in text:
        return False
    lines = [
        "BEGIN:VEVENT", f"UID:{UID}", f"DTSTAMP:{AT_ICS}", f"LAST-MODIFIED:{AT_ICS}",
        "SEQUENCE:0", "STATUS:CONFIRMED", "PRIORITY:5", "X-FORTNITE-PRIORITY:IMPORTANT",
        "X-FORTNITE-ACTION:PLAY", "X-FORTNITE-EVENT-TYPE:LIMITED_TIME_EVENT", "X-FORTNITE-MODE:BATTLE_ROYALE",
        "X-FORTNITE-THEME:SONIC_SPRITES", "X-FORTNITE-EVIDENCE-GRADE:A", "X-FORTNITE-SOURCE-ID:fortnite_news",
        "X-FORTNITE-SOURCE-TIMEZONE:UTC", "X-FORTNITE-TIME-PRECISION:EXACT", f"X-FORTNITE-CANDIDATE-ID:{CID}",
        f"X-FORTNITE-LAST-CHANGE-ID:{change_id}", f"X-FORTNITE-FIRST-ADDED-AT:{AT_ICS}", "X-FORTNITE-NEW-UNTIL:20260903T020055Z",
        "X-FORTNITE-SESSION;TYPE=POWER_HOUR_1:20260829T200000/20260829T220000",
        "X-FORTNITE-SESSION;TYPE=POWER_HOUR_2:20260830T030000/20260830T050000",
        "DTSTART;TZID=Europe/Paris:20260829T200000", "DTEND;TZID=Europe/Paris:20260829T220000",
        "SUMMARY:⭐ ✅ 🆕 💨 Power Hours — Sonic Sprites",
        "DESCRIPTION:Priorité : ⭐ Important — événement Battle Royale limité confirmé directement par Epic/Fortnite.\\nFenêtre 1 : samedi 29 août 20h00–22h00 à Paris.\\nFenêtre 2 : dimanche 30 août 03h00–05h00 à Paris.\\n⚠️ Les deux fenêtres sont distinctes : l’événement n’est pas présenté comme actif entre 22h et 03h.\\nLe Storm Scout Sprite fait ses débuts pendant ces Power Hours. Sonic, Tails et Shadow Sprites apparaissent plus souvent, variantes incluses ; les Sonic Power Sneakers ont un taux de drop accru depuis les coffres. Des 1-Up Tokens et Portable Extractors peuvent aussi apparaître comme trouvailles rares.\\nAucun taux chiffré ni garantie de drop n’est déduit.\\nSource : https://communities.epicgames.com/thread/power-hours-sonic-sprites-this-weekend-august-29/XvRq",
        f"URL:{SOURCE}", "CATEGORIES:Fortnite,Battle Royale,Power Hours,Sonic,Sprites,Événement limité",
        "BEGIN:VALARM", "TRIGGER:-PT1H", "ACTION:DISPLAY", "DESCRIPTION:💨 Sonic Sprites Power Hours dans 1 h — première fenêtre à 20h", "END:VALARM", "END:VEVENT"
    ]
    folded = []
    for line in lines:
        folded.extend(fold_line(line))
    event = "\n".join(folded) + "\n"
    if "END:VCALENDAR" not in text:
        raise RuntimeError("updates calendar missing END:VCALENDAR")
    text = text.replace("END:VCALENDAR", event + "END:VCALENDAR", 1)
    path.write_bytes(text.replace("\n","\r\n").encode("utf-8"))
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
    reservation_id = "nrs_" + sha(f"{key}|{AT}|sonic-sprites")[:24]
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
        "condition_snapshot": {"window_1":"2026-08-29T20:00:00+02:00/2026-08-29T22:00:00+02:00","window_2":"2026-08-30T03:00:00+02:00/2026-08-30T05:00:00+02:00","event_future":True},
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2"
    })
    data.setdefault("delivery_events", []).append({
        "delivery_event_id": delivery_id, "intent_id": intent_id, "notification_key": key,
        "state":"RESERVED", "at":AT, "reservation_id":reservation_id,
        "note":"Reserved after canonical revalidation of the newly published same-day Sonic Sprites Power Hours. This consumes the key before user-visible emission."
    })
    data.setdefault("consumed_keys", {})[key] = {"intent_id":intent_id,"state":"RESERVED","last_event_id":delivery_id}
    data.setdefault("history", []).append({"at":AT,"type":"NOTIFICATION_RESERVED","notification_key":key,"note":"One notification reserved for the official Sonic Sprites Power Hours exact windows."})
    data["updated_at"] = AT
    dump(path, data, compact=True)
    return key, True


def main():
    add_watchlist()
    change_id, disposition = add_change()
    add_calendar_event(change_id)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_fortnite_calendars.py")], cwd=ROOT, check=True)
    key, reserved = reserve_notification(change_id)
    print("SONIC_SPRITES_APPLIED", change_id, key, "RESERVED" if reserved else "ALREADY_CONSUMED", disposition)


if __name__ == "__main__":
    main()
