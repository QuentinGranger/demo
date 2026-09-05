from pathlib import Path
import re

PATH = Path('calendars/pokemon-paris.ics')
text = PATH.read_text(encoding='utf-8')
newline = '\r\n' if '\r\n' in text else '\n'

# Canonical events to remove because they are either superseded duplicates or
# future public-preorder alerts invalidated by the retailer's current public
# position (Pokémon 30th public preorders not opening / product pages closed).
REMOVE_UIDS = {
    'pokemon-30ans-collection-classeur-q4-2026@openai',
    'ff9a2a29-5818-4b14-bec0-38e9a74c1b2d@openai',
    'pokemon-fnac-beaune-30ans-20260919@openai',
    'preorder-guizette-etb-30ans-20260906@openai',
    'preorder-guizette-bundle-30ans-20260919@openai',
    'preorder-guizette-classeur-30ans-20260920@openai',
    'preorder-guizette-premium-30ans-20261004@openai',
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

# Re-parent any surviving legacy wave-2 children if they exist. This is
# idempotent and harmless after the invalidated Guizette public alerts vanish.
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
        raise SystemExit(f'Safety check failed: invalidated/superseded UID still present: {uid}')

# Global VCALENDAR and UID uniqueness validation.
if new_text.count('BEGIN:VCALENDAR') != 1 or new_text.count('END:VCALENDAR') != 1:
    raise SystemExit('Safety check failed: VCALENDAR envelope invalid')
uids = re.findall(r'^UID:(.+)$', new_text, flags=re.M)
if len(uids) != len(set(uids)):
    dupes = sorted({u for u in uids if uids.count(u) > 1})
    raise SystemExit(f'Safety check failed: duplicate UIDs remain: {dupes}')

# Preserve original line-ending policy.
PATH.write_text(new_text.replace('\n', newline), encoding='utf-8', newline='')
print('Removed invalidated/superseded events:', ', '.join(sorted(removed)))
print('VEVENT count:', new_text.count('BEGIN:VEVENT'))
print('UID count:', len(uids))
