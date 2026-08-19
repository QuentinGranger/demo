#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"

FILES = {
    "ledger": CAL / "fortnite-competitive-ledger-france.json",
    "engine": CAL / "fortnite-competitive-deadline-engine-france.json",
    "deadlines": CAL / "fortnite-end-reminders-france.json",
    "participants": CAL / "fortnite-competitive-participants-france.json",
}

ALLOWED_OUTCOMES = {
    "UNKNOWN", "PENDING", "ACTIVE", "ADVANCED", "QUALIFIED",
    "ELIMINATED_PATH", "ELIMINATED_EVENT", "WITHDRAWN", "DISQUALIFIED",
}
STRONG_OUTCOMES = {
    "ADVANCED", "QUALIFIED", "ELIMINATED_PATH", "ELIMINATED_EVENT",
    "WITHDRAWN", "DISQUALIFIED",
}
STRONG_EVIDENCE = {"OFFICIAL_EXPLICIT", "OFFICIAL_STANDINGS_DERIVED"}
FINAL_RESULT_STATES = {"FINAL_OFFICIAL", "CORRECTED_FINAL"}
ACTIVE_ROUTE_STATES = {
    "ANNOUNCED", "REGISTRATION_PENDING", "REGISTRATION_OPEN", "REGISTERED",
    "CHECK_IN_PENDING", "READY", "LIVE", "RESULT_PENDING", "ADVANCED",
}
NOTICE_STATES = {
    "DORMANT", "ARMED", "PLANNED", "DEFERRED_QUIET_HOURS", "SENT",
    "SUPPRESSED_CONDITION", "INVALIDATED", "EXPIRED_SILENT",
}


def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def iso_ok(value):
    if value is None:
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def fail(errors, msg):
    errors.append(msg)


