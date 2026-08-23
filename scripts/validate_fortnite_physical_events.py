#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
VENUES = CAL / "fortnite-venues-france.json"
PHYSICAL = CAL / "fortnite-physical-events-france.json"
ACCESS = CAL / "fortnite-physical-access-france.json"
ENGINE = CAL / "fortnite-physical-events-engine-france.json"
INDEX = CAL / "fortnite-physical-events-index-france.json"
TICKETING = CAL / "fortnite-ticketing-france.json"
PROVIDERS = CAL / "fortnite-ticketing-providers-france.json"
SOURCES = CAL / "fortnite-sources-france.json"

VENUE_PRECISION = {"COUNTRY","REGION","CITY","SITE","VENUE","BUILDING","EXACT_ENTRANCE"}
SPACE_TYPES = {"SITE","HALL","ARENA_BOWL","STAGE","STAND","ZONE","LOUNGE","CHECK_IN_AREA","QUEUE_AREA","ENTRANCE","EXIT","OTHER"}
EVENT_TYPES = {"ESPORTS_LAN","VIEWING_PARTY","CONVENTION","EPIC_FORTNITE_STAND","PARTNER_STAND","BRAND_ACTIVATION","OFFICIAL_COMMUNITY_EVENT","POPUP","MEET_AND_GREET","OTHER_OFFICIAL_PHYSICAL"}
EVENT_STATUS = {"DISCOVERED","ANNOUNCED","VENUE_TBA","VENUE_CONFIRMED","ACCESS_ANNOUNCED","REGISTRATION_OPEN","TICKETS_ON_SALE","READY_FOR_PUBLIC","ACTIVE","ENDED","POSTPONED","CANCELLED"}
VISIBILITY = {"LEDGER_ONLY","CALENDAR","FEATURED"}
COMPLETENESS = {"IDENTITY_ONLY","DATE_CITY_KNOWN","VENUE_KNOWN","ACCESS_PATH_KNOWN","PUBLIC_SESSION_KNOWN","PUBLIC_INFO_MATURE"}
TRAVEL_SCOPE = {"PARIS_IDF","FRANCE_DOMESTIC","CROSS_BORDER_EU","EUROPE_OTHER","UNKNOWN"}
ACTIONS = {"ATTEND","REGISTER_INTEREST","REGISTER_ATTENDANCE","BUY_TICKET","JOIN_WAITLIST","CHECK_IN","WATCH","VISIT_STAND","MEET","FOLLOW"}
SESSION_TYPES = {"DOORS_OPEN","VENUE_TIME","PUBLIC_VIEWING","STAND_OPEN","MEET_AND_GREET","CHECK_IN","LAST_ENTRY","ACTIVATION_SLOT","OTHER_PUBLIC"}
TICKET_STATUS = {"NOT_ANNOUNCED","ANNOUNCED","PREREGISTRATION","ON_SALE","AVAILABLE","LOW_AVAILABILITY","NEARLY_SOLD_OUT","SOLD_OUT","WAITLIST","CLOSED","ENDED","CANCELLED"}
SCARCITY = {"EXPLICIT_TEXT","OFFICIAL_SESSION_DISABLED","CATEGORY_SOLD_OUT","WAITLIST_OFFERED","SEATMAP_STRONG_SIGNAL","UNKNOWN"}
STRONG_SCARCITY = {"LOW_AVAILABILITY","NEARLY_SOLD_OUT","SOLD_OUT"}
ADMISSION_MODES = {"FREE_WALK_IN","FREE_REGISTRATION","PAID_TICKET","WAITLIST","INVITE_ONLY","ACCREDITATION","MIXED","UNKNOWN"}
ACCESS_STATES = {"UNKNOWN","ANNOUNCED","INTEREST_PREREGISTRATION","REGISTRATION_REQUIRED","TICKET_REQUIRED","WAITLIST_ONLY","OPEN_ACCESS","INVITE_ONLY","ACCREDITATION_ONLY","CLOSED","ENDED","CANCELLED"}
REQ_STATES = {"CONFIRMED","NOT_REQUIRED","UNKNOWN"}
CREDENTIALS = {"DIGITAL_TICKET","PRINTED_TICKET","QR_CODE","REGISTRATION_CONFIRMATION","PHOTO_ID","WRISTBAND","ACCREDITATION_BADGE","INVITATION","UNKNOWN"}


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


