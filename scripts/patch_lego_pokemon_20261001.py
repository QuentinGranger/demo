from pathlib import Path

PATH = Path('calendars/pokemon-paris.ics')
UID = 'lego-pokemon-wave-20261001@openai'

EVENT_LINES = [
    'BEGIN:VEVENT',
    f'UID:{UID}',
    'DTSTAMP:20260902T073400Z',
    'LAST-MODIFIED:20260902T073400Z',
    'SEQUENCE:0',
    'STATUS:CONFIRMED',
    'PRIORITY:5',
    'X-POKEMON-PRIORITY:IMPORTANT',
    'X-POKEMON-REMINDER-PROFILE:PRODUCT_RELEASE',
    'X-POKEMON-ACTION:BUY',
    'X-POKEMON-WAVE-ID:LEGO-POKEMON-20261001',
    'X-POKEMON-WAVE-COMPLETENESS:PARTIAL',
    'X-POKEMON-WAVE-PRODUCT-COUNT:2',
    'X-POKEMON-WAVE-PREORDER-COUNT:2',
    'X-POKEMON-WAVE-PRODUCTS:Poké Ball Moments culte de Dresseur #72154|Minifigurine de Red grand format #40868',
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Poké Ball Moments culte de Dresseur #72154',
    'X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Minifigurine de Red grand format #40868',
    'X-POKEMON-RETAILER-OFFER;SELLER=LEGO France;TYPE=OFFICIAL;CHANNEL=WEB;STATUS=PREORDER;DATE=20261001;PRICE=259.99:https://www.lego.com/fr-fr/product/iconic-trainer-moments-poke-ball-72154',
    'X-POKEMON-RETAILER-OFFER;SELLER=LEGO France;TYPE=OFFICIAL;CHANNEL=WEB;STATUS=PREORDER;DATE=20261001;PRICE=79.99:https://www.lego.com/fr-fr/product/up-scaled-red-minifigure-40868',
    'DTSTART;VALUE=DATE:20261001',
    'DTEND;VALUE=DATE:20261002',
    'SUMMARY:⭐ ✅ 🧱 LEGO Pokémon — expédition Poké Ball #72154 + Red #40868',
    'LOCATION:France — Boutique LEGO officielle',
    'DESCRIPTION:Priorité : ⭐ Important — deux références LEGO Pokémon officielles sont en précommande sur LEGO France.\\nFiabilité : ✅ Confirmé par les fiches produit LEGO France.\\n📦 Poké Ball Moments culte de Dresseur #72154 — 259,99 € — limite 3 — expédition à partir du 1 octobre 2026.\\n📦 Minifigurine de Red grand format #40868 — 79,99 € — limite 3 — expédition à partir du 1 octobre 2026.\\n⚠️ La date correspond explicitement au début d’expédition annoncé par LEGO France ; elle n’est pas sur-précisée comme heure de lancement.\\nSources : https://www.lego.com/fr-fr/product/iconic-trainer-moments-poke-ball-72154 ; https://www.lego.com/fr-fr/product/up-scaled-red-minifigure-40868',
    'URL:https://www.lego.com/fr-fr/themes/pokemon',
    'CATEGORIES:Pokémon,LEGO,Collector,Licence,Sortie produit,Précommande,Priorité Important',
    'BEGIN:VALARM',
    'TRIGGER:-P1D',
    'ACTION:DISPLAY',
    'DESCRIPTION:LEGO Pokémon demain — début d’expédition #72154 et #40868',
    'END:VALARM',
    'END:VEVENT',
]


def main():
    data = PATH.read_bytes()
    if not data.startswith(b'BEGIN:VCALENDAR') or not data.rstrip().endswith(b'END:VCALENDAR'):
        raise SystemExit('Invalid VCALENDAR bounds')

    # Idempotency: exact UID or exact product references already calendarized.
    text = data.decode('utf-8')
    if f'UID:{UID}' in text:
        print('No business change: UID already present')
        return

    newline = '\r\n' if b'\r\n' in data else '\n'
    event = newline.join(EVENT_LINES) + newline
    marker = ('END:VCALENDAR' + newline).encode('utf-8')
    if marker not in data:
        # tolerate final VCALENDAR without trailing newline
        marker = b'END:VCALENDAR'
    idx = data.rfind(marker)
    if idx < 0:
        raise SystemExit('END:VCALENDAR not found')

    out = data[:idx] + event.encode('utf-8') + data[idx:]
    out_text = out.decode('utf-8')

    if out_text.count(f'UID:{UID}') != 1:
        raise SystemExit('UID uniqueness validation failed')
    if out_text.count('BEGIN:VCALENDAR') != 1 or out_text.count('END:VCALENDAR') != 1:
        raise SystemExit('VCALENDAR bounds validation failed')
    if out_text.count('BEGIN:VEVENT') != out_text.count('END:VEVENT'):
        raise SystemExit('VEVENT balance validation failed')

    PATH.write_bytes(out)
    print('Added LEGO Pokémon wave 2026-10-01')


if __name__ == '__main__':
    main()
