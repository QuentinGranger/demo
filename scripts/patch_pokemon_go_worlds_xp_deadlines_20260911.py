from pathlib import Path
from collections import Counter

p = Path('calendars/pokemon-paris.ics')
text = p.read_text(encoding='utf-8')

if 'BEGIN:VCALENDAR' not in text or 'END:VCALENDAR' not in text:
    raise SystemExit('invalid calendar markers')

source = 'https://www.pokemon.com/fr/actualites/regardez-les-mondiaux-et-pokemonxp-pour-obtenir-de-superbes-recompenses-en-jeu'

events = [
    (
        'pokemon-go-worlds2026-rewards-deadline-20260911@openai',
        'pokemon-go-worlds2026-rewards-expiry-fr-20260911',
        '20260911T220000',
        '⏳ Fin récompenses Pokémon GO — Mondiaux 2026',
        'Les récompenses Pokémon GO obtenues via les diffusions des Championnats du Monde 2026 expirent le 11 septembre 2026 à 13h PDT, soit 22h en Europe/Paris (CEST). Cela couvre notamment les Études ponctuelles et récompenses associées annoncées par Pokémon.',
    ),
    (
        'pokemon-go-xp2026-pikachu-reward-deadline-20260912@openai',
        'pokemon-go-pokemonxp2026-pikachu-claim-fr-20260912',
        '20260912T050000',
        '⏳ Fin récupération Pokémon GO — Pikachu PokémonXP',
        'La récompense Pokémon GO du panel PokémonXP permettant une Étude ponctuelle avec Pikachu en costume PokémonXP doit être récupérée avant le 11 septembre 2026 à 20h PDT, soit le 12 septembre à 05h en Europe/Paris (CEST).',
    ),
]

added = []
for uid, effect, dtstart, summary, detail in events:
    if uid in text:
        continue
    event = (
        'BEGIN:VEVENT\r\n'
        f'UID:{uid}\r\n'
        'DTSTAMP:20260905T205437Z\r\n'
        'LAST-MODIFIED:20260905T205437Z\r\n'
        'SEQUENCE:0\r\n'
        'STATUS:CONFIRMED\r\n'
        'PRIORITY:5\r\n'
        'X-POKEMON-PRIORITY:IMPORTANT\r\n'
        'X-POKEMON-REMINDER-PROFILE:DEADLINE\r\n'
        'X-POKEMON-ACTION:REDEEM\r\n'
        'X-POKEMON-FIRST-ADDED-AT:20260905T205437Z\r\n'
        'X-POKEMON-DATE-PRECISION:EXACT_DATETIME\r\n'
        'X-POKEMON-CONFIDENCE:99\r\n'
        'X-POKEMON-ACTIONABILITY:82\r\n'
        f'X-POKEMON-USER-EFFECT-ID:{effect}\r\n'
        f'DTSTART;TZID=Europe/Paris:{dtstart}\r\n'
        f'DTEND;TZID=Europe/Paris:{dtstart}\r\n'
        f'SUMMARY:{summary}\r\n'
        'LOCATION:En ligne — Pokémon GO\r\n'
        f'DESCRIPTION:Priorité : ⭐ Important — deadline officielle de récompense.\\nFiabilité : ✅ Source primaire Pokémon. {detail}\\nAction : récupère/valide la récompense avant cette échéance.\\nSource : {source}\r\n'
        f'URL:{source}\r\n'
        'CATEGORIES:Pokémon,Pokémon GO,Deadline,Twitch Drops,Récompense\r\n'
        'BEGIN:VALARM\r\n'
        'TRIGGER:-P1D\r\n'
        'ACTION:DISPLAY\r\n'
        f'DESCRIPTION:{summary} dans 24 h\r\n'
        'END:VALARM\r\n'
        'END:VEVENT\r\n'
    )
    text = text.replace('END:VCALENDAR', event + 'END:VCALENDAR', 1)
    added.append(uid)

if not added:
    raise SystemExit(0)

uids = []
for line in text.replace('\r\n', '\n').split('\n'):
    if line.startswith('UID:'):
        uids.append(line[4:])
dups = [u for u, n in Counter(uids).items() if n > 1]
if dups:
    raise SystemExit(f'duplicate UIDs: {dups}')
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('calendar envelope count invalid')
for uid in added:
    if text.count(uid) != 1:
        raise SystemExit(f'UID validation failed: {uid}')

p.write_text(text, encoding='utf-8', newline='')
print('added', ', '.join(added))
