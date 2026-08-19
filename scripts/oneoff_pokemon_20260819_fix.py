#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
STAMP = "20260819T185408Z"
MEGA_UID = "pokemon-mega-forces-20260828@openai"
PLAY_UID = "pokemon-worlds-celebration-stores-20260821@openai"

MEGA_EVENT = rf"""BEGIN:VEVENT
UID:{MEGA_UID}
DTSTAMP:{STAMP}
LAST-MODIFIED:{STAMP}
SEQUENCE:10
STATUS:TENTATIVE
PRIORITY:9
X-POKEMON-PRIORITY:INFO
X-POKEMON-REMINDER-PROFILE:TCG_RELEASE
X-POKEMON-ACTION:BUY
X-POKEMON-WAVE-ID:TCG-MEGA-FORCES-20260828
X-POKEMON-WAVE-COMPLETENESS:COMPLETE
X-POKEMON-WAVE-PRODUCT-COUNT:3
X-POKEMON-WAVE-PREORDER-COUNT:0
X-POKEMON-WAVE-PRODUCTS:Boîte Méga Puissances — Méga-Zeraora-ex|Boîte Méga Puissances — Méga-Darkrai-ex|Boîte Méga Puissances — Méga-Dracolosse-ex
X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Boîte Méga Puissances — Méga-Zeraora-ex
X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Boîte Méga Puissances — Méga-Darkrai-ex
X-POKEMON-WAVE-ITEM;STATE=CONFIRMED:Boîte Méga Puissances — Méga-Dracolosse-ex
X-POKEMON-RETAILER-OFFER;SELLER=Pokemagic;TYPE=INDEPENDENT;CHANNEL=WEB;STATUS=PREORDER;DATE=20260828;PRICE=29.99:https://pokemagic.fr/products/pokebox-tin-mega-puissances-pokemon-mega-dracolosse-ex
X-POKEMON-LAST-MAJOR-UPDATE-AT:{STAMP}
X-POKEMON-UPDATE-UNTIL:20260822T185408Z
X-POKEMON-UPDATE-REASON:OFFICIAL_PRODUCT_NAME_AND_CONTENT
X-POKEMON-FRESHNESS:UPDATED
X-POKEMON-BADGE:UPDATED
DTSTART;VALUE=DATE:20260828
DTEND;VALUE=DATE:20260829
SUMMARY:ℹ️ 🟡 ✨ 🃏 Sortie JCC — Boîte Méga Puissances
LOCATION:France
DESCRIPTION:Priorité : ℹ️ Info — produit standard, mais fiche désormais enrichie par une source Pokémon officielle.\nFiabilité : 🟡 pour la date exacte du 28 août en France ; Pokémon confirme officiellement le nom « Boîte Méga Puissances » et le contenu, mais sa galerie n'indique que le 3e trimestre 2026. La date du 28 août reste donc une date France issue de vendeurs/sources spécialisées et n'est pas présentée comme une date officielle Pokémon.\n📦 Variantes officielles : Méga-Zeraora-ex, Méga-Darkrai-ex ou Méga-Dracolosse-ex. Chaque boîte contient 1 carte promo brillante, 4 boosters et 1 carte à code JCC Pokémon Live.\n🛒 Boutique repérée : Pokemagic — précommande Méga-Dracolosse-ex à 29,99 €, sortie annoncée le 28 août 2026 ; cette date concerne l'offre du vendeur.\n✨ Mise à jour majeure le 19 août 2026 : nom français et contenu officialisés.\nRappels : J-7 et J-1 — vérifier prix et stock.\nSource officielle produit : https://www.pokemon.com/fr/jcc-pokemon/galerie-produits/boite-mega-puissances\nSource date France suivie : https://www.pokecardex.com/forums/viewtopic.php?t=49894
URL:https://www.pokemon.com/fr/jcc-pokemon/galerie-produits/boite-mega-puissances
CATEGORIES:Pokémon,TCG,Sortie JCC,Vague,Mise à jour,Priorité Info
BEGIN:VALARM
TRIGGER:-P7D
ACTION:DISPLAY
DESCRIPTION:🃏 Sortie dans 7 jours — vérifie prix et stock : Boîte Méga Puissances
END:VALARM
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:🃏 Sortie demain — prépare ton achat : Boîte Méga Puissances
END:VALARM
END:VEVENT
"""

