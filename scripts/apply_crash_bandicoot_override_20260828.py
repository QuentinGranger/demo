#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
AT = "2026-08-27T20:00:11Z"
AT_ICS = "20260827T200011Z"
CID = "override-series-crash-bandicoot-eu-2026-08-28"
UID = "fortnite-crash-bandicoot-cup-eu-20260828@openai"
SOURCE = "https://www.fortnite.com/competitive/events/S42_CrashBandicootCup/?region=EU"
SOURCE_MOBILE = "https://www.fortnite.com/competitive/events/S42_CrashBandicootMobileCup/?region=EU"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value):
    if not isinstance(value, str):
        value = canonical(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, obj, *, compact=False):
    if compact:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def sorted_add(mapping, key, value):
    values = list(mapping.get(key, []))
    values.append(value)
    mapping[key] = sorted(set(values))


def competition_record():
    sessions = [
        {
            "session_id": f"{CID}:mobile:EU:20260828T1600:session1",
            "official_session_id": "S42_CrashBandicootMobileCup_EU",
            "name": "Override Series: Crash Bandicoot Mobile Cup",
            "session_number": 1,
            "round_number": 1,
            "round_label": "MOBILE",
            "status": "SCHEDULED",
            "region": "EU",
            "ruleset": "BUILD",
            "team_format": "SOLOS",
            "platform_scope": "MOBILE",
            "start_at": "2026-08-28T16:00:00+02:00",
            "end_at": "2026-08-28T17:15:00+02:00",
            "source_timezone": "Europe/Paris",
            "display_timezone": "Europe/Paris",
            "time_precision": "EXACT",
            "registration_deadline_at": None,
            "check_in_at": None,
            "max_matches": None,
            "qualification": None,
            "prize": {"distribution": "Chance to earn Crash Bandicoot cosmetic rewards; exact thresholds are not asserted here.", "source_id": "fortnite_competitive", "confidence": "OFFICIAL"},
            "source_url": SOURCE_MOBILE,
            "visibility": "CALENDAR",
            "calendar_uid": UID,
            "related_service_event_ids": []
        },
        {
            "session_id": f"{CID}:reload:EU:20260828T1700:session1",
            "official_session_id": "S42_CrashBandicootCup_Reload_EU",
            "name": "Override Series: Crash Bandicoot Cup Reload",
            "session_number": 1,
            "round_number": 1,
            "round_label": "RELOAD",
            "status": "SCHEDULED",
            "region": "EU",
            "ruleset": "RELOAD",
            "team_format": "DUOS",
            "platform_scope": "ALL_SUPPORTED",
            "start_at": "2026-08-28T17:00:00+02:00",
            "end_at": "2026-08-28T19:30:00+02:00",
            "source_timezone": "Europe/Paris",
            "display_timezone": "Europe/Paris",
            "time_precision": "EXACT",
            "registration_deadline_at": None,
            "check_in_at": None,
            "max_matches": None,
            "qualification": None,
            "prize": {"distribution": "Chance to earn Crash Bandicoot cosmetic rewards; exact thresholds are not asserted here.", "source_id": "fortnite_competitive", "confidence": "OFFICIAL"},
            "source_url": SOURCE,
            "visibility": "CALENDAR",
            "calendar_uid": UID,
            "related_service_event_ids": []
        },
        {
            "session_id": f"{CID}:zero-build-reload:EU:20260828T1700:session1",
            "official_session_id": "S42_CrashBandicootCup_ZB_Reload_EU",
            "name": "Override Series: Crash Bandicoot Cup Zero Build Reload",
            "session_number": 1,
            "round_number": 1,
            "round_label": "ZERO_BUILD_RELOAD",
            "status": "SCHEDULED",
            "region": "EU",
            "ruleset": "ZERO_BUILD",
            "team_format": "DUOS",
            "platform_scope": "ALL_SUPPORTED",
            "start_at": "2026-08-28T17:00:00+02:00",
            "end_at": "2026-08-28T19:30:00+02:00",
            "source_timezone": "Europe/Paris",
            "display_timezone": "Europe/Paris",
            "time_precision": "EXACT",
            "registration_deadline_at": None,
            "check_in_at": None,
            "max_matches": None,
            "qualification": None,
            "prize": {"distribution": "Chance to earn Crash Bandicoot cosmetic rewards; exact thresholds are not asserted here.", "source_id": "fortnite_competitive", "confidence": "OFFICIAL"},
            "source_url": SOURCE,
            "visibility": "CALENDAR",
            "calendar_uid": UID,
            "related_service_event_ids": []
        }
    ]
    phases = []
    for key, label, session in (("mobile", "Mobile", sessions[0]), ("reload", "Reload", sessions[1]), ("zero-build-reload", "Zero Build Reload", sessions[2])):
        phases.append({
            "phase_id": f"{CID}:{key}",
            "name": label,
            "phase_type": "OTHER",
            "order": len(phases) + 1,
            "status": "SCHEDULED",
            "registration": None,
            "eligibility_override": {"status": "PARTIAL", "age_min": 13, "two_factor_required": True},
            "qualification_override": None,
            "sessions": [session],
            "schedule_completeness": "EXACT"
        })
    return {
        "competition_id": CID,
        "official_event_id": "S42_CrashBandicootCup",
        "official_event_slug": "S42_CrashBandicootCup",
        "series_id": "OVERRIDE_SERIES",
        "season_id": "C7S4",
        "name": "Override Series — Crash Bandicoot Cup — EU",
        "competition_class": "OTHER",
        "status": "SCHEDULED",
        "regions": ["EU"],
        "ruleset": "MIXED",
        "team_format": "UNKNOWN",
        "platform_scope": "UNKNOWN",
        "physical_event": False,
        "venue": None,
        "date_window": {"start_date": "2026-08-28", "end_date": "2026-08-28", "time_precision": "EXACT"},
        "registration": None,
        "eligibility": {"status": "PARTIAL", "age_min": 13, "two_factor_required": True},
        "prize_pool": {"currency": None, "total_amount": None, "region_amount": None, "session_amount": None, "distribution": "Crash Bandicoot cosmetic rewards; exact thresholds not asserted from the event page.", "source_id": "fortnite_competitive", "confidence": "OFFICIAL"},
        "qualification": None,
        "visibility": "CALENDAR",
        "calendar_uid": UID,
        "source_ids": ["fortnite_competitive"],
        "source_urls": [SOURCE, SOURCE_MOBILE],
        "phases": phases,
        "history": [{"at": AT, "type": "COMPETITION_CREATED", "source_id": "fortnite_competitive", "note": "Official EU schedule confirms three Crash Bandicoot sessions on Aug 28 with exact times and cosmetic rewards. Projected as one logical calendar event to avoid three overlapping VEVENTs."}]
    }


