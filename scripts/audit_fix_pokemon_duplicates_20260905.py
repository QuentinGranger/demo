from pathlib import Path
import re

PATH = Path('calendars/pokemon-paris.ics')
text = PATH.read_text(encoding='utf-8')
newline = '\r\n' if '\r\n' in text else '\n'

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

# Remove RELATED-TO relations pointing at events that are now absent.
cleaned = []
for line in out:
    if line.startswith('RELATED-TO;') and ':' in line:
        target = line.split(':', 1)[1]
        if target in REMOVE_UIDS:
            continue
    cleaned.append(line)
out = cleaned

new_text = '\n'.join(out)

# If any valid surviving legacy child ever remains, point it to the canonical wave.
legacy_parent = 'RELATED-TO;RELTYPE=PARENT:ff9a2a29-5818-4b14-bec0-38e9a74c1b2d@openai'
new_parent = 'RELATED-TO;RELTYPE=PARENT:pokemon-jcc-30ans-wave2-fr-20261002@openai'
new_text = new_text.replace(legacy_parent, new_parent)

# Complete the canonical 16 September launch wave using the now-confirmed product set.
launch_uid = '74a1a108-68cd-4c81-b8f1-9206bfa31970@openai'
launch_match = re.search(
    r'BEGIN:VEVENT\n(?:(?!END:VEVENT).)*?UID:' + re.escape(launch_uid) + r'\n(?:(?!END:VEVENT).)*?END:VEVENT',
    new_text,
    flags=re.S,
)
if not launch_match:
    raise SystemExit('Safety check failed: canonical 16 September launch wave not found')
launch = launch_match.group(0)
launch = re.sub(r'^X-POKEMON-WAVE-COMPLETENESS:.*$', 'X-POKEMON-WAVE-COMPLETENESS:COMPLETE', launch, flags=re.M)
launch = re.sub(r'^X-POKEMON-WAVE-PRODUCT-COUNT:.*$', 'X-POKEMON-WAVE-PRODUCT-COUNT:5', launch, flags=re.M)
launch = re.sub(r'^X-POKEMON-WAVE-PREORDER-COUNT:.*$', 'X-POKEMON-WAVE-PREORDER-COUNT:0', launch, flags=re.M)
launch = re.sub(
    r'^X-POKEMON-WAVE-PRODUCTS:.*$',
    'X-POKEMON-WAVE-PRODUCTS:Coffret Dresseur d’Élite 30 ans|Coffret Nymphali-ex 30 ans|Coffret Amphinobi-ex 30 ans|Collection Poster 30 ans|Collection Autocollant réajustable 30 ans',
    launch,
    flags=re.M,
)
launch = re.sub(r'^X-POKEMON-WAVE-ITEM;STATE=CONFIRMED(?:;PREORDER=\d+)?:.*\n?', '', launch, flags=re.M)
insert_after = 'X-POKEMON-WAVE-PRODUCTS:Coffret Dresseur d’Élite 30 ans|Coffret Nymphali-ex 30 ans|Coffret Amphinobi-ex 30 ans|Collection Poster 30 ans|Collection Autocollant réajustable 30 ans\n'
items = (
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Coffret Dresseur d’Élite 30 ans\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Coffret Nymphali-ex 30 ans\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Coffret Amphinobi-ex 30 ans\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Collection Poster 30 ans\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Collection Autocollant réajustable 30 ans\n'
)
launch = launch.replace(insert_after, insert_after + items, 1)
launch = re.sub(r'^SEQUENCE:(\d+)$', lambda m: f'SEQUENCE:{int(m.group(1)) + 1}', launch, count=1, flags=re.M)
launch = re.sub(r'^LAST-MODIFIED:.*$', 'LAST-MODIFIED:20260905T183733Z', launch, count=1, flags=re.M)
launch = re.sub(
    r'^DESCRIPTION:.*?(?=\nURL:)',
    'DESCRIPTION:Priorité : ⭐ Important — sortie majeure de la gamme 30ᵉ Anniversaire.\\nFiabilité : ✅ Pokémon confirme la sortie mondiale du 16 septembre 2026 et sa page produits de septembre recoupe la vague de lancement.\\n📦 Checklist consolidée : Coffret Dresseur d’Élite 30 ans ; Coffret Nymphali-ex 30 ans ; Coffret Amphinobi-ex 30 ans ; Collection Poster 30 ans ; Collection Autocollant réajustable 30 ans.\\nLa précédente précommande Guizette du 6 septembre est invalidée et ne doit plus être présentée comme opportunité publique.\\nDATE_PRECISION=EXACT_DATE. Aucun horaire de vente global n’est inventé.\\nSource : https://www.pokemon.com/fr/actualites/decouvrez-tous-les-produits-du-jcc-pokemon-qui-sortiront-en-septembre-2026',
    launch,
    flags=re.S | re.M,
)
new_text = new_text[:launch_match.start()] + launch + new_text[launch_match.end():]

required_uids = [
    'pokemon-jcc-30ans-wave2-fr-20261002@openai',
    'fnac-beaune-pokemon-30-20260919@openai',
    launch_uid,
]
for uid in required_uids:
    count = new_text.count(f'UID:{uid}')
    if count != 1:
        raise SystemExit(f'Safety check failed: {uid} count={count}')

for uid in REMOVE_UIDS:
    if f'UID:{uid}' in new_text:
        raise SystemExit(f'Safety check failed: invalidated/superseded UID still present: {uid}')
    if re.search(r'^RELATED-TO;[^:]*:' + re.escape(uid) + r'$', new_text, flags=re.M):
        raise SystemExit(f'Safety check failed: orphan relation still points to {uid}')

if 'X-POKEMON-WAVE-COMPLETENESS:COMPLETE' not in launch or 'X-POKEMON-WAVE-PRODUCT-COUNT:5' not in launch:
    raise SystemExit('Safety check failed: launch wave completion patch missing')
for product in ['Coffret Nymphali-ex 30 ans', 'Coffret Amphinobi-ex 30 ans', 'Collection Poster 30 ans', 'Collection Autocollant réajustable 30 ans']:
    if product not in launch:
        raise SystemExit(f'Safety check failed: launch product missing: {product}')

if new_text.count('BEGIN:VCALENDAR') != 1 or new_text.count('END:VCALENDAR') != 1:
    raise SystemExit('Safety check failed: VCALENDAR envelope invalid')
uids = re.findall(r'^UID:(.+)$', new_text, flags=re.M)
if len(uids) != len(set(uids)):
    dupes = sorted({u for u in uids if uids.count(u) > 1})
    raise SystemExit(f'Safety check failed: duplicate UIDs remain: {dupes}')

# Check every RELATED-TO target against current UIDs to prevent hidden orphans.
uid_set = set(uids)
relations = re.findall(r'^RELATED-TO;[^:]*:(.+)$', new_text, flags=re.M)
orphans = sorted({target for target in relations if target not in uid_set})
if orphans:
    raise SystemExit(f'Safety check failed: unrelated orphan RELATED-TO targets remain: {orphans}')

PATH.write_text(new_text.replace('\n', newline), encoding='utf-8', newline='')
print('Removed invalidated/superseded events:', ', '.join(sorted(removed)))
print('Launch wave patched to COMPLETE with 5 products')
print('VEVENT count:', new_text.count('BEGIN:VEVENT'))
print('UID count:', len(uids))
print('RELATED-TO orphan count: 0')
