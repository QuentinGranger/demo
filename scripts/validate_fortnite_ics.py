#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

DEFAULT_FILES = [
    Path('calendars/fortnite-paris.ics'),
    Path('calendars/fortnite-updates-france.ics'),
    Path('calendars/fortnite-competitive-france.ics'),
]

PROPERTY_NAME_RE = re.compile(r'^[A-Z0-9-]+$')
PARAM_NAME_RE = re.compile(r'^[A-Z0-9-]+$')
DATE_RE = re.compile(r'^\d{8}$')
UTC_DT_RE = re.compile(r'^\d{8}T\d{6}Z$')
LOCAL_DT_RE = re.compile(r'^\d{8}T\d{6}$')


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Property:
    name: str
    params: tuple[tuple[str, str], ...]
    value: str
    raw: str

    def param(self, key: str) -> str | None:
        key = key.upper()
        for k, v in self.params:
            if k == key:
                return v
        return None


def utf8_len(s: str) -> int:
    return len(s.encode('utf-8'))


def split_universal_lines(text: str) -> list[str]:
    return text.replace('\r\n', '\n').replace('\r', '\n').split('\n')


def unfold_lines(physical_lines: Iterable[str]) -> list[str]:
    logical: list[str] = []
    for line in physical_lines:
        if line.startswith((' ', '\t')):
            if not logical:
                raise ValidationError('Continuation line appears before any content line')
            logical[-1] += line[1:]
        else:
            logical.append(line)
    return logical


def fold_line(line: str, limit: int = 75) -> list[str]:
    if utf8_len(line) <= limit:
        return [line]
    out: list[str] = []
    remaining = line
    first = True
    while remaining:
        budget = limit if first else limit - 1
        used = 0
        cut = 0
        for idx, ch in enumerate(remaining):
            n = utf8_len(ch)
            if used + n > budget:
                break
            used += n
            cut = idx + 1
        if cut == 0:
            raise ValidationError('Unable to fold line without splitting UTF-8 code point')
        chunk = remaining[:cut]
        out.append(chunk if first else ' ' + chunk)
        remaining = remaining[cut:]
        first = False
    return out


def normalize_ics_bytes(raw: bytes) -> bytes:
    text = raw.decode('utf-8-sig')
    physical = split_universal_lines(text)
    while physical and physical[-1] == '':
        physical.pop()
    logical = unfold_lines(physical)
    folded: list[str] = []
    for line in logical:
        folded.extend(fold_line(line))
    return ('\r\n'.join(folded) + '\r\n').encode('utf-8')


def find_value_colon(line: str) -> int:
    quoted = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == '\\':
            escaped = True
            continue
        if ch == '"':
            quoted = not quoted
        elif ch == ':' and not quoted:
            return i
    return -1


def split_unquoted(s: str, sep: str) -> list[str]:
    parts: list[str] = []
    quoted = False
    escaped = False
    start = 0
    for i, ch in enumerate(s):
        if escaped:
            escaped = False
            continue
        if ch == '\\':
            escaped = True
            continue
        if ch == '"':
            quoted = not quoted
        elif ch == sep and not quoted:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return parts


def parse_property(line: str) -> Property:
    colon = find_value_colon(line)
    if colon <= 0:
        raise ValidationError(f'Content line has no valid property/value separator: {line!r}')
    head, value = line[:colon], line[colon + 1:]
    pieces = split_unquoted(head, ';')
    name = pieces[0].upper()
    if not PROPERTY_NAME_RE.match(name):
        raise ValidationError(f'Invalid property name {name!r}')
    params: list[tuple[str, str]] = []
    for p in pieces[1:]:
        if '=' not in p:
            raise ValidationError(f'Invalid parameter (missing =): {p!r} in {line!r}')
        k, v = p.split('=', 1)
        k = k.upper()
        if not PARAM_NAME_RE.match(k) or not v:
            raise ValidationError(f'Invalid parameter {p!r} in {line!r}')
        params.append((k, v))
    return Property(name, tuple(params), value, line)


def validate_line_endings(path: Path, raw: bytes, errors: list[str]) -> None:
    if raw.startswith(b'\xef\xbb\xbf'):
        errors.append(f'{path}: UTF-8 BOM is not allowed')
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        errors.append(f'{path}: invalid UTF-8: {e}')
        return
    for i, b in enumerate(raw):
        if b == 0x0A and (i == 0 or raw[i - 1] != 0x0D):
            errors.append(f'{path}: bare LF detected; RFC 5545 requires CRLF')
            break
        if b == 0x0D and (i + 1 >= len(raw) or raw[i + 1] != 0x0A):
            errors.append(f'{path}: bare CR detected; RFC 5545 requires CRLF')
            break
    if not raw.endswith(b'\r\n'):
        errors.append(f'{path}: file must end with CRLF')


