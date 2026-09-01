from pathlib import Path
import re
from datetime import datetime, timezone

SOURCE = Path('calendars/pokemon-tcg-france.ics')
UID = 'UID:watch-etb-30ans-fr-20260830@openai'
URL = 'https://www.multimediashop.be/80354-Acheter_Pok_mon_JCC_Coffret_Dresseur_d_lite_30e_Anniversaire_sur_tcard.html'
ALERT_LINK = f'X-POKEMON-ALERT-LINK;RETAILER=Multimedia-Shop;STATUS=PREORDER_RESERVATION_OPEN;CONFIDENCE=82;SELLER=95;PRICE=64.99:{URL}'

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
    'DESCRIPTION:🔴 PRÉCOMMANDE OUVERTE\\n\\n'
    "Multimedia Shop — réservation ouverte pour l’ETB Pokémon JCC 30e Anniversaire FR ; non commandable en ligne, réservation uniquement en magasin, par téléphone ou Facebook Messenger et non garantie tant que l’allocation fournisseur n’est pas confirmée.\\n"
    'Prix : 64,99 € en retrait magasin | score : A | écart vs 62,99 € : +2,00 € | livraison : non proposée sur cette fiche\\n'
    "Date/heure Europe/Paris : ouverte au 01/09/2026 04:27 | limite/client : allocation/limitation possible | retrait : magasin Braine-l’Alleud\\n"
    'Confiance produit : 82/100 | SELLER_RELIABILITY : 95/100 TRUSTED | EAN 196214144835\\n'
    'INFO À SURVEILLER'
)
block, count = re.subn(r'^DESCRIPTION:.*?(?=^URL:)', latest_description + '\n', block, count=1, flags=re.M | re.S)
if count != 1:
    raise SystemExit('ETB DESCRIPTION block not replaced exactly once')

replacements = {
    r'^LAST-MODIFIED:.*$': f'LAST-MODIFIED:{now_utc}',
    r'^SEQUENCE:\d+$': f'SEQUENCE:{sequence}',
    r'^SUMMARY:.*$': 'SUMMARY:🔴 PRÉCO OUVERTE — Multimedia Shop — ETB 30 ans',
    r'^LOCATION:.*$': "LOCATION:Belgique — Multimedia Shop / Braine-l'Alleud",
    r'^URL:.*$': f'URL:{URL}',
    r'^X-POKEMON-LATEST-ALERT-LEVEL:.*$': 'X-POKEMON-LATEST-ALERT-LEVEL:RED_PREORDER_OPEN',
    r'^X-POKEMON-LATEST-ALERT-RETAILER:.*$': 'X-POKEMON-LATEST-ALERT-RETAILER:Multimedia-Shop',
    r'^X-POKEMON-LATEST-ALERT-STATUS:.*$': 'X-POKEMON-LATEST-ALERT-STATUS:PREORDER_RESERVATION_OPEN',
    r'^X-POKEMON-LATEST-ALERT-CONFIDENCE:.*$': 'X-POKEMON-LATEST-ALERT-CONFIDENCE:82',
    r'^X-POKEMON-LATEST-SELLER-RELIABILITY:.*$': 'X-POKEMON-LATEST-SELLER-RELIABILITY:95',
    r'^X-POKEMON-LATEST-ALERT-AT:.*$': 'X-POKEMON-LATEST-ALERT-AT:20260901T042724+0200',
}
for pattern, replacement in replacements.items():
    block, count = re.subn(pattern, replacement, block, count=1, flags=re.M)
    if count == 0 and pattern.startswith('^X-POKEMON-LATEST-SELLER-RELIABILITY'):
        anchor = 'X-POKEMON-LATEST-ALERT-AT:'
        block = block.replace(anchor, replacement + '\n' + anchor, 1)

text = text[:start] + block + text[end:]
SOURCE.write_text(text, encoding='utf-8')
