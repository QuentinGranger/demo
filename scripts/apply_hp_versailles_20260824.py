#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
NOW = "2026-08-24T01:59:44Z"
NOW_ICS = "20260824T015944Z"

DAY_UID = "hp-back-to-hogwarts-versailles-20260829@openai"
NIGHT_UID = "hp-grandes-eaux-harry-potter-versailles-20260829@openai"

DAY_EVENT = f'''BEGIN:VEVENT
UID:{DAY_UID}
DTSTAMP:{NOW_ICS}
LAST-MODIFIED:{NOW_ICS}
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:1
X-HARRYPOTTER-PRIORITY:CRITICAL
X-HARRYPOTTER-REMINDER-PROFILE:PARIS_LIMITED
X-HARRYPOTTER-ACTION:ATTEND
X-HARRYPOTTER-EVENT-TYPE:OFFICIAL_COMMUNITY_EVENT
X-HARRYPOTTER-FORMAT:BACK_TO_HOGWARTS_GATHERING
X-HARRYPOTTER-MARKET:FR
X-HARRYPOTTER-SOURCE-ID:retourapoudlard-fr
X-HARRYPOTTER-RUN-MODE:SINGLE_DAY_MULTI_SESSION
X-HARRYPOTTER-SESSION-TIME-1:20260829T090000-120000
X-HARRYPOTTER-SESSION-TIME-2:20260829T130000-160000
X-HARRYPOTTER-SESSION-TIME-3:20260829T170000-200000
X-HARRYPOTTER-FIRST-ADDED-AT:{NOW_ICS}
X-HARRYPOTTER-NEW-UNTIL:20260829T015944Z
X-HARRYPOTTER-FRESHNESS:NEW
X-HARRYPOTTER-BADGE:NEW
DTSTART;TZID=Europe/Paris:20260829T090000
DTEND;TZID=Europe/Paris:20260829T200000
SUMMARY:🔥 ✅ 🆕 ⚡ Retour à Poudlard 2026 — Château de Versailles
LOCATION:Grille des Premières Cent Marches du Jardin de l'Orangerie\\, 3 route de Saint-Cyr\\, 78000 Versailles\\, France
X-HARRYPOTTER-LOCATION-PRECISION:ENTRANCE
X-HARRYPOTTER-TICKET-URL:https://www.retourapoudlard.com/
X-HARRYPOTTER-TICKET-STATUS:ON_SALE
X-HARRYPOTTER-TICKET-PROVIDER:Retour à Poudlard / Warner Bros. Discovery France
X-HARRYPOTTER-TICKET-PROVIDER-ID:retourapoudlard-fr
X-HARRYPOTTER-TICKET-CONFIDENCE:HIGH
X-HARRYPOTTER-TICKET-SCARCITY-EVIDENCE:UNKNOWN
X-HARRYPOTTER-ACCESS-MODE:FREE_REGISTRATION
DESCRIPTION:Priorité : 🔥 Critique — grand rassemblement officiel Retour à Poudlard en Île-de-France\\, gratuit mais sur inscription.\\nFiabilité : ✅ Confirmé par le communiqué de Château de Versailles Spectacles en partenariat avec Warner Bros. Discovery France et par le site officiel Retour à Poudlard.\\nDate : samedi 29 août 2026\\, de 9h à 20h au Jardin de l'Orangerie du Château de Versailles.\\nSessions : 9h–12h\\, 13h–16h et 17h–20h. L'accès à chaque session se fait uniquement pendant sa première heure : 9h–10h\\, 13h–14h ou 17h–18h.\\nAccès : inscription gratuite obligatoire ; pas de billets sur place ; toute sortie est définitive. Toutes les personnes doivent être inscrites.\\n📍 Entrée dédiée : Grille des Premières Cent Marches du Jardin de l'Orangerie — 3 route de Saint-Cyr\\, 78000 Versailles. L'entrée principale du Château ne donne pas accès à cet événement.\\n⚠️ Le billet gratuit de la journée ne donne PAS accès aux Grandes Eaux Nocturnes Harry Potter du soir.\\nRappel : J-1 uniquement\\, les jalons plus anciens étant déjà passés lors de l'ajout.\\nSources : https://www.retourapoudlard.com/ ; https://www.chateauversailles-spectacles.fr/app/uploads/2026/03/CP-GE-HARRY-POTTER-10mars.pdf
URL:https://www.retourapoudlard.com/
CATEGORIES:Harry Potter,Back to Hogwarts,Événement,Versailles,Île-de-France,Gratuit,Inscription,Nouveau,Priorité Critique
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:⚡ Retour à Poudlard Versailles demain — vérifie ton inscription et ton créneau d'accès
END:VALARM
END:VEVENT'''

