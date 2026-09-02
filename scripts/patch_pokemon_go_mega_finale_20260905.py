from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-go-mega-finale-20260905@openai'
EVENT = '''BEGIN:VEVENT\r\nUID:pokemon-go-mega-finale-20260905@openai\r\nDTSTAMP:20260902T010207Z\r\nLAST-MODIFIED:20260902T010207Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-REMINDER-PROFILE:GO_GLOBAL_WEEKEND\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:84\r\nX-POKEMON-USER-EFFECT:GO-MEGA-FINALE-20260905-FR\r\nDTSTART;TZID=Europe/Paris:20260905T100000\r\nDTEND;TZID=Europe/Paris:20260906T180000\r\nSUMMARY:⭐ ✅ 🆕 ⚡ Pokémon GO — Festival 2026 : Méga-Finale\r\nLOCATION:France — Pokémon GO\r\nDESCRIPTION:Priorité : ⭐ Important — grand événement mondial officiel limité au week-end.\\nFiabilité : ✅ Confirmé officiellement par Pokémon GO. Samedi 5 et dimanche 6 septembre 2026 de 10h à 18h heure locale.\\n⚡ Méga-Raids en rotations horaires ; Méga-Mewtwo X revient le 5 septembre et Méga-Mewtwo Y le 6 septembre.\\n🛡️ Mewtwo en armure apparaît dans les Raids de niveau 5 pendant les deux jours ; sa version chromatique n'est pas disponible cette fois-ci.\\n🌐 Aucune limite de Raids à distance les 5 et 6 septembre. Tous les Pokémon méga-évolués reçoivent un boost de PC pendant le week-end.\\nSource officielle principale : https://www.pokemon.com/fr/actualites/des-mega-raids-et-des-super-mega-raids-au-programme-du-festival-pokemon-go-2026-mega-finale\\nSource officielle Mewtwo en armure : https://pokemongo.com/fr/news/megafinale-2026-armored-mewtwo\r\nURL:https://pokemongo.com/fr/news/gofest2026-finale-save-the-date\r\nCATEGORIES:Pokémon,Pokémon GO,Festival GO,Méga-Raid,Événement,Nouveau,Priorité Important\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:⚡ Méga-Finale Pokémon GO demain à 10h — prépare tes équipes et passes de Raid\r\nEND:VALARM\r\nEND:VEVENT\r\n'''

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
