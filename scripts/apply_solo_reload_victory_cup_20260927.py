#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-09-27T05:13:46Z"
ATICS = "20260927T051346Z"
CID = "solo-reload-victory-cup-eu-2026"
UID = "fortnite-solo-reload-victory-cup-eu-2026@openai"
SOURCE = "https://www.fortnite.com/competitive/events/S42_ReloadSoloVictoryCup/?lang=fr&region=EU"
NOTICE = "SOLO_RELOAD_VICTORY_CUP_EU_SCHEDULED"
PAYLOAD = (
    "🏆 Fortnite — la Coupe victoire solo (Recharge) Europe débute vendredi 2 octobre. "
    "Le round 1 se joue de 17 h à 19 h, puis le round 2 de 20 h à 20 h 45 (heure de Paris). "
    "Il faut atteindre Platine ou plus en classé Recharge combiné ; le top 4 000 EU accède au round 2, "
    "où chaque Victoire royale rapporte 100 $ US."
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, obj, compact=False):
    value = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) if compact else json.dumps(obj, ensure_ascii=False, indent=2)
    path.write_text(value + "\n", encoding="utf-8", newline="\n")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj):
    return hashlib.sha256((obj if isinstance(obj, str) else canonical(obj)).encode()).hexdigest()


def add(mapping, key, value):
    mapping[key] = sorted(set(mapping.get(key, []) + [value]))


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()


def fold(line):
    output = []
    first = True
    while line:
        limit = 75 if first else 74
        used = 0
        cut = 0
        for index, char in enumerate(line):
            size = len(char.encode())
            if index and used + size > limit:
                break
            used += size
            cut = index + 1
        output.append(("" if first else " ") + line[:cut])
        line = line[cut:]
        first = False
    return output


class Base:
    load = staticmethod(load)
    dump = staticmethod(dump)
    h = staticmethod(digest)
    add = staticmethod(add)
    fold = staticmethod(fold)


base = Base()


