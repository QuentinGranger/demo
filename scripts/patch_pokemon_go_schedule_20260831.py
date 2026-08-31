from pathlib import Path
import re

p = Path('calendars/pokemon-paris.ics')
data = p.read_bytes().decode('utf-8')
nl = '\r\n' if '\r\n' in data else '\n'

EVENTS = [
'''BEGIN:VEVENT
UID:pokemon-go-pass-september-20260908@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:DIGITAL_EVENT_IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:68
DTSTART;TZID=Europe/Paris:20260908T100000
DTEND;TZID=Europe/Paris:20261006T100000
SUMMARY:⭐ ✅ 📱 Pokémon GO — Passe GO : septembre — Latios
LOCATION:Pokémon GO — France
DESCRIPTION:Événement officiel Pokémon GO. Le Passe GO de septembre est disponible du 8 septembre 2026 à 10:00 au 6 octobre 2026 à 10:00, heure locale. Récompense vedette : rencontre avec Latios. Les 3 et 4 octobre, la limite journalière de Points GO est levée. Les récompenses non récupérées expirent le 8 octobre à 10:00. Source : https://pokemongo.com/fr/news/go-pass-september-2026
URL:https://pokemongo.com/fr/news/go-pass-september-2026
CATEGORIES:Pokémon,Pokémon GO,Passe GO,Événement,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:📱 Passe GO de septembre demain — Latios et nouvelles récompenses
END:VALARM
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-pass-september-rewards-expiry-20261008@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:DEADLINE_IMPORTANT
X-POKEMON-ACTION:CLAIM
X-POKEMON-DATE-PRECISION:EXACT_DATETIME
X-POKEMON-CONFIDENCE:99
X-POKEMON-ACTIONABILITY:78
DTSTART;TZID=Europe/Paris:20261008T094500
DTEND;TZID=Europe/Paris:20261008T100000
SUMMARY:⏳ Fin de récupération — Passe GO septembre
LOCATION:Pokémon GO — en ligne
DESCRIPTION:Les récompenses du Passe GO de septembre expirent le 8 octobre 2026 à 10:00, heure locale. Récupère les récompenses avant la deadline. Source : https://pokemongo.com/fr/news/go-pass-september-2026
URL:https://pokemongo.com/fr/news/go-pass-september-2026
CATEGORIES:Pokémon,Pokémon GO,Deadline,Passe GO
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:⏳ Passe GO septembre — récompenses à récupérer avant demain 10h
END:VALARM
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-community-classic-20260912@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20260912
DTEND;VALUE=DATE:20260913
SUMMARY:⭐ ✅ 📱 Pokémon GO — Classique de la Journée Communauté
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée pour la saison suivante : Classique de la Journée Communauté le 12 septembre 2026. Aucun horaire n'est publié dans l'annonce « Notez bien les dates », donc aucune heure n'est inventée. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Journée Communauté,Événement
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-super-mega-raid-day-20260919@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20260919
DTEND;VALUE=DATE:20260920
SUMMARY:⭐ ✅ 📱 Pokémon GO — Journée de Super Méga-Raids
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée de Super Méga-Raids le 19 septembre 2026. L'annonce ne donne pas encore d'horaire, donc l'événement reste en journée entière. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Raid,Événement
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-catch-mastery-20260926@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20260926
DTEND;VALUE=DATE:20260927
SUMMARY:ℹ️ ✅ 📱 Pokémon GO — Maîtrise de capture
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : événement Maîtrise de capture le 26 septembre 2026. Aucun horaire officiel n'est encore publié dans l'annonce. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Événement,Priorité Info
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-dynamax-battle-day-20261003@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261003
DTEND;VALUE=DATE:20261004
SUMMARY:ℹ️ ✅ 📱 Pokémon GO — Journée Combat Dynamax
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée Combat Dynamax le 3 octobre 2026. Aucun horaire officiel n'est encore publié dans l'annonce. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Dynamax,Événement,Priorité Info
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-community-day-20261010@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261010
DTEND;VALUE=DATE:20261011
SUMMARY:⭐ ✅ 📱 Pokémon GO — Journée Communauté — 10 octobre
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée Communauté le 10 octobre 2026. Aucun Pokémon vedette ni horaire n'est publié dans l'annonce initiale ; aucune précision n'est inventée. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Journée Communauté,Événement
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-hatch-day-20261017@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261017
DTEND;VALUE=DATE:20261018
SUMMARY:ℹ️ ✅ 📱 Pokémon GO — Journée Éclosion
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée Éclosion le 17 octobre 2026. Aucun horaire officiel n'est encore publié. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Éclosion,Événement,Priorité Info
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-dynamax-battle-day-20261024@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261024
DTEND;VALUE=DATE:20261025
SUMMARY:ℹ️ ✅ 📱 Pokémon GO — Journée Combat Dynamax — 24 octobre
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée Combat Dynamax le 24 octobre 2026. Aucun horaire officiel n'est encore publié. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Dynamax,Événement,Priorité Info
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-super-mega-raid-day-20261031@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261031
DTEND;VALUE=DATE:20261101
SUMMARY:⭐ ✅ 📱 Pokémon GO — Journée de Super Méga-Raids — 31 octobre
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée de Super Méga-Raids le 31 octobre 2026. Aucun horaire officiel n'est encore publié. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Raid,Événement
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-community-day-20261121@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261121
DTEND;VALUE=DATE:20261122
SUMMARY:⭐ ✅ 📱 Pokémon GO — Journée Communauté — 21 novembre
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée Communauté le 21 novembre 2026. Aucun Pokémon vedette ni horaire n'est publié dans l'annonce initiale. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Journée Communauté,Événement
END:VEVENT''',
'''BEGIN:VEVENT
UID:pokemon-go-super-mega-raid-day-20261128@openai
DTSTAMP:20260831T045947Z
LAST-MODIFIED:20260831T045947Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-ACTION:PLAY
X-POKEMON-DATE-PRECISION:EXACT_DATE
X-POKEMON-CONFIDENCE:98
DTSTART;VALUE=DATE:20261128
DTEND;VALUE=DATE:20261129
SUMMARY:⭐ ✅ 📱 Pokémon GO — Journée de Super Méga-Raids — 28 novembre
LOCATION:Pokémon GO — France
DESCRIPTION:Date officielle publiée : Journée de Super Méga-Raids le 28 novembre 2026. Aucun horaire officiel n'est encore publié. Source : https://pokemongo.com/fr/news/save-the-date-s24
URL:https://pokemongo.com/fr/news/save-the-date-s24
CATEGORIES:Pokémon,Pokémon GO,Raid,Événement
END:VEVENT'''
]

for raw in EVENTS:
    raw = raw.replace('\n', nl)
    uid = re.search(r'^UID:(.+?)\r?$', raw, flags=re.M).group(1).strip()
    if f'UID:{uid}' not in data:
        data = data.replace('END:VCALENDAR' + nl, raw + nl + 'END:VCALENDAR' + nl)

if data.count('BEGIN:VCALENDAR') != 1 or data.count('END:VCALENDAR') != 1:
    raise SystemExit('Invalid VCALENDAR envelope')
uids = re.findall(r'^UID:(.+?)\r?$', data, flags=re.M)
if len(uids) != len(set(uids)):
    raise SystemExit('Duplicate UID detected')
for event in EVENTS:
    uid = re.search(r'^UID:(.+?)$', event, flags=re.M).group(1).strip()
    if f'UID:{uid}' not in data:
        raise SystemExit(f'Missing expected UID: {uid}')

p.write_bytes(data.encode('utf-8'))
