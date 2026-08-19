#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
POLICY = CAL / "calendar-health-policy.json"
STATE = CAL / "calendar-health-state.json"

EXPECTED_POLICY = "CROSS_CALENDAR_HEALTH_POLICY_FR_V1"
EXPECTED_STATE = "CROSS_CALENDAR_HEALTH_STATE_FR_V1"
VALID_HEALTH = {"HEALTHY", "DEGRADED", "CRITICAL"}
VALID_INCIDENT = {"OPEN", "ESCALATED", "RECOVERED"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_ics(path, errors):
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8-sig")
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)} is not readable UTF-8: {exc}")
        return

    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path.relative_to(ROOT)} must not contain UTF-8 BOM")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    nonempty = [line for line in lines if line != ""]
    if not nonempty or nonempty[0] != "BEGIN:VCALENDAR":
        errors.append(f"{path.relative_to(ROOT)} does not start with BEGIN:VCALENDAR")
        return
    if nonempty[-1] != "END:VCALENDAR":
        errors.append(f"{path.relative_to(ROOT)} does not end with END:VCALENDAR")
    if "VERSION:2.0" not in nonempty:
        errors.append(f"{path.relative_to(ROOT)} missing VERSION:2.0")

    stack = []
    uids = set()
    current_event_uid = None
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("BEGIN:"):
            component = line[6:]
            stack.append(component)
            if component == "VEVENT":
                current_event_uid = None
        elif line.startswith("END:"):
            component = line[4:]
            if not stack or stack[-1] != component:
                errors.append(f"{path.relative_to(ROOT)} component mismatch at line {line_no}: {line}")
                continue
            if component == "VEVENT":
                if not current_event_uid:
                    errors.append(f"{path.relative_to(ROOT)} VEVENT without UID ending at line {line_no}")
                current_event_uid = None
            stack.pop()
        elif stack and stack[-1] == "VEVENT" and line.startswith("UID:"):
            uid = line[4:].strip()
            if uid in uids:
                errors.append(f"{path.relative_to(ROOT)} duplicate VEVENT UID: {uid}")
            uids.add(uid)
            current_event_uid = uid
    if stack:
        errors.append(f"{path.relative_to(ROOT)} has unclosed components: {stack}")


def main():
    errors = []
    for path in (POLICY, STATE):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    policy = load_json(POLICY)
    state = load_json(STATE)

    if policy.get("version") != EXPECTED_POLICY:
        errors.append(f"unexpected health policy version {policy.get('version')!r}")
    if state.get("version") != EXPECTED_STATE:
        errors.append(f"unexpected health state version {state.get('version')!r}")
    if state.get("policy") != "calendar-health-policy.json":
        errors.append("health state must reference calendar-health-policy.json")
    if policy.get("repository") != "QuentinGranger/demo":
        errors.append("health policy repository must remain QuentinGranger/demo")
    if policy.get("pinned_branch") != "master":
        errors.append("health policy pinned_branch must remain master unless subscription migration is explicit")

    declared_paths = set()
    franchises = policy.get("franchises", {})
    for franchise, cfg in franchises.items():
        global_file = cfg.get("global_file")
        specialists = cfg.get("specialist_files", [])
        all_files = [global_file] + list(specialists)
        if not cfg.get("main_automation_title"):
            errors.append(f"{franchise} missing main_automation_title")
        if cfg.get("expected_recurrence") not in {"HOURLY", "DAILY"}:
            errors.append(f"{franchise} invalid expected_recurrence")
        if not isinstance(cfg.get("max_liveness_gap_hours"), (int, float)) or cfg.get("max_liveness_gap_hours") <= 0:
            errors.append(f"{franchise} invalid max_liveness_gap_hours")
        expected_raw = f"https://raw.githubusercontent.com/QuentinGranger/demo/master/{global_file}"
        if cfg.get("global_raw_url") != expected_raw:
            errors.append(f"{franchise} global_raw_url no longer matches pinned subscribed path")

        for rel in all_files:
            if not isinstance(rel, str) or not rel.startswith("calendars/") or not rel.endswith(".ics"):
                errors.append(f"{franchise} invalid calendar path: {rel!r}")
                continue
            if rel in declared_paths:
                errors.append(f"calendar path declared more than once: {rel}")
            declared_paths.add(rel)
            local = ROOT / rel
            if not local.exists():
                errors.append(f"missing subscribed/specialist file: {rel}")
            else:
                validate_ics(local, errors)

    baseline_paths = set()
    manifest = state.get("baseline_manifest", {})
    for franchise, items in manifest.items():
        if franchise not in franchises:
            errors.append(f"health state baseline contains unknown franchise {franchise}")
        for item in items:
            rel = item.get("path")
            sha = item.get("sha")
            if rel in baseline_paths:
                errors.append(f"duplicate baseline manifest path: {rel}")
            baseline_paths.add(rel)
            if not HEX40.match(str(sha or "")):
                errors.append(f"baseline path {rel} has invalid blob SHA")
    if baseline_paths != declared_paths:
        missing = sorted(declared_paths - baseline_paths)
        extra = sorted(baseline_paths - declared_paths)
        if missing:
            errors.append(f"baseline manifest missing declared files: {missing}")
        if extra:
            errors.append(f"baseline manifest has undeclared files: {extra}")

    if state.get("current_overall_state") not in VALID_HEALTH:
        errors.append("invalid current_overall_state")
    franchise_state = state.get("franchise_state", {})
    if set(franchise_state) != set(franchises):
        errors.append("franchise_state keys must exactly match health-policy franchises")
    for franchise, health in franchise_state.items():
        if health not in VALID_HEALTH:
            errors.append(f"{franchise} invalid health state {health}")

    allowed_codes = set(policy.get("incident_codes", []))
    active_keys = set()
    for incident in state.get("active_incidents", []):
        key = incident.get("incident_key")
        if not key:
            errors.append("active incident missing incident_key")
            continue
        if key in active_keys:
            errors.append(f"duplicate active incident key: {key}")
        active_keys.add(key)
        if incident.get("state") not in {"OPEN", "ESCALATED"}:
            errors.append(f"active incident {key} must be OPEN or ESCALATED")
        if incident.get("code") not in allowed_codes:
            errors.append(f"active incident {key} uses unknown code {incident.get('code')}")
        if incident.get("franchise") not in franchises:
            errors.append(f"active incident {key} uses unknown franchise {incident.get('franchise')}")

    seen_history_ids = set()
    for incident in state.get("incident_history", []):
        iid = incident.get("incident_id")
        if iid:
            if iid in seen_history_ids:
                errors.append(f"duplicate incident_history incident_id: {iid}")
            seen_history_ids.add(iid)
        if incident.get("state") not in VALID_INCIDENT:
            errors.append(f"incident history entry has invalid state {incident.get('state')}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print(f"FAILED: {len(errors)} health validation error(s)")
        return 1

    print(f"OK: permanent calendar health policy validated — {len(declared_paths)} ICS paths across {len(franchises)} franchises")
    return 0


if __name__ == "__main__":
    sys.exit(main())
