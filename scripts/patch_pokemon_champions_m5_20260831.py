# Verified canonical gap on 2026-09-01; trigger idempotent calendar patch workflow.
from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-champions-m5-deadline-20260909@openai'
SOURCE = 'https://www.pokemon.com/fr/actualites/evenements-pokemon-champions-daout-2026-defi-mensuel-saison-des-combats-classes-et-pass-de-combat'

raw = PATH.read_bytes()
text = raw.decode('utf-8')
newline = '\r\n' if b'\r\n' in raw else '\n'

if f'UID:{UID}' in text:
    print('Event already present; no change.')
    raise SystemExit(0)

marker = 'END:VCALENDAR'
if text.count(marker) != 1:
    raise SystemExit('Unsafe calendar envelope: END:VCALENDAR count != 1')

event_lines = [
    'BEGIN:VEVENT',
    f'UID:{UID}',
    'DTSTAMP:20260831T070100Z',
    'LAST-MODIFIED:20260831T070100Z',
    'SEQUENCE:0',
    'STATUS:CONFIRMED',
    'PRIORITY:5',
    'X-POKEMON-PRIORITY:IMPORTANT',
    'X-POKEMON-REMINDER-PROFILE:DIGITAL_DEADLINE',
    'X-POKEMON-ACTION:PLAY',
    'X-POKEMON-DATE-PRECISION:EXACT_DATETIME',
    'X-POKEMON-CONFIDENCE:98',
    'X-POKEMON-ACTIONABILITY:78',
    'X-POKEMON-USER-EFFECT-ID:champions-m5-end-global-20260909',
    'DTSTART;TZID=Europe/Paris:20260909T035900',
    'DTEND;TZID=Europe/Paris:20260909T041400',
    'SUMMARY:⭐ ✅ ⏳ Pokémon Champions — Fin saison M-5 + pass de combat',
    'LOCATION:En ligne — Pokémon Champions',
    'DESCRIPTION:Priorité : ⭐ Important — dernière échéance pour progresser dans la saison M-5 des combats classés et le pass de combat associé.\\nFiabilité : ✅ Confirmé officiellement par Pokémon France. La saison M-5 et le pass de combat se terminent le 9 septembre 2026 à 01:59 UTC, soit 03:59 à Paris (CEST).\\n🎁 Pass M-5 : Lugulabre, Lugulabrite, icône Lugulabre, 48 Coupons de Vitesse, 4 Tickets de Recrutement Permanent, 4 Tickets d’Entraînement et 10 000 PdV selon progression.\\nAction : terminer la progression et récupérer les récompenses utiles avant l’échéance.\\nSource : ' + SOURCE,
    'URL:' + SOURCE,
    'CATEGORIES:Pokémon,Pokémon Champions,Jeu vidéo,Deadline,Pass de combat,Priorité Important',
    'BEGIN:VALARM',
    'TRIGGER:-P1D',
    'ACTION:DISPLAY',
    'DESCRIPTION:⏳ Pokémon Champions — la saison M-5 et son pass se terminent demain',
    'END:VALARM',
    'END:VEVENT',
]
event = newline.join(event_lines) + newline

idx = text.index(marker)
prefix = text[:idx]
suffix = text[idx:]
if prefix and not prefix.endswith(('\r\n', '\n')):
    prefix += newline
text = prefix + event + suffix
PATH.write_bytes(text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8'))
print('Added', UID)
