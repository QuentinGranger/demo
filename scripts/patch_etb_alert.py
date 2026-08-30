from pathlib import Path

SOURCE = Path('calendars/pokemon-tcg-france.ics')
UID = 'UID:watch-etb-30ans-fr-20260830@openai'
URL = 'https://lestresorsdekanto.com/products/etb-30-ans-me5-5'

text = SOURCE.read_text(encoding='utf-8')
pos = text.find(UID)
if pos < 0:
    raise SystemExit('ETB watch event not found')

start = text.rfind('BEGIN:VEVENT\n', 0, pos)
end = text.find('\nEND:VEVENT', pos)
if start < 0 or end < 0:
    raise SystemExit('ETB watch event boundaries not found')
end += len('\nEND:VEVENT')

block = f'''BEGIN:VEVENT
UID:watch-etb-30ans-fr-20260830@openai
DTSTAMP:20260830T051000Z
LAST-MODIFIED:20260830T072434Z
SEQUENCE:4
STATUS:CONFIRMED
PRIORITY:1
X-POKEMON-PRIORITY:CRITICAL
X-POKEMON-REMINDER-PROFILE:PREORDER_WATCH
X-POKEMON-ACTION:MONITOR
X-POKEMON-GROUP-ID:TCG-30TH-LAUNCH-20260916
RELATED-TO;RELTYPE=PARENT:74a1a108-68cd-4c81-b8f1-9206bfa31970@openai
X-POKEMON-PRODUCT-EAN:0196214144835
X-POKEMON-PRODUCT-UPC:196214144835
X-POKEMON-DISTRIBUTOR-REFS:POK1010447102|POK2114483|CLD-169049
X-POKEMON-CLD-AVAILABILITY-DATE:20260915
X-POKEMON-RETAIL-STREET-DATE:20260916
X-POKEMON-WATCH-MODE:ZERO_MISS_ULTRA
X-POKEMON-WATCH-FREQUENCY:HOURLY
X-POKEMON-REFERENCE-PRICE-EUR:62.99
X-POKEMON-PRICE-BANDS:SPLUS_LE_59.99|S_60_62.99|A_63_69.99|B_70_79.99|C_80_99.99|D_GE_100
X-POKEMON-WATCH-TIER0:Pokemon|CLD-Distribution
X-POKEMON-WATCH-TIER1:Fnac|Cultura|Micromania|Carrefour|E.Leclerc|Auchan|Amazon-FR|Smyths|JoueClub|King-Jouet
X-POKEMON-ALERT-LINK;RETAILER=Carrefour;STATUS=PREOPEN;CONFIDENCE=92:https://www.carrefour.fr/p/cartes-a-jouer-et-a-collectionner-coffret-dresseur-d-elite-30e-anniversaire-pokemon-0196214144835
X-POKEMON-ALERT-LINK;RETAILER=Micromania;STATUS=INDEXED;CONFIDENCE=78:https://www.micromania.fr/c/carte-pokemon-30-ans
X-POKEMON-ALERT-LINK;RETAILER=CLD-Distribution;STATUS=DISTRIBUTOR;CONFIDENCE=95:https://cld.eu/
X-POKEMON-ALERT-LINK;RETAILER=Foxchip-Collector;STATUS=OUT_OF_STOCK;CONFIDENCE=82:https://www.foxchip-collector.com/fr/coffrets-dresseur-d-elite-etb/81311-coffret-dresseur-d-elite-pokemon-30e-anniversaire-0196214144835.html
X-POKEMON-ALERT-LINK;RETAILER=Les-Tresors-de-Kanto;STATUS=PREORDER_LOW_STOCK;CONFIDENCE=82:{URL}
DTSTART;VALUE=DATE:20260830
DTEND;VALUE=DATE:20260917
SUMMARY:🔴 PRÉCO OUVERTE — Les Trésors de Kanto — ETB 30 ans
LOCATION:France / Europe — en ligne
DESCRIPTION:🔴 PRÉCO OUVERTE\\n\\nLes Trésors de Kanto — précommande ETB 30 ans FR ouverte, stock faible, EAN exact 0196214144835.\\nPrix : 74,90 € | livré : ≥ 74,90 € (frais calculés au checkout) | score : B minimum | écart vs 62,99 € : +11,91 €\\nDate : 16/09/2026 | limite/client : non indiquée | retrait magasin : non indiqué\\nConfiance : 82/100 | EAN : 0196214144835\\n🔗 Ouvrir la fiche Les Trésors de Kanto : {URL}\\n📅 Calendrier : ajouté + lien direct + synchronisation vérifiée dans pokemon-tcg-france.ics et pokemon-paris.ics\\nATTENDS UNE MEILLEURE OFFRE
URL:{URL}
X-POKEMON-LATEST-ALERT-LEVEL:RED_PREORDER_OPEN
X-POKEMON-LATEST-ALERT-RETAILER:Les-Tresors-de-Kanto
X-POKEMON-LATEST-ALERT-STATUS:PREORDER_LOW_STOCK
X-POKEMON-LATEST-ALERT-CONFIDENCE:82
X-POKEMON-LATEST-ALERT-AT:20260830T092434+0200
CATEGORIES:Pokémon,TCG,Précommande,Surveillance,30e Anniversaire,Priorité Critique
BEGIN:VALARM
TRIGGER;VALUE=DATE-TIME:20260902T080000Z
ACTION:DISPLAY
DESCRIPTION:🔥 ETB 30 ans — point préco J-14 : vérifie les retailers TIER 1
END:VALARM
BEGIN:VALARM
TRIGGER;VALUE=DATE-TIME:20260909T080000Z
ACTION:DISPLAY
DESCRIPTION:🔥 ETB 30 ans — point préco J-7 : vérifie prix, comptes et paiement
END:VALARM
BEGIN:VALARM
TRIGGER;VALUE=DATE-TIME:20260913T080000Z
ACTION:DISPLAY
DESCRIPTION:🔥 ETB 30 ans — point préco J-3 : vérifie stock et click & collect
END:VALARM
BEGIN:VALARM
TRIGGER;VALUE=DATE-TIME:20260915T080000Z
ACTION:DISPLAY
DESCRIPTION:🚨 ETB 30 ans demain — prépare achat et retrait magasin
END:VALARM
END:VEVENT'''

text = text[:start] + block + text[end:]
SOURCE.write_text(text, encoding='utf-8')
