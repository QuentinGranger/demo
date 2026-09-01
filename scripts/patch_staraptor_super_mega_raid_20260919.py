from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-go-staraptor-super-mega-raid-day-20260919@openai'
EVENT = '''BEGIN:VEVENT\r\nUID:pokemon-go-staraptor-super-mega-raid-day-20260919@openai\r\nDTSTAMP:20260901T174854Z\r\nLAST-MODIFIED:20260901T174854Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-REMINDER-PROFILE:GO_RAID_DAY\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:78\r\nDTSTART;TZID=Europe/Paris:20260919T140000\r\nDTEND;TZID=Europe/Paris:20260919T170000\r\nSUMMARY:⭐ ✅ 🆕 🪽 Pokémon GO — Journée de Super Méga-Raids Étouraptor\r\nLOCATION:France — Pokémon GO\r\nDESCRIPTION:Priorité : ⭐ Important — événement officiel limité à 3 heures.\\nFiabilité : ✅ Confirmé officiellement par Pokémon GO. Samedi 19 septembre 2026 de 14h à 17h heure locale.\\n🪽 Première apparition de Méga-Étouraptor dans les Super Méga-Raids et accès au Super Niveau Max.\\n🎟️ Jusqu’à 6 passes de Raid supplémentaires gratuits via les PhotoDisques des Arènes. Une Étude ponctuelle permet d’obtenir un passe de combat premium et une rencontre avec Gardevoir.\\n🛒 Ticket optionnel annoncé à 4,99 USD ou équivalent local, disponible jusqu’à 17h heure locale le 19 septembre.\\nSource officielle : https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\nURL:https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Super Méga-Raid,Événement,Nouveau,Priorité Important\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:🪽 Journée de Super Méga-Raids Étouraptor demain à 14h\r\nEND:VALARM\r\nEND:VEVENT\r\n'''

raw = PATH.read_bytes()
if UID.encode() in raw:
    print('No business change: UID already present')
    raise SystemExit(0)

if not (raw.startswith(b'BEGIN:VCALENDAR') and raw.rstrip().endswith(b'END:VCALENDAR')):
    raise SystemExit('Invalid VCALENDAR bounds')

newline = b'\r\n' if b'\r\n' in raw else b'\n'
marker = b'END:VCALENDAR'
pos = raw.rfind(marker)
if pos < 0:
    raise SystemExit('END:VCALENDAR missing')

event = EVENT.encode('utf-8')
if newline == b'\n':
    event = event.replace(b'\r\n', b'\n')

prefix = raw[:pos]
if not prefix.endswith(newline):
    prefix += newline
updated = prefix + event + marker + newline

# Validate one calendar, one new UID, and no duplicate UIDs.
text = updated.decode('utf-8')
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('VCALENDAR count validation failed')
uids = [line[4:] for line in text.replace('\r\n','\n').split('\n') if line.startswith('UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
if UID not in uids:
    raise SystemExit('Expected UID missing')

PATH.write_bytes(updated)
print('Added', UID)
