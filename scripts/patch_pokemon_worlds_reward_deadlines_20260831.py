from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
SOURCE = 'https://www.pokemon.com/fr/actualites/regardez-les-mondiaux-et-pokemonxp-pour-obtenir-de-superbes-recompenses-en-jeu'

raw = PATH.read_bytes()
text = raw.decode('utf-8')
newline = '\r\n' if b'\r\n' in raw else '\n'
marker = 'END:VCALENDAR'
if text.count(marker) != 1:
    raise SystemExit('Unsafe calendar envelope: END:VCALENDAR count != 1')

events = [
    (
        'pokemon-champions-worlds-outfit-deadline-20260904@openai',
        [
            'DTSTART;TZID=Europe/Paris:20260904T015900',
            'DTEND;TZID=Europe/Paris:20260904T021400',
            'SUMMARY:⭐ ✅ ⏳ Pokémon Champions — Fin mot de passe tenue Mondiaux 2026',
            'LOCATION:En ligne — Pokémon Champions',
            'DESCRIPTION:Priorité : ⭐ Important — dernière échéance officielle pour utiliser le mot de passe de la tenue des Mondiaux 2026 dans Pokémon Champions.\\nFiabilité : ✅ Confirmé officiellement par Pokémon. Le mot de passe est valable jusqu’au 3 septembre 2026 à 23:59 UTC, soit le 4 septembre à 01:59 à Paris (CEST).\\n🎁 Récompense : Casquette des Mondiaux 2026 (rouge) + T-shirt des Mondiaux 2026 (rouge).\\nAction : saisir le mot de passe avant l’échéance si ce n’est pas déjà fait.\\nSource : ' + SOURCE,
            'CATEGORIES:Pokémon,Pokémon Champions,Deadline,Récompense,Mondiaux 2026,Priorité Important',
            'X-POKEMON-ACTIONABILITY:91',
            'X-POKEMON-USER-EFFECT-ID:champions-worlds-2026-outfit-password-deadline',
        ],
    ),
    (
        'pokemon-go-worlds-twitch-rewards-deadline-20260911@openai',
        [
            'DTSTART;TZID=Europe/Paris:20260911T220000',
            'DTEND;TZID=Europe/Paris:20260911T221500',
            'SUMMARY:⭐ ✅ ⏳ Pokémon GO — Fin récompenses Twitch Mondiaux 2026',
            'LOCATION:En ligne — Pokémon GO',
            'DESCRIPTION:Priorité : ⭐ Important — expiration des récompenses Pokémon GO obtenues via les diffusions des Mondiaux 2026.\\nFiabilité : ✅ Confirmé officiellement par Pokémon. Les récompenses expirent le 11 septembre 2026 à 13:00 PDT, soit 22:00 à Paris (CEST).\\n🎁 Sont notamment concernés les Études ponctuelles Esprit d’équipe, Champion du Monde avec Forgelina, le t-shirt Mondiaux 2026 et l’Étude Pikachu en costume Mondiaux selon le drop obtenu.\\nAction : réclamer/échanger les récompenses obtenues avant l’échéance.\\nSource : ' + SOURCE,
            'CATEGORIES:Pokémon,Pokémon GO,Deadline,Twitch Drop,Mondiaux 2026,Priorité Important',
            'X-POKEMON-ACTIONABILITY:88',
            'X-POKEMON-USER-EFFECT-ID:pokemon-go-worlds-2026-twitch-rewards-expiry',
        ],
    ),
    (
        'pokemon-pocket-worlds-drop-code-deadline-20271128@openai',
        [
            'DTSTART;TZID=Europe/Paris:20271128T155900',
            'DTEND;TZID=Europe/Paris:20271128T161400',
            'SUMMARY:ℹ️ ✅ ⏳ JCC Pokémon Pocket — Fin code 24 Sabliers Booster Mondiaux 2026',
            'LOCATION:En ligne — JCC Pokémon Pocket',
            'DESCRIPTION:Priorité : ℹ️ Info — échéance lointaine mais exacte pour le code issu du drop Mondiaux/PokémonXP 2026.\\nFiabilité : ✅ Confirmé officiellement par Pokémon. Le code permettant d’obtenir 24 Sabliers Booster est valable jusqu’au 28 novembre 2027 à 14:59 UTC, soit 15:59 à Paris (CET).\\nAction : conserver le code de manière sûre puis l’utiliser avant l’échéance si nécessaire.\\nSource : ' + SOURCE,
            'CATEGORIES:Pokémon,JCC Pokémon Pocket,Deadline,Twitch Drop,Mondiaux 2026,Priorité Info',
            'X-POKEMON-ACTIONABILITY:40',
            'X-POKEMON-USER-EFFECT-ID:pocket-worlds-2026-booster-hourglass-code-expiry',
        ],
    ),
]

stamp = '20260831T155633Z'
base_common = [
    'DTSTAMP:' + stamp,
    'LAST-MODIFIED:' + stamp,
    'SEQUENCE:0',
    'STATUS:CONFIRMED',
    'PRIORITY:5',
    'X-POKEMON-PRIORITY:IMPORTANT',
    'X-POKEMON-REMINDER-PROFILE:DIGITAL_DEADLINE',
    'X-POKEMON-ACTION:CLAIM',
    'X-POKEMON-DATE-PRECISION:EXACT_DATETIME',
    'X-POKEMON-CONFIDENCE:98',
]

added = []
blocks = []
for uid, body in events:
    if f'UID:{uid}' in text:
        continue
    lines = ['BEGIN:VEVENT', f'UID:{uid}'] + base_common + body + [
        'URL:' + SOURCE,
        'BEGIN:VALARM',
        'TRIGGER:-P1D',
        'ACTION:DISPLAY',
        'DESCRIPTION:⏳ Récompense Pokémon limitée — échéance demain',
        'END:VALARM',
        'END:VEVENT',
    ]
    blocks.append(newline.join(lines) + newline)
    added.append(uid)

if not blocks:
    print('All events already present; no change.')
    raise SystemExit(0)

idx = text.index(marker)
prefix = text[:idx]
suffix = text[idx:]
if prefix and not prefix.endswith(('\r\n', '\n')):
    prefix += newline
text = prefix + ''.join(blocks) + suffix
PATH.write_bytes(text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8'))
print('Added', ', '.join(added))
