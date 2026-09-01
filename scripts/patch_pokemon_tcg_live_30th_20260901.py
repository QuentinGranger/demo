from pathlib import Path
import re

P = Path('calendars/pokemon-paris.ics')
UID = 'pokemon-tcg-live-30th-20260915@openai'
SOURCE = 'https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon'

s = P.read_text(encoding='utf-8')
if f'UID:{UID}' in s:
    print('Already present')
    raise SystemExit(0)

assert s.count('BEGIN:VCALENDAR') == 1 and s.count('END:VCALENDAR') == 1
assert s.rstrip().endswith('END:VCALENDAR')

event = '''BEGIN:VEVENT\nUID:pokemon-tcg-live-30th-20260915@openai\nDTSTAMP:20260901T215500Z\nLAST-MODIFIED:20260901T215500Z\nSEQUENCE:0\nSTATUS:CONFIRMED\nPRIORITY:5\nX-POKEMON-PRIORITY:IMPORTANT\nX-POKEMON-ACTION:PLAY\nX-POKEMON-DATE-PRECISION:EXACT_DATETIME\nX-POKEMON-CONFIDENCE:99\nX-POKEMON-ACTIONABILITY:72\nDTSTART;TZID=Europe/Paris:20260915T190000\nDTEND;TZID=Europe/Paris:20260915T191500\nSUMMARY:⭐ ✅ 🃏 JCC Pokémon Live — 30e Anniversaire disponible\nLOCATION:En ligne — JCC Pokémon Live\nDESCRIPTION:Priorité : ⭐ Important — accès numérique anticipé à l'extension 30e Anniversaire avant la sortie physique du lendemain.\\nFiabilité : ✅ Confirmé par The Pokémon Company International. Les Dresseurs et Dresseuses pourront jouer avec l'extension 30e Anniversaire dans le JCC Pokémon Live à partir du 15 septembre 2026 à 19:00 CEST.\\nAction : ouvrir JCC Pokémon Live à partir de 19h pour découvrir, collectionner et jouer les nouvelles cartes.\\nSource : https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon\nURL:https://the-pokemon-company-international.prezly.com/the-pokemon-company-international-devoile-sa-gamme-de-produits-celebrant-lextension-30-anniversaire-du-jeu-de-cartes-a-collectionner-pokemon\nCATEGORIES:Pokémon,JCC Pokémon Live,30e Anniversaire,Sortie numérique,Priorité Important\nBEGIN:VALARM\nTRIGGER:-P1D\nACTION:DISPLAY\nDESCRIPTION:JCC Pokémon Live — 30e Anniversaire disponible demain à 19h\nEND:VALARM\nEND:VEVENT\n'''

idx = s.rfind('END:VCALENDAR')
assert idx >= 0
s2 = s[:idx] + event + s[idx:]

uids = re.findall(r'^UID:(.+?)\r?$', s2, flags=re.M)
assert len(uids) == len(set(uids))
assert f'UID:{UID}' in s2
assert s2.count('BEGIN:VCALENDAR') == 1 and s2.count('END:VCALENDAR') == 1

P.write_text(s2, encoding='utf-8', newline='')
print('Patched', UID)