PLAY_EVENT = rf"""BEGIN:VEVENT
UID:{PLAY_UID}
DTSTAMP:{STAMP}
LAST-MODIFIED:{STAMP}
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:1
X-POKEMON-PRIORITY:CRITICAL
X-POKEMON-REMINDER-PROFILE:PLAY_EVENT_LIMITED
X-POKEMON-ACTION:ATTEND
X-POKEMON-FIRST-ADDED-AT:{STAMP}
X-POKEMON-NEW-UNTIL:20260824T185408Z
X-POKEMON-FRESHNESS:NEW
X-POKEMON-BADGE:NEW
DTSTART;VALUE=DATE:20260821
DTEND;VALUE=DATE:20260831
SUMMARY:🔥 ✅ 🆕 🏆 Play! Pokémon — Célébration des Mondiaux 2026 + promo Pikachu
LOCATION:Play! Pokémon Stores participants — France
DESCRIPTION:Priorité : 🔥 Critique — événement officiel imminent avec récompense promotionnelle distribuée dans la limite des stocks disponibles.\nFiabilité : ✅ Confirmé officiellement par Pokémon. Du 21 au 30 août 2026, les Play! Pokémon Stores participants organisent des tournois « Célébration des Mondiaux 2026 ».\n🎁 Participation : carte promo Pikachu Mondiaux 2026 dans la limite des stocks disponibles et selon l'ordre d'arrivée ; les personnes en tête des catégories junior, senior et master dans chaque magasin peuvent recevoir la version estampillée « WINNER ». Des accessoires commémoratifs sont aussi annoncés pour les vainqueurs.\n📍 France : rechercher le magasin et la séance exacte dans le Localisateur d'évènements Play! Pokémon en utilisant le nom « Célébration des Mondiaux 2026 ». Aucun magasin parisien précis n'est affirmé tant qu'une fiche locale officielle n'a pas été vérifiée.\n🆕 Ajouté au calendrier le 19 août 2026 — nouveau jusqu'au 24 août 2026.\nRappels : J-1 uniquement ; le rappel J-7 est déjà passé au moment de l'ajout.\nSource : https://www.pokemon.com/fr/actualites/participez-a-des-tournois-de-celebration-des-championnats-du-monde-2026-dans-votre-play-pokemon-store-local-et-obtenez-une-carte-promo-pikachu
URL:https://www.pokemon.com/fr/actualites/participez-a-des-tournois-de-celebration-des-championnats-du-monde-2026-dans-votre-play-pokemon-store-local-et-obtenez-une-carte-promo-pikachu
CATEGORIES:Pokémon,Play! Pokémon,Événement,Promo,Championnat du Monde,Priorité Critique,Nouveau
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:🏆 Célébration des Mondiaux demain — trouve ton Play! Pokémon Store et vérifie la promo Pikachu
END:VALARM
END:VEVENT
"""

def replace_event(text, uid, event):
    pat = re.compile(r"BEGIN:VEVENT\nUID:" + re.escape(uid) + r"\n.*?END:VEVENT\n", re.S)
    text2, n = pat.subn(lambda m: event, text, count=1)
    if n != 1:
        raise RuntimeError(f"event {uid}: expected 1 match, got {n}")
    return text2

for name, uid, event in [
    ("pokemon-tcg-france.ics", MEGA_UID, MEGA_EVENT),
    ("pokemon-events-france-paris.ics", PLAY_UID, PLAY_EVENT),
]:
    p = CAL / name
    p.write_text(replace_event(p.read_text(encoding="utf-8"), uid, event), encoding="utf-8", newline="\n")

p = CAL / "pokemon-paris.ics"
text = p.read_text(encoding="utf-8")
text = replace_event(text, MEGA_UID, MEGA_EVENT)
text = replace_event(text, PLAY_UID, PLAY_EVENT)
p.write_text(text, encoding="utf-8", newline="\n")
print("Pokemon ICS escaping fixed")
