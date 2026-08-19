#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
LEDGER = CAL / "fortnite-change-ledger.json"
ENGINE = CAL / "fortnite-change-engine-france.json"
OUTBOX = CAL / "fortnite-notification-outbox-france.json"
INDEX = CAL / "fortnite-change-index-france.json"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CHANGE_ID = re.compile(r"^chg_[0-9a-f]{24}$")
INTENT_ID = re.compile(r"^nti_[0-9a-f]{24}$")
NOTIFICATION_KEY = re.compile(r"^ntf_[0-9a-f]{64}$")

EXPECTED = {
    "ledger": "FORTNITE_CHANGE_LEDGER_FR_V2",
    "engine": "FORTNITE_CHANGE_ENGINE_FR_V2",
    "outbox": "FORTNITE_NOTIFICATION_OUTBOX_FR_V1",
    "index": "FORTNITE_CHANGE_INDEX_FR_V1",
}
VALID_MATERIALITY = {"IGNORE", "LEDGER_ONLY", "CALENDAR", "NOTIFY"}
VALID_CHANGE_STATE = {"OPEN", "SUPERSEDED", "ARCHIVED"}
VALID_DISPOSITION = {"BASELINE", "SILENT_POLICY", "ELIGIBLE_NOW", "ELIGIBLE_WHEN_DUE", "CONDITION_BLOCKED", "STALE", "NOT_APPLICABLE"}
VALID_DELIVERY_STATES = {"RESERVED", "SENT", "UNKNOWN_DELIVERY", "CANCELLED_BEFORE_SEND"}
CONSUMED_STATES = {"RESERVED", "SENT", "UNKNOWN_DELIVERY"}
VALID_WRITE_STATES = {"PLANNED", "COMMITTED", "SKIPPED_IDENTICAL", "FAILED_BEFORE_COMMIT", "UNKNOWN_COMMIT_STATE"}


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iso_dt(value):
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def fail(errors):
    for error in errors:
        print(f"ERROR: {error}")
    print(f"FAILED: {len(errors)} error(s)")
    return 1


