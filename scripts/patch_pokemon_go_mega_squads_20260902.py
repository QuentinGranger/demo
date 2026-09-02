from pathlib import Path
import re

p = Path('calendars/pokemon-paris.ics')
data = p.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in data else '\n'
uid = 'pokemon-go-hordes-mega-20260908@openai'

raw = '''BEGIN:VEVENT
UID:pokemon-go-hordes-mega-20260908@openai
DTSTAMP:20260902T034929Z
LAST-MODIFIED:20260902T034929Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:PLAY_EVENT_LIMITED
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:82
DTSTART;TZID=Europe/Paris:20260908T100000
DTEND;TZID=Europe/Paris:20260914T200000
SUMMARY:⭐ ✅ Pokémon GO — Hordes Méga
LOCATION:Pokémon GO — France
DESCRIPTION:Événement officiel Pokémon GO du 8 septembre 2026 à 10:00 au 14 septembre à 20:00, heure locale. Débuts de Grondogue et Dogrino, premier Flamenroule chromatique, Super Niveau Max pour Méga-Dardargnan et Méga-Démolosse, Passe GO Hordes Méga. Les récompenses du Passe GO expirent le 16 septembre 2026 à 20:00. Source officielle : https://pokemongo.com/fr/news/mega-squads-2026
URL:https://pokemongo.com/fr/news/mega-squads-2026
CATEGORIES:Pokémon,Pokémon GO,Événement,France,Hordes Méga
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Pokémon GO Hordes Méga commence demain à 10h
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
    raise SystemExit('Expected Hordes Méga UID missing')

p.write_bytes(data.encode('utf-8'))
