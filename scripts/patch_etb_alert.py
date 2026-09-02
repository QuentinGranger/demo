from pathlib import Path
import re
from datetime import datetime, timezone

SOURCE = Path('calendars/pokemon-tcg-france.ics')
UID = 'UID:watch-etb-30ans-fr-20260830@openai'
URL = 'https://www.atmos-arena.com/product/fr-pokemon-30-ans-30c-etb-precommande/'
ALERT_LINK = f'X-POKEMON-ALERT-LINK;RETAILER=Atmos-Arena;STATUS=PREORDER_OPEN;CONFIDENCE=82;SELLER=90;PRICE=259.00:{URL}'

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

latest_description = (
    'DESCRIPTION:🔴 PRÉCO OUVERTE\\n\\n'
    "Atmos Arena — précommande ouverte pour l’ETB Pokémon JCC 30e Anniversaire FR ; EAN exact et bouton Ajouter au panier actif. Offre exploitable mais très au-dessus du prix de référence.\\n"
    'Prix : 259,00 € TTC | score D | écart vs 62,99 € : +196,01 € | livraison : calculée au checkout\\n'
    'Date/heure Europe/Paris : détectée au 02/09/2026 07:14 | limite/client : non publiée | retrait : boutique physique Paris confirmée, disponibilité retrait produit non confirmée\\n'
    'Confiance produit : 82/100 | SELLER_RELIABILITY : 90/100 TRUSTED | EAN 0196214144835\\n'
    'ATTENDS UNE MEILLEURE OFFRE'
)
block, count = re.subn(r'^DESCRIPTION:.*?(?=^URL:)', latest_description + '\n', block, count=1, flags=re.M | re.S)
if count != 1:
    raise SystemExit('ETB DESCRIPTION block not replaced exactly once')

replacements = {
    r'^LAST-MODIFIED:.*$': f'LAST-MODIFIED:{now_utc}',
    r'^SEQUENCE:\d+$': f'SEQUENCE:{sequence}',
    r'^SUMMARY:.*$': 'SUMMARY:🔴 PRÉCO OUVERTE — Atmos Arena — ETB 30 ans',
    r'^LOCATION:.*$': 'LOCATION:France — Atmos Arena',
    r'^URL:.*$': f'URL:{URL}',
    r'^X-POKEMON-LATEST-ALERT-LEVEL:.*$': 'X-POKEMON-LATEST-ALERT-LEVEL:PREORDER_OPEN',
    r'^X-POKEMON-LATEST-ALERT-RETAILER:.*$': 'X-POKEMON-LATEST-ALERT-RETAILER:Atmos-Arena',
    r'^X-POKEMON-LATEST-ALERT-STATUS:.*$': 'X-POKEMON-LATEST-ALERT-STATUS:PREORDER_OPEN',
    r'^X-POKEMON-LATEST-ALERT-CONFIDENCE:.*$': 'X-POKEMON-LATEST-ALERT-CONFIDENCE:82',
    r'^X-POKEMON-LATEST-SELLER-RELIABILITY:.*$': 'X-POKEMON-LATEST-SELLER-RELIABILITY:90',
    r'^X-POKEMON-LATEST-ALERT-AT:.*$': 'X-POKEMON-LATEST-ALERT-AT:20260902T071400+0200',
}
for pattern, replacement in replacements.items():
    block, count = re.subn(pattern, replacement, block, count=1, flags=re.M)
    if count == 0 and pattern.startswith('^X-POKEMON-LATEST-SELLER-RELIABILITY'):
        anchor = 'X-POKEMON-LATEST-ALERT-AT:'
        block = block.replace(anchor, replacement + '\n' + anchor, 1)

text = text[:start] + block + text[end:]
SOURCE.write_text(text, encoding='utf-8')
