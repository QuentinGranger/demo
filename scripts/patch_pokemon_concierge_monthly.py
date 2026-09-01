from pathlib import Path
import re

PATH = Path('calendars/pokemon-paris.ics')
MONTH = '2026-09'
UID = f'pokemon-concierge-{MONTH}@openai'
STAMP = '20260901T080300Z'
SUMMARY = '🎒 Pokémon Monthly Experience — La Rentrée des 30 ans'


def esc(s: str) -> str:
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def fold(line: str, limit: int = 75):
    if len(line.encode()) <= limit:
        return [line]
    parts, cur, first = [], '', True
    for ch in line:
        prefix = '' if first else ' '
        if cur and len((prefix + cur + ch).encode()) > limit:
            parts.append(prefix + cur)
            cur, first = ch, False
        else:
            cur += ch
    if cur:
        parts.append(('' if first else ' ') + cur)
    return parts


def render(lines, nl):
    return nl.join(p for line in lines for p in fold(line)) + nl


raw = PATH.read_bytes()
text = raw.decode('utf-8')
nl = '\r\n' if b'\r\n' in raw else '\n'
assert text.count('BEGIN:VCALENDAR') == 1 and text.count('END:VCALENDAR') == 1

# Continuity: August already proposed the Kanto Tome 1, so September advances to Johto
# instead of repeating the same object.
description = '\n'.join([
    '🍂 Saison/période : rentrée en France, fin d’été et mois du 30e anniversaire du JCC Pokémon.',
    '🌟 Thème : des origines vers Johto avant la grande fête des 30 ans.',
    '⚡ Mascotte : Pikachu | 🌍 Région/génération : Kanto→Johto / Générations I–II | 🕰 Époque : 1996→1999→2026.',
    '🎮 Inspiration : JCC 30e Anniversaire, manga Pokémon La Grande Aventure, histoire et art Pokémon.',
    'Verdict : SELECTIVE BUY — profiter de Pokémon sans surpayer les précommandes 30 ans.',
    '🛒 Achats retenus :',
    '1) Admirez-les tous ! — visite libre Musée en Herbe — 8,00 € TTC — UTILISER — https://www.musee-en-herbe.com/50-ans-ca-se-fete-en-grand-lo4435.html',
    '2) Pokémon - La Grande Aventure - Or et Argent, Tome 1 (Kurokawa) — 10,00 € TTC — UTILISER — https://www.cultura.com/p-pokemon-la-grande-aventure-or-et-argent-t-1-9782368522219.html',
    '💰 TOTAL TTC : 18,00 € / 50 € | Réserve Pokédollars : 32,00 €.',
    '🧠 Anti-FOMO : l’ETB 30 ans dépasse le budget de cette Experience et plusieurs offres observées sont au-dessus du prix de référence du calendrier. Ne pas courir après une ETB chère.',
    '🎒 Rituel : visite de l’exposition puis lecture du départ vers Johto ; à la maison, créer une mini-vitrine 1996→1999→2026 avec des pièces déjà possédées.',
    '🧳 Mini-expédition <=25 € : manga Or et Argent seul à 10,00 € + rituel chronologique.',
    '🌿 No-buy 0 € : découvrir les cartes 30e Anniversaire sur Pokemon.fr, jouer à Pokémon Pocket/TCG Live avec ce que tu possèdes déjà et réorganiser 30 pièces par ordre chronologique.',
    '📅 Rappels du calendrier : 6 sept. précommande ETB 30 ans Guizette (retailer) ; 16 sept. sortie officielle JCC 30e Anniversaire ; 19 sept. précommande Bundle 6 boosters Guizette ; 20 sept. précommande Coffret Classeur Guizette.',
    '⭐ Score : 94/100 — 🟢 Badge obtenu. Émotion 20/20 | Immersion 19/20 | Culture 15/15 | Expérience 14/15 | Objets 8/10 | Plaisir/prix 9/10 | Long terme 9/10.'
])

business = [
    'BEGIN:VEVENT',
    f'UID:{UID}',
    'STATUS:CONFIRMED',
    'DTSTART;TZID=Europe/Paris:20260901T100000',
    'DTEND;TZID=Europe/Paris:20260901T103000',
    f'SUMMARY:{esc(SUMMARY)}',
    f'DESCRIPTION:{esc(description)}',
    'CATEGORIES:POKEMON,CONCIERGE,MONTHLY-EXPERIENCE',
    'X-POKEMON-CONCIERGE:YES',
    'X-POKEMON-CONCIERGE-BUDGET:50EUR',
    'X-POKEMON-CONCIERGE-MONTH:2026-09',
    'X-POKEMON-CONCIERGE-VERDICT:SELECTIVE_BUY',
    'X-POKEMON-CONCIERGE-SCORE:94',
    'URL:https://www.pokemon.com/fr/actualites/preparez-vous-pour-lextension-30-anniversaire-du-jcc-pokemon',
    'BEGIN:VALARM',
    'TRIGGER:-P1D',
    'ACTION:DISPLAY',
    'DESCRIPTION:🎒 La Pokémon Monthly Experience de septembre arrive demain',
    'END:VALARM',
    'END:VEVENT',
]

unfolded = text.replace('\r\n ', '').replace('\n ', '')
pat = re.compile(r'BEGIN:VEVENT(?:\r?\n).*?END:VEVENT(?:\r?\n)?', re.S)
old = next((m for m in pat.finditer(unfolded) if f'UID:{UID}' in m.group(0)), None)
old_seq = 0
if old:
    m = re.search(r'^SEQUENCE:(\d+)$', old.group(0), re.M)
    old_seq = int(m.group(1)) if m else 0


def norm(block: str):
    return '\n'.join(x for x in block.replace('\r\n', '\n').split('\n')
                     if x and not x.startswith(('DTSTAMP:', 'LAST-MODIFIED:', 'SEQUENCE:')))

candidate = '\n'.join(business)
if old and norm(old.group(0)) == norm(candidate):
    print('Monthly Experience already current; no change.')
    raise SystemExit(0)

seq = old_seq + 1 if old else 0
lines = [business[0], business[1], f'DTSTAMP:{STAMP}', f'LAST-MODIFIED:{STAMP}', f'SEQUENCE:{seq}', *business[2:]]
event = render(lines, nl)

if old:
    pos = text.find(f'UID:{UID}')
    start = text.rfind('BEGIN:VEVENT', 0, pos)
    end = text.find('END:VEVENT', pos) + len('END:VEVENT')
    if text.startswith('\r\n', end): end += 2
    elif text.startswith('\n', end): end += 1
    text = text[:start] + event + text[end:]
else:
    idx = text.index('END:VCALENDAR')
    prefix = text[:idx]
    if prefix and not prefix.endswith(('\r\n', '\n')): prefix += nl
    text = prefix + event + text[idx:]

text = text.replace('\r\n', '\n').replace('\n', nl)
assert text.count(f'UID:{UID}') == 1
assert text.count('BEGIN:VEVENT') == text.count('END:VEVENT')
assert text.rstrip().endswith('END:VCALENDAR')
assert 'X-POKEMON-CONCIERGE:YES' in text
PATH.write_bytes(text.encode('utf-8'))
print(f'Applied {UID} with SEQUENCE:{seq}')
