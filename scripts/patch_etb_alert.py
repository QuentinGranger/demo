from pathlib import Path
import re
from datetime import datetime, timezone

SOURCE = Path('calendars/pokemon-tcg-france.ics')
UID = 'UID:watch-etb-30ans-fr-20260830@openai'
URL = 'https://www.play-in.com/fr/produit/659570/coffret-dresseur-d-elite-etb-pokemon-30-ans-fr'
ALERT_LINK = f'X-POKEMON-ALERT-LINK;RETAILER=Playin;STATUS=OUT_OF_STOCK;CONFIDENCE=81;SELLER=95:{URL}'

text = SOURCE.read_text(encoding='utf-8')
pos = text.find(UID)
if pos < 0:
    raise SystemExit('ETB watch event not found')

start = text.rfind('BEGIN:VEVENT\n', 0, pos)
end = text.find('\nEND:VEVENT', pos)
if start < 0 or end < 0:
    raise SystemExit('ETB watch event boundaries not found')
end += len('\nEND:VEVENT')
block = text[start:end]

# Preserve all prior retailer history and append this event only once.
if ALERT_LINK not in block:
    alert_lines = list(re.finditer(r'^X-POKEMON-ALERT-LINK.*$', block, flags=re.M))
    if alert_lines:
        insert_at = alert_lines[-1].end()
        block = block[:insert_at] + '\n' + ALERT_LINK + block[insert_at:]
    else:
        anchor = 'DTSTART;VALUE=DATE:20260830'
        block = block.replace(anchor, ALERT_LINK + '\n' + anchor, 1)

seq_match = re.search(r'^SEQUENCE:(\d+)$', block, flags=re.M)
sequence = int(seq_match.group(1)) + 1 if seq_match else 1
now_utc = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

replacements = {
    r'^LAST-MODIFIED:.*$': f'LAST-MODIFIED:{now_utc}',
    r'^SEQUENCE:\d+$': f'SEQUENCE:{sequence}',
    r'^SUMMARY:.*$': 'SUMMARY:⚫ ÉPUISÉ — Playin — ETB 30 ans',
    r'^LOCATION:.*$': 'LOCATION:France — Playin / en ligne',
    r'^DESCRIPTION:.*$': ('DESCRIPTION:⚫ ÉPUISÉ/FERMÉ\\n\\n'
        'Playin — première fiche ETB 30 ans FR détectée ; sortie affichée le 16/09/2026 ; livraison actuellement indisponible avec rupture temporaire.\\n'
        'Prix : non publié | score : —\\n'
        'Date/heure Europe/Paris : aucune ouverture annoncée | limite/client : non indiquée | retrait : selon disponibilité magasin\\n'
        'Confiance produit : 81/100 | SELLER_RELIABILITY : 95/100 TRUSTED\\n'
        'INFO À SURVEILLER'),
    r'^URL:.*$': f'URL:{URL}',
    r'^X-POKEMON-LATEST-ALERT-LEVEL:.*$': 'X-POKEMON-LATEST-ALERT-LEVEL:BLACK_OUT_OF_STOCK',
    r'^X-POKEMON-LATEST-ALERT-RETAILER:.*$': 'X-POKEMON-LATEST-ALERT-RETAILER:Playin',
    r'^X-POKEMON-LATEST-ALERT-STATUS:.*$': 'X-POKEMON-LATEST-ALERT-STATUS:OUT_OF_STOCK',
    r'^X-POKEMON-LATEST-ALERT-CONFIDENCE:.*$': 'X-POKEMON-LATEST-ALERT-CONFIDENCE:81',
    r'^X-POKEMON-LATEST-SELLER-RELIABILITY:.*$': 'X-POKEMON-LATEST-SELLER-RELIABILITY:95',
    r'^X-POKEMON-LATEST-ALERT-AT:.*$': 'X-POKEMON-LATEST-ALERT-AT:20260831T132830+0200',
}
for pattern, replacement in replacements.items():
    block, count = re.subn(pattern, replacement, block, count=1, flags=re.M)
    if count == 0 and pattern.startswith('^X-POKEMON-LATEST-SELLER-RELIABILITY'):
        anchor = 'X-POKEMON-LATEST-ALERT-AT:'
        block = block.replace(anchor, replacement + '\n' + anchor, 1)

text = text[:start] + block + text[end:]
SOURCE.write_text(text, encoding='utf-8')