NIGHT_EVENT = f'''BEGIN:VEVENT
UID:{NIGHT_UID}
DTSTAMP:{NOW_ICS}
LAST-MODIFIED:{NOW_ICS}
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-HARRYPOTTER-PRIORITY:IMPORTANT
X-HARRYPOTTER-REMINDER-PROFILE:EVENT_IMPORTANT
X-HARRYPOTTER-ACTION:ATTEND
X-HARRYPOTTER-EVENT-TYPE:EXPERIENCE
X-HARRYPOTTER-FORMAT:NIGHT_FOUNTAIN_DRONE_SHOW
X-HARRYPOTTER-MARKET:FR
X-HARRYPOTTER-SOURCE-ID:chateau-versailles-spectacles
X-HARRYPOTTER-FIRST-ADDED-AT:{NOW_ICS}
X-HARRYPOTTER-NEW-UNTIL:20260829T015944Z
X-HARRYPOTTER-FRESHNESS:NEW
X-HARRYPOTTER-BADGE:NEW
DTSTART;TZID=Europe/Paris:20260829T203000
DTEND;TZID=Europe/Paris:20260829T231500
SUMMARY:⭐ ✅ 🆕 ✨ Grandes Eaux Nocturnes — Harry Potter Retour à Poudlard — Versailles
LOCATION:Jardins du Château de Versailles\\, Place d'Armes\\, 78000 Versailles\\, France
X-HARRYPOTTER-LOCATION-PRECISION:SITE
X-HARRYPOTTER-TICKET-URL:https://www.chateauversailles-spectacles.fr/evenement/les-grandes-eaux-nocturnes-harry-potter-retour-a-poudlard/
X-HARRYPOTTER-TICKET-STATUS:SOLD_OUT
X-HARRYPOTTER-TICKET-PROVIDER:Château de Versailles Spectacles
X-HARRYPOTTER-TICKET-PROVIDER-ID:chateau-versailles-spectacles
X-HARRYPOTTER-TICKET-CONFIDENCE:HIGH
X-HARRYPOTTER-TICKET-SCARCITY-EVIDENCE:EXPLICIT_TEXT
X-HARRYPOTTER-ACCESS-MODE:TICKET
DESCRIPTION:Priorité : ⭐ Important — soirée officielle Harry Potter au Château de Versailles pour le 25e anniversaire du premier film.\\nFiabilité : ✅ Confirmé directement par Château de Versailles Spectacles.\\nHoraire : samedi 29 août 2026 de 20h30 à 23h15.\\nExpérience : parcours nocturne dans les jardins sur les musiques des films\\, fontaines illuminées\\, objets inspirés du monde des sorciers et final mêlant drones et pyrotechnie.\\n🎟️ Billetterie : COMPLET selon la FAQ officielle Retour à Poudlard / la billetterie officielle. Aucun billet disponible n'est affirmé ici.\\n⚠️ L'inscription gratuite au rassemblement de journée ne donne pas accès à cette soirée payante.\\n📍 Jardins du Château de Versailles — 78000 Versailles.\\nRappel : J-1 uniquement\\, les jalons plus anciens étant déjà passés lors de l'ajout.\\nSources : https://www.chateauversailles-spectacles.fr/evenement/les-grandes-eaux-nocturnes-harry-potter-retour-a-poudlard/ ; https://www.retourapoudlard.com/faq
URL:https://www.chateauversailles-spectacles.fr/evenement/les-grandes-eaux-nocturnes-harry-potter-retour-a-poudlard/
CATEGORIES:Harry Potter,Back to Hogwarts,Événement,Versailles,Île-de-France,Grandes Eaux,Drone,Sold Out,Nouveau,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:✨ Grandes Eaux Nocturnes Harry Potter à Versailles demain — prépare ton billet et ton trajet
END:VALARM
END:VEVENT'''


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def insert_events(path):
    text = path.read_text(encoding="utf-8")
    changed = False
    for uid, block in ((DAY_UID, DAY_EVENT), (NIGHT_UID, NIGHT_EVENT)):
        if f"UID:{uid}" not in text:
            marker = "\nEND:VCALENDAR"
            if marker not in text:
                raise RuntimeError(f"{path} missing END:VCALENDAR")
            text = text.replace(marker, "\n" + block + marker, 1)
            changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
    return changed


