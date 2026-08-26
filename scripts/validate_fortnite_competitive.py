#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

LEDGER = Path('calendars/fortnite-competitive-ledger-france.json')
ENGINE = Path('calendars/fortnite-competitive-engine-france.json')
INDEX = Path('calendars/fortnite-competitive-index-france.json')
SOURCES = Path('calendars/fortnite-sources-france.json')
DEADLINES = Path('calendars/fortnite-end-reminders-france.json')

EXPECTED = {
    LEDGER: 'FORTNITE_COMPETITIVE_INTELLIGENCE_EU_V1',
    ENGINE: 'FORTNITE_COMPETITIVE_ENGINE_EU_V2',
    INDEX: 'FORTNITE_COMPETITIVE_INDEX_EU_V1',
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        raise ValueError(f'missing file: {path}')
    except json.JSONDecodeError as exc:
        raise ValueError(f'invalid JSON in {path}: {exc}')


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    header = f'blob {len(raw)}\0'.encode('ascii')
    return hashlib.sha1(header + raw).hexdigest()


def parse_iso(value: str, context: str, errors: list[str]) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        errors.append(f'{context}: invalid ISO-8601 timestamp {value!r}')
        return None


def assert_unique(values: list[str], label: str, errors: list[str]) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            errors.append(f'duplicate {label}: {value}')
        seen.add(value)


def validate_ledger(ledger: dict[str, Any], errors: list[str]) -> tuple[set[str], set[str], set[str]]:
    if ledger.get('version') != EXPECTED[LEDGER]:
        errors.append(f'{LEDGER}: expected version {EXPECTED[LEDGER]!r}')

    competitions = ledger.get('competitions')
    if not isinstance(competitions, list):
        errors.append(f'{LEDGER}: competitions must be a list')
        return set(), set(), set()

    competition_ids: list[str] = []
    phase_ids: list[str] = []
    session_ids: list[str] = []
    calendar_uids: list[str] = []
    valid_visibility = {'LEDGER_ONLY', 'CALENDAR', 'FEATURED'}
    valid_session_status = {'ANNOUNCED', 'SCHEDULED', 'LIVE', 'COMPLETED', 'POSTPONED', 'CANCELLED'}

    for competition in competitions:
        cid = competition.get('competition_id')
        if not isinstance(cid, str) or not cid:
            errors.append('competition missing non-empty competition_id')
            continue
        competition_ids.append(cid)

        visibility = competition.get('visibility')
        if visibility not in valid_visibility:
            errors.append(f'{cid}: invalid visibility {visibility!r}')

        calendar_uid = competition.get('calendar_uid')
        if calendar_uid is not None:
            if not isinstance(calendar_uid, str) or not calendar_uid:
                errors.append(f'{cid}: calendar_uid must be non-empty string or null')
            else:
                calendar_uids.append(calendar_uid)

        phases = competition.get('phases')
        if not isinstance(phases, list):
            errors.append(f'{cid}: phases must be a list')
            continue

        for phase in phases:
            pid = phase.get('phase_id')
            if not isinstance(pid, str) or not pid:
                errors.append(f'{cid}: phase missing non-empty phase_id')
                continue
            phase_ids.append(pid)
            if not pid.startswith(cid + ':'):
                errors.append(f'{pid}: phase_id must start with competition_id + colon')

            sessions = phase.get('sessions')
            if not isinstance(sessions, list):
                errors.append(f'{pid}: sessions must be a list')
                continue

            for session in sessions:
                sid = session.get('session_id')
                if not isinstance(sid, str) or not sid:
                    errors.append(f'{pid}: session missing non-empty session_id')
                    continue
                session_ids.append(sid)
                if not sid.startswith(pid + ':'):
                    errors.append(f'{sid}: session_id must start with phase_id + colon')

                status = session.get('status')
                if status not in valid_session_status:
                    errors.append(f'{sid}: invalid session status {status!r}')

                start = session.get('start_at')
                end = session.get('end_at')
                start_dt = parse_iso(start, sid, errors) if isinstance(start, str) else None
                end_dt = parse_iso(end, sid, errors) if isinstance(end, str) else None
                if start_dt and end_dt and end_dt <= start_dt:
                    errors.append(f'{sid}: end_at must be later than start_at')

                session_visibility = session.get('visibility')
                if session_visibility not in valid_visibility:
                    errors.append(f'{sid}: invalid visibility {session_visibility!r}')

    assert_unique(competition_ids, 'competition_id', errors)
    assert_unique(phase_ids, 'phase_id', errors)
    assert_unique(session_ids, 'session_id', errors)
    assert_unique(calendar_uids, 'calendar_uid', errors)
    return set(competition_ids), set(phase_ids), set(session_ids)


def validate_engine(engine: dict[str, Any], errors: list[str]) -> None:
    if engine.get('version') != EXPECTED[ENGINE]:
        errors.append(f'{ENGINE}: expected version {EXPECTED[ENGINE]!r}')
    if engine.get('base_ledger') != LEDGER.name:
        errors.append(f'{ENGINE}: base_ledger must be {LEDGER.name!r}')
    if engine.get('base_ledger_version') != EXPECTED[LEDGER]:
        errors.append(f'{ENGINE}: base_ledger_version mismatch')
    if engine.get('derived_index') != INDEX.name:
        errors.append(f'{ENGINE}: derived_index must be {INDEX.name!r}')

    thresholds = engine.get('projection_engine', {}).get('thresholds', {})
    calendar = thresholds.get('CALENDAR')
    featured = thresholds.get('FEATURED')
    if not isinstance(calendar, int) or not isinstance(featured, int) or not 0 <= calendar < featured <= 100:
        errors.append(f'{ENGINE}: projection thresholds must satisfy 0 <= CALENDAR < FEATURED <= 100')


def refs_are_known(values: Any, known: set[str], context: str, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f'{context}: expected list')
        return
    if values != sorted(set(values)):
        errors.append(f'{context}: IDs must be sorted and deduplicated')
    for value in values:
        if value not in known:
            errors.append(f'{context}: unknown ID {value!r}')


def validate_index(index: dict[str, Any], competition_ids: set[str], session_ids: set[str], errors: list[str]) -> None:
    if index.get('version') != EXPECTED[INDEX]:
        errors.append(f'{INDEX}: expected version {EXPECTED[INDEX]!r}')
    if index.get('derived_only') is not True:
        errors.append(f'{INDEX}: derived_only must be true')

    source = index.get('source', {})
    if source.get('ledger') != str(LEDGER):
        errors.append(f'{INDEX}: source.ledger mismatch')
    if source.get('engine') != str(ENGINE):
        errors.append(f'{INDEX}: source.engine mismatch')
    if source.get('ledger_version') != EXPECTED[LEDGER]:
        errors.append(f'{INDEX}: source.ledger_version mismatch')
    if source.get('engine_version') != EXPECTED[ENGINE]:
        errors.append(f'{INDEX}: source.engine_version mismatch')

    expected_ledger_sha = git_blob_sha(LEDGER)
    expected_engine_sha = git_blob_sha(ENGINE)
    if source.get('ledger_sha') != expected_ledger_sha:
        errors.append(f'{INDEX}: stale ledger_sha; rebuild index ({source.get("ledger_sha")} != {expected_ledger_sha})')
    if source.get('engine_sha') != expected_engine_sha:
        errors.append(f'{INDEX}: stale engine_sha; rebuild index ({source.get("engine_sha")} != {expected_engine_sha})')

    indexed_competitions = index.get('competition_ids')
    refs_are_known(indexed_competitions, competition_ids, f'{INDEX}:competition_ids', errors)
    if isinstance(indexed_competitions, list) and set(indexed_competitions) != competition_ids:
        errors.append(f'{INDEX}: competition_ids must exactly match ledger competitions')

    for section_name in ('by_visibility', 'by_status', 'by_region', 'by_series_id', 'by_competition_class', 'by_ruleset', 'by_team_format', 'by_platform_scope', 'by_date'):
        section = index.get(section_name, {})
        if not isinstance(section, dict):
            errors.append(f'{INDEX}:{section_name} must be object')
            continue
        for key, values in section.items():
            refs_are_known(values, competition_ids, f'{INDEX}:{section_name}.{key}', errors)

    sessions = index.get('sessions', {})
    all_session_ids = sessions.get('all_ids', [])
    refs_are_known(all_session_ids, session_ids, f'{INDEX}:sessions.all_ids', errors)
    if isinstance(all_session_ids, list) and set(all_session_ids) != session_ids:
        errors.append(f'{INDEX}: sessions.all_ids must exactly match ledger sessions')

    for section_name in ('by_exact_date', 'by_status', 'by_start_at'):
        section = sessions.get(section_name, {})
        if not isinstance(section, dict):
            errors.append(f'{INDEX}:sessions.{section_name} must be object')
            continue
        for key, values in section.items():
            refs_are_known(values, session_ids, f'{INDEX}:sessions.{section_name}.{key}', errors)


def validate_links(sources: dict[str, Any], deadlines: dict[str, Any], errors: list[str]) -> None:
    linked = sources.get('linked_ledgers', {})
    expected = {
        'competitive_intelligence': LEDGER.name,
        'competitive_engine': ENGINE.name,
        'competitive_index': INDEX.name,
    }
    for key, value in expected.items():
        if linked.get(key) != value:
            errors.append(f'{SOURCES}: linked_ledgers.{key} must be {value!r}')

    deadline_links = deadlines.get('linked_ledgers', {})
    for key, value in expected.items():
        if deadline_links.get(key) != value:
            errors.append(f'{DEADLINES}: linked_ledgers.{key} must be {value!r}')

    # Deadline Intelligence V3 renamed the canonical policy block from
    # competitive_deadline_policy to competitive_lifecycle_policy. Accept the
    # V3 name first while retaining the legacy fallback for older snapshots.
    policy = deadlines.get('competitive_lifecycle_policy') or deadlines.get('competitive_deadline_policy', {})
    if policy.get('canonical_data_source') != EXPECTED[LEDGER]:
        errors.append(f'{DEADLINES}: canonical_data_source mismatch')
    if policy.get('semantic_engine') != EXPECTED[ENGINE]:
        errors.append(f'{DEADLINES}: semantic_engine mismatch')


def main() -> int:
    errors: list[str] = []
    try:
        ledger = load_json(LEDGER)
        engine = load_json(ENGINE)
        index = load_json(INDEX)
        sources = load_json(SOURCES)
        deadlines = load_json(DEADLINES)
    except ValueError as exc:
        print(f'Fortnite competitive validation FAILED:\n - {exc}', file=sys.stderr)
        return 1

    competition_ids, phase_ids, session_ids = validate_ledger(ledger, errors)
    validate_engine(engine, errors)
    validate_index(index, competition_ids, session_ids, errors)
    validate_links(sources, deadlines, errors)

    if errors:
        print('Fortnite competitive validation FAILED:', file=sys.stderr)
        for error in errors:
            print(f' - {error}', file=sys.stderr)
        return 1

    print(
        'Fortnite competitive validation OK: '
        f'{len(competition_ids)} competitions, {len(phase_ids)} phases, {len(session_ids)} sessions.'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
