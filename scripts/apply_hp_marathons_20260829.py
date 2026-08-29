#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
NOW = "2026-08-29T01:50:55Z"

EVENTS = [
    {
        "uid": "hp-ugc-marathon-25ans-idf-20260829@openai",
        "candidate_id": "hp-ugc-marathon-25ans-idf-20260829",
        "source_id": "ugc-fr",
        "provider_id": "ugc-fr",
        "provider": "UGC",
        "title": "Marathon Harry Potter — 25 ans de magie — UGC Île-de-France",
        "city": "Île-de-France",
        "url": "https://www.ugc.fr/cinema-ugc-cine-cite-sqy-ouest.html",
        "location": "Île-de-France — cinémas UGC participants, dont SQY Ouest, Créteil et Rosny-sous-Bois",
        "dtstart": "20260829",
        "dtend": "20260831",
        "summary": "⭐ ✅ 🆕 🎬 Marathon Harry Potter — 25 ans de magie — UGC Île-de-France",
        "description": "Priorité : ⭐ Important — marathon officiel UGC des huit films pour les 25 ans de la saga.\\nFiabilité : ✅ Vérifié directement sur les pages UGC des cinémas participants.\\nPériode : samedi 29 et dimanche 30 août 2026.\\nProgramme : les huit films de la saga ; bonus inédit annoncé après Harry Potter à l'école des sorciers.\\nTarif pack annoncé par UGC : 40 € les huit films ; séances non numérotées, placement libre.\\nÎle-de-France : participation vérifiée notamment à UGC Ciné Cité SQY Ouest, UGC Ciné Cité Créteil et UGC Ciné Cité Rosny.\\nAjout le 29 août 2026 après vérification directe ; aucun rappel rétroactif n'est créé.\\nSource : https://www.ugc.fr/cinema-ugc-cine-cite-sqy-ouest.html",
        "categories": "Harry Potter,Événement,Cinéma,Marathon,25e anniversaire,Île-de-France,Nouveau,Priorité Important",
        "ticket_status": "ON_SALE",
        "ticket_url": "https://www.ugc.fr/cinema-ugc-cine-cite-sqy-ouest.html",
        "price_min": 40.0,
        "price_max": 40.0,
    },
    {
        "uid": "hp-cgr-torcy-marathon-25ans-20260829@openai",
        "candidate_id": "hp-cgr-torcy-marathon-25ans-20260829",
        "source_id": "cgr-fr",
        "provider_id": "cgr-fr",
        "provider": "CGR Cinémas",
        "title": "Marathon Harry Potter — 25 ans — CGR Torcy Marne-la-Vallée",
        "city": "Torcy / Marne-la-Vallée",
        "url": "https://www.cgrcinemas.fr/evenements/77943-harry-potter-le-marathon-des-25-ans/",
        "location": "CGR Torcy - Marne-la-Vallée, Torcy, Seine-et-Marne, France",
        "dtstart": "20260829",
        "dtend": "20260831",
        "summary": "⭐ ✅ 🆕 🎬 Marathon Harry Potter — 25 ans — CGR Torcy Marne-la-Vallée",
        "description": "Priorité : ⭐ Important — marathon anniversaire officiel CGR en Île-de-France.\\nFiabilité : ✅ Confirmé directement par CGR Torcy - Marne-la-Vallée.\\nPériode : samedi 29 et dimanche 30 août 2026.\\nProgramme : quatre films samedi puis quatre films dimanche, en VF.\\nHoraires publiés : samedi 10h30, 14h00, 17h10, 20h30 ; dimanche 10h45, 14h00, 17h10, 20h30.\\nTarifs publiés : 26 € la journée de quatre films, 48 € les huit films ; membres fidélité 20 € / 36 €.\\nAjout le 29 août 2026 après vérification directe ; aucun rappel rétroactif n'est créé.\\nSource : https://www.cgrcinemas.fr/evenements/77943-harry-potter-le-marathon-des-25-ans/",
        "categories": "Harry Potter,Événement,Cinéma,Marathon,25e anniversaire,Île-de-France,Torcy,Nouveau,Priorité Important",
        "ticket_status": "ON_SALE",
        "ticket_url": "https://www.cgrcinemas.fr/evenements/77943-harry-potter-le-marathon-des-25-ans/",
        "price_min": 20.0,
        "price_max": 48.0,
    },
]


