#!/usr/bin/env python3
"""Keep subscribed Pokémon feeds readable without changing event dates or UIDs."""
import argparse
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / 'calendars/pokemon-presentation-policy.json'
EVENT = re.compile(r'BEGIN:VEVENT\n.*?\nEND:VEVENT\n?', re.S)


def policy():
    return json.loads(POLICY_PATH.read_text(encoding='utf-8'))


def logical(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'\n[ \t]', '', text)


def properties(event):
    # Alarm descriptions are not event descriptions.
    result = {}
    depth = 0
    for line in logical(event).splitlines():
        if line.startswith('BEGIN:'):
            depth += 1
        elif line.startswith('END:'):
            depth -= 1
        elif depth == 1 and ':' in line:
            key, value = line.split(':', 1)
            result[key.split(';')[0]] = value
    return result


def plain(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower())
                   if not unicodedata.combining(c))


def excluded(event):
    props = properties(event)
    # Do not exclude a physical/TCG event for an incidental mention in its notes.
    identity = plain(' '.join(props.get(k, '') for k in ('UID', 'SUMMARY', 'CATEGORIES', 'URL')))
    products = [r'[\s_-]*'.join(re.escape(word) for word in plain(name).split())
                for name in policy()['excluded_products']]
    return bool(re.search(r'(?:' + '|'.join(products) + r')\b|pokemongolive\.com|pokemongo\.com|pokemonsleep\.net', identity)
                or re.search(r'^\W*go\s*[—–-]', plain(props.get('SUMMARY', ''))))


def clean_title(title, status=''):
    # Remove decorative prefix only; preserve names, quantities, cities and meaning.
    uncertain = status == 'TENTATIVE' or '🟡' in title or '🟠' in title
    title = re.sub(r'^[^\w\[]+', '', title).strip()
    title = re.sub(r'^ℹ\ufe0f?\s*[^\w\[]*', '', title).strip()
    if uncertain and '[À confirmer]' not in title:
        title += ' [À confirmer]'
    return title


def fold(line):
    parts, chunk = [], ''
    for char in line:
        if len((chunk + char).encode('utf-8')) > 75:
            trimmed = chunk.rstrip(' ')
            parts.append(trimmed)
            chunk = ' ' + chunk[len(trimmed):]
        chunk += char
    return '\n'.join(parts + [chunk])


def set_property(event, key, value):
    # Replace only direct VEVENT properties, never those of VALARM.
    lines = event.splitlines()
    depth = 0
    for i, line in enumerate(lines):
        if line.startswith('BEGIN:'):
            depth += 1
        elif line.startswith('END:'):
            depth -= 1
        elif depth == 1 and line.startswith(key + ':'):
            lines[i] = f'{key}:{value}'
            return '\n'.join(lines)
    lines.insert(1, f'{key}:{value}')
    return '\n'.join(lines)


def present_event(event, stamp=None):
    original = logical(event).strip()
    props = properties(original)
    title = clean_title(props.get('SUMMARY', ''), props.get('STATUS'))
    event = set_property(original, 'SUMMARY', title)
    # Subscription information does not reserve the user's personal availability.
    event = set_property(event, 'TRANSP', 'TRANSPARENT')
    if event != original:
        stamp = stamp or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        event = set_property(event, 'SEQUENCE', str(int(props.get('SEQUENCE', '0')) + 1))
        event = set_property(event, 'LAST-MODIFIED', stamp)
        event = set_property(event, 'DTSTAMP', stamp)
    return '\n'.join(fold(line) if line.startswith('SUMMARY:') else line for line in event.splitlines())


def assert_allowed(event):
    if excluded(event):
        raise SystemExit('Pokémon GO/Sleep excluded by user preference (pokemon-presentation-policy.json)')
    uid = properties(event).get('UID')
    for keeper, aliases in policy()['duplicate_aliases'].items():
        if uid in aliases:
            raise SystemExit(f'Duplicate event UID: update the existing canonical UID {keeper}')


def clean_calendar(text, stamp=None):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    matches = list(EVENT.finditer(text))
    events = [m.group(0).strip() for m in matches]
    present = {properties(e).get('UID') for e in events}
    aliases = {alias for keeper, values in policy()['duplicate_aliases'].items()
               if keeper in present for alias in values}
    kept, removed = [], []
    for event in events:
        uid = properties(event).get('UID')
        if excluded(event) or uid in aliases:
            removed.append(uid)
        else:
            kept.append(present_event(event, stamp))
    kept.sort(key=lambda e: (properties(e).get('DTSTART', ''), properties(e).get('UID', '')))
    if matches:
        # Preserve calendar headers, timezone components and trailers verbatim.
        chunks, end = [], 0
        for match in matches:
            chunks.append(text[end:match.start()])
            end = match.end()
        chunks.append(text[end:])
        base = ''.join(chunks)
        result = base.replace('END:VCALENDAR', '\n'.join(kept) + '\nEND:VCALENDAR')
    else:
        result = text
    return result.replace('\n', '\r\n'), removed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    dirty = False
    for name in policy()['feeds']:
        path = ROOT / name
        raw = path.read_bytes()
        result, removed = clean_calendar(raw.decode('utf-8'))
        if result.encode('utf-8') != raw:
            dirty = True
            print(f'{name}: {len(removed)} removed; presentation updated')
            if not args.check:
                path.write_bytes(result.encode('utf-8'))
    if args.check and dirty:
        raise SystemExit('Run python scripts/pokemon_calendar_presentation.py')


if __name__ == '__main__':
    main()
