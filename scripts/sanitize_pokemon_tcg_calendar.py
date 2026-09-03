#!/usr/bin/env python3
from pathlib import Path
import re

CAL = Path('calendars/pokemon-tcg-france.ics')

PROP_RE = re.compile(r'^[A-Z0-9-]+(?:;[^:]*)?:')


def event_uids(text: str):
    return re.findall(r'(?m)^UID:([^\r\n]+)', text)


def sanitize(text: str) -> str:
    # Normalize to logical LF first.
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('DESCRIPTION:') and line.endswith('\\'):
            parts = [line[:-1]]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                # Stop at the next real iCalendar property/component line.
                if nxt.startswith(('BEGIN:', 'END:')) or PROP_RE.match(nxt):
                    break
                if nxt.endswith('\\'):
                    parts.append('\\n' + nxt[:-1])
                else:
                    parts.append('\\n' + nxt)
                i += 1
            out.append(''.join(parts))
            continue
        out.append(line)
        i += 1
    # Strip accidental trailing blank logical lines, then RFC5545 CRLF.
    while out and out[-1] == '':
        out.pop()
    return '\r\n'.join(out) + '\r\n'


def validate(text: str, before_uids):
    if not text.startswith('BEGIN:VCALENDAR\r\n'):
        raise SystemExit('VCALENDAR start invalid')
    if not text.endswith('END:VCALENDAR\r\n'):
        raise SystemExit('VCALENDAR end invalid')
    if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
        raise SystemExit('VCALENDAR multiplicity invalid')

    after_uids = event_uids(text)
    if after_uids != before_uids:
        raise SystemExit('UID set/order changed during sanitation')
    if len(after_uids) != len(set(after_uids)):
        raise SystemExit('duplicate UID detected')

    # Every unfolded physical line must be a property/component or an RFC fold.
    bad = []
    for n, ln in enumerate(text.split('\r\n'), start=1):
        if not ln:
            continue
        if ln[0] in (' ', '\t'):
            continue
        if ln.startswith(('BEGIN:', 'END:')):
            continue
        if PROP_RE.match(ln):
            continue
        bad.append((n, ln[:120]))
    if bad:
        sample = '; '.join(f'{n}:{s}' for n, s in bad[:8])
        raise SystemExit(f'non-RFC property lines remain: {sample}')

    required_uid = 'fnac-beaune-pokemon-30-20260919@openai'
    if required_uid not in after_uids:
        raise SystemExit('Fnac Beaune event missing after sanitation')


def main():
    raw = CAL.read_text(encoding='utf-8')
    before = event_uids(raw)
    cleaned = sanitize(raw)
    validate(cleaned, before)
    if cleaned.encode('utf-8') == CAL.read_bytes():
        print('No sanitation needed')
        return
    CAL.write_bytes(cleaned.encode('utf-8'))
    print(f'Sanitized calendar; preserved {len(before)} VEVENT UIDs')


if __name__ == '__main__':
    main()