def event_block(e):
    lines = [
        "BEGIN:VEVENT",
        f"UID:{e['uid']}",
        "DTSTAMP:20260829T015055Z",
        "LAST-MODIFIED:20260829T015055Z",
        "SEQUENCE:0",
        "STATUS:CONFIRMED",
        "PRIORITY:5",
        "X-HARRYPOTTER-PRIORITY:IMPORTANT",
        "X-HARRYPOTTER-REMINDER-PROFILE:EVENT_IMPORTANT",
        "X-HARRYPOTTER-ACTION:ATTEND",
        "X-HARRYPOTTER-EVENT-TYPE:CINEMA_MARATHON",
        "X-HARRYPOTTER-FORMAT:CINEMA_SPECIAL",
        "X-HARRYPOTTER-MARKET:FR",
        f"X-HARRYPOTTER-CANDIDATE-ID:{e['candidate_id']}",
        f"X-HARRYPOTTER-SOURCE-ID:{e['source_id']}",
        "X-HARRYPOTTER-EVIDENCE-GRADE:A",
        "X-HARRYPOTTER-COLLECTOR-INTEREST:LOW",
        "X-HARRYPOTTER-LIMITED:UNKNOWN",
        "X-HARRYPOTTER-FIRST-ADDED-AT:20260829T015055Z",
        "X-HARRYPOTTER-NEW-UNTIL:20260903T015055Z",
        "X-HARRYPOTTER-FRESHNESS:NEW",
        "X-HARRYPOTTER-BADGE:NEW",
        f"X-HARRYPOTTER-TICKET-STATUS:{e['ticket_status']}",
        f"X-HARRYPOTTER-TICKET-PROVIDER:{e['provider']}",
        f"X-HARRYPOTTER-TICKET-PROVIDER-ID:{e['provider_id']}",
        "X-HARRYPOTTER-TICKET-CONFIDENCE:HIGH",
        "X-HARRYPOTTER-TICKET-SCARCITY-EVIDENCE:UNKNOWN",
        f"X-HARRYPOTTER-TICKET-URL:{e['ticket_url']}",
        f"X-HARRYPOTTER-TICKET-PRICE-MIN-EUR:{e['price_min']:.2f}",
        f"X-HARRYPOTTER-TICKET-PRICE-MAX-EUR:{e['price_max']:.2f}",
        f"DTSTART;VALUE=DATE:{e['dtstart']}",
        f"DTEND;VALUE=DATE:{e['dtend']}",
        f"SUMMARY:{e['summary']}",
        f"LOCATION:{e['location']}",
        f"DESCRIPTION:{e['description']}",
        f"URL:{e['url']}",
        f"CATEGORIES:{e['categories']}",
        "END:VEVENT",
    ]
    return "\n".join(lines) + "\n"


def insert_events(path):
    text = path.read_text(encoding="utf-8-sig")
    changed = False
    for e in EVENTS:
        if f"UID:{e['uid']}" in text:
            continue
        marker = "END:VCALENDAR"
        if marker not in text:
            raise RuntimeError(f"{path} missing END:VCALENDAR")
        text = text.replace(marker, event_block(e) + marker, 1)
        changed = True
    if changed:
        path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")
    return changed


def update_watchlist(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = {x.get("candidate_id") for x in data.get("targets", [])}
    changed = False
    for e in EVENTS:
        if e["candidate_id"] in existing:
            continue
        data.setdefault("targets", []).append({
            "candidate_id": e["candidate_id"],
            "subject": e["title"],
            "category": "CINEMA_MARATHON",
            "status": "CALENDAR_ADDED",
            "priority": "HIGH",
            "source_ids": [e["source_id"]],
            "promotion_requirements": ["organisateur directement responsable", "date et lieu/périmètre précis", "action de réservation exploitable"],
            "last_signal_at": NOW,
            "last_checked_at": NOW,
            "calendar_uid": e["uid"],
        })
        changed = True
    if changed:
        data["updated_at"] = NOW
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def update_ticketing(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    tracked = data.setdefault("tracked", [])
    existing = {x.get("event_uid") for x in tracked}
    changed = False
    for e in EVENTS:
        if e["uid"] in existing:
            continue
        tracked.append({
            "event_uid": e["uid"],
            "title": e["title"],
            "city": e["city"],
            "provider": e["provider"],
            "provider_id": e["provider_id"],
            "source_id": e["source_id"],
            "ticket_url": e["ticket_url"],
            "status": "ON_SALE",
            "status_origin": "DIRECT_VERIFIED",
            "evidence_grade": "A",
            "confidence": "HIGH",
            "scarcity_evidence": "UNKNOWN",
            "check_tier": "HOT",
            "last_verified_at": NOW,
            "last_changed_at": NOW,
            "price_min_eur": e["price_min"],
            "price_max_eur": e["price_max"],
            "run_start": "2026-08-29",
            "run_end": "2026-08-30",
            "session_states": [],
            "history": [{
                "at": NOW,
                "transition": "SALE_OPENED",
                "from": "NOT_TRACKED",
                "to": "ON_SALE",
                "evidence": "Direct official cinema page verified on 2026-08-29",
            }],
        })
        changed = True
    if changed:
        data["updated_at"] = NOW
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def main():
    changed = []
    for name in ["harry-potter-events-france-paris.ics", "harry-potter-paris.ics"]:
        if insert_events(CAL / name):
            changed.append(name)
    if update_watchlist(CAL / "harry-potter-watchlist-france.json"):
        changed.append("harry-potter-watchlist-france.json")
    if update_ticketing(CAL / "harry-potter-ticketing-france.json"):
        changed.append("harry-potter-ticketing-france.json")
    print("changed:", ", ".join(changed) if changed else "none")


if __name__ == "__main__":
    main()
