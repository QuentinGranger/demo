#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

ALLOWED_CALENDARS = {
    'calendars/pokemon-paris.ics',
    'calendars/pokemon-tcg-france.ics',
}
DEFAULT_CALENDAR = 'calendars/pokemon-paris.ics'


def blob_sha(data: bytes) -> str:
    hdr = f'blob {len(data)}\0'.encode()
    return hashlib.sha1(hdr + data).hexdigest()


def resolve_calendar(req: dict) -> Path:
    calendar_path = req.get('calendar_path', DEFAULT_CALENDAR)
    if calendar_path not in ALLOWED_CALENDARS:
        raise SystemExit(f'calendar_path not allowed: {calendar_path}')
    return Path(calendar_path)


def read_calendar(cal: Path):
    raw = cal.read_bytes()
    text = raw.decode('utf-8')
    return raw, text


def validate_calendar(text: str):
    if not text.startswith('BEGIN:VCALENDAR') or not text.rstrip().endswith('END:VCALENDAR'):
        raise SystemExit('invalid calendar bounds')
    if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
        raise SystemExit('invalid VCALENDAR multiplicity')
    events = re.findall(r'BEGIN:VEVENT\r?\n.*?\r?\nEND:VEVENT', text, flags=re.S)
    uids = []
    for ev in events:
        m = re.search(r'(?m)^UID:(.+)$', ev)
        if not m:
            raise SystemExit('VEVENT missing UID')
        uids.append(m.group(1).rstrip('\r'))
    if len(uids) != len(set(uids)):
        raise SystemExit('duplicate UID detected')
    return events


def uid_of(event: str) -> str:
    m = re.search(r'(?m)^UID:(.+)$', event)
    if not m:
        raise SystemExit('request event missing UID')
    return m.group(1).rstrip('\r')


def normalize_event(event: str) -> str:
    event = event.replace('\r\n', '\n').replace('\r', '\n').strip('\n')
    if not event.startswith('BEGIN:VEVENT\n') or not event.endswith('\nEND:VEVENT'):
        raise SystemExit('event must be a complete VEVENT')
    if event.count('BEGIN:VEVENT') != 1 or event.count('END:VEVENT') != 1:
        raise SystemExit('nested/multiple VEVENT not allowed')
    return event.replace('\n', '\r\n')


def find_event_span(text: str, uid: str):
    pat = re.compile(r'BEGIN:VEVENT\r?\n.*?\r?\nEND:VEVENT(?:\r?\n)?', re.S)
    for m in pat.finditer(text):
        ev = m.group(0)
        if re.search(rf'(?m)^UID:{re.escape(uid)}\r?$', ev):
            return m.start(), m.end(), ev.rstrip('\r\n')
    return None


def bump_sequence(new_event: str, old_event: str):
    old_m = re.search(r'(?m)^SEQUENCE:(\d+)\r?$', old_event)
    old_seq = int(old_m.group(1)) if old_m else 0
    if re.search(r'(?m)^SEQUENCE:\d+\r?$', new_event):
        return re.sub(r'(?m)^SEQUENCE:\d+\r?$', f'SEQUENCE:{old_seq + 1}', new_event, count=1)
    lines = new_event.split('\r\n')
    insert_at = 2 if len(lines) > 2 else 1
    lines.insert(insert_at, f'SEQUENCE:{old_seq + 1}')
    return '\r\n'.join(lines)


def semantic(event: str):
    lines = []
    for ln in event.replace('\r\n', '\n').split('\n'):
        if ln.startswith(('DTSTAMP:', 'LAST-MODIFIED:', 'SEQUENCE:')):
            continue
        lines.append(ln)
    return '\n'.join(lines).strip()


def apply_request(req_path: Path):
    req = json.loads(req_path.read_text(encoding='utf-8'))
    cal = resolve_calendar(req)
    raw, text = read_calendar(cal)
    validate_calendar(text)

    expected = req.get('expected_calendar_blob_sha')
    actual = blob_sha(raw)
    if expected and expected != actual:
        raise SystemExit(f'stale calendar: expected {expected}, got {actual}')

    op = req['operation']
    uid = req.get('uid')
    changed = False

    if op in ('add', 'upsert', 'update'):
        event = normalize_event(req['event'])
        event_uid = uid_of(event)
        if uid and uid != event_uid:
            raise SystemExit('uid field does not match VEVENT UID')
        uid = event_uid
        span = find_event_span(text, uid)

        if op == 'add' and span:
            raise SystemExit(f'UID already exists: {uid}')
        if op == 'update' and not span:
            raise SystemExit(f'UID not found for update: {uid}')

        if span:
            start, end, old = span
            if semantic(old) == semantic(event):
                print(f'CALENDAR_PATH={cal.as_posix()}')
                print('No business change')
                return False
            event = bump_sequence(event, old)
            text = text[:start] + event + '\r\n' + text[end:]
            changed = True
        else:
            marker = 'END:VCALENDAR'
            pos = text.rfind(marker)
            if pos < 0:
                raise SystemExit('END:VCALENDAR missing')
            prefix = text[:pos]
            if prefix and not prefix.endswith(('\r\n', '\n')):
                prefix += '\r\n'
            text = prefix + event + '\r\n' + marker + text[pos + len(marker):]
            changed = True

    elif op == 'delete':
        if not uid:
            raise SystemExit('delete requires uid')
        span = find_event_span(text, uid)
        if not span:
            print(f'CALENDAR_PATH={cal.as_posix()}')
            print('No business change')
            return False
        start, end, _ = span
        text = text[:start] + text[end:]
        changed = True
    else:
        raise SystemExit(f'unsupported operation: {op}')

    # Canonicalize line endings only at final write; untouched logical lines stay unchanged.
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
    validate_calendar(text)

    expected_uid = uid if op != 'delete' else None
    if expected_uid and not find_event_span(text, expected_uid):
        raise SystemExit('post-write expected UID missing')
    if op == 'delete' and find_event_span(text, uid):
        raise SystemExit('post-delete UID still present')

    if changed:
        cal.write_bytes(text.encode('utf-8'))

    print(f'CALENDAR_PATH={cal.as_posix()}')
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('request')
    args = ap.parse_args()
    changed = apply_request(Path(args.request))
    print('CHANGED=1' if changed else 'CHANGED=0')


if __name__ == '__main__':
    main()