def main():
    errors = []
    for path in (LEDGER, ENGINE, OUTBOX, INDEX):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        return fail(errors)

    ledger = load(LEDGER)
    engine = load(ENGINE)
    outbox = load(OUTBOX)
    index = load(INDEX)

    actual_versions = {
        "ledger": ledger.get("version"),
        "engine": engine.get("version"),
        "outbox": outbox.get("version"),
        "index": index.get("version"),
    }
    for name, wanted in EXPECTED.items():
        if actual_versions[name] != wanted:
            errors.append(f"unexpected {name} version {actual_versions[name]!r}; wanted {wanted}")

    if ledger.get("notification_outbox") != "fortnite-notification-outbox-france.json":
        errors.append("ledger must reference notification outbox")
    if ledger.get("derived_index") != "fortnite-change-index-france.json":
        errors.append("ledger must reference derived change index")
    if engine.get("ledger") != "fortnite-change-ledger.json":
        errors.append("engine must reference fortnite-change-ledger.json")
    if engine.get("outbox") != "fortnite-notification-outbox-france.json":
        errors.append("engine must reference notification outbox")
    if outbox.get("change_ledger") != "fortnite-change-ledger.json":
        errors.append("outbox must reference fortnite-change-ledger.json")
    if index.get("source_ledger") != "fortnite-change-ledger.json" or index.get("notification_outbox") != "fortnite-notification-outbox-france.json":
        errors.append("derived index must reference ledger and outbox")

    if outbox.get("delivery_semantics", {}).get("guarantee") != "AT_MOST_ONCE_DELIVERY_ATTEMPT":
        errors.append("outbox guarantee must remain AT_MOST_ONCE_DELIVERY_ATTEMPT")
    if outbox.get("delivery_semantics", {}).get("intent_guarantee") != "EXACTLY_ONCE_LOGICAL_INTENT_PER_NOTIFICATION_KEY":
        errors.append("outbox must guarantee exactly-once logical intent per notification_key")
    if outbox.get("cas_protocol", {}).get("fresh_read_required") is not True:
        errors.append("outbox CAS protocol must require fresh read")
    if outbox.get("delivery_semantics", {}).get("no_early_reservation") is None:
        errors.append("outbox must define no_early_reservation policy")

    manifest_paths = set()
    for item in ledger.get("bootstrap", {}).get("manifest", []):
        path = item.get("path")
        sha = item.get("sha")
        if not path:
            errors.append("bootstrap manifest item missing path")
            continue
        if path in manifest_paths:
            errors.append(f"duplicate bootstrap path: {path}")
        manifest_paths.add(path)
        if not HEX40.match(str(sha or "")):
            errors.append(f"bootstrap path {path} has invalid git blob sha")
        if not (ROOT / path).exists():
            errors.append(f"bootstrap path missing from repo: {path}")

    domains = set(ledger.get("domains", []))
    change_types = set(ledger.get("change_type_registry", []))
    changes = ledger.get("changes", [])
    change_by_id = {}
    revision_key = {}
    head_by_subject = {}
    supersedes = {}

    for c in changes:
        cid = c.get("change_id")
        if not CHANGE_ID.match(str(cid or "")):
            errors.append(f"invalid change_id: {cid!r}")
            continue
        if cid in change_by_id:
            errors.append(f"duplicate change_id: {cid}")
        change_by_id[cid] = c
        if c.get("domain") not in domains:
            errors.append(f"change {cid} invalid domain {c.get('domain')}")
        if c.get("change_type") not in change_types:
            errors.append(f"change {cid} invalid change_type {c.get('change_type')}")
        if c.get("materiality") not in VALID_MATERIALITY:
            errors.append(f"change {cid} invalid materiality {c.get('materiality')}")
        if c.get("state", "OPEN") not in VALID_CHANGE_STATE:
            errors.append(f"change {cid} invalid state {c.get('state')}")
        if c.get("notification_disposition") not in VALID_DISPOSITION:
            errors.append(f"change {cid} invalid notification_disposition {c.get('notification_disposition')}")
        if not c.get("subject_key") or not c.get("subject_scope_key"):
            errors.append(f"change {cid} missing subject identity")
        rev = c.get("subject_revision")
        if not isinstance(rev, int) or rev < 1:
            errors.append(f"change {cid} invalid subject_revision {rev!r}")
        key = (c.get("subject_scope_key"), rev)
        if key in revision_key:
            errors.append(f"duplicate subject revision {key} for {cid} and {revision_key[key]}")
        else:
            revision_key[key] = cid
        if not HEX64.match(str(c.get("state_fingerprint") or "")):
            errors.append(f"change {cid} invalid state_fingerprint")
        if not HEX64.match(str(c.get("transition_fingerprint") or "")):
            errors.append(f"change {cid} invalid transition_fingerprint")
        if not iso_dt(c.get("detected_at")):
            errors.append(f"change {cid} invalid detected_at")
        parent = c.get("causal_parent_change_id")
        if rev == 1 and parent is not None:
            errors.append(f"change {cid} revision 1 must have null causal parent")
        sup = c.get("supersedes_change_id")
        if sup:
            supersedes[cid] = sup
        old = head_by_subject.get(c.get("subject_scope_key"))
        if old is None or rev > old[0]:
            head_by_subject[c.get("subject_scope_key")] = (rev, cid)

    for cid, c in change_by_id.items():
        rev = c.get("subject_revision")
        parent = c.get("causal_parent_change_id")
        if isinstance(rev, int) and rev > 1:
            expected_parent = revision_key.get((c.get("subject_scope_key"), rev - 1))
            if not expected_parent:
                errors.append(f"change {cid} revision {rev} has no previous revision")
            elif parent != expected_parent:
                errors.append(f"change {cid} causal parent {parent!r} != previous revision {expected_parent!r}")
        if parent:
            p = change_by_id.get(parent)
            if not p:
                errors.append(f"change {cid} references unknown causal parent {parent}")
            elif p.get("subject_scope_key") != c.get("subject_scope_key"):
                errors.append(f"change {cid} causal parent belongs to different subject scope")

    for cid, sup in supersedes.items():
        if sup not in change_by_id:
            errors.append(f"change {cid} supersedes unknown change {sup}")
        seen = {cid}
        cur = sup
        while cur:
            if cur in seen:
                errors.append(f"supersession cycle detected from {cid}")
                break
            seen.add(cur)
            cur = supersedes.get(cur)

    legacy = ledger.get("legacy_v1_notification_fields", {})
    if legacy.get("notification_receipts") not in ([], None):
        errors.append("legacy V1 notification_receipts must remain empty; outbox is canonical")
    if legacy.get("notification_key_index") not in ({}, None):
        errors.append("legacy V1 notification_key_index must remain empty; outbox is canonical")

    for collection_name in ("calendar_write_receipts", "ledger_write_receipts"):
        seen = set()
        for w in ledger.get(collection_name, []):
            key = w.get("write_key")
            if not key:
                errors.append(f"{collection_name} receipt missing write_key")
                continue
            if key in seen:
                errors.append(f"duplicate {collection_name} write_key {key}")
            seen.add(key)
            if w.get("state") not in VALID_WRITE_STATES:
                errors.append(f"write receipt {key} invalid state {w.get('state')}")
            if not HEX64.match(str(w.get("semantic_fingerprint") or "")):
                errors.append(f"write receipt {key} invalid semantic_fingerprint")

    intents = outbox.get("intents", [])
    intent_by_id = {}
    intent_by_key = {}
    for i in intents:
        iid = i.get("intent_id")
        key = i.get("notification_key")
        if not INTENT_ID.match(str(iid or "")):
            errors.append(f"invalid intent_id {iid!r}")
            continue
        if iid in intent_by_id:
            errors.append(f"duplicate intent_id {iid}")
        intent_by_id[iid] = i
        if not NOTIFICATION_KEY.match(str(key or "")):
            errors.append(f"intent {iid} invalid notification_key")
        elif key in intent_by_key:
            errors.append(f"duplicate logical notification intent for key {key}")
        else:
            intent_by_key[key] = iid
        change_ids = i.get("change_ids")
        if not isinstance(change_ids, list) or not change_ids:
            errors.append(f"intent {iid} must reference at least one change_id")
        else:
            for cid in change_ids:
                if cid not in change_by_id:
                    errors.append(f"intent {iid} references unknown change_id {cid}")
        if not HEX64.match(str(i.get("payload_fingerprint") or "")):
            errors.append(f"intent {iid} invalid payload_fingerprint")
        if not i.get("notice_kind") or not i.get("audience_key") or not i.get("channel_key") or not i.get("render_version"):
            errors.append(f"intent {iid} missing routing/render metadata")
        if not iso_dt(i.get("created_at")):
            errors.append(f"intent {iid} invalid created_at")

    events = outbox.get("delivery_events", [])
    event_ids = set()
    events_by_intent = {}
    for e in events:
        eid = e.get("delivery_event_id")
        iid = e.get("intent_id")
        key = e.get("notification_key")
        state = e.get("state")
        if not eid:
            errors.append("delivery event missing delivery_event_id")
            continue
        if eid in event_ids:
            errors.append(f"duplicate delivery_event_id {eid}")
        event_ids.add(eid)
        if iid not in intent_by_id:
            errors.append(f"delivery event {eid} references unknown intent {iid}")
        elif intent_by_id[iid].get("notification_key") != key:
            errors.append(f"delivery event {eid} notification_key mismatch")
        if state not in VALID_DELIVERY_STATES:
            errors.append(f"delivery event {eid} invalid state {state}")
        if not iso_dt(e.get("at")):
            errors.append(f"delivery event {eid} invalid at")
        if state == "RESERVED" and not e.get("reservation_id"):
            errors.append(f"RESERVED delivery event {eid} missing reservation_id")
        events_by_intent.setdefault(iid, []).append(e)

    derived_consumed = {}
    for iid, evs in events_by_intent.items():
        evs_sorted = sorted(evs, key=lambda x: x.get("at", ""))
        reserved_seen = False
        latest_consumed = None
        for e in evs_sorted:
            state = e.get("state")
            if state == "RESERVED":
                if reserved_seen:
                    errors.append(f"intent {iid} has multiple RESERVED events")
                reserved_seen = True
                latest_consumed = e
            elif state in {"SENT", "UNKNOWN_DELIVERY"}:
                if not reserved_seen:
                    errors.append(f"intent {iid} has {state} before RESERVED")
                latest_consumed = e
            elif state == "CANCELLED_BEFORE_SEND" and reserved_seen:
                errors.append(f"intent {iid} cannot CANCEL_BEFORE_SEND after reservation")
        if latest_consumed:
            key = intent_by_id.get(iid, {}).get("notification_key")
            if key:
                derived_consumed[key] = {
                    "intent_id": iid,
                    "state": latest_consumed.get("state"),
                    "last_event_id": latest_consumed.get("delivery_event_id"),
                }

    consumed = outbox.get("consumed_keys", {})
    if not isinstance(consumed, dict):
        errors.append("outbox consumed_keys must be an object")
        consumed = {}
    if consumed != derived_consumed:
        errors.append("outbox consumed_keys diverges from append-only delivery events")

    group_index = outbox.get("group_index", {})
    if not isinstance(group_index, dict):
        errors.append("outbox group_index must be an object")
    else:
        for group_key, iid in group_index.items():
            if iid not in intent_by_id:
                errors.append(f"group_index {group_key} points to unknown intent {iid}")
            elif intent_by_id[iid].get("group_key") != group_key:
                errors.append(f"group_index mismatch for {group_key}")
        for iid, intent in intent_by_id.items():
            g = intent.get("group_key")
            if g and group_index.get(g) != iid:
                errors.append(f"intent {iid} group_key missing/mismatched in group_index")

    # Derived index must exactly match current canonical heads and consumed keys.
    expected_heads = {k: {"revision": rev, "change_id": cid} for k, (rev, cid) in sorted(head_by_subject.items())}
    if index.get("subject_heads", {}) != expected_heads:
        errors.append("change index subject_heads diverges from ledger")
    expected_consumed_keys = sorted(derived_consumed.keys())
    if index.get("consumed_notification_keys", []) != expected_consumed_keys:
        errors.append("change index consumed_notification_keys diverges from outbox")
    expected_unknown = sorted(k for k, v in derived_consumed.items() if v.get("state") == "UNKNOWN_DELIVERY")
    if index.get("unknown_delivery_keys", []) != expected_unknown:
        errors.append("change index unknown_delivery_keys diverges from outbox")

    stats = index.get("stats", {})
    if stats.get("changes") != len(changes):
        errors.append("change index stats.changes mismatch")
    if stats.get("subjects") != len(head_by_subject):
        errors.append("change index stats.subjects mismatch")
    if stats.get("notification_intents") != len(intents):
        errors.append("change index stats.notification_intents mismatch")
    if stats.get("consumed_notification_keys") != len(derived_consumed):
        errors.append("change index stats.consumed_notification_keys mismatch")
    if stats.get("unknown_delivery") != len(expected_unknown):
        errors.append("change index stats.unknown_delivery mismatch")

    if errors:
        return fail(errors)

    print(
        "OK: Fortnite change/outbox validated — "
        f"{len(changes)} changes, {len(head_by_subject)} subjects, "
        f"{len(intents)} intents, {len(derived_consumed)} consumed notification keys"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
