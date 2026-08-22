#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
NOW = "2026-08-22T01:54:24Z"
NOW_ICS = "20260822T015424Z"

EVENTS = {
"hp-marathon-arcueil-20260826@openai": """BEGIN:VEVENT
UID:hp-marathon-arcueil-20260826@openai
DTSTAMP:20260822T015424Z
LAST-MODIFIED:20260822T015424Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-HARRYPOTTER-PRIORITY:IMPORTANT
X-HARRYPOTTER-REMINDER-PROFILE:EVENT_IMPORTANT
X-HARRYPOTTER-ACTION:ATTEND
X-HARRYPOTTER-EVENT-TYPE:CINEMA_MARATHON
X-HARRYPOTTER-FORMAT:CINEMA_RUN
X-HARRYPOTTER-MARKET:FR
X-HARRYPOTTER-SOURCE-ID:arcueil-jean-vilar
X-HARRYPOTTER-RUN-MODE:DATE_RANGE
X-HARRYPOTTER-SESSION-MODE:ONE_RUN_NOT_EACH_SHOW
X-HARRYPOTTER-FIRST-ADDED-AT:20260822T015424Z
X-HARRYPOTTER-NEW-UNTIL:20260827T015424Z
X-HARRYPOTTER-FRESHNESS:NEW
X-HARRYPOTTER-BADGE:NEW
DTSTART;VALUE=DATE:20260826
DTEND;VALUE=DATE:20260831
SUMMARY:⭐ ✅ 🆕 🎬 Marathon Harry Potter — Arcueil
LOCATION:Espace municipal Jean Vilar\, 1 rue Paul Signac\, 94110 Arcueil\, France
X-HARRYPOTTER-LOCATION-PRECISION:BUILDING
X-HARRYPOTTER-ACCESS-MODE:TICKET
X-HARRYPOTTER-TICKET-PRICE-MIN-EUR:4.00
X-HARRYPOTTER-TICKET-PRICE-MAX-EUR:6.00
DESCRIPTION:Priorité : ⭐ Important — marathon officiel des huit films à Arcueil\, en Île-de-France.\\nFiabilité : ✅ Confirmé directement par la Ville d'Arcueil / Espace Jean Vilar.\\nPériode : du 26 au 30 août 2026 ; la programmation municipale répartit les huit films sur le run.\\nTarifs publiés par film : 6 € plein tarif\, 5 € réduit\, moins de 18 ans 4 €.\\n📍 Espace municipal Jean Vilar — 1 rue Paul Signac\, 94110 Arcueil.\\nRappel : J-1 uniquement\, le jalon J-7 étant déjà passé lors de l'ajout.\\nSource : https://www.arcueil.fr/evenement/marathon-harry-potter-a-lespace-jean-vilar/
URL:https://www.arcueil.fr/evenement/marathon-harry-potter-a-lespace-jean-vilar/
CATEGORIES:Harry Potter,Événement,Île-de-France,Arcueil,Cinéma,Marathon,Nouveau,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:🎬 Marathon Harry Potter à Arcueil demain — vérifie la séance souhaitée
END:VALARM
END:VEVENT""",
"hp-droneart-paris-20260930@openai": """BEGIN:VEVENT
UID:hp-droneart-paris-20260930@openai
DTSTAMP:20260822T015424Z
LAST-MODIFIED:20260822T015424Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-HARRYPOTTER-PRIORITY:IMPORTANT
X-HARRYPOTTER-REMINDER-PROFILE:PARIS_EXPERIENCE_IMPORTANT
X-HARRYPOTTER-ACTION:ATTEND
X-HARRYPOTTER-EVENT-TYPE:EXPERIENCE
X-HARRYPOTTER-FORMAT:DRONE_SHOW
X-HARRYPOTTER-MARKET:FR
X-HARRYPOTTER-SOURCE-ID:droneart-harry-potter-paris
X-HARRYPOTTER-RUN-MODE:SPARSE_DATES
X-HARRYPOTTER-SESSION-MODE:ONE_RUN_NOT_EACH_SHOW
X-HARRYPOTTER-SESSION-TIME-1:20260930T204500
X-HARRYPOTTER-SESSION-TIME-2:20261001T204500
X-HARRYPOTTER-SESSION-TIME-3:20261003T204500
X-HARRYPOTTER-SESSION-TIME-4:20261007T204500
X-HARRYPOTTER-SESSION-TIME-5:20261008T204500
X-HARRYPOTTER-SESSION-TIME-6:20261010T204500
X-HARRYPOTTER-DOORS-TIME:18:45
X-HARRYPOTTER-FIRST-ADDED-AT:20260822T015424Z
X-HARRYPOTTER-NEW-UNTIL:20260827T015424Z
X-HARRYPOTTER-FRESHNESS:NEW
X-HARRYPOTTER-BADGE:NEW
DTSTART;VALUE=DATE:20260930
DTEND;VALUE=DATE:20261011
SUMMARY:⭐ ✅ 🆕 ✨ DroneArt Show: Harry Potter — Paris-Vincennes
LOCATION:Hippodrome de Paris-Vincennes\, 2 route de la Ferme\, 75012 Paris\, France
X-HARRYPOTTER-LOCATION-PRECISION:VENUE
X-HARRYPOTTER-TICKET-STATUS:ON_SALE
X-HARRYPOTTER-TICKET-PROVIDER:DroneArt / Fever
X-HARRYPOTTER-TICKET-PROVIDER-ID:droneart-paris
X-HARRYPOTTER-TICKET-URL:https://thedroneartshow.com/paris/harry-potter/
X-HARRYPOTTER-ACCESS-MODE:TICKET
DESCRIPTION:Priorité : ⭐ Important — expérience Harry Potter officielle/licenciée à Paris avec 1 200 drones et musique live.\\nFiabilité : ✅ Confirmé par l'organisateur direct DroneArt.\\nDates : 30 septembre ; 1\, 3\, 7\, 8 et 10 octobre 2026. Chaque spectacle commence à 20h45 ; portes à 18h45 ; durée annoncée environ 60 minutes.\\nAccès : aucune restriction d'âge annoncée ; lieu accessible PMR ; retardataires susceptibles de ne pas être admis.\\n📍 Hippodrome de Paris-Vincennes — 2 route de la Ferme\, 75012 Paris.\\n🎟️ Billets en vente en ligne via l'organisateur/Fever ; pas de vente sur place selon la FAQ.\\nRappels : J-30\, J-7 et J-1 avant la première date.\\nSource : https://thedroneartshow.com/paris/harry-potter/
URL:https://thedroneartshow.com/paris/harry-potter/
CATEGORIES:Harry Potter,Événement,Paris,Île-de-France,Expérience,DroneArt,Nouveau,Priorité Important
BEGIN:VALARM
TRIGGER:-P30D
ACTION:DISPLAY
DESCRIPTION:✨ DroneArt Harry Potter Paris dans 30 jours — vérifie billets et date
END:VALARM
BEGIN:VALARM
TRIGGER:-P7D
ACTION:DISPLAY
DESCRIPTION:✨ DroneArt Harry Potter Paris dans 7 jours — vérifie billet et trajet
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:✨ DroneArt Harry Potter Paris commence demain — portes 18h45, show 20h45
END:VALARM
END:VEVENT"""
}