def add_competition():
    path = CAL / "fortnite-competitive-ledger-france.json"
    ledger = load(path)
    if any(c.get("competition_id") == CID for c in ledger.get("competitions", [])):
        return False
    ledger.setdefault("competitions", []).append(competition_record())
    ledger["updated_at"] = AT
    dump(path, ledger)
    return True


def rebuild_competitive_index():
    ledger_path = CAL / "fortnite-competitive-ledger-france.json"
    engine_path = CAL / "fortnite-competitive-engine-france.json"
    index_path = CAL / "fortnite-competitive-index-france.json"
    ledger = load(ledger_path)
    engine = load(engine_path)
    old = load(index_path)

    idx = {
        "version": "FORTNITE_COMPETITIVE_INDEX_EU_V1",
        "generated_at": AT,
        "derived_only": True,
        "authority": "NONE — rebuild from competitive ledger + competitive engine when inconsistent.",
        "source": {
            "ledger": "calendars/fortnite-competitive-ledger-france.json",
            "ledger_version": ledger.get("version"),
            "ledger_sha": git_blob_sha(ledger_path),
            "engine": "calendars/fortnite-competitive-engine-france.json",
            "engine_version": engine.get("version"),
            "engine_sha": git_blob_sha(engine_path)
        },
        "principles": old.get("principles", {}),
        "competition_ids": [],
        "by_visibility": {}, "by_status": {}, "by_region": {}, "by_series_id": {},
        "by_competition_class": {}, "by_ruleset": {}, "by_team_format": {}, "by_platform_scope": {},
        "by_phase_type": {}, "by_date": {},
        "sessions": {"all_ids": [], "by_exact_date": {}, "by_status": {}, "by_start_at": {}},
        "actionable": {"ATTEND": [], "WATCH": [], "REGISTER": [], "CHECK_IN": [], "PLAY": [], "FOLLOW": []},
        "deadlines": old.get("deadlines", {"LAST_REGISTRATION_AT": [], "LAST_CHECK_IN_AT": [], "LAST_QUALIFIER_AT": []}),
        "qualification_graph": old.get("qualification_graph", {"edges": [], "unresolved_candidates": []}),
        "projection": {},
        "conflicts": old.get("conflicts", []),
        "watch_targets": sorted({w.get("watch_id") for w in ledger.get("watch_targets", []) if isinstance(w, dict) and w.get("watch_id")}),
        "rebuild_triggers": old.get("rebuild_triggers", [])
    }

    def add(section, key, value):
        sorted_add(section, str(key), value)

    for comp in ledger.get("competitions", []):
        cid = comp["competition_id"]
        idx["competition_ids"].append(cid)
        for section, key in ((idx["by_visibility"], comp.get("visibility")), (idx["by_status"], comp.get("status")), (idx["by_series_id"], comp.get("series_id")), (idx["by_competition_class"], comp.get("competition_class")), (idx["by_ruleset"], comp.get("ruleset")), (idx["by_team_format"], comp.get("team_format")), (idx["by_platform_scope"], comp.get("platform_scope"))):
            if key is not None:
                add(section, key, cid)
        for region in comp.get("regions", []):
            add(idx["by_region"], region, cid)
        date_window = comp.get("date_window") or {}
        start_d, end_d = date_window.get("start_date"), date_window.get("end_date")
        if start_d:
            add(idx["by_date"], start_d, cid)
        if end_d and end_d != start_d:
            add(idx["by_date"], end_d, cid)
        for phase in comp.get("phases", []):
            pid = phase.get("phase_id")
            ptype = phase.get("phase_type")
            if pid and ptype:
                add(idx["by_phase_type"], ptype, pid)
            for session in phase.get("sessions", []):
                sid = session["session_id"]
                idx["sessions"]["all_ids"].append(sid)
                start = session.get("start_at")
                if start:
                    add(idx["sessions"]["by_exact_date"], start[:10], sid)
                    add(idx["sessions"]["by_start_at"], start, sid)
                    add(idx["by_date"], start[:10], cid)
                add(idx["sessions"]["by_status"], session.get("status"), sid)
        level = comp.get("visibility")
        idx["projection"][cid] = {"initial_level": level, "v2_score_status": "NOT_MATERIALIZED", "calendar_uid": comp.get("calendar_uid")}
        if cid == CID:
            idx["actionable"]["PLAY"].append(cid)
        elif cid in (old.get("actionable", {}).get("ATTEND", [])):
            idx["actionable"]["ATTEND"].append(cid)
        if cid in old.get("actionable", {}).get("WATCH", []): idx["actionable"]["WATCH"].append(cid)
        if cid in old.get("actionable", {}).get("REGISTER", []): idx["actionable"]["REGISTER"].append(cid)
        if cid in old.get("actionable", {}).get("CHECK_IN", []): idx["actionable"]["CHECK_IN"].append(cid)
        if cid in old.get("actionable", {}).get("PLAY", []): idx["actionable"]["PLAY"].append(cid)
        if cid in old.get("actionable", {}).get("FOLLOW", []): idx["actionable"]["FOLLOW"].append(cid)

    idx["competition_ids"] = sorted(set(idx["competition_ids"]))
    idx["sessions"]["all_ids"] = sorted(set(idx["sessions"]["all_ids"]))
    for values in idx["actionable"].values():
        values[:] = sorted(set(values))
    dump(index_path, idx)


