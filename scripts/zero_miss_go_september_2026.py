from pathlib import Path

P = Path('calendars/pokemon-paris.ics')
text = P.read_text(encoding='utf-8')
newline = '\r\n' if '\r\n' in text else '\n'

EVENTS = [
'''BEGIN:VEVENT
UID:pokemon-go-pass-september-20260908@openai
DTSTAMP:20260901T124614Z
LAST-MODIFIED:20260901T124614Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
DTSTART;TZID=Europe/Paris:20260908T100000
DTEND;TZID=Europe/Paris:20261006T100000
SUMMARY:⭐ ✅ Pokémon GO — Passe GO septembre
LOCATION:En ligne — Pokémon GO
DESCRIPTION:Événement officiel Pokémon GO. Passe GO de septembre disponible du 8 septembre 2026 à 10:00 au 6 octobre 2026 à 10:00, heure locale. Récompenses incluant notamment Latios. Les récompenses du Passe expirent le 8 octobre 2026 à 10:00, heure locale. Source officielle : https://pokemongo.com/fr/news/go-pass-september-2026
URL:https://pokemongo.com/fr/news/go-pass-september-2026
CATEGORIES:Pokémon,Pokémon GO,Passe GO,Événement numérique
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Passe GO septembre demain à 10h
END:VALARM
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-mega-squads-20260908@openai
DTSTAMP:20260901T124614Z
LAST-MODIFIED:20260901T124614Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
DTSTART;TZID=Europe/Paris:20260908T100000
DTEND;TZID=Europe/Paris:20260914T200000
SUMMARY:⭐ ✅ Pokémon GO — Hordes Méga
LOCATION:En ligne — Pokémon GO
DESCRIPTION:Événement officiel Pokémon GO du 8 septembre 2026 à 10:00 au 14 septembre 2026 à 20:00, heure locale. Débuts de Grondogue et Dogrino, première disponibilité chromatique de Flamenroule, nouveau Super Niveau Max pour certaines Méga-Évolutions et Passe GO dédié. Source officielle : https://pokemongo.com/fr/news/mega-squads-2026
URL:https://pokemongo.com/fr/news/mega-squads-2026
CATEGORIES:Pokémon,Pokémon GO,Événement,Méga-Évolution
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Hordes Méga commence demain à 10h
END:VALARM
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-community-day-classic-gible-20260912@openai
DTSTAMP:20260901T124614Z
LAST-MODIFIED:20260901T124614Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
DTSTART;TZID=Europe/Paris:20260912T140000
DTEND;TZID=Europe/Paris:20260912T170000
SUMMARY:⭐ ✅ Pokémon GO — Community Day Classic Griknot
LOCATION:France — Pokémon GO
DESCRIPTION:Classique de la Journée Communauté officiel Pokémon GO le 12 septembre 2026 de 14:00 à 17:00, heure locale. Griknot à l'affiche. Faire évoluer Carmache avant 21:00 permet d'obtenir Carchacrok avec Telluriforce. Des événements communautaires locaux peuvent offrir une Étude ponctuelle supplémentaire. Source officielle : https://pokemongo.com/fr/news/communitydayclassic-gible-september-2026
URL:https://pokemongo.com/fr/news/communitydayclassic-gible-september-2026
CATEGORIES:Pokémon,Pokémon GO,Community Day,Événement
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Community Day Classic Griknot demain à 14h
END:VALARM
END:VEVENT'''
]

if not text.startswith('BEGIN:VCALENDAR') or 'END:VCALENDAR' not in text:
    raise SystemExit('Invalid VCALENDAR bounds')

changed = False
for event in EVENTS:
    uid_line = next(line for line in event.splitlines() if line.startswith('UID:'))
    if uid_line in text:
        continue
    block = event.replace('\n', newline)
    marker = 'END:VCALENDAR'
    idx = text.rfind(marker)
    text = text[:idx] + block + newline + text[idx:]
    changed = True

uids = [line[4:] for line in text.replace('\r\n','\n').split('\n') if line.startswith('UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR bounds after patch')

if changed:
    P.write_text(text, encoding='utf-8', newline='')
    print('calendar patched')
else:
    print('no business change')
