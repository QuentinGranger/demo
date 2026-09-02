from pathlib import Path

P = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-go-twilight-trails-20260908@openai'
EVENT = '''BEGIN:VEVENT\r\nUID:pokemon-go-twilight-trails-20260908@openai\r\nDTSTAMP:20260902T100328Z\r\nLAST-MODIFIED:20260902T100328Z\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\nPRIORITY:9\r\nX-POKEMON-PRIORITY:INFO\r\nX-POKEMON-REMINDER-PROFILE:SEASON_START_INFO\r\nX-POKEMON-ACTION:PLAY\r\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\nX-POKEMON-CONFIDENCE:99\r\nX-POKEMON-ACTIONABILITY:68\r\nDTSTART;TZID=Europe/Paris:20260908T100000\r\nDTEND;TZID=Europe/Paris:20261201T100000\r\nSUMMARY:ℹ️ ✅ 🌆 Pokémon GO — Saison Sentiers crépusculaires\r\nLOCATION:Pokémon GO — France\r\nDESCRIPTION:Fiabilité : ✅ Confirmé officiellement par Pokémon GO. La Saison Sentiers crépusculaires débute le 8 septembre 2026 à 10 h et se termine le 1er décembre 2026 à 10 h\, heure locale. Parmi les temps forts annoncés : nouveaux Pokémon de Paldea\, nouvelles Méga-Évolutions\, nouveaux Pokémon Dynamax et plusieurs Journées Communauté.\nSource officielle : https://pokemongo.com/fr/seasons/twilight-trails\r\nURL:https://pokemongo.com/fr/seasons/twilight-trails\r\nCATEGORIES:Pokémon,Pokémon GO,Saison,Sortie numérique,Priorité Info\r\nEND:VEVENT\r\n'''

def main():
    raw = P.read_bytes()
    text = raw.decode('utf-8')
    if UID in text:
        print('No business change')
        return
    if not text.startswith('BEGIN:VCALENDAR\r\n') or not text.endswith('END:VCALENDAR\r\n'):
        raise SystemExit('Invalid VCALENDAR bounds/CRLF')
    updated = text[:-len('END:VCALENDAR\r\n')] + EVENT + 'END:VCALENDAR\r\n'
    uids = [line[4:] for line in updated.split('\r\n') if line.startswith('UID:')]
    if len(uids) != len(set(uids)):
        raise SystemExit('Duplicate UID detected')
    P.write_bytes(updated.encode('utf-8'))

if __name__ == '__main__':
    main()
