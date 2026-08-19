#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"

FILES = {
    "ledger": CAL / "fortnite-competitive-ledger-france.json",
    "deadlines": CAL / "fortnite-end-reminders-france.json",
    "participants": CAL / "fortnite-competitive-participants-france.json",
}

ALLOWED_OUTCOMES = {"UNKNOWN", "PENDING", "QUALIFIED", "ELIMINATED", "WITHDRAWN", "DISQUALIFIED"}
STRONG_EVIDENCE = {"OFFICIAL_EXPLICIT", "OFFICIAL_STANDINGS_DERIVED"}


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
    for name, path in FILES.items():
        if not path.exists():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1

    ledger = load(FILES["ledger"])
    deadlines = load(FILES["deadlines"])
    participants = load(FILES["participants"])

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

    if deadlines.get("version") != "FORTNITE_DEADLINE_INTELLIGENCE_FR_V2":
        fail(errors, "deadline ledger must be FORTNITE_DEADLINE_INTELLIGENCE_FR_V2")

    lifecycle_ids = set()
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
        for history in lc.get("history", []):
            if not iso_ok(history.get("at")):
                fail(errors, f"invalid lifecycle history timestamp for {cid}: {history.get('at')}")

    participant_entries = {}
    for entry in participants.get("entries", []):
        participant_id = entry.get("participant_id")
        if not participant_id:
            fail(errors, "participant entry without participant_id")
            continue
        if participant_id in participant_entries:
            fail(errors, f"duplicate participant_id: {participant_id}")
        participant_entries[participant_id] = entry
        for outcome in entry.get("outcomes", []):
            state = outcome.get("state")
            if state not in ALLOWED_OUTCOMES:
                fail(errors, f"invalid participant outcome state {state} for {participant_id}")
            cid = outcome.get("competition_id")
            pid = outcome.get("phase_id")
            sid = outcome.get("session_id")
            if cid not in competitions:
                fail(errors, f"participant {participant_id} references unknown competition {cid}")
            if pid not in phases:
                fail(errors, f"participant {participant_id} references unknown phase {pid}")
            if sid is not None and sid not in sessions:
                fail(errors, f"participant {participant_id} references unknown session {sid}")
            evidence = outcome.get("evidence_level")
            if state in {"QUALIFIED", "ELIMINATED", "WITHDRAWN", "DISQUALIFIED"} and evidence not in STRONG_EVIDENCE:
                fail(errors, f"strong outcome {state} for {participant_id} lacks strong evidence")
            if not outcome.get("source_id") or not outcome.get("source_url"):
                fail(errors, f"participant outcome for {participant_id} lacks source")
            if not iso_ok(outcome.get("observed_at")):
                fail(errors, f"invalid observed_at for {participant_id}: {outcome.get('observed_at')}")

    tracked = participants.get("tracked_participants", [])
    if len(tracked) != len(set(tracked)):
        fail(errors, "tracked_participants contains duplicates")
    for participant_id in tracked:
        if participant_id not in participant_entries:
            fail(errors, f"tracked participant has no entry: {participant_id}")

    deadline_types = set(deadlines.get("deadline_types", []))
    milestone_types = set(deadlines.get("milestone_types", []))
    if "LAST_REGISTRATION_AT" not in deadline_types or "LAST_QUALIFIER_AT" not in deadline_types:
        fail(errors, "required competitive deadline types missing")
    if "REGISTRATION_OPENS_AT" not in milestone_types or "FINAL_START_AT" not in milestone_types:
        fail(errors, "required competitive milestone types missing")

    for entry in deadlines.get("entries", []):
        for notice in entry.get("planned_notices", []):
            trigger = notice.get("trigger_at")
            if trigger and not iso_ok(trigger):
                fail(errors, f"invalid planned notice timestamp: {trigger}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(
        "OK: competitive deadlines validated — "
        f"{len(competitions)} competitions, {len(phases)} phases, {len(sessions)} sessions, "
        f"{len(lifecycle_ids)} lifecycles, {len(participant_entries)} tracked participant records"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
