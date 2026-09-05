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


def blob_sha(data: bytes) -> str:
    hdr = f'blob {len(data)}\0'.encode()
    return hashlib.sha1(hdr + data).hexdigest()


def unfold(text: str) -> str:
    return re.sub(r'\r?\n[ \t]', '', text)


def event_blocks(text: str):
    return re.findall(r'BEGIN:VEVENT\r?\n.*?\r?\nEND:VEVENT', text, flags=re.S)


def event_uid(event: str):
    m = re.search(r'(?m)^UID:(.+?)\r?$', event)
    return m.group(1) if m else None


def compact_event(event: str, max_chars: int = 3500) -> str:
    lines = []
    for line in event.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if line.startswith(('UID:', 'DTSTART', 'DTEND', 'SUMMARY:', 'LOCATION:', 'URL:', 'X-POKEMON-PRODUCT-EAN:', 'X-POKEMON-PRODUCT-UPC:', 'X-POKEMON-DISTRIBUTOR-REFS:', 'X-POKEMON-USER-EFFECT:', 'CATEGORIES:')):
            lines.append(line)
    out = '\n'.join(lines)
    return out[:max_chars]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('request')
    args = ap.parse_args()

    req = json.loads(Path(args.request).read_text(encoding='utf-8'))
    cal_path = req.get('calendar_path', 'calendars/pokemon-paris.ics')
    if cal_path not in ALLOWED_CALENDARS:
        raise SystemExit(f'calendar_path not allowed: {cal_path}')

    cal = Path(cal_path)
    raw = cal.read_bytes()
    text = raw.decode('utf-8')
    if not text.startswith('BEGIN:VCALENDAR') or not text.rstrip().endswith('END:VCALENDAR'):
        raise SystemExit('invalid VCALENDAR bounds')

    events = event_blocks(text)
    uids = [event_uid(ev) for ev in events]
    if any(uid is None for uid in uids):
        raise SystemExit('VEVENT missing UID')
    if len(uids) != len(set(uids)):
        raise SystemExit('duplicate UID detected')

    uid_query = req.get('uid')
    terms = [str(x) for x in req.get('terms', []) if str(x).strip()]
    exact_matches = []
    if uid_query:
        exact_matches = [ev for ev in events if event_uid(ev) == uid_query]

    unfolded = unfold(text)
    term_results = []
    for term in terms:
        count = unfolded.casefold().count(term.casefold())
        matched_events = [ev for ev in events if term.casefold() in unfold(ev).casefold()]
        term_results.append({
            'term': term,
            'count': count,
            'event_uids': [event_uid(ev) for ev in matched_events[:20]],
            'truncated_event_uids': len(matched_events) > 20,
        })

    result = {
        'calendar_path': cal_path,
        'blob_sha': blob_sha(raw),
        'bytes': len(raw),
        'physical_lines': text.count('\n') + 1,
        'vevent_count': len(events),
        'uid_unique': len(uids) == len(set(uids)),
        'uid_query': uid_query,
        'uid_present': bool(exact_matches) if uid_query else None,
        'terms': term_results,
        'matching_event_excerpt': compact_event(exact_matches[0]) if exact_matches else None,
    }
    print('PROBE_RESULT=' + json.dumps(result, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