def rebuild_index():
    ledger_path = CAL / "fortnite-competitive-ledger-france.json"
    engine_path = CAL / "fortnite-competitive-engine-france.json"
    index_path = CAL / "fortnite-competitive-index-france.json"
    ledger = load(ledger_path)
    engine = load(engine_path)
    old = load(index_path)
    index = {
        "version": "FORTNITE_COMPETITIVE_INDEX_EU_V1",
        "generated_at": AT,
        "derived_only": True,
        "authority": "NONE — rebuild from competitive ledger + competitive engine when inconsistent.",
        "source": {
            "ledger": "calendars/fortnite-competitive-ledger-france.json",
            "ledger_version": ledger["version"],
            "ledger_sha": blob(ledger_path),
            "engine": "calendars/fortnite-competitive-engine-france.json",
            "engine_version": engine["version"],
            "engine_sha": blob(engine_path),
        },
        "principles": old.get("principles", {}),
        "competition_ids": [],
        "by_visibility": {}, "by_status": {}, "by_region": {}, "by_series_id": {},
        "by_competition_class": {}, "by_ruleset": {}, "by_team_format": {},
        "by_platform_scope": {}, "by_phase_type": {}, "by_date": {},
        "sessions": {"all_ids": [], "by_exact_date": {}, "by_status": {}, "by_start_at": {}},
        "actionable": {"ATTEND": [], "WATCH": [], "REGISTER": [], "CHECK_IN": [], "PLAY": [], "FOLLOW": []},
        "deadlines": old.get("deadlines", {}),
        "qualification_graph": old.get("qualification_graph", {}),
        "projection": {},
        "conflicts": old.get("conflicts", []),
        "watch_targets": sorted({w.get("watch_id") for w in ledger.get("watch_targets", []) if w.get("watch_id")}),
        "rebuild_triggers": old.get("rebuild_triggers", []),
    }
    for comp in ledger["competitions"]:
        competition_id = comp["competition_id"]
        index["competition_ids"].append(competition_id)
        for section, key in (("by_visibility", comp.get("visibility")), ("by_status", comp.get("status")), ("by_series_id", comp.get("series_id")), ("by_competition_class", comp.get("competition_class")), ("by_ruleset", comp.get("ruleset")), ("by_team_format", comp.get("team_format")), ("by_platform_scope", comp.get("platform_scope"))):
            if key is not None:
                add(index[section], str(key), competition_id)
        for region in comp.get("regions", []):
            add(index["by_region"], region, competition_id)
        window = comp.get("date_window") or {}
        for day in {window.get("start_date"), window.get("end_date")}:
            if day:
                add(index["by_date"], day, competition_id)
        for phase in comp.get("phases", []):
            if phase.get("phase_type"):
                add(index["by_phase_type"], phase["phase_type"], phase["phase_id"])
            for item in phase.get("sessions", []):
                session_id = item["session_id"]
                index["sessions"]["all_ids"].append(session_id)
                add(index["sessions"]["by_status"], item["status"], session_id)
                if item.get("start_at"):
                    add(index["sessions"]["by_exact_date"], item["start_at"][:10], session_id)
                    add(index["sessions"]["by_start_at"], item["start_at"], session_id)
                    add(index["by_date"], item["start_at"][:10], competition_id)
        index["projection"][competition_id] = {"initial_level": comp.get("visibility"), "v2_score_status": "NOT_MATERIALIZED", "calendar_uid": comp.get("calendar_uid")}
        for action, values in old.get("actionable", {}).items():
            if action in index["actionable"] and competition_id in values:
                index["actionable"][action].append(competition_id)
    if CID not in index["actionable"]["PLAY"]:
        index["actionable"]["PLAY"].append(CID)
    index["competition_ids"] = sorted(set(index["competition_ids"]))
    index["sessions"]["all_ids"] = sorted(set(index["sessions"]["all_ids"]))
    sections = [index[name] for name in ("by_visibility", "by_status", "by_region", "by_series_id", "by_competition_class", "by_ruleset", "by_team_format", "by_platform_scope", "by_phase_type", "by_date")]
    sections += [index["sessions"][name] for name in ("by_exact_date", "by_status", "by_start_at")]
    for section in sections:
        for key in section:
            section[key] = sorted(set(section[key]))
    for key in index["actionable"]:
        index["actionable"][key] = sorted(set(index["actionable"][key]))
    dump(index_path, index)


def session(round_number: int, start: str, end: str):
    return {
        "session_id": f"{CID}:session-1:round-{round_number}:EU:{start[0:10].replace('-', '')}T{start[11:16].replace(':', '')}",
        "official_session_id": f"S42_ReloadSoloVictoryCup_Event1_Round{round_number}_EU",
        "name": f"Coupe victoire solo (Recharge) — Session 1, round {round_number}",
        "session_number": 1,
        "round_number": round_number,
        "round_label": f"Session 1 — Round {round_number}",
        "status": "SCHEDULED",
        "region": "EU",
        "ruleset": "RELOAD",
        "team_format": "SOLOS",
        "platform_scope": "ALL_SUPPORTED",
        "start_at": start,
        "end_at": end,
        "source_timezone": "Europe/Paris",
        "display_timezone": "Europe/Paris",
        "time_precision": "EXACT",
        "registration_deadline_at": None,
        "check_in_at": None,
        "max_matches": None,
        "qualification": {"advances_to": "Session 1 — Round 2", "eu_slots": 4000} if round_number == 1 else None,
        "prize": None if round_number == 1 else {"type": "VICTORY_ROYALE", "amount_usd": 100},
        "source_url": SOURCE,
        "visibility": "CALENDAR",
        "calendar_uid": UID,
        "related_service_event_ids": [],
    }


