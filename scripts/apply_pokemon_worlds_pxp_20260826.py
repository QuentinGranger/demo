#!/usr/bin/env python3
from pathlib import Path

PATH = Path('calendars/pokemon-events-france-paris.ics')
UID = 'pokemon-worlds-pokemonxp-streams-20260828@openai'
STAMP = '20260826T184340Z'
EVENT = '''BEGIN:VEVENT
UID:pokemon-worlds-pokemonxp-streams-20260828@openai
DTSTAMP:20260826T184340Z
LAST-MODIFIED:20260826T184340Z
SEQUENCE:0
STATUS:CONFIRMED
PRIORITY:5
X-POKEMON-PRIORITY:IMPORTANT
X-POKEMON-REMINDER-PROFILE:MEDIA_IMPORTANT
X-POKEMON-ACTION:WATCH
X-POKEMON-FIRST-ADDED-AT:20260826T184340Z
X-POKEMON-NEW-UNTIL:20260831T184340Z
X-POKEMON-FRESHNESS:NEW
X-POKEMON-BADGE:NEW
X-POKEMON-SOURCE-TIMEZONE:America/Los_Angeles
X-POKEMON-SESSION;DATE=20260828;START=2200;END=2300:Pokémon TCG — The Making of Full-Art Card Illustrations
X-POKEMON-SESSION;DATE=20260829;START=0200;END=0300:Pokémon TCG Pocket — Cards\, Creators and Clashes
X-POKEMON-SESSION;DATE=20260829;START=1900;END=2000:Pokémon GO — panel PokémonXP
DTSTART;VALUE=DATE:20260828
DTEND;VALUE=DATE:20260831
SUMMARY:⭐ ✅ 🆕 📡 Mondiaux 2026 & PokémonXP — diffusions + drops
LOCATION:En ligne — Pokemon.com / Twitch officiel Pokémon / Twitch PokémonXP
DESCRIPTION:Priorité : ⭐ Important — week-end officiel des Mondiaux et de PokémonXP avec plusieurs récompenses limitées liées au visionnage.\\nFiabilité : ✅ Confirmé officiellement par Pokémon le 24 août 2026. Les Championnats du Monde Pokémon et PokémonXP se déroulent du 28 au 30 août 2026 et sont retransmis en ligne.\\n🎁 Drops Mondiaux : récompenses Pokémon Champions les 28\, 29 et 30 août ; Félinferno des Mondiaux après 60 minutes de diffusion VGC ; autres récompenses JCC Live\, Pokémon GO\, UNITE et Pocket selon les chaînes et durées publiées.\\n🃏 PokémonXP — vendredi 28 août 22h–23h heure de Paris : panel « The Making of Full-Art Card Illustrations » ; après 30 minutes sur Twitch PokémonXP\, code JCC Pokémon Live pour 6 boosters Méga-Évolution – Nuit Noire + 1 Jeton d’évènement Stratégies et Combats.\\n📱 Pokémon Pocket — samedi 29 août 02h–03h heure de Paris : panel « Cards\, Creators and Clashes—From B Series to What’s Next » ; le temps de visionnage peut contribuer au drop de 24 Sabliers Booster.\\n📍 Pokémon GO — samedi 29 août 19h–20h heure de Paris : panel Pokémon GO sur Twitch PokémonXP ; après 30 minutes\, Étude ponctuelle permettant de rencontrer un Pikachu en costume PokémonXP.\\n⏱️ Les horaires ci-dessus sont les horaires officiels PDT convertis en Europe/Paris (+9 h fin août). Les rediffusions publiées dans l’heure suivant chaque journée peuvent aussi compter pour certains drops selon Pokémon.\\n🆕 Ajouté au calendrier le 26 août 2026.\\nRappel : J-1 — activer les drops Twitch et vérifier les chaînes officielles avant le début du week-end.\\nSource principale : https://www.pokemon.com/fr/actualites/regardez-les-mondiaux-et-pokemonxp-pour-obtenir-de-superbes-recompenses-en-jeu\\nProgramme officiel : https://championships.pokemon.com/en-gb/broadcasts/pxp
URL:https://www.pokemon.com/fr/actualites/regardez-les-mondiaux-et-pokemonxp-pour-obtenir-de-superbes-recompenses-en-jeu
CATEGORIES:Pokémon,Événement,Play! Pokémon,Mondiaux,PokémonXP,Streaming,Drops,Nouveau,Priorité Important
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:📡 Mondiaux Pokémon & PokémonXP demain — active les drops Twitch et vérifie les horaires
END:VALARM
END:VEVENT
'''

def main():
    text = PATH.read_text(encoding='utf-8')
    if UID in text:
        print('Event already present; no change needed.')
        return
    marker = 'END:VCALENDAR'
    if not text.rstrip().endswith(marker):
        raise SystemExit('pokemon events calendar does not end with END:VCALENDAR')
    # Preserve the existing newline convention.
    nl = '\r\n' if '\r\n' in text else '\n'
    normalized_event = EVENT.replace('\n', nl)
    stripped = text.rstrip('\r\n')
    updated = stripped[:-len(marker)] + normalized_event + marker + nl
    PATH.write_text(updated, encoding='utf-8', newline='')
    print('Added Pokémon Worlds/PokémonXP streaming event.')

if __name__ == '__main__':
    main()
