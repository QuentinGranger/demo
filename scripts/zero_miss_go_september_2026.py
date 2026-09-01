from pathlib import Path
import subprocess

P = Path('calendars/pokemon-paris.ics')
BASELINE = '90fdb13725ae9895c552e6b2805ed87ed586f8fb'

EVENTS = [
'''BEGIN:VEVENT\r\nUID:pokemon-go-pass-september-20260908@openai\r\nDTSTAMP:20260901T124614Z\r\nLAST-MODIFIED:20260901T124614Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nDTSTART;TZID=Europe/Paris:20260908T100000\r\nDTEND;TZID=Europe/Paris:20261006T100000\r\nSUMMARY:⭐ ✅ Pokémon GO — Passe GO septembre\r\nLOCATION:En ligne — Pokémon GO\r\nDESCRIPTION:Événement officiel Pokémon GO. Passe GO de septembre disponible du 8 septembre 2026 à 10:00 au 6 octobre 2026 à 10:00, heure locale. Récompenses incluant notamment Latios. Les récompenses du Passe expirent le 8 octobre 2026 à 10:00, heure locale. Source officielle : https://pokemongo.com/fr/news/go-pass-september-2026\r\nURL:https://pokemongo.com/fr/news/go-pass-september-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Passe GO,Événement numérique\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:Passe GO septembre demain à 10h\r\nEND:VALARM\r\nEND:VEVENT\r\n''',
'''BEGIN:VEVENT\r\nUID:pokemon-go-mega-squads-20260908@openai\r\nDTSTAMP:20260901T124614Z\r\nLAST-MODIFIED:20260901T124614Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nDTSTART;TZID=Europe/Paris:20260908T100000\r\nDTEND;TZID=Europe/Paris:20260914T200000\r\nSUMMARY:⭐ ✅ Pokémon GO — Hordes Méga\r\nLOCATION:En ligne — Pokémon GO\r\nDESCRIPTION:Événement officiel Pokémon GO du 8 septembre 2026 à 10:00 au 14 septembre 2026 à 20:00, heure locale. Débuts de Grondogue et Dogrino, première disponibilité chromatique de Flamenroule, nouveau Super Niveau Max pour certaines Méga-Évolutions et Passe GO dédié. Source officielle : https://pokemongo.com/fr/news/mega-squads-2026\r\nURL:https://pokemongo.com/fr/news/mega-squads-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Événement,Méga-Évolution\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:Hordes Méga commence demain à 10h\r\nEND:VALARM\r\nEND:VEVENT\r\n''',
'''BEGIN:VEVENT\r\nUID:pokemon-go-community-day-classic-gible-20260912@openai\r\nDTSTAMP:20260901T124614Z\r\nLAST-MODIFIED:20260901T124614Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nDTSTART;TZID=Europe/Paris:20260912T140000\r\nDTEND;TZID=Europe/Paris:20260912T170000\r\nSUMMARY:⭐ ✅ Pokémon GO — Community Day Classic Griknot\r\nLOCATION:France — Pokémon GO\r\nDESCRIPTION:Classique de la Journée Communauté officiel Pokémon GO le 12 septembre 2026 de 14:00 à 17:00, heure locale. Griknot à l'affiche. Faire évoluer Carmache avant 21:00 permet d'obtenir Carchacrok avec Telluriforce. Des événements communautaires locaux peuvent offrir une Étude ponctuelle supplémentaire. Source officielle : https://pokemongo.com/fr/news/communitydayclassic-gible-september-2026\r\nURL:https://pokemongo.com/fr/news/communitydayclassic-gible-september-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Community Day,Événement\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:Community Day Classic Griknot demain à 14h\r\nEND:VALARM\r\nEND:VEVENT\r\n'''
]

# Restore the exact pre-patch canonical bytes, avoiding any newline reformatting.
base = subprocess.check_output(['git', 'show', f'{BASELINE}:calendars/pokemon-paris.ics'])
marker = b'END:VCALENDAR'
if not base.startswith(b'BEGIN:VCALENDAR') or base.count(marker) != 1:
    raise SystemExit('Invalid baseline VCALENDAR')

out = base
for event in EVENTS:
    uid = next(line for line in event.split('\r\n') if line.startswith('UID:')).encode('utf-8')
    if uid in out:
        continue
    idx = out.rfind(marker)
    out = out[:idx] + event.encode('utf-8') + out[idx:]

norm = out.replace(b'\r\n', b'\n')
uids = [line[4:] for line in norm.split(b'\n') if line.startswith(b'UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
if out.count(b'BEGIN:VCALENDAR') != 1 or out.count(b'END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR bounds after patch')

current = P.read_bytes()
if out != current:
    P.write_bytes(out)
    print('calendar repaired and patched byte-preserving')
else:
    print('no business change')
