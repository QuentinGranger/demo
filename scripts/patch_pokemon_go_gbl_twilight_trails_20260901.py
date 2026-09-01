from pathlib import Path
import re

p = Path('calendars/pokemon-paris.ics')
data = p.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in data else '\n'
uid = 'pokemon-go-gbl-twilight-trails-20260908@openai'

raw = '''BEGIN:VEVENT
UID:pokemon-go-gbl-twilight-trails-20260908@openai
DTSTAMP:20260901T165003Z
LAST-MODIFIED:20260901T165003Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:DIGITAL_SEASON
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:68
DTSTART;TZID=Europe/Paris:20260908T220000
DTEND;TZID=Europe/Paris:20261201T220000
SUMMARY:⭐ ✅ Pokémon GO — Ligue Combat GO : Sentiers crépusculaires
LOCATION:En ligne — Pokémon GO
DESCRIPTION:Saison officielle de la Ligue Combat GO « Sentiers crépusculaires », du 8 septembre 2026 à 22:00 heure de Paris (13:00 PDT) au 1er décembre 2026 à 22:00 heure de Paris (13:00 PST). Début de saison : récompenses de fin de saison disponibles et classement réinitialisé. Les Méga-Évolutions sont autorisées dans de nouvelles ligues Méga. Un Passe d’Étude ponctuelle Ligue Combat GO gratuit sera disponible dans la boutique du jeu dès le début de la saison. Le programme hebdomadaire détaillé et les règles des coupes figurent dans la source officielle. Source : https://pokemongo.com/fr/news/go-battle-league-twilight-trails
URL:https://pokemongo.com/fr/news/go-battle-league-twilight-trails
CATEGORIES:Pokémon,Pokémon GO,Ligue Combat GO,Saison,Compétitif
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Ligue Combat GO — Sentiers crépusculaires commence demain à 22h
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
    raise SystemExit('Expected Twilight Trails UID missing')

p.write_bytes(data.encode('utf-8'))
