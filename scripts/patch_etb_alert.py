from pathlib import Path
import re
from datetime import datetime, timezone

SOURCE = Path('calendars/pokemon-tcg-france.ics')
UID = 'UID:watch-etb-30ans-fr-20260830@openai'
URL = 'https://comptoirdesecoliers.com/index.php/produit/pokemon-30-anniversaire-etb-pre-commande-en-attente/'
ALERT_LINK = f'X-POKEMON-ALERT-LINK;RETAILER=Comptoir-des-Ecoliers;STATUS=PREORDER_CLOSED;CONFIDENCE=82;SELLER=89;PRICE=69.95:{URL}'

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

latest_description = (
    'DESCRIPTION:⚫ ÉPUISÉ / PRÉCOMMANDE FERMÉE\\n\\n'
    "Comptoir des Écoliers / FANTASIO — l’ETB Pokémon JCC 30e Anniversaire FR est repassée en rupture de stock après une fenêtre de précommande ouverte plus tôt aujourd’hui.\\n"
    'Prix : 69,95 € | score A | écart vs 62,99 € : +6,96 € | commande actuellement impossible\\n'
    'Date/heure Europe/Paris : constat au 09/09/2026 20:49 | limite : 1 commande/jour, même produit non renouvelable | retrait : Villeurbanne proposé par la boutique\\n'
    'Confiance produit : 82/100 | SELLER_RELIABILITY : 89/100 TRUSTED | EAN 0196214144835\\n'
    'INFO À SURVEILLER'
)
block, count = re.subn(r'^DESCRIPTION:.*?(?=^URL:)', latest_description + '\n', block, count=1, flags=re.M | re.S)
if count != 1:
    raise SystemExit('ETB DESCRIPTION block not replaced exactly once')

replacements = {
    r'^LAST-MODIFIED:.*$': f'LAST-MODIFIED:{now_utc}',
    r'^SEQUENCE:\d+$': f'SEQUENCE:{sequence}',
    r'^SUMMARY:.*$': 'SUMMARY:⚫ ÉPUISÉ — Comptoir des Écoliers — ETB 30 ans',
    r'^LOCATION:.*$': 'LOCATION:France — Comptoir des Écoliers / FANTASIO',
    r'^URL:.*$': f'URL:{URL}',
    r'^X-POKEMON-LATEST-ALERT-LEVEL:.*$': 'X-POKEMON-LATEST-ALERT-LEVEL:OUT_OF_STOCK',
    r'^X-POKEMON-LATEST-ALERT-RETAILER:.*$': 'X-POKEMON-LATEST-ALERT-RETAILER:Comptoir-des-Ecoliers',
    r'^X-POKEMON-LATEST-ALERT-STATUS:.*$': 'X-POKEMON-LATEST-ALERT-STATUS:PREORDER_CLOSED',
    r'^X-POKEMON-LATEST-ALERT-CONFIDENCE:.*$': 'X-POKEMON-LATEST-ALERT-CONFIDENCE:82',
    r'^X-POKEMON-LATEST-SELLER-RELIABILITY:.*$': 'X-POKEMON-LATEST-SELLER-RELIABILITY:89',
    r'^X-POKEMON-LATEST-ALERT-AT:.*$': 'X-POKEMON-LATEST-ALERT-AT:20260909T204900+0200',
}
for pattern, replacement in replacements.items():
    block, count = re.subn(pattern, replacement, block, count=1, flags=re.M)
    if count == 0 and pattern.startswith('^X-POKEMON-LATEST-SELLER-RELIABILITY'):
        anchor = 'X-POKEMON-LATEST-ALERT-AT:'
        block = block.replace(anchor, replacement + '\n' + anchor, 1)

text = text[:start] + block + text[end:]
SOURCE.write_text(text, encoding='utf-8')