def add_change():
    path = CAL / "fortnite-change-ledger.json"
    change = load(path)
    existing = next((c for c in change.get("changes", []) if c.get("domain") == "COMPETITIVE" and c.get("subject_key") == CID), None)
    if existing:
        return existing["change_id"]
    material_after = {
        "competition_id": CID,
        "status": "SCHEDULED",
        "date": "2026-08-28",
        "visibility": "CALENDAR",
        "sessions": [
            {"type": "MOBILE", "start_at": "2026-08-28T16:00:00+02:00", "end_at": "2026-08-28T17:15:00+02:00", "team_format": "SOLOS"},
            {"type": "RELOAD", "start_at": "2026-08-28T17:00:00+02:00", "end_at": "2026-08-28T19:30:00+02:00", "team_format": "DUOS"},
            {"type": "ZERO_BUILD_RELOAD", "start_at": "2026-08-28T17:00:00+02:00", "end_at": "2026-08-28T19:30:00+02:00", "team_format": "DUOS"}
        ],
        "reward_type": "CRASH_BANDICOOT_COSMETICS",
        "eligibility": {"age_min": 13, "mfa_required": True}
    }
    evidence = "FORTNITE_COMPETITIVE_OFFICIAL_EU_EXACT"
    transition_fp = sha256({"change_type": "ENTITY_CREATED", "material_before": None, "material_after": material_after, "material_evidence_state": evidence})
    state_fp = sha256(material_after)
    subject_scope_key = "sub_" + sha256(f"COMPETITIVE|{CID}|")
    change_id = "chg_" + sha256(f"COMPETITIVE|{CID}||1||{transition_fp}")[:24]
    rec = {
        "change_id": change_id,
        "domain": "COMPETITIVE",
        "subject_scope_key": subject_scope_key,
        "subject_key": CID,
        "subject_revision": 1,
        "causal_parent_change_id": None,
        "change_type": "ENTITY_CREATED",
        "materiality": "CALENDAR",
        "state_fingerprint": state_fp,
        "transition_fingerprint": transition_fp,
        "detected_at": AT,
        "source_refs": [SOURCE, SOURCE_MOBILE],
        "notification_disposition": "SILENT_POLICY",
        "scope_key": None,
        "material_before": None,
        "material_after": material_after,
        "material_evidence_state": evidence,
        "projection_targets": ["calendars/fortnite-competitive-france.ics", "calendars/fortnite-paris.ics"],
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
        "notes": "Official branded cosmetic-reward cup projected as one logical event. Calendar H-1 alarm covers the actionable timing; no separate chat notification/outbox intent is created."
    }
    change.setdefault("changes", []).append(rec)
    change["updated_at"] = AT
    change.setdefault("history", []).append({"at": AT, "type": "MATERIAL_COMPETITIVE_EVENT_CREATED", "note": "Crash Bandicoot Override Series EU projected as one calendar event with three exact sessions and cosmetic-reward context."})
    dump(path, change, compact=True)

    idx_path = CAL / "fortnite-change-index-france.json"
    idx = load(idx_path)
    idx["updated_at"] = AT
    idx.setdefault("subject_heads", {})[subject_scope_key] = {"revision": 1, "change_id": change_id}
    sorted_add(idx.setdefault("by_domain", {}), "COMPETITIVE", change_id)
    sorted_add(idx.setdefault("by_change_type", {}), "ENTITY_CREATED", change_id)
    idx.setdefault("open_changes_by_subject", {})[subject_scope_key] = [change_id]
    stats = idx.setdefault("stats", {})
    stats["changes"] = len(change.get("changes", []))
    stats["subjects"] = len(idx.get("subject_heads", {}))
    dump(idx_path, idx, compact=True)
    return change_id


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


