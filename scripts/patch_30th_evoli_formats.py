from pathlib import Path

# trigger: 2026-09-03T01:02 Europe/Paris
p = Path('calendars/pokemon-paris.ics')
s = p.read_text(encoding='utf-8')
uid = 'UID:74a1a108-68cd-4c81-b8f1-9206bfa31970@openai\r\n'
start = s.index(uid)
end = s.index('END:VEVENT\r\n', start) + len('END:VEVENT\r\n')
e = s[start:end]
old_count = 'X-POKEMON-WAVE-PRODUCT-COUNT:8\r\n'
new_count = 'X-POKEMON-WAVE-PRODUCT-COUNT:10\r\n'
old_products = 'X-POKEMON-WAVE-PRODUCTS:Extension JCC 30e Anniversaire|Coffret Dresseur d’élite 30e Anniversaire|Collection poster 30e Anniversaire|Collection autocollant réajustable 30e Anniversaire|Coffret 30e Anniversaire Nymphali-ex|Coffret 30e Anniversaire Amphinobi-ex|Pokébox 30e Anniversaire Nymphali-ex|Pokébox 30e Anniversaire Amphinobi-ex\r\n'
new_products = 'X-POKEMON-WAVE-PRODUCTS:Extension JCC 30e Anniversaire|Coffret Dresseur d’élite 30e Anniversaire|Collection poster 30e Anniversaire|Collection autocollant réajustable 30e Anniversaire|Coffret 30e Anniversaire Nymphali-ex|Coffret 30e Anniversaire Amphinobi-ex|Pokébox 30e Anniversaire Nymphali-ex|Pokébox 30e Anniversaire Amphinobi-ex|Blister 2 boosters 30e Anniversaire Évoli|Collection K.O. 30e Anniversaire Évoli\r\n'
anchor = 'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Pokébox 30e Anniversaire Amphinobi-ex\r\n'
insert = anchor + 'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Blister 2 boosters 30e Anniversaire Évoli\r\nX-POKEMON-WAVE-ITEM;STATE=CONFIRMED;REF=COLKOME5.5:Collection K.O. 30e Anniversaire Évoli\r\n'
for x in (old_count, old_products, anchor):
    if x not in e:
        raise SystemExit(f'expected marker missing: {x!r}')
e = e.replace(old_count, new_count, 1).replace(old_products, new_products, 1).replace(anchor, insert, 1)
e = e.replace('DTSTAMP:20260819T025700Z\r\n', 'DTSTAMP:20260902T230249Z\r\n', 1)
e = e.replace('LAST-MODIFIED:20260830T051000Z\r\n', 'LAST-MODIFIED:20260902T230249Z\r\n', 1)
e = e.replace('SEQUENCE:12\r\n', 'SEQUENCE:13\r\n', 1)
old_desc = "DESCRIPTION:Correction ZERO MISS du 2 septembre 2026 : variantes Nymphali-ex et Amphinobi-ex séparées ; coffrets et Pokébox ne sont plus fusionnés.\\n"
new_desc = "DESCRIPTION:Correction ZERO MISS du 3 septembre 2026 : ajout des deux formats Évoli distincts du lancement (Blister 2 boosters et Collection K.O.) ; variantes Nymphali-ex/Amphinobi-ex restent séparées.\\n"
if old_desc in e:
    e = e.replace(old_desc, new_desc, 1)
s2 = s[:start] + e + s[end:]
if s2.count('UID:74a1a108-68cd-4c81-b8f1-9206bfa31970@openai') != 1:
    raise SystemExit('UID uniqueness failed')
if 'X-POKEMON-WAVE-PRODUCT-COUNT:10' not in e:
    raise SystemExit('count update failed')
if 'Blister 2 boosters 30e Anniversaire Évoli' not in e or 'Collection K.O. 30e Anniversaire Évoli' not in e:
    raise SystemExit('new products missing')
p.write_text(s2, encoding='utf-8', newline='')