def main():
    errors = []
    for path in FILES.values():
        if not path.exists():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1

    ledger = load(FILES["ledger"])
    engine = load(FILES["engine"])
    deadlines = load(FILES["deadlines"])
    participants = load(FILES["participants"])

    if engine.get("version") != "FORTNITE_COMPETITIVE_DEADLINE_ENGINE_EU_V3":
        fail(errors, "deadline engine must be FORTNITE_COMPETITIVE_DEADLINE_ENGINE_EU_V3")
    if deadlines.get("version") != "FORTNITE_DEADLINE_INTELLIGENCE_FR_V3":
        fail(errors, "deadline ledger must be FORTNITE_DEADLINE_INTELLIGENCE_FR_V3")
    if participants.get("version") != "FORTNITE_COMPETITIVE_PARTICIPANT_OUTCOMES_EU_V2":
        fail(errors, "participant ledger must be FORTNITE_COMPETITIVE_PARTICIPANT_OUTCOMES_EU_V2")
    if deadlines.get("policy_engine") != "fortnite-competitive-deadline-engine-france.json":
        fail(errors, "deadline ledger policy_engine reference is missing or incorrect")

    competitions = {}
    phases = {}
    sessions = {}
    for comp in ledger.get("competitions", []):
        cid = comp.get("competition_id")
        if not cid:
            fail(errors, "competition without competition_id")
            continue
        if cid in competitions:
            fail(errors, f"duplicate competition_id: {cid}")
        competitions[cid] = comp
        for phase in comp.get("phases", []):
            pid = phase.get("phase_id")
            if not pid:
                fail(errors, f"phase without phase_id in {cid}")
                continue
            if pid in phases:
                fail(errors, f"duplicate phase_id: {pid}")
            phases[pid] = phase
            for session in phase.get("sessions", []):
                sid = session.get("session_id")
                if not sid:
                    fail(errors, f"session without session_id in {pid}")
                    continue
                if sid in sessions:
                    fail(errors, f"duplicate session_id: {sid}")
                sessions[sid] = session

    engine_route_states = set(engine.get("route_model", {}).get("route_states", []))
    engine_route_types = set(engine.get("route_model", {}).get("route_types", []))
    engine_next_actions = set(engine.get("participant_model", {}).get("next_actions", []))

    lifecycle_ids = set()
    route_ids = set()
    lifecycle_routes = {}
    for lc in deadlines.get("competitive_lifecycles", []):
        cid = lc.get("competition_id")
        if cid not in competitions:
            fail(errors, f"lifecycle references unknown competition_id: {cid}")
        if cid in lifecycle_ids:
            fail(errors, f"duplicate competitive lifecycle: {cid}")
        lifecycle_ids.add(cid)

        pid = lc.get("final_phase_id")
        if pid is not None and pid not in phases:
            fail(errors, f"lifecycle {cid} references unknown final_phase_id: {pid}")
        if not isinstance(lc.get("lifecycle_version"), int) or lc.get("lifecycle_version", 0) < 1:
            fail(errors, f"invalid lifecycle_version for {cid}")

        lifecycle_routes[cid] = {}
        for route in lc.get("routes", []):
            rid = route.get("route_id")
            if not rid:
                fail(errors, f"route without route_id in lifecycle {cid}")
                continue
            if rid in route_ids:
                fail(errors, f"duplicate route_id: {rid}")
            route_ids.add(rid)
            lifecycle_routes[cid][rid] = route

            if route.get("route_type") not in engine_route_types:
                fail(errors, f"invalid route_type for {rid}: {route.get('route_type')}")
            if route.get("state") not in engine_route_states:
                fail(errors, f"invalid route state for {rid}: {route.get('state')}")
            if not isinstance(route.get("route_version"), int) or route.get("route_version", 0) < 1:
                fail(errors, f"invalid route_version for {rid}")
            for phase_id in route.get("phase_ids", []):
                if phase_id not in phases:
                    fail(errors, f"route {rid} references unknown phase_id: {phase_id}")
            for session_id in route.get("session_ids", []):
                if session_id not in sessions:
                    fail(errors, f"route {rid} references unknown session_id: {session_id}")
            if not route.get("target_id"):
                fail(errors, f"route {rid} has no target_id")

        for history in lc.get("history", []):
            if not iso_ok(history.get("at")):
                fail(errors, f"invalid lifecycle history timestamp for {cid}: {history.get('at')}")

    participant_entries = {}
    outcome_ids = set()
    outcome_by_id = {}
    for entry in participants.get("entries", []):
        participant_id = entry.get("participant_id")
        if not participant_id:
            fail(errors, "participant entry without participant_id")
            continue
        if participant_id in participant_entries:
            fail(errors, f"duplicate participant_id: {participant_id}")
        participant_entries[participant_id] = entry

        action = entry.get("next_action")
        if isinstance(action, dict):
            action_value = action.get("action")
        else:
            action_value = action
        if action_value is not None and action_value not in engine_next_actions:
            fail(errors, f"invalid next_action {action_value} for {participant_id}")

        for route in entry.get("active_routes", []):
            rid = route.get("route_id")
            cid = route.get("competition_id")
            if cid not in competitions:
                fail(errors, f"participant {participant_id} route references unknown competition {cid}")
            if rid and rid not in lifecycle_routes.get(cid, {}):
                fail(errors, f"participant {participant_id} references unknown route {rid}")

        for outcome in entry.get("outcomes", []):
            oid = outcome.get("outcome_id")
            if not oid:
                fail(errors, f"participant outcome for {participant_id} lacks outcome_id")
            elif oid in outcome_ids:
                fail(errors, f"duplicate outcome_id: {oid}")
            else:
                outcome_ids.add(oid)
                outcome_by_id[oid] = outcome

            state = outcome.get("state")
            if state not in ALLOWED_OUTCOMES:
                fail(errors, f"invalid participant outcome state {state} for {participant_id}")
            cid = outcome.get("competition_id")
            pid = outcome.get("phase_id")
            sid = outcome.get("session_id")
            rid = outcome.get("route_id")
            if cid not in competitions:
                fail(errors, f"participant {participant_id} references unknown competition {cid}")
            if pid not in phases:
                fail(errors, f"participant {participant_id} references unknown phase {pid}")
            if sid is not None and sid not in sessions:
                fail(errors, f"participant {participant_id} references unknown session {sid}")
            if rid is not None and rid not in lifecycle_routes.get(cid, {}):
                fail(errors, f"participant {participant_id} outcome references unknown route {rid}")

            evidence = outcome.get("evidence_level")
            finality = outcome.get("result_finality")
            if state in STRONG_OUTCOMES and evidence not in STRONG_EVIDENCE:
                fail(errors, f"strong outcome {state} for {participant_id} lacks strong evidence")
            if state in {"ADVANCED", "QUALIFIED", "ELIMINATED_PATH", "ELIMINATED_EVENT"} and finality not in FINAL_RESULT_STATES:
                fail(errors, f"outcome {state} for {participant_id} requires final official result_finality")
            if state == "QUALIFIED" and not outcome.get("qualification_target"):
                fail(errors, f"QUALIFIED outcome for {participant_id} lacks qualification_target")
            if not outcome.get("source_id") or not outcome.get("source_url"):
                fail(errors, f"participant outcome for {participant_id} lacks source")
            if not iso_ok(outcome.get("observed_at")):
                fail(errors, f"invalid observed_at for {participant_id}: {outcome.get('observed_at')}")

            if state == "ELIMINATED_EVENT":
                target = outcome.get("qualification_target")
                active_same_target = []
                for route in entry.get("active_routes", []):
                    if route.get("target_id") == target and route.get("state") in ACTIVE_ROUTE_STATES:
                        active_same_target.append(route.get("route_id"))
                if active_same_target:
                    fail(errors, f"ELIMINATED_EVENT for {participant_id} while active route(s) remain: {active_same_target}")

    for entry in participants.get("entries", []):
        for outcome in entry.get("outcomes", []):
            supersedes = outcome.get("supersedes_outcome_id")
            if supersedes and supersedes not in outcome_by_id:
                fail(errors, f"outcome {outcome.get('outcome_id')} supersedes unknown outcome {supersedes}")

    tracked = participants.get("tracked_participants", [])
    if len(tracked) != len(set(tracked)):
        fail(errors, "tracked_participants contains duplicates")
    for participant_id in tracked:
        entry = participant_entries.get(participant_id)
        if entry is None:
            fail(errors, f"tracked participant has no entry: {participant_id}")
        elif entry.get("tracked") is False:
            fail(errors, f"tracked_participants contains {participant_id} but entry.tracked is false")
    for participant_id, entry in participant_entries.items():
        if entry.get("tracked") is True and participant_id not in tracked:
            fail(errors, f"participant entry {participant_id} is tracked but missing from tracked_participants")

    deadline_types = set(deadlines.get("deadline_types", []))
    milestone_types = set(deadlines.get("milestone_types", []))
    required_deadlines = {"LAST_REGISTRATION_AT", "LAST_CHECK_IN_AT", "LAST_QUALIFIER_AT"}
    required_milestones = {"REGISTRATION_OPENS_AT", "QUALIFIER_START_AT", "RESULT_PROVISIONAL_AT", "FINAL_START_AT"}
    if not required_deadlines.issubset(deadline_types):
        fail(errors, f"required competitive deadline types missing: {sorted(required_deadlines - deadline_types)}")
    if not required_milestones.issubset(milestone_types):
        fail(errors, f"required competitive milestone types missing: {sorted(required_milestones - milestone_types)}")

    for entry in deadlines.get("entries", []):
        for notice in entry.get("planned_notices", []):
            trigger = notice.get("trigger_at")
            if trigger and not iso_ok(trigger):
                fail(errors, f"invalid planned notice timestamp: {trigger}")
            state = notice.get("state")
            if state is not None and state not in NOTICE_STATES:
                fail(errors, f"invalid notice state: {state}")
            participant_id = notice.get("participant_id")
            if state == "ARMED" and participant_id and participant_id not in tracked:
                fail(errors, f"ARMED participant notice references untracked participant: {participant_id}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(
        "OK: competitive deadline V3 validated — "
        f"{len(competitions)} competitions, {len(phases)} phases, {len(sessions)} sessions, "
        f"{len(lifecycle_ids)} lifecycles, {len(route_ids)} routes, "
        f"{len(participant_entries)} participant records, {len(outcome_ids)} outcomes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
