from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
raw = p.read_text(encoding='utf-8')

old = (
    'X-POKEMON-WAVE-COMPLETENESS:PARTIAL\n'
    'X-POKEMON-WAVE-PRODUCT-COUNT:2\n'
    'X-POKEMON-WAVE-PREORDER-COUNT:1\n'
    'X-POKEMON-WAVE-PRODUCTS:Extension JCC 30e Anniversaire|ETB 30 ans\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Extension JCC 30e Anniversaire\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED;PREORDER=20260906:ETB 30 ans\n'
)
new = (
    'X-POKEMON-WAVE-COMPLETENESS:COMPLETE\n'
    'X-POKEMON-WAVE-PRODUCT-COUNT:6\n'
    'X-POKEMON-WAVE-PREORDER-COUNT:1\n'
    'X-POKEMON-WAVE-PRODUCTS:Extension JCC 30e Anniversaire|Coffret Dresseur d’élite 30e Anniversaire|Collection poster 30e Anniversaire|Collection autocollant réajustable 30e Anniversaire|Coffret 30e Anniversaire Pokémon-ex|Boîte 30e Anniversaire Pokémon-ex\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Extension JCC 30e Anniversaire\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED;PREORDER=20260906:Coffret Dresseur d’élite 30e Anniversaire\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Collection poster 30e Anniversaire\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Collection autocollant réajustable 30e Anniversaire\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Coffret 30e Anniversaire Pokémon-ex\n'
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Boîte 30e Anniversaire Pokémon-ex\n'
)

# Normalize temporarily so matching is robust, then restore RFC5545 CRLF.
s = raw.replace('\r\n', '\n')
if new in s:
    raise SystemExit(0)
if old not in s:
    raise SystemExit('Target 30th launch wave block not found; refusing unsafe write')
s = s.replace(old, new, 1)

# Reconcile human-readable checklist in the same VEVENT only.
s = s.replace(
    '✅ Extension JCC 30e Anniversaire\\\n✅ ETB 30 ans — 🔔 précommande Guizette le 6 septembre\\\nComplétude : liste partielle des produits de lancement actuellement suivis ; aucun produit non nommé n\'est compté.',
    '✅ Extension JCC 30e Anniversaire\\\n✅ Coffret Dresseur d’élite 30e Anniversaire — 🔔 précommande Guizette le 6 septembre\\\n✅ Collection poster 30e Anniversaire\\\n✅ Collection autocollant réajustable 30e Anniversaire\\\n✅ Coffret 30e Anniversaire Pokémon-ex\\\n✅ Boîte 30e Anniversaire Pokémon-ex\\\nComplétude : vague de lancement du 16 septembre réconciliée avec la gamme officiellement confirmée par The Pokémon Company International.',
    1,
)

# Add source attribution only if absent in this event description.
needle = 'Rappels calendrier : J-14, J-7, J-3 et J-1 — vérifier précommandes, compte client, paiement et disponibilité.'
source = 'Source gamme officielle : https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon\\n'
if source not in s and needle in s:
    s = s.replace(needle, source + needle, 1)

if s.count('BEGIN:VCALENDAR') != 1 or s.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR bounds')

uids = []
for line in s.split('\n'):
    if line.startswith('UID:'):
        uid = line[4:]
        if uid in uids:
            raise SystemExit(f'Duplicate UID: {uid}')
        uids.append(uid)

p.write_bytes(s.replace('\n', '\r\n').encode('utf-8'))
