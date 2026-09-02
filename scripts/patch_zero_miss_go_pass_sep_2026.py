from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
raw = p.read_text(encoding='utf-8')
text = raw.replace('\r\n','\n')

uid = 'pokemon-go-pass-september-2026@openai'
if f'UID:{uid}' in text:
    print('No business change')
    raise SystemExit(0)

if not text.startswith('BEGIN:VCALENDAR\n') or not text.rstrip().endswith('END:VCALENDAR'):
    raise SystemExit('Invalid VCALENDAR bounds')

block = '''BEGIN:VEVENT
UID:pokemon-go-pass-september-2026@openai
DTSTAMP:20260902T124500Z
LAST-MODIFIED:20260902T124500Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:DIGITAL_EVENT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:76
X-POKEMON-USER-EFFECT:go-pass-september-2026-france
DTSTART;TZID=Europe/Paris:20260908T100000
DTEND;TZID=Europe/Paris:20261006T100000
SUMMARY:⭐ ✅ 🎮 Pokémon GO — Passe GO de septembre — Latios
LOCATION:En ligne — Pokémon GO
DESCRIPTION:Priorité : ⭐ Important — Passe GO mensuel avec fenêtre exacte et récompense vedette Latios.\\nFiabilité : ✅ Confirmé par la page officielle Pokémon GO France.\\n📅 Disponible du 8 septembre 2026 à 10:00 au 6 octobre 2026 à 10:00, heure locale.\\n🎁 Récompenses à récupérer avant le 8 octobre 2026 à 10:00, heure locale.\\n⭐ Rencontre vedette : Latios, avec possibilité chromatique.\\n⏳ L'Incubateur ponctuel du Passe GO deluxe expire le 13 octobre 2026 à 10:00.\\nSource : https://pokemongo.com/fr/news/go-pass-september-2026
URL:https://pokemongo.com/fr/news/go-pass-september-2026
CATEGORIES:Pokémon,Pokémon GO,Passe GO,Événement numérique,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:⏳ Le Passe GO de septembre commence demain à 10h
END:VALARM
END:VEVENT
'''

insert_at = text.rfind('END:VCALENDAR')
text = text[:insert_at] + block + text[insert_at:]

uids = [line[4:] for line in text.splitlines() if line.startswith('UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR count')
if f'UID:{uid}' not in text:
    raise SystemExit('Expected event missing')

p.write_bytes(text.replace('\n','\r\n').encode('utf-8'))
print('Patched', uid)