def competition():
    return {
        "competition_id": CID,
        "official_event_id": "S42_ReloadSoloVictoryCup",
        "official_event_slug": "S42_ReloadSoloVictoryCup",
        "series_id": "VICTORY_CUP",
        "season_id": "C7S4",
        "name": "Coupe victoire solo (Recharge) 2026 — Europe",
        "competition_class": "VICTORY_CUP",
        "status": "SCHEDULED",
        "regions": ["EU"],
        "ruleset": "RELOAD",
        "team_format": "SOLOS",
        "platform_scope": "ALL_SUPPORTED",
        "physical_event": False,
        "venue": None,
        "date_window": {"start_date": "2026-10-02", "end_date": "2026-10-23", "time_precision": "DATE_WINDOW_WITH_EXACT_SESSIONS"},
        "registration": None,
        "eligibility": {
            "status": "CONFIRMED",
            "minimum_rank": "Platine ou plus en classé Recharge combiné pendant la saison précédente ou actuelle",
            "account_level": None,
            "age_min": 13,
            "two_factor_required": True,
            "region_lock": "EU",
            "platform_requirements": None,
            "team_requirements": "SOLOS",
            "other_rules": None,
            "rules_url": "https://www.fortnite.com/competitive/rules-guidelines/rules-library",
        },
        "prize_pool": {"round_2_victory_royale_usd": 100},
        "qualification": {"round1_eu_to_round2": 4000},
        "visibility": "CALENDAR",
        "calendar_uid": UID,
        "source_ids": ["fortnite_competitive"],
        "source_urls": [SOURCE],
        "phases": [{
            "phase_id": f"{CID}:session-1",
            "name": "Session 1",
            "phase_type": "QUALIFIER",
            "order": 1,
            "status": "SCHEDULED",
            "registration": None,
            "eligibility_override": None,
            "qualification_override": None,
            "sessions": [
                session(1, "2026-10-02T17:00:00+02:00", "2026-10-02T19:00:00+02:00"),
                session(2, "2026-10-02T20:00:00+02:00", "2026-10-02T20:45:00+02:00"),
            ],
            "schedule_completeness": "PARTIAL_EXACT",
        }],
        "history": [{
            "at": AT,
            "type": "COMPETITION_CREATED",
            "source_id": "fortnite_competitive",
            "note": "Official EU event page confirmed the Oct 2–23 window, the first two exact sessions, eligibility, qualification threshold and victory prize.",
        }],
    }


