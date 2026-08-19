#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
VENUES = CAL / "fortnite-venues-france.json"
PHYSICAL = CAL / "fortnite-physical-events-france.json"
ENGINE = CAL / "fortnite-physical-events-engine-france.json"
TICKETING = CAL / "fortnite-ticketing-france.json"
PROVIDERS = CAL / "fortnite-ticketing-providers-france.json"
SOURCES = CAL / "fortnite-sources-france.json"

VENUE_PRECISION = {"COUNTRY","REGION","CITY","SITE","VENUE","BUILDING","EXACT_ENTRANCE"}
EVENT_TYPES = {"ESPORTS_LAN","VIEWING_PARTY","CONVENTION","EPIC_FORTNITE_STAND","PARTNER_STAND","BRAND_ACTIVATION","OFFICIAL_COMMUNITY_EVENT","POPUP","MEET_AND_GREET","OTHER_OFFICIAL_PHYSICAL"}
EVENT_STATUS = {"DISCOVERED","ANNOUNCED","VENUE_TBA","VENUE_CONFIRMED","ACCESS_ANNOUNCED","REGISTRATION_OPEN","TICKETS_ON_SALE","ACTIVE","ENDED","POSTPONED","CANCELLED"}
VISIBILITY = {"LEDGER_ONLY","CALENDAR","FEATURED"}
TICKET_STATUS = {"NOT_ANNOUNCED","ANNOUNCED","PREREGISTRATION","ON_SALE","AVAILABLE","LOW_AVAILABILITY","NEARLY_SOLD_OUT","SOLD_OUT","WAITLIST","CLOSED","ENDED","CANCELLED"}
SCARCITY = {"EXPLICIT_TEXT","OFFICIAL_SESSION_DISABLED","CATEGORY_SOLD_OUT","WAITLIST_OFFERED","SEATMAP_STRONG_SIGNAL","UNKNOWN"}
STRONG_SCARCITY = {"LOW_AVAILABILITY","NEARLY_SOLD_OUT","SOLD_OUT"}


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iso_dt(value):
    if value is None:
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def main():
    errors = []
    for path in (VENUES, PHYSICAL, ENGINE, TICKETING, PROVIDERS, SOURCES):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors: print(f"ERROR: {e}")
        return 1

    venues = load(VENUES)
    physical = load(PHYSICAL)
    engine = load(ENGINE)
    ticketing = load(TICKETING)
    providers = load(PROVIDERS)
    sources = load(SOURCES)

    expected = {
        "venues": (venues.get("version"), "FORTNITE_VENUE_REGISTRY_EU_V1"),
        "physical": (physical.get("version"), "FORTNITE_PHYSICAL_EVENTS_EU_V1"),
        "engine": (engine.get("version"), "FORTNITE_PHYSICAL_EVENT_ENGINE_EU_V1"),
        "ticketing": (ticketing.get("version"), "FORTNITE_TICKETING_INTELLIGENCE_FR_V2"),
        "providers": (providers.get("version"), "FORTNITE_TICKETING_PROVIDER_REGISTRY_FR_V2")
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            errors.append(f"unexpected {label} version {actual!r}; wanted {wanted}")

    source_ids = {x.get("source_id") for x in sources.get("sources", []) if x.get("source_id")}
    provider_ids = set()
    for p in providers.get("providers", []):
        pid = p.get("provider_id")
        if not pid:
            errors.append("provider without provider_id")
            continue
        if pid in provider_ids:
            errors.append(f"duplicate provider_id: {pid}")
        provider_ids.add(pid)

    venue_ids = {}
    for v in venues.get("venues", []):
        vid = v.get("venue_id")
        if not vid:
            errors.append("venue without venue_id")
            continue
        if vid in venue_ids:
            errors.append(f"duplicate venue_id: {vid}")
        venue_ids[vid] = v
        if v.get("address_precision") not in VENUE_PRECISION:
            errors.append(f"invalid address_precision on {vid}: {v.get('address_precision')}")
        if v.get("source_id") not in source_ids:
            errors.append(f"venue {vid} uses unknown source_id {v.get('source_id')}")
        geo = v.get("geo")
        if geo is not None:
            if not isinstance(geo, dict) or not isinstance(geo.get("lat"), (int,float)) or not isinstance(geo.get("lon"), (int,float)):
                errors.append(f"venue {vid} has invalid geo")
            if not v.get("geo_source"):
                errors.append(f"venue {vid} has GEO without geo_source")
        if v.get("address_precision") in {"BUILDING","EXACT_ENTRANCE"} and not v.get("address"):
            errors.append(f"venue {vid} needs an address at {v.get('address_precision')} precision")

    physical_ids = {}
    event_uids = set()
    for e in physical.get("entries", []):
        pid = e.get("physical_event_id")
        uid = e.get("event_uid")
        if not pid: errors.append("physical event without physical_event_id")
        elif pid in physical_ids: errors.append(f"duplicate physical_event_id: {pid}")
        else: physical_ids[pid] = e
        if not uid: errors.append(f"physical event {pid} without event_uid")
        elif uid in event_uids: errors.append(f"duplicate physical event_uid: {uid}")
        else: event_uids.add(uid)
        if e.get("event_type") not in EVENT_TYPES: errors.append(f"invalid event_type on {pid}: {e.get('event_type')}")
        if e.get("status") not in EVENT_STATUS: errors.append(f"invalid physical status on {pid}: {e.get('status')}")
        if e.get("visibility") not in VISIBILITY: errors.append(f"invalid visibility on {pid}: {e.get('visibility')}")
        vid = e.get("venue_id")
        if vid not in venue_ids: errors.append(f"physical event {pid} references unknown venue_id {vid}")
        for sid_key in ("organizer_source_id","venue_source_id","competitive_source_id"):
            if e.get(sid_key) and e.get(sid_key) not in source_ids:
                errors.append(f"physical event {pid} has unknown {sid_key}={e.get(sid_key)}")
        seen_sessions = set()
        for s in e.get("public_sessions", []):
            sid = s.get("session_id")
            if not sid: errors.append(f"physical event {pid} session without session_id")
            elif sid in seen_sessions: errors.append(f"physical event {pid} duplicate session_id {sid}")
            else: seen_sessions.add(sid)
            if not iso_dt(s.get("start_at")): errors.append(f"physical event {pid} session {sid} invalid start_at")
            if not iso_dt(s.get("end_at")): errors.append(f"physical event {pid} session {sid} invalid end_at")

    ticket_event_uids = set()
    for t in ticketing.get("entries", []):
        uid = t.get("event_uid")
        peid = t.get("physical_event_id")
        ticket_event_uids.add(uid)
        if peid not in physical_ids:
            errors.append(f"ticketing entry {uid} references unknown physical_event_id {peid}")
        elif physical_ids[peid].get("event_uid") != uid:
            errors.append(f"ticketing/physical event_uid mismatch for {peid}")
        if t.get("provider_id") not in provider_ids:
            errors.append(f"ticketing entry {uid} references unknown provider {t.get('provider_id')}")
        if t.get("status") not in TICKET_STATUS:
            errors.append(f"ticketing entry {uid} has invalid status {t.get('status')}")
        scarcity = t.get("scarcity_evidence", "UNKNOWN")
        if scarcity not in SCARCITY:
            errors.append(f"ticketing entry {uid} invalid scarcity_evidence {scarcity}")
        if t.get("status") in STRONG_SCARCITY and scarcity == "UNKNOWN":
            errors.append(f"ticketing entry {uid} strong scarcity status without evidence")
        seen = set()
        for s in t.get("session_states", []):
            sk = s.get("session_key")
            if not sk: errors.append(f"ticketing {uid} session without session_key")
            elif sk in seen: errors.append(f"ticketing {uid} duplicate session_key {sk}")
            else: seen.add(sk)
            if s.get("status") not in TICKET_STATUS:
                errors.append(f"ticketing {uid}/{sk} invalid session status {s.get('status')}")
        cats = set()
        for c in t.get("category_states", []):
            ck = c.get("category_key")
            if not ck: errors.append(f"ticketing {uid} category without category_key")
            elif ck in cats: errors.append(f"ticketing {uid} duplicate category_key {ck}")
            else: cats.add(ck)
            if c.get("status") not in TICKET_STATUS:
                errors.append(f"ticketing {uid}/{ck} invalid category status {c.get('status')}")
            if c.get("scarcity_evidence", "UNKNOWN") not in SCARCITY:
                errors.append(f"ticketing {uid}/{ck} invalid category scarcity evidence")

    for peid, e in physical_ids.items():
        if e.get("ticketing_event_uid") and e.get("ticketing_event_uid") not in ticket_event_uids:
            errors.append(f"physical event {peid} points to missing ticketing entry {e.get('ticketing_event_uid')}")
        if e.get("ticketing_event_uid"):
            matching = next((x for x in ticketing.get("entries", []) if x.get("event_uid") == e.get("ticketing_event_uid")), None)
            if matching and e.get("current_access_state") != matching.get("status"):
                errors.append(f"physical event {peid} current_access_state {e.get('current_access_state')} != ticketing {matching.get('status')}")

    if errors:
        for e in errors: print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(f"OK: Fortnite physical events validated — {len(venue_ids)} venues, {len(physical_ids)} physical events, {len(ticketing.get('entries', []))} ticketing entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