def validate_physical_lines(path: Path, raw: bytes, errors: list[str]) -> list[str]:
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return []
    lines = text.split('\r\n')
    if lines and lines[-1] == '':
        lines.pop()
    for n, line in enumerate(lines, 1):
        length = utf8_len(line)
        if length > 75:
            errors.append(f'{path}:{n}: physical line is {length} octets (>75)')
        if '\x00' in line:
            errors.append(f'{path}:{n}: NUL byte is not allowed')
    return lines


def validate_datetime_value(prop: Property, context: str, errors: list[str]) -> None:
    value_type = (prop.param('VALUE') or '').upper()
    v = prop.value
    if value_type == 'DATE':
        if not DATE_RE.match(v):
            errors.append(f'{context}: {prop.name};VALUE=DATE must be YYYYMMDD, got {v!r}')
    elif prop.name in {'DTSTAMP', 'LAST-MODIFIED'}:
        if not UTC_DT_RE.match(v):
            errors.append(f'{context}: {prop.name} must be UTC YYYYMMDDTHHMMSSZ, got {v!r}')
    elif prop.name in {'DTSTART', 'DTEND'}:
        if not (UTC_DT_RE.match(v) or LOCAL_DT_RE.match(v)):
            errors.append(f'{context}: {prop.name} must be DATE-TIME or VALUE=DATE, got {v!r}')


def event_signature(lines: list[str]) -> str:
    return '\n'.join(lines)


def validate_file(path: Path) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    raw = path.read_bytes()
    validate_line_endings(path, raw, errors)
    physical = validate_physical_lines(path, raw, errors)
    if not physical:
        return errors, {}
    try:
        logical = unfold_lines(physical)
    except ValidationError as e:
        errors.append(f'{path}: {e}')
        return errors, {}

    stack: list[str] = []
    calendar_props: list[Property] = []
    current_event_lines: list[str] | None = None
    current_event_props: list[Property] = []
    current_alarm_props: list[Property] | None = None
    events: dict[str, str] = {}

    for idx, line in enumerate(logical, 1):
        if not line:
            errors.append(f'{path}: logical line {idx}: blank content line')
            continue
        if line.startswith('BEGIN:'):
            component = line[6:].upper()
            if component not in {'VCALENDAR', 'VEVENT', 'VALARM'}:
                errors.append(f'{path}: unsupported component BEGIN:{component}')
            if component == 'VCALENDAR' and stack:
                errors.append(f'{path}: VCALENDAR must be top-level')
            if component == 'VEVENT' and stack != ['VCALENDAR']:
                errors.append(f'{path}: VEVENT must be directly inside VCALENDAR')
            if component == 'VALARM' and (not stack or stack[-1] != 'VEVENT'):
                errors.append(f'{path}: VALARM must be inside VEVENT')
            stack.append(component)
            if component == 'VEVENT':
                current_event_lines = [line]
                current_event_props = []
            elif component == 'VALARM':
                current_alarm_props = []
                if current_event_lines is not None:
                    current_event_lines.append(line)
            continue

        if line.startswith('END:'):
            component = line[4:].upper()
            if not stack or stack[-1] != component:
                errors.append(f'{path}: mismatched END:{component}; stack={stack}')
                continue
            if current_event_lines is not None:
                current_event_lines.append(line)
            if component == 'VALARM':
                props = current_alarm_props or []
                names = [p.name for p in props]
                if 'ACTION' not in names or 'TRIGGER' not in names:
                    errors.append(f'{path}: VALARM requires ACTION and TRIGGER')
                action = next((p.value.upper() for p in props if p.name == 'ACTION'), None)
                if action == 'DISPLAY' and 'DESCRIPTION' not in names:
                    errors.append(f'{path}: DISPLAY VALARM requires DESCRIPTION')
                current_alarm_props = None
            elif component == 'VEVENT':
                by_name: dict[str, list[Property]] = {}
                for p in current_event_props:
                    by_name.setdefault(p.name, []).append(p)
                for required in ('UID', 'DTSTAMP', 'DTSTART', 'SUMMARY'):
                    if len(by_name.get(required, [])) != 1:
                        errors.append(f'{path}: VEVENT requires exactly one {required}')
                uid = by_name.get('UID', [Property('UID', (), '', '')])[0].value.strip()
                if not uid:
                    errors.append(f'{path}: VEVENT UID must not be empty')
                elif uid in events:
                    errors.append(f'{path}: duplicate UID {uid}')
                else:
                    events[uid] = event_signature(current_event_lines or [])

                for name in ('DTSTAMP', 'LAST-MODIFIED', 'DTSTART', 'DTEND'):
                    for p in by_name.get(name, []):
                        validate_datetime_value(p, f'{path} UID={uid}', errors)

                dtstart = by_name.get('DTSTART', [None])[0]
                dtend = by_name.get('DTEND', [None])[0]
                if dtstart and dtend:
                    ds_date = (dtstart.param('VALUE') or '').upper() == 'DATE'
                    de_date = (dtend.param('VALUE') or '').upper() == 'DATE'
                    if ds_date != de_date:
                        errors.append(f'{path} UID={uid}: DTSTART/DTEND VALUE types must match')
                    if ds_date and DATE_RE.match(dtstart.value) and DATE_RE.match(dtend.value) and dtend.value <= dtstart.value:
                        errors.append(f'{path} UID={uid}: all-day DTEND must be exclusive and later than DTSTART')

                for url_prop in by_name.get('URL', []):
                    parsed = urlparse(url_prop.value)
                    if parsed.scheme not in {'https', 'http'} or not parsed.netloc:
                        errors.append(f'{path} UID={uid}: invalid URL {url_prop.value!r}')

                current_event_lines = None
                current_event_props = []
            stack.pop()
            continue

        try:
            prop = parse_property(line)
        except ValidationError as e:
            errors.append(f'{path}: logical line {idx}: {e}')
            continue

        if current_event_lines is not None:
            current_event_lines.append(line)
        if current_alarm_props is not None:
            current_alarm_props.append(prop)
        elif stack and stack[-1] == 'VEVENT':
            current_event_props.append(prop)
        elif stack and stack[-1] == 'VCALENDAR':
            calendar_props.append(prop)
        else:
            errors.append(f'{path}: property outside supported component: {line!r}')

    if stack:
        errors.append(f'{path}: unclosed component(s): {stack}')

    by_name: dict[str, list[Property]] = {}
    for p in calendar_props:
        by_name.setdefault(p.name, []).append(p)
    version = by_name.get('VERSION', [])
    prodid = by_name.get('PRODID', [])
    if len(version) != 1 or version[0].value != '2.0':
        errors.append(f'{path}: VCALENDAR requires VERSION:2.0 exactly once')
    if len(prodid) != 1 or not prodid[0].value:
        errors.append(f'{path}: VCALENDAR requires non-empty PRODID exactly once')
    return errors, events