def append_events(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    changed = False
    for uid, block in EVENTS.items():
        if f"UID:{uid}" in text:
            continue
        marker = "END:VCALENDAR"
        if marker not in text:
            raise RuntimeError(f"{path} missing END:VCALENDAR")
        text = text.replace(marker, block + "\n" + marker, 1)
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8", newline="")
    return changed


def update_sources():
    path = CAL / "harry-potter-sources-france.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = {s.get("source_id") for s in data.get("sources", [])}
    additions = [
        {
            "source_id":"arcueil-jean-vilar","name":"Ville d'Arcueil / Espace Jean Vilar","authority":"VENUE_DIRECT","evidence_grade":"A","territory":"LOCAL_FR","url":"https://www.arcueil.fr/evenement/marathon-harry-potter-a-lespace-jean-vilar/","domains":["cinema_fr","small_events","paris_idf"],"expected_information":["programmation locale","dates","horaires","tarifs","lieu"],"can_confirm":["LOCAL_EVENT_DATE","LOCAL_EVENT_TIME","LOCAL_EVENT_LOCATION","LOCAL_TICKET_PRICE"],"cannot_confirm":["NATIONAL_CINEMA_DATE","OTHER_VENUE_STATUS"],"status":"ACTIVE","priority":2,"cadence":"EVENT_DRIVEN","last_verified_at":NOW
        },
        {
            "source_id":"droneart-harry-potter-paris","name":"DroneArt Show — Harry Potter Paris","authority":"ORGANIZER_DIRECT","evidence_grade":"A","territory":"LOCAL_FR","url":"https://thedroneartshow.com/paris/harry-potter/","domains":["experiences_fr","paris_idf","ticketing"],"expected_information":["dates","horaires","lieu","conditions d'accès","billetterie"],"can_confirm":["FR_EVENT_WINDOW","LOCAL_EVENT_DATE","LOCAL_EVENT_TIME","LOCAL_EVENT_LOCATION","TICKET_STATUS","ACCESS_RULES"],"cannot_confirm":["OTHER_CITY_EVENT","THIRD_PARTY_RESALE_STATUS"],"status":"ACTIVE","priority":1,"cadence":"EVENT_DRIVEN","last_verified_at":NOW
        }
    ]
    changed=False
    for s in additions:
        if s["source_id"] not in existing:
            data.setdefault("sources", []).append(s); changed=True
    if changed:
        data["updated_at"] = NOW
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return changed


def update_provider():
    path = CAL / "harry-potter-ticketing-providers-france.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    ids={p.get("provider_id") for p in data.get("providers",[])}
    if "droneart-paris" in ids: return False
    data["providers"].append({
        "provider_id":"droneart-paris","name":"DroneArt Show Paris / Fever","authority":"ORGANIZER_DIRECT","territory":"Paris","status":"ACTIVE","primary_url":"https://thedroneartshow.com/paris/harry-potter/","can_confirm":["LOCAL_EVENT_DATE","LOCAL_EVENT_TIME","SESSION_LIST","TICKET_URL","TICKET_STATUS","ACCESS_RULES","LOCAL_CANCELLATION"],"cannot_confirm":["OTHER_CITY_STATUS","SECONDARY_RESALE_STATUS"],"linked_source_id":"droneart-harry-potter-paris"
    })
    data["updated_at"] = NOW
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return True


def update_ticketing():
    path = CAL / "harry-potter-ticketing-france.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    tracked=data.setdefault("tracked",[])
    if any(x.get("event_uid")=="hp-droneart-paris-20260930@openai" for x in tracked): return False
    tracked.append({
        "event_uid":"hp-droneart-paris-20260930@openai","title":"DroneArt Show: Harry Potter — Paris-Vincennes","city":"Paris","provider":"DroneArt Show Paris / Fever","provider_id":"droneart-paris","source_id":"droneart-harry-potter-paris","ticket_url":"https://thedroneartshow.com/paris/harry-potter/","status":"ON_SALE","status_origin":"DIRECT_VERIFIED","evidence_grade":"A","confidence":"HIGH","scarcity_evidence":"UNKNOWN","check_tier":"WARM","last_verified_at":NOW,"last_changed_at":NOW,"run_start":"2026-09-30","run_end":"2026-10-10","session_states":[
            {"session_key":"2026-09-30T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]},
            {"session_key":"2026-10-01T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]},
            {"session_key":"2026-10-03T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]},
            {"session_key":"2026-10-07T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]},
            {"session_key":"2026-10-08T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]},
            {"session_key":"2026-10-10T20:45-Europe-Paris","status":"ON_SALE","confidence":"HIGH","category_states":[]}
        ],"history":[{"at":NOW,"transition":"SALE_OPENED","source_id":"droneart-harry-potter-paris","note":"Billets proposés en ligne sur la page officielle de l'expérience ; aucune rareté inférée."}]
    })
    data["updated_at"] = NOW
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return True


def main():
    changed=[]
    for rel in ["harry-potter-events-france-paris.ics","harry-potter-paris.ics"]:
        if append_events(CAL/rel): changed.append(rel)
    if update_sources(): changed.append("harry-potter-sources-france.json")
    if update_provider(): changed.append("harry-potter-ticketing-providers-france.json")
    if update_ticketing(): changed.append("harry-potter-ticketing-france.json")
    print("changed:", ", ".join(changed) if changed else "none")

if __name__ == "__main__":
    main()
