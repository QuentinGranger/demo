#!/usr/bin/env python3
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
POLICY = CAL / "calendar-health-policy.json"
STATE = CAL / "calendar-health-state.json"
HEARTBEAT = CAL / "calendar-health-heartbeat.json"

EXPECTED_POLICY = "CROSS_CALENDAR_HEALTH_POLICY_FR_V2"
EXPECTED_STATE = "CROSS_CALENDAR_HEALTH_STATE_FR_V2"
EXPECTED_HEARTBEAT = "CROSS_CALENDAR_HEALTH_HEARTBEAT_FR_V2"
VALID_HEALTH = {"HEALTHY", "DEGRADED", "CRITICAL"}
VALID_INCIDENT = {"OPEN", "ESCALATED", "RECOVERED"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def normalize_lines(raw):
    text = raw.decode("utf-8-sig")
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def calname_from_raw(raw):
    for line in normalize_lines(raw):
        if line.startswith("X-WR-CALNAME:"):
            return line.split(":", 1)[1]
    return None


def validate_ics(path, errors):
    try:
        raw = path.read_bytes()
        lines = normalize_lines(raw)
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)} is not readable UTF-8: {exc}")
        return

    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append(f"{path.relative_to(ROOT)} must not contain UTF-8 BOM")
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


def fetch_raw(url, attempts=3, timeout=12):
    last_exc = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "calendar-health-validator/2", "Cache-Control": "no-cache"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status < 200 or response.status >= 300:
                    raise RuntimeError(f"HTTP {response.status}")
                return response.read()
        except Exception as exc:
            last_exc = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(str(last_exc))


def monitored_automations(policy):
    result = {}
    for franchise, cfg in policy.get("franchises", {}).items():
        title = cfg.get("main_automation_title")
        if title:
            result[title] = {
                "franchise": franchise,
                "expected_recurrence": cfg.get("expected_recurrence"),
                "max_gap": cfg.get("max_liveness_gap_hours"),
            }
        for support in cfg.get("supporting_automations", []):
            title = support.get("title")
            if title:
                result[title] = {
                    "franchise": franchise,
                    "expected_recurrence": support.get("expected_recurrence"),
                    "max_gap": support.get("max_liveness_gap_hours"),
                }
    return result