def validate_sync(files_to_events: dict[Path, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    global_path = Path('calendars/fortnite-paris.ics')
    updates_path = Path('calendars/fortnite-updates-france.ics')
    competitive_path = Path('calendars/fortnite-competitive-france.ics')
    if not all(p in files_to_events for p in (global_path, updates_path, competitive_path)):
        return errors
    global_events = files_to_events[global_path]
    updates = files_to_events[updates_path]
    competitive = files_to_events[competitive_path]
    specialist_union = set(updates) | set(competitive)
    if set(global_events) != specialist_union:
        missing_global = sorted(specialist_union - set(global_events))
        extra_global = sorted(set(global_events) - specialist_union)
        if missing_global:
            errors.append(f'Sync: specialist UID(s) missing from global: {missing_global}')
        if extra_global:
            errors.append(f'Sync: global UID(s) missing from specialists: {extra_global}')
    for path, events in ((updates_path, updates), (competitive_path, competitive)):
        for uid, sig in events.items():
            if uid in global_events and global_events[uid] != sig:
                errors.append(f'Sync: UID {uid} differs between {path} and global calendar')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Strict RFC 5545 / Apple-oriented validator for Fortnite iCalendar feeds.')
    parser.add_argument('files', nargs='*', type=Path, default=DEFAULT_FILES)
    parser.add_argument('--fix', action='store_true', help='Normalize UTF-8, CRLF, final CRLF, and 75-octet folding before validation.')
    args = parser.parse_args()
    files: list[Path] = args.files or DEFAULT_FILES
    missing = [p for p in files if not p.exists()]
    if missing:
        for p in missing:
            print(f'ERROR: missing {p}', file=sys.stderr)
        return 2
    if args.fix:
        for p in files:
            p.write_bytes(normalize_ics_bytes(p.read_bytes()))
            print(f'FIXED: {p}')
    all_errors: list[str] = []
    files_to_events: dict[Path, dict[str, str]] = {}
    for p in files:
        errs, events = validate_file(p)
        all_errors.extend(errs)
        files_to_events[p] = events
    all_errors.extend(validate_sync(files_to_events))
    if all_errors:
        print('Fortnite iCalendar validation FAILED:', file=sys.stderr)
        for e in all_errors:
            print(f' - {e}', file=sys.stderr)
        return 1
    total_events = sum(len(v) for v in files_to_events.values())
    print(f'Fortnite iCalendar validation OK: {len(files)} files, {total_events} event copies checked.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
