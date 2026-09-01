from pathlib import Path
import re

p = Path('calendars/pokemon-paris.ics')
data = p.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in data else '\n'
uid = 'pokemon-go-city-safari-marseille-20260926@openai'

raw = '''BEGIN:VEVENT
UID:pokemon-go-city-safari-marseille-20260926@openai
DTSTAMP:20260901T144809Z
LAST-MODIFIED:20260901T144809Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:PLAY_EVENT_LIMITED
X-POKEMON-ACTION:ATTEND
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:76
DTSTART;TZID=Europe/Paris:20260926T100000
DTEND;TZID=Europe/Paris:20260927T180000
SUMMARY:⭐ ✅ Pokémon GO City Safari — Marseille
LOCATION:Marseille, France
DESCRIPTION:Événement officiel Pokémon GO City Safari à Marseille les 26 et 27 septembre 2026, de 10:00 à 18:00 CEST. Billet d'une journée : 10,00 € taxes et frais applicables compris. Possibilité d'ajouter le second jour via un add-on. Source officielle : https://pokemongo.com/fr/featured-in-person-events/citysafari/marseille
URL:https://pokemongo.com/fr/featured-in-person-events/citysafari/marseille
CATEGORIES:Pokémon,Pokémon GO,Événement,France,Marseille,City Safari
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Pokémon GO City Safari Marseille commence demain à 10h
END:VALARM
END:VEVENT'''.replace('\n', nl)

if f'UID:{uid}' not in data:
    marker = 'END:VCALENDAR' + nl
    if marker not in data:
        raise SystemExit('Missing VCALENDAR end marker')
    data = data.replace(marker, raw + nl + marker, 1)

if data.count('BEGIN:VCALENDAR') != 1 or data.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR envelope')
uids = re.findall(r'^UID:(.+?)\r?$', data, flags=re.M)
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
if f'UID:{uid}' not in data:
    raise SystemExit('Expected Marseille UID missing')

p.write_bytes(data.encode('utf-8'))