def add_calendar_event(change_id: str):
    path = CAL / "fortnite-competitive-france.ics"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    if f"UID:{UID}" in text:
        return False
    lines = [
        "BEGIN:VEVENT",
        f"UID:{UID}",
        f"DTSTAMP:{AT_ICS}",
        f"LAST-MODIFIED:{AT_ICS}",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "PRIORITY:5",
        "X-FORTNITE-PRIORITY:IMPORTANT",
        "X-FORTNITE-ACTION:PARTICIPATE",
        "X-FORTNITE-EVENT-TYPE:SPECIAL_COSMETIC_CUP",
        "X-FORTNITE-SERIES:OVERRIDE_SERIES",
        "X-FORTNITE-MODE:MIXED",
        "X-FORTNITE-FORMAT:MIXED",
        "X-FORTNITE-REGION:EU",
        "X-FORTNITE-THEME:CRASH_BANDICOOT",
        "X-FORTNITE-EVIDENCE-GRADE:A",
        "X-FORTNITE-SOURCE-ID:fortnite_competitive",
        "X-FORTNITE-TIME-PRECISION:EXACT",
        f"X-FORTNITE-LAST-CHANGE-ID:{change_id}",
        f"X-FORTNITE-FIRST-ADDED-AT:{AT_ICS}",
        "X-FORTNITE-NEW-UNTIL:20260901T200011Z",
        "X-FORTNITE-SESSION;TYPE=MOBILE;FORMAT=SOLOS:20260828T160000/20260828T171500",
        "X-FORTNITE-SESSION;TYPE=RELOAD;FORMAT=DUOS:20260828T170000/20260828T193000",
        "X-FORTNITE-SESSION;TYPE=ZERO_BUILD_RELOAD;FORMAT=DUOS:20260828T170000/20260828T193000",
        "DTSTART;TZID=Europe/Paris:20260828T160000",
        "DTEND;TZID=Europe/Paris:20260828T193000",
        "SUMMARY:⭐ ✅ 🆕 🥭 Override Series — Crash Bandicoot Cup EU",
        "DESCRIPTION:Priorité : ⭐ Important — opportunité compétitive officielle Crash Bandicoot le 28 août avec récompenses cosmétiques.\\n📱 Mobile : 16h00–17h15, solos.\\n🎮 Reload : 17h00–19h30, duos.\\n🚫 Zero Build Reload : 17h00–19h30, duos.\\nFortnite indique que les joueurs peuvent concourir pour tenter de gagner des récompenses cosmétiques Crash Bandicoot. Les seuils exacts ne sont pas affirmés ici tant qu’ils ne sont pas matérialisés depuis les règles officielles.\\nÉligibilité publiée : au moins 13 ans (ou l’âge minimum du pays de résidence) et MFA activée.\\nSource : https://www.fortnite.com/competitive/events/S42_CrashBandicootCup/?region=EU",
        f"URL:{SOURCE}",
        "CATEGORIES:Fortnite,Compétition,Override Series,Crash Bandicoot,EU,Cosmétiques",
        "BEGIN:VALARM",
        "TRIGGER:-PT1H",
        "ACTION:DISPLAY",
        "DESCRIPTION:🥭 Crash Bandicoot Cup EU dans 1 h — Mobile à 16h, Reload à 17h",
        "END:VALARM",
        "END:VEVENT"
    ]
    folded = []
    for line in lines:
        folded.extend(fold_line(line))
    marker = "END:VCALENDAR"
    event = "\n".join(folded) + "\n"
    if marker not in text:
        raise RuntimeError("competitive calendar missing END:VCALENDAR")
    text = text.replace(marker, event + marker, 1)
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    return True


def main():
    changed = add_competition()
    change_id = add_change()
    add_calendar_event(change_id)
    rebuild_competitive_index()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_fortnite_calendars.py")], cwd=ROOT, check=True)
    print("APPLIED" if changed else "ALREADY_PRESENT", CID, change_id)


if __name__ == "__main__":
    main()