def add_change():
    p = CAL / "fortnite-change-ledger.json"
    data = base.load(p)
    subject = f"calendars/fortnite-competitive-france.ics|{UID}"
    scope = "calendars/fortnite-paris.ics"
    old = next((x for x in data["changes"] if x.get("domain") == "CALENDAR_PROJECTION" and x.get("subject_key") == subject), None)
    if old:
        return old["change_id"]
    after = {
        "uid": UID,
        "competition_id": CID,
        "status": "SCHEDULED",
        "action": "PLAY",
        "region": "EU",
        "format": "SOLOS",
        "date_window": {"start": "2026-10-02", "end": "2026-10-23"},
        "sessions": [
            {"start_at": "2026-10-02T17:00:00+02:00", "end_at": "2026-10-02T19:00:00+02:00"},
            {"start_at": "2026-10-02T20:00:00+02:00", "end_at": "2026-10-02T20:45:00+02:00"},
        ],
        "projection_targets": ["calendars/fortnite-competitive-france.ics", "calendars/fortnite-paris.ics"],
    }
    evidence = "FORTNITE_COMPETITIVE_OFFICIAL_EU_EXACT"
    tf = base.h({"change_type": "CALENDAR_PROMOTED", "material_before": None, "material_after": after, "material_evidence_state": evidence})
    sk = "sub_" + base.h(f"CALENDAR_PROJECTION|{subject}|{scope}")
    change_id = "chg_" + base.h(f"CALENDAR_PROJECTION|{subject}|{scope}|1||{tf}")[:24]
    data["changes"].append({
        "change_id": change_id,
        "domain": "CALENDAR_PROJECTION",
        "subject_scope_key": sk,
        "subject_key": subject,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": "CALENDAR_PROMOTED",
        "materiality": "NOTIFY",
        "state_fingerprint": base.h(after),
        "transition_fingerprint": tf,
        "detected_at": AT,
        "source_refs": [SOURCE],
        "notification_disposition": "ELIGIBLE_NOW",
        "scope_key": scope,
        "material_before": None,
        "material_after": after,
        "material_evidence_state": evidence,
        "projection_targets": after["projection_targets"],
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
        "notes": "New official EU Solo Reload Victory Cup window; the first cash-prize session begins within one week.",
    })
    data["updated_at"] = AT
    data["history"].append({"at": AT, "type": "MATERIAL_CALENDAR_PROMOTION", "note": "Official Solo Reload Victory Cup EU window and first two exact sessions projected into competitive + global calendars."})
    base.dump(p, data, True)

    ip = CAL / "fortnite-change-index-france.json"
    index = base.load(ip)
    index["updated_at"] = AT
    index.setdefault("subject_heads", {})[sk] = {"revision": 1, "change_id": change_id}
    base.add(index.setdefault("by_domain", {}), "CALENDAR_PROJECTION", change_id)
    base.add(index.setdefault("by_change_type", {}), "CALENDAR_PROMOTED", change_id)
    index.setdefault("open_changes_by_subject", {})[sk] = [change_id]
    index["stats"]["changes"] = len(data["changes"])
    index["stats"]["subjects"] = len(index["subject_heads"])
    base.dump(ip, index, True)
    return change_id


def add_event(change_id):
    path = CAL / "fortnite-competitive-france.ics"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    if f"UID:{UID}" in text:
        return
    lines = [
        "BEGIN:VEVENT",
        f"UID:{UID}",
        f"DTSTAMP:{ATICS}",
        f"LAST-MODIFIED:{ATICS}",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "PRIORITY:5",
        "X-FORTNITE-PRIORITY:IMPORTANT",
        "X-FORTNITE-ACTION:PLAY",
        "X-FORTNITE-EVIDENCE-GRADE:A",
        "X-FORTNITE-SOURCE-ID:fortnite_competitive",
        f"X-FORTNITE-LAST-CHANGE-ID:{change_id}",
        f"X-FORTNITE-COMPETITION-ID:{CID}",
        "X-FORTNITE-PROJECTION-LEVEL:CALENDAR",
        "X-FORTNITE-PROJECTION-GRANULARITY:COMPETITION",
        "X-FORTNITE-REGION:EU",
        "X-FORTNITE-RULESET:RELOAD",
        "X-FORTNITE-FORMAT:SOLOS",
        "X-FORTNITE-PLATFORM:ALL_SUPPORTED",
        "X-FORTNITE-SESSION;ROUND=SESSION1-R1:20261002T170000/20261002T190000",
        "X-FORTNITE-SESSION;ROUND=SESSION1-R2:20261002T200000/20261002T204500",
        "DTSTART;VALUE=DATE:20261002",
        "DTEND;VALUE=DATE:20261024",
        "SUMMARY:🏆 ✅ 🆕 Coupe victoire solo (Recharge) — Europe",
        "DESCRIPTION:Période officielle : du 2 au 23 octobre 2026. Première journée exacte : vendredi 2 octobre, round 1 de 17h00 à 19h00 puis round 2 de 20h00 à 20h45 (Paris). Éligibilité : atteindre Platine ou plus en classé Recharge combiné pendant la saison précédente ou actuelle, avoir au moins 13 ans et activer l’A2F. Le top 4 000 EU du round 1 accède au round 2 ; chaque Victoire royale du round 2 rapporte 100 $ US. Les horaires ultérieurs ne sont pas extrapolés ici. Source officielle Fortnite Competitive.",
        f"URL:{SOURCE}",
        "CATEGORIES:Fortnite,Compétition,Coupe victoire,Recharge,Solos,Europe",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        "DESCRIPTION:🏆 La Coupe victoire solo Recharge Europe commence demain à 17h",
        "END:VALARM",
        "END:VEVENT",
    ]
    event = "\n".join(x for line in lines for x in base.fold(line)) + "\n"
    path.write_bytes(text.replace("END:VCALENDAR", event + "END:VCALENDAR", 1).replace("\n", "\r\n").encode())