def https_url(value):
    if not isinstance(value, str):
        return False
    try:
        p = urlparse(value)
        return p.scheme == "https" and bool(p.netloc)
    except Exception:
        return False


def unique_list(values):
    return values == sorted(set(values))


def main():
    errors = []
    required = (VENUES, PHYSICAL, ACCESS, ENGINE, INDEX, TICKETING, PROVIDERS, SOURCES)
    for path in required:
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    venues = load(VENUES)
    physical = load(PHYSICAL)
    access = load(ACCESS)
    engine = load(ENGINE)
    index = load(INDEX)
    ticketing = load(TICKETING)
    providers = load(PROVIDERS)
    sources = load(SOURCES)

    expected = {
        "venues": (venues.get("version"), "FORTNITE_VENUE_REGISTRY_EU_V2"),
        "physical": (physical.get("version"), "FORTNITE_PHYSICAL_EVENTS_EU_V2"),
        "access": (access.get("version"), "FORTNITE_PHYSICAL_ACCESS_INTELLIGENCE_EU_V1"),
        "engine": (engine.get("version"), "FORTNITE_PHYSICAL_EVENT_ENGINE_EU_V2"),
        "index": (index.get("version"), "FORTNITE_PHYSICAL_EVENT_INDEX_EU_V1"),
        "ticketing": (ticketing.get("version"), "FORTNITE_TICKETING_INTELLIGENCE_FR_V2"),
        "providers": (providers.get("version"), "FORTNITE_TICKETING_PROVIDER_REGISTRY_FR_V2")
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            errors.append(f"unexpected {label} version {actual!r}; wanted {wanted}")

    if engine.get("ledger") != PHYSICAL.name:
        errors.append("physical engine ledger reference mismatch")
    if engine.get("venue_registry") != VENUES.name:
        errors.append("physical engine venue registry mismatch")
    if engine.get("access_ledger") != ACCESS.name:
        errors.append("physical engine access ledger mismatch")
    if engine.get("index") != INDEX.name:
        errors.append("physical engine index mismatch")
    if ACCESS.name not in index.get("derived_from", []):
        errors.append("physical index does not derive from access ledger")

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
    venue_space_ids = {}
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
        if not v.get("timezone"):
            errors.append(f"venue {vid} missing timezone")
        geo = v.get("geo")
        if geo is not None:
            if not isinstance(geo, dict) or not isinstance(geo.get("lat"), (int, float)) or not isinstance(geo.get("lon"), (int, float)):
                errors.append(f"venue {vid} has invalid geo")
            else:
                if not (-90 <= geo["lat"] <= 90 and -180 <= geo["lon"] <= 180):
                    errors.append(f"venue {vid} GEO out of range")
            if not v.get("geo_source"):
                errors.append(f"venue {vid} has GEO without geo_source")
        if v.get("address_precision") in {"BUILDING", "EXACT_ENTRANCE"} and not v.get("address"):
            errors.append(f"venue {vid} needs an address at {v.get('address_precision')} precision")
        local_spaces = set()
        for s in v.get("spaces", []):
            sid = s.get("space_id")
            if not sid:
                errors.append(f"venue {vid} has space without space_id")
                continue
            if sid in local_spaces:
                errors.append(f"venue {vid} duplicate space_id {sid}")
            local_spaces.add(sid)
            if s.get("space_type") not in SPACE_TYPES:
                errors.append(f"venue {vid}/{sid} invalid space_type {s.get('space_type')}")
        venue_space_ids[vid] = local_spaces
        accessibility = v.get("accessibility", {})
        if accessibility.get("state") not in {"CONFIRMED", "PARTIAL", "UNKNOWN"}:
            errors.append(f"venue {vid} invalid accessibility state {accessibility.get('state')}")
        if accessibility.get("state") in {"CONFIRMED", "PARTIAL"} and not accessibility.get("source_url"):
            errors.append(f"venue {vid} accessibility claim lacks source_url")

    physical_ids = {}
    event_uids = set()
    session_refs = set()
    for e in physical.get("entries", []):
        pid = e.get("physical_event_id")
        uid = e.get("event_uid")
        if not pid:
            errors.append("physical event without physical_event_id")
        elif pid in physical_ids:
            errors.append(f"duplicate physical_event_id: {pid}")
        else:
            physical_ids[pid] = e
        if not uid:
            errors.append(f"physical event {pid} without event_uid")
        elif uid in event_uids:
            errors.append(f"duplicate physical event_uid: {uid}")
        else:
            event_uids.add(uid)
        if e.get("event_type") not in EVENT_TYPES:
            errors.append(f"invalid event_type on {pid}: {e.get('event_type')}")
        if e.get("status") not in EVENT_STATUS:
            errors.append(f"invalid physical status on {pid}: {e.get('status')}")
        if e.get("visibility") not in VISIBILITY:
            errors.append(f"invalid visibility on {pid}: {e.get('visibility')}")
        if e.get("operational_completeness") not in COMPLETENESS:
            errors.append(f"invalid operational_completeness on {pid}: {e.get('operational_completeness')}")
        if e.get("travel_scope") not in TRAVEL_SCOPE:
            errors.append(f"invalid travel_scope on {pid}: {e.get('travel_scope')}")
        if e.get("primary_action") not in ACTIONS:
            errors.append(f"invalid primary_action on {pid}: {e.get('primary_action')}")
        vid = e.get("venue_id")
        if vid not in venue_ids:
            errors.append(f"physical event {pid} references unknown venue_id {vid}")
        for sid_key in ("organizer_source_id", "venue_source_id", "competitive_source_id"):
            if e.get(sid_key) and e.get(sid_key) not in source_ids:
                errors.append(f"physical event {pid} has unknown {sid_key}={e.get(sid_key)}")
        for role in e.get("organizer_roles", []):
            if role.get("source_id") not in source_ids:
                errors.append(f"physical event {pid} organizer role uses unknown source_id {role.get('source_id')}")
        seen_sessions = set()
        for s in e.get("public_sessions", []):
            sid = s.get("session_id")
            if not sid:
                errors.append(f"physical event {pid} session without session_id")
                continue
            if sid in seen_sessions:
                errors.append(f"physical event {pid} duplicate session_id {sid}")
            seen_sessions.add(sid)
            session_refs.add(f"{pid}:{sid}")
            if s.get("session_type") not in SESSION_TYPES:
                errors.append(f"physical event {pid}/{sid} invalid session_type {s.get('session_type')}")
            if not iso_dt(s.get("start_at")):
                errors.append(f"physical event {pid} session {sid} invalid start_at")
            if not iso_dt(s.get("end_at")):
                errors.append(f"physical event {pid} session {sid} invalid end_at")
            if s.get("start_at") and s.get("end_at"):
                a = datetime.fromisoformat(s["start_at"].replace("Z", "+00:00"))
                b = datetime.fromisoformat(s["end_at"].replace("Z", "+00:00"))
                if b <= a:
                    errors.append(f"physical event {pid}/{sid} end_at <= start_at")
            space_id = s.get("venue_space_id")
            if space_id and space_id not in venue_space_ids.get(vid, set()):
                errors.append(f"physical event {pid}/{sid} references unknown venue space {space_id}")

    access_ids = {}
    for a in access.get("entries", []):
        aid = a.get("access_profile_id")
        peid = a.get("physical_event_id")
        uid = a.get("event_uid")
        if not aid:
            errors.append("access entry without access_profile_id")
            continue
        if aid in access_ids:
            errors.append(f"duplicate access_profile_id: {aid}")
        access_ids[aid] = a
        if peid not in physical_ids:
            errors.append(f"access {aid} references unknown physical_event_id {peid}")
        elif physical_ids[peid].get("event_uid") != uid:
            errors.append(f"access/physical event_uid mismatch for {aid}")
        if a.get("provider_id") not in provider_ids:
            errors.append(f"access {aid} references unknown provider {a.get('provider_id')}")
        if a.get("source_id") not in source_ids:
            errors.append(f"access {aid} references unknown source_id {a.get('source_id')}")
        if a.get("access_state") not in ACCESS_STATES:
            errors.append(f"access {aid} invalid access_state {a.get('access_state')}")
        if a.get("admission_mode") not in ADMISSION_MODES:
            errors.append(f"access {aid} invalid admission_mode {a.get('admission_mode')}")
        if a.get("source_url") and not https_url(a.get("source_url")):
            errors.append(f"access {aid} source_url is not valid HTTPS")
        if a.get("interest_preregistration_only") and a.get("access_state") != "INTEREST_PREREGISTRATION":
            errors.append(f"access {aid} interest preregistration flag conflicts with access_state")
        if a.get("interest_preregistration_only") and a.get("admission_guarantee") not in {"NOT_ESTABLISHED", "NONE"}:
            errors.append(f"access {aid} generic preregistration must not guarantee admission")
        age = a.get("age_rule", {})
        if age.get("state") not in REQ_STATES:
            errors.append(f"access {aid} invalid age_rule state {age.get('state')}")
        if age.get("state") == "CONFIRMED":
            if not isinstance(age.get("minimum_age"), int) or age.get("minimum_age") < 0:
                errors.append(f"access {aid} confirmed age rule lacks valid minimum_age")
            if not https_url(age.get("source_url")):
                errors.append(f"access {aid} confirmed age rule lacks HTTPS source_url")
        identity = a.get("identity_requirement", {})
        if identity.get("state") not in REQ_STATES:
            errors.append(f"access {aid} invalid identity requirement state")
        if identity.get("credential") not in CREDENTIALS:
            errors.append(f"access {aid} invalid identity credential {identity.get('credential')}")
        for field in ("named_ticket", "ticket_transferability", "reentry", "security_check", "bag_policy"):
            if a.get(field, {}).get("state") not in REQ_STATES:
                errors.append(f"access {aid} invalid {field} state")
        queue = a.get("queue", {})
        if queue.get("published_wait_time_minutes") is not None:
            if not isinstance(queue.get("published_wait_time_minutes"), int) or queue.get("published_wait_time_minutes") < 0:
                errors.append(f"access {aid} invalid published queue wait")
            if queue.get("state") != "CONFIRMED":
                errors.append(f"access {aid} queue wait value without CONFIRMED state")
        capacity = a.get("capacity", {})
        if capacity.get("value") is not None and capacity.get("state") != "CONFIRMED":
            errors.append(f"access {aid} capacity value without CONFIRMED state")
        for w in a.get("check_in_windows", []) + a.get("last_entry_windows", []):
            if not iso_dt(w.get("at")) and not iso_dt(w.get("start_at")) and not iso_dt(w.get("end_at")):
                errors.append(f"access {aid} has invalid access window")

    ticket_event_uids = set()
    ticket_by_uid = {}
    for t in ticketing.get("entries", []):
        uid = t.get("event_uid")
        peid = t.get("physical_event_id")
        ticket_event_uids.add(uid)
        ticket_by_uid[uid] = t
        if peid not in physical_ids:
            errors.append(f"ticketing entry {uid} references unknown physical_event_id {peid}")
        elif physical_ids[peid].get("event_uid") != uid:
            errors.append(f"ticketing/physical event_uid mismatch for {peid}")
        if t.get("provider_id") not in provider_ids:
            errors.append(f"ticketing entry {uid} references unknown provider {t.get('provider_id')}")
        if t.get("access_profile_id") not in access_ids:
            errors.append(f"ticketing entry {uid} references unknown access_profile_id {t.get('access_profile_id')}")
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
            if not sk:
                errors.append(f"ticketing {uid} session without session_key")
            elif sk in seen:
                errors.append(f"ticketing {uid} duplicate session_key {sk}")
            else:
                seen.add(sk)
            if s.get("status") not in TICKET_STATUS:
                errors.append(f"ticketing {uid}/{sk} invalid session status {s.get('status')}")
        cats = set()
        for c in t.get("category_states", []):
            ck = c.get("category_key")
            if not ck:
                errors.append(f"ticketing {uid} category without category_key")
            elif ck in cats:
                errors.append(f"ticketing {uid} duplicate category_key {ck}")
            else:
                cats.add(ck)
            if c.get("status") not in TICKET_STATUS:
                errors.append(f"ticketing {uid}/{ck} invalid category status {c.get('status')}")
            if c.get("scarcity_evidence", "UNKNOWN") not in SCARCITY:
                errors.append(f"ticketing {uid}/{ck} invalid category scarcity evidence")

    for peid, e in physical_ids.items():
        aid = e.get("access_profile_id")
        if aid is None:
            # A venue-confirmed physical event may legitimately have no access profile yet
            # when public admission/ticketing is still entirely UNKNOWN. Do not force a
            # fabricated provider or access record just to satisfy validation.
            allowed_unknown = (
                e.get("current_admission_state") == "UNKNOWN"
                and e.get("current_ticket_state") is None
                and e.get("primary_action") == "FOLLOW"
                and e.get("operational_completeness") in {"IDENTITY_ONLY", "DATE_CITY_KNOWN", "VENUE_KNOWN"}
            )
            if not allowed_unknown:
                errors.append(f"physical event {peid} has null access profile outside explicit UNKNOWN/FOLLOW state")
        elif aid not in access_ids:
            errors.append(f"physical event {peid} points to missing access profile {aid}")
        elif access_ids[aid].get("physical_event_id") != peid:
            errors.append(f"physical event {peid} access profile belongs to another event")
        tuid = e.get("ticketing_event_uid")
        if tuid and tuid not in ticket_event_uids:
            errors.append(f"physical event {peid} points to missing ticketing entry {tuid}")
        matching = ticket_by_uid.get(tuid)
        if matching and e.get("current_ticket_state") != matching.get("status"):
            errors.append(f"physical event {peid} current_ticket_state {e.get('current_ticket_state')} != ticketing {matching.get('status')}")
        if aid in access_ids and e.get("current_admission_state") != access_ids[aid].get("access_state"):
            errors.append(f"physical event {peid} current_admission_state mismatch")
        if e.get("primary_action") == "REGISTER_INTEREST" and access_ids.get(aid, {}).get("access_state") != "INTEREST_PREREGISTRATION":
            errors.append(f"physical event {peid} REGISTER_INTEREST without interest preregistration access state")
        if e.get("primary_action") == "JOIN_WAITLIST" and (not matching or matching.get("status") != "WAITLIST"):
            errors.append(f"physical event {peid} JOIN_WAITLIST without ticket WAITLIST")

    # Derived index must only reference canonical IDs and remain deterministic.
    for section in ("by_type", "by_country", "by_city", "by_visibility", "by_operational_completeness", "by_primary_action", "by_travel_scope", "by_access_state", "by_venue", "by_date"):
        for key, ids in index.get(section, {}).items():
            if not unique_list(ids):
                errors.append(f"physical index {section}/{key} is not sorted/deduplicated")
            for peid in ids:
                if peid not in physical_ids:
                    errors.append(f"physical index {section}/{key} references unknown event {peid}")
    for date_key, refs in index.get("public_sessions_by_date", {}).items():
        if not unique_list(refs):
            errors.append(f"physical index public_sessions_by_date/{date_key} not sorted/deduplicated")
        for ref in refs:
            if ref not in session_refs:
                errors.append(f"physical index session ref unknown: {ref}")
    for peid, uid in index.get("calendar_uids", {}).items():
        if peid not in physical_ids:
            errors.append(f"physical index calendar_uids unknown event {peid}")
        elif physical_ids[peid].get("event_uid") != uid:
            errors.append(f"physical index calendar UID mismatch for {peid}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(
        "OK: Fortnite physical operations V2 validated — "
        f"{len(venue_ids)} venues, {len(physical_ids)} physical events, "
        f"{len(access_ids)} access profiles, {len(ticketing.get('entries', []))} ticketing entries"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
