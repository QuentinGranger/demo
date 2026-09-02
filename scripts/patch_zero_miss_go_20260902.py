from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
raw = p.read_bytes().decode('utf-8')
assert raw.startswith('BEGIN:VCALENDAR\r\n') and raw.endswith('END:VCALENDAR\r\n')

EVENTS = {
'pokemon-go-super-mega-raid-day-staraptor-20260919@openai': """BEGIN:VEVENT\r\nUID:pokemon-go-super-mega-raid-day-staraptor-20260919@openai\r\nDTSTAMP:20260902T135200Z\r\nLAST-MODIFIED:20260902T135200Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-REMINDER-PROFILE:GO_LIMITED_EVENT\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:84\r\nDTSTART;TZID=Europe/Paris:20260919T140000\r\nDTEND;TZID=Europe/Paris:20260919T170000\r\nSUMMARY:⭐ ✅ 🦅 Pokémon GO — Journée de Super Méga-Raids Étouraptor\r\nLOCATION:Pokémon GO — France / heure locale\r\nDESCRIPTION:Priorité : ⭐ Important — événement limité de 3 heures.\\nFiabilité : ✅ Confirmé officiellement par Pokémon GO.\\n📅 Samedi 19 septembre 2026 de 14:00 à 17:00, heure locale.\\n✨ Début de Méga-Étouraptor dans les Super Méga-Raids et accès au Super Niveau Max.\\n🎟️ Jusqu’à 6 passes de Raid supplémentaires gratuits via les PhotoDisques des Arènes ; ticket payant optionnel.\\nSource officielle : https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\nURL:https://pokemongo.com/fr/news/staraptor-super-mega-raid-day-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Événement,Raid,Méga,Priorité Important\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:🦅 Journée de Super Méga-Raids Étouraptor demain à 14h\r\nEND:VALARM\r\nEND:VEVENT\r\n""",
'pokemon-go-horizons-celebration-20260916@openai': """BEGIN:VEVENT\r\nUID:pokemon-go-horizons-celebration-20260916@openai\r\nDTSTAMP:20260902T135200Z\r\nLAST-MODIFIED:20260902T135200Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-REMINDER-PROFILE:GO_EVENT\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:78\r\nDTSTART;TZID=Europe/Paris:20260916T100000\r\nDTEND;TZID=Europe/Paris:20260922T200000\r\nSUMMARY:⭐ ✅ 📺 Pokémon GO — Célébration Pokémon, les horizons\r\nLOCATION:Pokémon GO — France / heure locale\r\nDESCRIPTION:Priorité : ⭐ Important — événement officiel avec contenu limité dans le temps.\\nFiabilité : ✅ Confirmé officiellement par Pokémon GO.\\n📅 Du 16 septembre 2026 à 10:00 au 22 septembre 2026 à 20:00, heure locale.\\n✨ Début de Salamèche portant les lunettes de Friede ; raids, rencontres sauvages, études et Passe GO de collaboration.\\n⏳ Récompenses du Passe GO à récupérer avant le 24 septembre 2026 à 20:00, heure locale.\\nSource officielle : https://pokemongo.com/fr/news/pokemon-horizons-celebration-event-2026\r\nURL:https://pokemongo.com/fr/news/pokemon-horizons-celebration-event-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Événement,Pokémon Horizons,Priorité Important\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:📺 Célébration Pokémon Horizons demain à 10h\r\nEND:VALARM\r\nEND:VEVENT\r\n""",
'pokemon-go-horizons-pass-rewards-expiry-20260924@openai': """BEGIN:VEVENT\r\nUID:pokemon-go-horizons-pass-rewards-expiry-20260924@openai\r\nDTSTAMP:20260902T135200Z\r\nLAST-MODIFIED:20260902T135200Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:5\r\nX-POKEMON-PRIORITY:IMPORTANT\r\nX-POKEMON-REMINDER-PROFILE:DEADLINE\r\nX-POKEMON-ACTION:CLAIM\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:86\r\nDTSTART;TZID=Europe/Paris:20260924T200000\r\nDTEND;TZID=Europe/Paris:20260924T201500\r\nSUMMARY:⏳ Pokémon GO — Fin de récupération des récompenses Passe GO Horizons\r\nLOCATION:Pokémon GO — en ligne\r\nDESCRIPTION:Deadline officielle : récupérer les récompenses du Passe GO Célébration de collaboration avant le 24 septembre 2026 à 20:00, heure locale.\\nSource officielle : https://pokemongo.com/fr/news/pokemon-horizons-celebration-event-2026\r\nURL:https://pokemongo.com/fr/news/pokemon-horizons-celebration-event-2026\r\nCATEGORIES:Pokémon,Pokémon GO,Deadline,Pokémon Horizons\r\nBEGIN:VALARM\r\nTRIGGER:-P1D\r\nACTION:DISPLAY\r\nDESCRIPTION:⏳ Dernier jour demain pour récupérer les récompenses du Passe GO Horizons\r\nEND:VALARM\r\nEND:VEVENT\r\n"""
}

changed = False
for uid, event in EVENTS.items():
    if f'UID:{uid}\r\n' not in raw:
        raw = raw.replace('END:VCALENDAR\r\n', event + 'END:VCALENDAR\r\n')
        changed = True

uids = [line[4:] for line in raw.split('\r\n') if line.startswith('UID:')]
assert len(uids) == len(set(uids)), 'duplicate UID'
assert raw.count('BEGIN:VCALENDAR') == 1 and raw.count('END:VCALENDAR') == 1

if changed:
    p.write_bytes(raw.encode('utf-8'))
else:
    print('No business change')