def add_source_registry():
    path = CAL / "harry-potter-sources-france.json"
    data = load_json(path)
    sources = data.setdefault("sources", [])
    ids = {s.get("source_id") for s in sources}
    additions = [
        {
            "source_id": "retourapoudlard-fr",
            "name": "Retour à Poudlard France / Warner Bros. Discovery France",
            "authority": "ORGANIZER_DIRECT",
            "evidence_grade": "A",
            "territory": "LOCAL_FR",
            "url": "https://www.retourapoudlard.com/",
            "domains": ["back_to_hogwarts", "activations_fr", "paris_idf"],
            "expected_information": ["date locale", "sessions", "inscription", "conditions d'accès", "entrée dédiée"],
            "can_confirm": ["FR_ACTIVATION_DATE", "FR_LOCAL_EVENT_TIME", "REGISTRATION_RULES", "ACCESS_RULES", "LOCAL_LOCATION"],
            "cannot_confirm": ["EVENING_TICKET_STATUS hors FAQ officielle", "OTHER_FR_EVENT"],
            "status": "ACTIVE",
            "priority": 1,
            "cadence": "EVENT_DRIVEN",
            "last_verified_at": NOW
        },
        {
            "source_id": "chateau-versailles-spectacles",
            "name": "Château de Versailles Spectacles",
            "authority": "ORGANIZER_DIRECT",
            "evidence_grade": "A",
            "territory": "LOCAL_FR",
            "url": "https://www.chateauversailles-spectacles.fr/",
            "domains": ["paris_idf", "live_events", "ticketing"],
            "expected_information": ["date locale", "horaire", "lieu", "billetterie", "statut de vente"],
            "can_confirm": ["FR_LOCAL_EVENT_TIME", "LOCAL_LOCATION", "FR_TICKET_STATUS", "LOCAL_TICKET_URL", "LOCAL_CANCELLATION"],
            "cannot_confirm": ["OTHER_VENUE_STATUS", "NATIONAL_FRANCHISE_STATUS"],
            "status": "ACTIVE",
            "priority": 1,
            "cadence": "EVENT_DRIVEN",
            "last_verified_at": NOW
        }
    ]
    changed = False
    for src in additions:
        if src["source_id"] not in ids:
            sources.append(src)
            changed = True
    fr = data.setdefault("field_rules", {}).setdefault("LOCAL_PARIS_EVENT", [])
    for sid in ("retourapoudlard-fr", "chateau-versailles-spectacles"):
        if sid not in fr:
            fr.append(sid)
            changed = True
    primary = data.setdefault("coverage_matrix", {}).setdefault("paris_idf", {}).setdefault("primary", [])
    for sid in ("retourapoudlard-fr", "chateau-versailles-spectacles"):
        if sid not in primary:
            primary.append(sid)
            changed = True
    if changed:
        data["updated_at"] = NOW
        save_json(path, data)
    return changed


def add_providers():
    path = CAL / "harry-potter-ticketing-providers-france.json"
    data = load_json(path)
    providers = data.setdefault("providers", [])
    ids = {p.get("provider_id") for p in providers}
    additions = [
        {
            "provider_id": "retourapoudlard-fr",
            "name": "Retour à Poudlard France / Warner Bros. Discovery France",
            "authority": "ORGANIZER_DIRECT",
            "territory": "Versailles / Île-de-France",
            "status": "ACTIVE",
            "primary_url": "https://www.retourapoudlard.com/",
            "can_confirm": ["LOCAL_EVENT_DATE", "LOCAL_EVENT_TIME", "SESSION_LIST", "TICKET_URL", "TICKET_STATUS", "ACCESS_RULES", "LOCAL_LOCATION"],
            "cannot_confirm": ["OTHER_EVENT_STATUS", "SECONDARY_RESALE_STATUS"],
            "linked_source_id": "retourapoudlard-fr"
        },
        {
            "provider_id": "chateau-versailles-spectacles",
            "name": "Château de Versailles Spectacles",
            "authority": "ORGANIZER_DIRECT",
            "territory": "Versailles / Île-de-France",
            "status": "ACTIVE",
            "primary_url": "https://www.chateauversailles-spectacles.fr/",
            "can_confirm": ["LOCAL_EVENT_DATE", "LOCAL_EVENT_TIME", "TICKET_URL", "TICKET_STATUS", "LOCAL_TICKET_PRICE", "LOCAL_CANCELLATION"],
            "cannot_confirm": ["OTHER_VENUE_STATUS", "SECONDARY_RESALE_STATUS"],
            "linked_source_id": "chateau-versailles-spectacles"
        }
    ]
    changed = False
    for p in additions:
        if p["provider_id"] not in ids:
            providers.append(p)
            changed = True
    if changed:
        data["updated_at"] = NOW
        save_json(path, data)
    return changed


