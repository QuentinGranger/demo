#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
LEDGER = CAL / "fortnite-change-ledger.json"
ENGINE = CAL / "fortnite-change-engine-france.json"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_LEDGER = "FORTNITE_CHANGE_LEDGER_FR_V1"
EXPECTED_ENGINE = "FORTNITE_CHANGE_ENGINE_FR_V1"
TERMINAL_RECEIPT_STATES = {
    "SUPPRESSED_BASELINE",
    "SUPPRESSED_POLICY",
    "RESERVED",
    "SENT",
    "UNKNOWN_DELIVERY",
}
VALID_RECEIPT_STATES = TERMINAL_RECEIPT_STATES | {"PENDING", "CANCELLED_BEFORE_SEND"}
VALID_WRITE_STATES = {"PLANNED", "COMMITTED", "SKIPPED_IDENTICAL", "FAILED_BEFORE_COMMIT", "UNKNOWN_COMMIT_STATE"}
VALID_MATERIALITY = {"IGNORE", "LEDGER_ONLY", "CALENDAR", "NOTIFY"}
VALID_CHANGE_STATE = {"OPEN", "SUPERSEDED", "ARCHIVED"}


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    errors = []
    for path in (LEDGER, ENGINE):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    ledger = load(LEDGER)
    engine = load(ENGINE)

    if ledger.get("version") != EXPECTED_LEDGER:
        errors.append(f"unexpected change ledger version {ledger.get('version')!r}")
    if engine.get("version") != EXPECTED_ENGINE:
        errors.append(f"unexpected change engine version {engine.get('version')!r}")
    if engine.get("ledger") != "fortnite-change-ledger.json":
        errors.append("change engine must reference fortnite-change-ledger.json")

    delivery = ledger.get("delivery_semantics", {})
    if delivery.get("notification_guarantee") != "AT_MOST_ONCE_PREFER_MISSING_OVER_DUPLICATE":
        errors.append("notification guarantee must remain AT_MOST_ONCE_PREFER_MISSING_OVER_DUPLICATE")

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
        local = ROOT / path
        if not local.exists():
            errors.append(f"bootstrap path does not exist in repo: {path}")

    changes = ledger.get("changes", [])
    change_ids = {}
    fingerprint_scope = {}
    supersedes = {}
    for c in changes:
        cid = c.get("change_id")
        if not cid:
            errors.append("change without change_id")
            continue
        if cid in change_ids:
            errors.append(f"duplicate change_id: {cid}")
        change_ids[cid] = c
        if c.get("domain") not in set(ledger.get("domains", [])):
            errors.append(f"change {cid} has invalid domain {c.get('domain')}")
        if c.get("materiality") not in VALID_MATERIALITY:
            errors.append(f"change {cid} has invalid materiality {c.get('materiality')}")
        if c.get("state", "OPEN") not in VALID_CHANGE_STATE:
            errors.append(f"change {cid} has invalid state {c.get('state')}")
        if c.get("change_type") not in set(ledger.get("change_type_registry", [])):
            errors.append(f"change {cid} has invalid change_type {c.get('change_type')}")
        fp = c.get("semantic_fingerprint")
        if not HEX64.match(str(fp or "")):
            errors.append(f"change {cid} has invalid semantic_fingerprint")
        scope_tuple = (c.get("domain"), c.get("subject_key"), c.get("scope_key"), c.get("change_type"), fp)
        if scope_tuple in fingerprint_scope:
            errors.append(f"duplicate semantic change for {cid} and {fingerprint_scope[scope_tuple]}")
        else:
            fingerprint_scope[scope_tuple] = cid
        sup = c.get("supersedes_change_id")
        if sup:
            supersedes[cid] = sup

    for cid, sup in supersedes.items():
        if sup not in change_ids:
            errors.append(f"change {cid} supersedes unknown change {sup}")
        seen = {cid}
        cur = sup
        while cur:
            if cur in seen:
                errors.append(f"supersession cycle detected from {cid}")
                break
            seen.add(cur)
            cur = supersedes.get(cur)

    receipts = ledger.get("notification_receipts", [])
    receipt_ids = {}
    key_to_receipt = {}
    for r in receipts:
        rid = r.get("receipt_id")
        key = r.get("notification_key")
        if not rid:
            errors.append("notification receipt without receipt_id")
            continue
        if rid in receipt_ids:
            errors.append(f"duplicate receipt_id: {rid}")
        receipt_ids[rid] = r
        if not key:
            errors.append(f"receipt {rid} missing notification_key")
        elif key in key_to_receipt:
            errors.append(f"duplicate notification_key {key} in {rid} and {key_to_receipt[key]}")
        else:
            key_to_receipt[key] = rid
        if r.get("state") not in VALID_RECEIPT_STATES:
            errors.append(f"receipt {rid} invalid state {r.get('state')}")
        member_changes = r.get("change_ids")
        if not isinstance(member_changes, list) or not member_changes:
            errors.append(f"receipt {rid} must reference at least one change_id")
        else:
            for cid in member_changes:
                if cid not in change_ids:
                    errors.append(f"receipt {rid} references unknown change_id {cid}")
        if r.get("state") == "SENT" and not r.get("sent_at"):
            errors.append(f"SENT receipt {rid} missing sent_at")
        if r.get("state") == "RESERVED" and not r.get("reserved_at"):
            errors.append(f"RESERVED receipt {rid} missing reserved_at")
        if r.get("state") == "UNKNOWN_DELIVERY" and not r.get("unknown_delivery_at"):
            errors.append(f"UNKNOWN_DELIVERY receipt {rid} missing unknown_delivery_at")

    key_index = ledger.get("notification_key_index", {})
    if not isinstance(key_index, dict):
        errors.append("notification_key_index must be an object")
        key_index = {}
    for key, rid in key_index.items():
        if key not in key_to_receipt:
            errors.append(f"notification_key_index contains orphan key {key}")
        elif key_to_receipt[key] != rid:
            errors.append(f"notification_key_index mismatch for {key}: {rid} != {key_to_receipt[key]}")
    for key, rid in key_to_receipt.items():
        if key_index.get(key) != rid:
            errors.append(f"notification receipt {rid} missing/mismatched in notification_key_index")

    for collection_name in ("calendar_write_receipts", "ledger_write_receipts"):
        seen_write_keys = set()
        for w in ledger.get(collection_name, []):
            key = w.get("write_key")
            if not key:
                errors.append(f"{collection_name} receipt missing write_key")
                continue
            if key in seen_write_keys:
                errors.append(f"duplicate write_key in {collection_name}: {key}")
            seen_write_keys.add(key)
            if w.get("state") not in VALID_WRITE_STATES:
                errors.append(f"write receipt {key} invalid state {w.get('state')}")
            fp = w.get("semantic_fingerprint")
            if not HEX64.match(str(fp or "")):
                errors.append(f"write receipt {key} invalid semantic_fingerprint")

    terminal_engine = set(engine.get("reservation_and_delivery", {}).get("terminal_dedupe_states", []))
    if terminal_engine != TERMINAL_RECEIPT_STATES:
        errors.append("engine terminal_dedupe_states must exactly match validator policy")
    if engine.get("reservation_and_delivery", {}).get("reserve_before_emit") is not True:
        errors.append("engine must require reserve_before_emit=true")
    if engine.get("reservation_and_delivery", {}).get("fresh_read_before_reserve") is not True:
        errors.append("engine must require fresh_read_before_reserve=true")

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    consumed = sum(1 for r in receipts if r.get("state") in TERMINAL_RECEIPT_STATES)
    print(f"OK: Fortnite change ledger validated — {len(changes)} changes, {len(receipts)} notification receipts, {consumed} consumed notification keys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
