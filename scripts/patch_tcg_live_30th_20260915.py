from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-tcg-live-30th-20260915@openai'

EVENT_LINES = [
    'BEGIN:VEVENT',
    f'UID:{UID}',
    'DTSTAMP:20260902T195800Z',
    'LAST-MODIFIED:20260902T195800Z',
    'SEQUENCE:0',
    'STATUS:CONFIRMED',
    'PRIORITY:5',
    'X-POKEMON-PRIORITY:IMPORTANT',
    'X-POKEMON-REMINDER-PROFILE:DIGITAL_RELEASE',
    'X-POKEMON-ACTION:PLAY',
    'X-POKEMON-DATE-PRECISION:EXACT_DATETIME',
    'X-POKEMON-CONFIDENCE:99',
    'X-POKEMON-ACTIONABILITY:72',
    'X-POKEMON-USER-EFFECT-ID:tcg-live-30th-digital-release-fr-20260915',
    'DTSTART;TZID=Europe/Paris:20260915T190000',
    'DTEND;TZID=Europe/Paris:20260915T191500',
    'SUMMARY:⭐ ✅ 💻 JCC Pokémon Live — 30ᵉ Anniversaire disponible',
    'LOCATION:En ligne — JCC Pokémon Live',
    'DESCRIPTION:Priorité : ⭐ Important — l’extension 30ᵉ Anniversaire devient jouable numériquement avant la sortie physique.\\nFiabilité : ✅ Confirmé par The Pokémon Company International.\\n📅 Disponibilité JCC Pokémon Live : 15 septembre 2026 à 19:00 CEST (Europe/Paris), sur iOS, Android, macOS et Windows.\\n🃏 Les Dresseurs pourront collectionner et jouer les cartes de l’extension et recevoir des bonus en jeu en se connectant.\\n⚠️ Cette échéance numérique est distincte de la sortie physique mondiale du 16 septembre 2026.\\nSource primaire : https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon',
    'URL:https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon',
    'CATEGORIES:Pokémon,JCC Pokémon Live,30e Anniversaire,Sortie numérique,Priorité Important',
    'BEGIN:VALARM',
    'TRIGGER:-P1D',
    'ACTION:DISPLAY',
    'DESCRIPTION:JCC Pokémon Live 30ᵉ Anniversaire demain à 19h',
    'END:VALARM',
    'END:VEVENT',
]


def main():
    data = PATH.read_bytes()
    if not data.startswith(b'BEGIN:VCALENDAR') or not data.rstrip().endswith(b'END:VCALENDAR'):
        raise SystemExit('Invalid VCALENDAR bounds')
    text = data.decode('utf-8')
    if f'UID:{UID}' in text:
        print('No business change: UID already present')
        return
    if 'DTSTART;TZID=Europe/Paris:20260915T190000' in text and '30' in text and 'JCC Pokémon Live' in text:
        print('No business change: equivalent digital release already present')
        return

    newline = '\r\n' if b'\r\n' in data else '\n'
    event = newline.join(EVENT_LINES) + newline
    marker = ('END:VCALENDAR' + newline).encode('utf-8')
    if marker not in data:
        marker = b'END:VCALENDAR'
    idx = data.rfind(marker)
    if idx < 0:
        raise SystemExit('END:VCALENDAR not found')

    out = data[:idx] + event.encode('utf-8') + data[idx:]
    out_text = out.decode('utf-8')
    if out_text.count(f'UID:{UID}') != 1:
        raise SystemExit('UID uniqueness validation failed')
    if out_text.count('BEGIN:VCALENDAR') != 1 or out_text.count('END:VCALENDAR') != 1:
        raise SystemExit('VCALENDAR bounds validation failed')
    if out_text.count('BEGIN:VEVENT') != out_text.count('END:VEVENT'):
        raise SystemExit('VEVENT balance validation failed')

    PATH.write_bytes(out)
    print('Added JCC Pokémon Live 30th digital release 2026-09-15 19:00 Europe/Paris')


if __name__ == '__main__':
    main()
