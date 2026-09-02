from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
raw = p.read_bytes()
text = raw.decode('utf-8')
uid = 'pokemon-go-staraptor-super-mega-raid-day-20260919@openai'
if uid in text:
    raise SystemExit(0)

event = (
'BEGIN:VEVENT\r\n'
'UID:pokemon-go-staraptor-super-mega-raid-day-20260919@openai\r\n'
'DTSTAMP:20260902T075000Z\r\n'
'LAST-MODIFIED:20260902T075000Z\r\n'
'SEQUENCE:0\r\n'
'STATUS:CONFIRMED\r\n'
'PRIORITY:5\r\n'
'X-POKEMON-PRIORITY:IMPORTANT\r\n'
'X-POKEMON-REMINDER-PROFILE:PLAY_EVENT_LIMITED\r\n'
'X-POKEMON-ACTION:PLAY\r\n'
'X-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\n'
'X-POKEMON-CONFIDENCE:99\r\n'
'X-POKEMON-ACTIONABILITY:84\r\n'
'X-POKEMON-USER-EFFECT:POKEMON_GO_STARAPTOR_SUPER_MEGA_RAID_DAY_FR_20260919\r\n'
'DTSTART;TZID=Europe/Paris:20260919T140000\r\n'
'DTEND;TZID=Europe/Paris:20260919T170000\r\n'
'SUMMARY:⭐ ✅ 🆕 Pokémon GO — Journée de Super Méga-Raids Étouraptor\r\n'
'LOCATION:Pokémon GO — France\r\n'
'DESCRIPTION:Priorité : ⭐ Important — événement officiel limité à 3 heures.\\nFiabilité : ✅ Confirmé officiellement par Pokémon GO.\\n📅 Samedi 19 septembre 2026 de 14 h à 17 h (heure locale).\\n✨ Début de Méga-Étouraptor dans les Super Méga-Raids et accès au Super Niveau Max ; Rapace+ devient disponible en forme méga-évoluée.\\nSource officielle : https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\n'
'URL:https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\n'
'CATEGORIES:Pokémon,Pokémon GO,Événement,Super Méga-Raid,Priorité Important,Nouveau\r\n'
'BEGIN:VALARM\r\n'
'TRIGGER:-P1D\r\n'
'ACTION:DISPLAY\r\n'
'DESCRIPTION:Pokémon GO — Journée de Super Méga-Raids Étouraptor demain à 14 h\r\n'
'END:VALARM\r\n'
'END:VEVENT\r\n'
)
marker = 'END:VCALENDAR\r\n'
if marker not in text:
    raise SystemExit('invalid calendar: END:VCALENDAR missing')
text = text.replace(marker, event + marker, 1)
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('invalid VCALENDAR bounds')
# Basic UID uniqueness validation
uids = [line[4:] for line in text.split('\r\n') if line.startswith('UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('duplicate UID')
p.write_bytes(text.encode('utf-8'))