def add_ticketing():
    path = CAL / "harry-potter-ticketing-france.json"
    data = load_json(path)
    tracked = data.setdefault("tracked", [])
    ids = {x.get("event_uid") for x in tracked}
    additions = [
        {
            "event_uid": DAY_UID,
            "title": "Retour à Poudlard 2026 — Château de Versailles",
            "city": "Versailles",
            "provider": "Retour à Poudlard / Warner Bros. Discovery France",
            "provider_id": "retourapoudlard-fr",
            "source_id": "retourapoudlard-fr",
            "ticket_url": "https://www.retourapoudlard.com/",
            "status": "ON_SALE",
            "status_origin": "DIRECT_VERIFIED",
            "evidence_grade": "A",
            "confidence": "HIGH",
            "scarcity_evidence": "UNKNOWN",
            "check_tier": "HOT",
            "last_verified_at": NOW,
            "last_changed_at": NOW,
            "price_min_eur": 0.0,
            "price_max_eur": 0.0,
            "session_states": [
                {"session_key": "2026-08-29T09:00-Europe-Paris", "status": "UNKNOWN", "confidence": "LOW", "category_states": []},
                {"session_key": "2026-08-29T13:00-Europe-Paris", "status": "UNKNOWN", "confidence": "LOW", "category_states": []},
                {"session_key": "2026-08-29T17:00-Europe-Paris", "status": "UNKNOWN", "confidence": "LOW", "category_states": []}
            ],
            "verification_notes": "Inscription gratuite obligatoire sur le site officiel ; accès à chaque session uniquement pendant la première heure. L'ouverture du flux d'inscription est confirmée, mais aucune quantité restante n'est inférée.",
            "history": []
        },
        {
            "event_uid": NIGHT_UID,
            "title": "Grandes Eaux Nocturnes — Harry Potter Retour à Poudlard — Versailles",
            "city": "Versailles",
            "provider": "Château de Versailles Spectacles",
            "provider_id": "chateau-versailles-spectacles",
            "source_id": "chateau-versailles-spectacles",
            "ticket_url": "https://www.chateauversailles-spectacles.fr/evenement/les-grandes-eaux-nocturnes-harry-potter-retour-a-poudlard/",
            "status": "SOLD_OUT",
            "status_origin": "DIRECT_VERIFIED",
            "evidence_grade": "A",
            "confidence": "HIGH",
            "scarcity_evidence": "EXPLICIT_TEXT",
            "check_tier": "HOT",
            "last_verified_at": NOW,
            "last_changed_at": NOW,
            "session_states": [
                {"session_key": "2026-08-29T20:30-Europe-Paris", "status": "SOLD_OUT", "confidence": "HIGH", "scarcity_evidence": "EXPLICIT_TEXT", "category_states": []}
            ],
            "verification_notes": "La FAQ officielle Retour à Poudlard indique explicitement que les Grandes Eaux Nocturnes Retour à Poudlard sont complètes.",
            "history": [{"at": NOW, "transition": "SOLD_OUT", "note": "État complet confirmé lors de l'enrôlement initial."}]
        }
    ]
    changed = False
    for item in additions:
        if item["event_uid"] not in ids:
            tracked.append(item)
            changed = True
    if changed:
        data["updated_at"] = NOW
        save_json(path, data)
    return changed


def main():
    changed = []
    for name in ("harry-potter-events-france-paris.ics", "harry-potter-paris.ics"):
        if insert_events(CAL / name):
            changed.append(name)
    if add_source_registry():
        changed.append("harry-potter-sources-france.json")
    if add_providers():
        changed.append("harry-potter-ticketing-providers-france.json")
    if add_ticketing():
        changed.append("harry-potter-ticketing-france.json")

    # One-shot helper cleans itself and its workflow from the final tree.
    me = ROOT / "scripts" / "apply_hp_versailles_20260824.py"
    wf = ROOT / ".github" / "workflows" / "apply-hp-versailles-once.yml"
    if me.exists():
        me.unlink()
    if wf.exists():
        wf.unlink()

    print("updated:", ", ".join(changed) if changed else "no material changes")

if __name__ == "__main__":
    main()
