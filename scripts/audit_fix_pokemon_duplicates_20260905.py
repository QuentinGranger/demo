from pathlib import Path
import re

PATH = Path('calendars/pokemon-paris.ics')
text = PATH.read_text(encoding='utf-8')
newline = '\r\n' if '\r\n' in text else '\n'

# Canonical events to remove because they are superseded by stronger,
# retailer-independent consolidated events already present in the calendar.
REMOVE_UIDS = {
    'pokemon-30ans-collection-classeur-q4-2026@openai',
    'ff9a2a29-5818-4b14-bec0-38e9a74c1b2d@openai',
    'pokemon-fnac-beaune-30ans-20260919@openai',
}

lines = text.replace('\r\n', '\n').split('\n')
out = []
i = 0
removed = []
while i < len(lines):
    if lines[i] == 'BEGIN:VEVENT':
        j = i + 1
        uid = None
        while j < len(lines) and lines[j] != 'END:VEVENT':
            if lines[j].startswith('UID:'):
                uid = lines[j][4:]
            j += 1
        if j >= len(lines):
            raise SystemExit('Malformed ICS: VEVENT without END:VEVENT')
        if uid in REMOVE_UIDS:
            removed.append(uid)
            i = j + 1
            continue
        out.extend(lines[i:j+1])
        i = j + 1
        continue
    out.append(lines[i])
    i += 1

new_text = '\n'.join(out)

# Re-parent the existing Guizette preorder child events to the consolidated
# wave-2 event so removing the legacy tentative parent does not create orphans.
legacy_parent = 'RELATED-TO;RELTYPE=PARENT:ff9a2a29-5818-4b14-bec0-38e9a74c1b2d@openai'
new_parent = 'RELATED-TO;RELTYPE=PARENT:pokemon-jcc-30ans-wave2-fr-20261002@openai'
new_text = new_text.replace(legacy_parent, new_parent)

# Safety checks: canonical consolidated entries must exist exactly once.
required_uids = [
    'pokemon-jcc-30ans-wave2-fr-20261002@openai',
    'fnac-beaune-pokemon-30-20260919@openai',
]
for uid in required_uids:
    count = new_text.count(f'UID:{uid}')
    if count != 1:
        raise SystemExit(f'Safety check failed: {uid} count={count}')

for uid in REMOVE_UIDS:
    if f'UID:{uid}' in new_text:
        raise SystemExit(f'Safety check failed: superseded UID still present: {uid}')

# Two preorder child links should now target the canonical wave-2 parent.
if new_text.count(new_parent) < 2:
    raise SystemExit('Safety check failed: preorder children were not re-parented')

# Global VCALENDAR and UID uniqueness validation.
if new_text.count('BEGIN:VCALENDAR') != 1 or new_text.count('END:VCALENDAR') != 1:
    raise SystemExit('Safety check failed: VCALENDAR envelope invalid')
uids = re.findall(r'^UID:(.+)$', new_text, flags=re.M)
if len(uids) != len(set(uids)):
    dupes = sorted({u for u in uids if uids.count(u) > 1})
    raise SystemExit(f'Safety check failed: duplicate UIDs remain: {dupes}')

# Preserve original line-ending policy.
PATH.write_text(new_text.replace('\n', newline), encoding='utf-8', newline='')
print('Removed superseded events:', ', '.join(sorted(removed)))
print('VEVENT count:', new_text.count('BEGIN:VEVENT'))
print('UID count:', len(uids))