def reserve(change_id):
    path = CAL / "fortnite-notification-outbox-france.json"
    data = base.load(path)
    key = "ntf_" + base.h(f"{change_id}|{NOTICE}|user|chat")
    if key in data.get("consumed_keys", {}):
        return key, False
    intent_id = "nti_" + base.h(key)[:24]
    reservation_id = "nrs_" + base.h(f"{key}|{AT}|solo-reload-victory")[:24]
    event_id = "nde_" + base.h(f"{intent_id}|RESERVED|1|{reservation_id}")[:24]
    data["intents"].append({"intent_id": intent_id, "notification_key": key, "change_ids": [change_id], "notice_kind": NOTICE, "audience_key": "user", "channel_key": "chat", "payload_fingerprint": base.h(PAYLOAD), "render_version": "FORTNITE_ALERT_FR_V1", "created_at": AT, "subject_key": UID, "locale": "fr-FR", "payload_snapshot": PAYLOAD, "condition_snapshot": {"first_session": "2026-10-02T17:00:00+02:00", "event_future": True}, "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2"})
    data["delivery_events"].append({"delivery_event_id": event_id, "intent_id": intent_id, "notification_key": key, "state": "RESERVED", "at": AT, "reservation_id": reservation_id, "note": "Reserved after fresh official EU schedule verification for the new Solo Reload Victory Cup window."})
    data["consumed_keys"][key] = {"intent_id": intent_id, "state": "RESERVED", "last_event_id": event_id}
    data["history"].append({"at": AT, "type": "NOTIFICATION_RESERVED", "notification_key": key, "note": "One notification reserved for the newly actionable Solo Reload Victory Cup EU schedule."})
    data["updated_at"] = AT
    base.dump(path, data, True)

    ip = CAL / "fortnite-change-index-france.json"
    index = base.load(ip)
    consumed = sorted(data["consumed_keys"])
    index["consumed_notification_keys"] = consumed
    index["unknown_delivery_keys"] = sorted(k for k, v in data["consumed_keys"].items() if v.get("state") == "UNKNOWN_DELIVERY")
    index["updated_at"] = AT
    index["stats"]["notification_intents"] = len(data["intents"])
    index["stats"]["consumed_notification_keys"] = len(consumed)
    index["stats"]["unknown_delivery"] = len(index["unknown_delivery_keys"])
    base.dump(ip, index, True)
    return key, True


def main():
    ledger_path = CAL / "fortnite-competitive-ledger-france.json"
    ledger = base.load(ledger_path)
    duplicate = next((x for x in ledger["competitions"] if x.get("competition_id") == CID or (x.get("name") == competition()["name"] and (x.get("date_window") or {}).get("start_date") == "2026-10-02")), None)
    if not duplicate:
        ledger["competitions"].append(competition())
    else:
        ledger["competitions"][ledger["competitions"].index(duplicate)] = competition()
    ledger["updated_at"] = AT
    base.dump(ledger_path, ledger)
    rebuild_index()
    change_id = add_change()
    add_event(change_id)
    subprocess.run([sys.executable, str(ROOT / "scripts/sync_fortnite_calendars.py")], cwd=ROOT, check=True)
    notification_key, reserved = reserve(change_id)
    print(change_id, notification_key, "RESERVED" if reserved else "ALREADY")


if __name__ == "__main__":
    main()
