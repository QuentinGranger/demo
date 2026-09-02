from pathlib import Path

p = Path('calendars/pokemon-paris.ics')
raw = p.read_bytes()
text = raw.decode('utf-8').replace('\r\n','\n').replace('\r','\n')

EVENTS = [
'''BEGIN:VEVENT
UID:pokemon-manga-ecarlate-violet-t4-20260903@openai
DTSTAMP:20260902T144600Z
LAST-MODIFIED:20260902T144600Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:BOOK_RELEASE
X-POKEMON-ACTION:READ
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:96
X-POKEMON-ACTIONABILITY:62
X-POKEMON-IDENTIFIER-TYPE:EAN13
X-POKEMON-IDENTIFIER:9791042021955
DTSTART;VALUE=DATE:20260903
DTEND;VALUE=DATE:20260904
SUMMARY:⭐ ✅ 📚 Manga FR — Pokémon Écarlate et Violet — Tome 4
LOCATION:France
DESCRIPTION:Sortie française du tome 4 de Pokémon Écarlate et Violet.\nÉditeur : Kurokawa.\nAuteurs : Hidenori Kusaka et Satoshi Yamamoto.\nEAN : 9791042021955.\nPrix public constaté : 7,30 €.\nDate : 3 septembre 2026.\nSources concordantes : Fnac et E.Leclerc.\nSource : https://www.fnac.com/a22717565/Les-Pokemon-Pokemon-Ecarlate-et-Violet-tome-4-Hidenori-Kusaka
URL:https://www.fnac.com/a22717565/Les-Pokemon-Pokemon-Ecarlate-et-Violet-tome-4-Hidenori-Kusaka
CATEGORIES:Pokémon,Manga,Livre,France,Sortie,Priorité Important
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-pokecologie-fr-20260930@openai
DTSTAMP:20260902T144600Z
LAST-MODIFIED:20260902T144600Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-REMINDER-PROFILE:BOOK_RELEASE
X-POKEMON-ACTION:READ
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:97
X-POKEMON-ACTIONABILITY:55
X-POKEMON-IDENTIFIER-TYPE:EAN13
X-POKEMON-IDENTIFIER:9782017901815
DTSTART;VALUE=DATE:20260930
DTEND;VALUE=DATE:20261001
SUMMARY:ℹ️ ✅ 📖 Livre FR — Pokémon : Pokécologie
LOCATION:France
DESCRIPTION:Sortie française de Pokémon : Pokécologie.\nAuteur crédité : The Pokémon Company.\nÉditeur : Hachette Jeunesse.\nFormat : relié, 208 pages.\nEAN : 9782017901815.\nPrix éditeur constaté : 12,90 €.\nDate : 30 septembre 2026.\nSources concordantes : Fnac, Decitre et librairies françaises.\nSource : https://www.fnac.com/a23281600/Les-Pokemon-Pokemon-Pokecologie-The-Pokemon-Company
URL:https://www.fnac.com/a23281600/Les-Pokemon-Pokemon-Pokecologie-The-Pokemon-Company
CATEGORIES:Pokémon,Livre,Pokécologie,France,Sortie,Priorité Info
END:VEVENT'''
]

changed = False
for event in EVENTS:
    uid = next(line[4:] for line in event.split('\n') if line.startswith('UID:'))
    if f'UID:{uid}' not in text:
        marker = '\nEND:VCALENDAR\n'
        if marker not in text:
            raise SystemExit('Invalid ICS: END:VCALENDAR missing')
        text = text.replace(marker, '\n' + event + '\nEND:VCALENDAR\n', 1)
        changed = True

# audit invariants
if text.count('BEGIN:VCALENDAR') != 1 or text.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR boundaries')
uids = [line[4:] for line in text.split('\n') if line.startswith('UID:')]
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
for event in EVENTS:
    uid = next(line[4:] for line in event.split('\n') if line.startswith('UID:'))
    if text.count(f'UID:{uid}') != 1:
        raise SystemExit(f'Expected exactly one UID {uid}')

if changed:
    p.write_bytes(text.replace('\n','\r\n').encode('utf-8'))
    print('calendar patched')
else:
    print('no business change')