def main():
    online = "--online" in sys.argv[1:]
    errors = []
    for path in (POLICY, STATE, HEARTBEAT):
        if not path.exists():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    policy = load_json(POLICY)
    state = load_json(STATE)
    heartbeat = load_json(HEARTBEAT)

    if policy.get("version") != EXPECTED_POLICY:
        errors.append(f"unexpected health policy version {policy.get('version')!r}")
    if state.get("version") != EXPECTED_STATE:
        errors.append(f"unexpected health state version {state.get('version')!r}")
    if heartbeat.get("version") != EXPECTED_HEARTBEAT:
        errors.append(f"unexpected health heartbeat version {heartbeat.get('version')!r}")
    if state.get("policy") != "calendar-health-policy.json" or heartbeat.get("policy") != "calendar-health-policy.json":
        errors.append("health state and heartbeat must reference calendar-health-policy.json")
    if policy.get("repository") != "QuentinGranger/demo":
        errors.append("health policy repository must remain QuentinGranger/demo")
    if policy.get("pinned_branch") != "master":
        errors.append("pinned_branch must remain master unless subscription migration is explicit")
    if heartbeat.get("repository") != policy.get("repository") or heartbeat.get("pinned_branch") != policy.get("pinned_branch"):
        errors.append("heartbeat repository/branch must match health policy")

    hb_policy = policy.get("heartbeat", {})
    if hb_policy.get("file") != "calendars/calendar-health-heartbeat.json":
        errors.append("unexpected heartbeat path")
    if hb_policy.get("version") != EXPECTED_HEARTBEAT:
        errors.append("heartbeat version mismatch between policy and heartbeat validator")
    max_age = hb_policy.get("max_age_hours")
    try:
        observed_at = parse_utc(heartbeat.get("last_observer_check_at"))
        age_hours = (datetime.now(timezone.utc) - observed_at).total_seconds() / 3600
        if age_hours < -1:
            errors.append("last_observer_check_at is implausibly in the future")
        if not isinstance(max_age, (int, float)) or max_age <= 0:
            errors.append("heartbeat max_age_hours must be positive")
        elif age_hours > max_age:
            errors.append(f"WATCHDOG_HEARTBEAT_STALE: heartbeat age {age_hours:.1f}h exceeds {max_age}h")
    except Exception as exc:
        observed_at = None
        errors.append(f"invalid last_observer_check_at: {exc}")
    try:
        parse_utc(heartbeat.get("last_deep_check_at"))
    except Exception as exc:
        errors.append(f"invalid last_deep_check_at: {exc}")

    observer_cfg = policy.get("observers", {})
    observer_titles = {item.get("title") for item in observer_cfg.get("chatgpt_observers", []) if item.get("title")}
    minimum_observers = observer_cfg.get("minimum_enabled_observers")
    if not isinstance(minimum_observers, int) or minimum_observers < 1:
        errors.append("minimum_enabled_observers must be a positive integer")
    if heartbeat.get("observer_title") not in observer_titles:
        if not (heartbeat.get("migration_bootstrap") is True and heartbeat.get("observer_title") == "MANUAL_POLICY_MIGRATION"):
            errors.append("heartbeat observer_title is not a declared observer")

    declared_paths = set()
    franchises = policy.get("franchises", {})
    monitor_cfg = monitored_automations(policy)
    for franchise, cfg in franchises.items():
        global_file = cfg.get("global_file")
        all_files = [global_file] + list(cfg.get("specialist_files", []))
        if cfg.get("expected_recurrence") not in {"HOURLY", "DAILY"}:
            errors.append(f"{franchise} invalid expected recurrence")
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

    contracts = policy.get("subscription_contracts", {})
    if set(contracts) != set(franchises):
        errors.append("subscription_contracts must exactly match franchises")
    for franchise, contract in contracts.items():
        cfg = franchises.get(franchise, {})
        path = contract.get("path")
        if path != cfg.get("global_file"):
            errors.append(f"{franchise} subscription contract path differs from global_file")
            continue
        expected_url = f"https://raw.githubusercontent.com/QuentinGranger/demo/master/{path}"
        if contract.get("raw_url") != expected_url:
            errors.append(f"{franchise} raw subscription URL no longer matches pinned path")
        local_path = ROOT / path
        if local_path.exists():
            local_raw = local_path.read_bytes()
            local_calname = calname_from_raw(local_raw)
            if local_calname != contract.get("expected_calname"):
                errors.append(f"{franchise} X-WR-CALNAME changed: {local_calname!r}")
            if online:
                try:
                    remote_raw = fetch_raw(contract.get("raw_url"))
                    if not remote_raw.startswith(b"BEGIN:VCALENDAR"):
                        errors.append(f"RAW_CONTENT_MISMATCH: {franchise} raw body is not an ICS calendar")
                    if calname_from_raw(remote_raw) != contract.get("expected_calname"):
                        errors.append(f"RAW_CONTENT_MISMATCH: {franchise} raw X-WR-CALNAME mismatch")
                    if hashlib.sha256(remote_raw).hexdigest() != hashlib.sha256(local_raw).hexdigest():
                        errors.append(f"RAW_CONTENT_MISMATCH: {franchise} raw content differs from checked-out master content")
                except Exception as exc:
                    errors.append(f"RAW_SUBSCRIPTION_UNREACHABLE: {franchise}: {exc}")

    if heartbeat.get("verified_ics_path_count") != len(declared_paths):
        errors.append("heartbeat verified_ics_path_count does not match declared ICS paths")

    snapshot = heartbeat.get("automation_snapshot", {})
    if set(snapshot) != set(monitor_cfg):
        missing = sorted(set(monitor_cfg) - set(snapshot))
        extra = sorted(set(snapshot) - set(monitor_cfg))
        if missing:
            errors.append(f"heartbeat automation snapshot missing: {missing}")
        if extra:
            errors.append(f"heartbeat automation snapshot has unexpected titles: {extra}")

    healthy_observers = 0
    expected_timezone = policy.get("automation_liveness", {}).get("expected_timezone")
    for title, expected in monitor_cfg.items():
        info = snapshot.get(title, {})
        if info.get("enabled") is not True:
            errors.append(f"AUTOMATION_DISABLED: {title}")
        if info.get("finite") is not False:
            errors.append(f"AUTOMATION_FINITE: {title}")
        if info.get("expected_recurrence") != expected.get("expected_recurrence") or info.get("observed_recurrence") != expected.get("expected_recurrence"):
            errors.append(f"AUTOMATION_CADENCE_CHANGED: {title}")
        if info.get("timezone") != expected_timezone:
            errors.append(f"AUTOMATION_TIMEZONE_CHANGED: {title}")

        max_gap = expected.get("max_gap")
        if observed_at is not None and isinstance(max_gap, (int, float)) and max_gap > 0:
            last_run = info.get("last_run_time")
            if last_run is None:
                try:
                    updated = parse_utc(info.get("updated_at"))
                    since_update = (observed_at - updated).total_seconds() / 3600
                    if since_update > max_gap:
                        errors.append(f"AUTOMATION_FIRST_RUN_OVERDUE: {title} had no run {since_update:.1f}h after update")
                except Exception as exc:
                    errors.append(f"invalid updated_at for {title}: {exc}")
            else:
                try:
                    last_run_dt = parse_utc(last_run)
                    gap = (observed_at - last_run_dt).total_seconds() / 3600
                    if gap < -1:
                        errors.append(f"{title} last_run_time is after heartbeat observation")
                    elif gap > max_gap:
                        errors.append(f"AUTOMATION_STALE: {title} gap {gap:.1f}h exceeds {max_gap}h at observation")
                except Exception as exc:
                    errors.append(f"invalid last_run_time for {title}: {exc}")
        if title in observer_titles and info.get("enabled") is True and info.get("finite") is False and info.get("liveness") == "HEALTHY":
            healthy_observers += 1

    if heartbeat.get("healthy_observer_count") != healthy_observers:
        errors.append("heartbeat healthy_observer_count does not match observer snapshot")
    if heartbeat.get("minimum_required_observers") != minimum_observers:
        errors.append("heartbeat minimum_required_observers does not match policy")
    if isinstance(minimum_observers, int) and healthy_observers < minimum_observers:
        errors.append(f"OBSERVER_REDUNDANCY_LOST: only {healthy_observers}/{minimum_observers} observers healthy")

    baseline_paths = set()
    for franchise, items in state.get("baseline_manifest", {}).items():
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
        errors.append("baseline manifest paths must exactly match declared calendar paths")

    if state.get("current_overall_state") not in VALID_HEALTH or state.get("redundancy_state") not in VALID_HEALTH:
        errors.append("invalid overall/redundancy health state")
    if heartbeat.get("overall_result") not in VALID_HEALTH:
        errors.append("invalid heartbeat overall_result")
    if set(state.get("franchise_state", {})) != set(franchises):
        errors.append("franchise_state keys must exactly match franchises")
    if set(state.get("observer_state", {})) != observer_titles:
        errors.append("observer_state keys must exactly match declared observers")

    allowed_codes = set(policy.get("incident_codes", []))
    valid_subject_groups = set(franchises) | {"SYSTEM"}
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
        if incident.get("franchise") not in valid_subject_groups:
            errors.append(f"active incident {key} uses unknown franchise/system group {incident.get('franchise')}")

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

    mode = "online+local" if online else "local"
    print(f"OK: permanent redundant calendar health validated ({mode}) — {len(declared_paths)} ICS paths, {len(monitor_cfg)} monitors, {healthy_observers} observers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
