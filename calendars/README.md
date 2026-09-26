# Calendriers Pokémon

Ce dépôt publie des abonnements iCalendar, sans interface web. L'affichage
(couleurs, disposition mensuelle, etc.) dépend de l'application d'agenda.

Le flux abonné reste `pokemon-tcg-france.ics` : aucune réinscription nécessaire.
Les chemins et noms des calendriers existants sont conservés.

## Présentation

- Titres sans accumulation de pictogrammes de priorité, de nouveauté ou de statut.
- Mention textuelle `[À confirmer]` pour les dates incertaines.
- Dates, horaires, sources, descriptions et rappels conservés pour les événements retenus.
- Événements informatifs marqués « disponible » : ils ne bloquent pas l'agenda personnel.
- Pokémon GO et Pokémon Sleep exclus des trois flux publics concernés.
- Doublons identifiés regroupés sous leur UID existant ; alias rejetés à l'import.

Les expositions, compétitions et fenêtres de disponibilité gardent leur durée
réelle. Une fenêtre trimestrielle n'est pas transformée en date de sortie précise.
Les événements distincts partageant un jour ou un lieu restent séparés.

## Maintenance

`pokemon-presentation-policy.json` conserve les exclusions et la liste des
doublons identifiés. Les demandes d'import GO/Sleep échouent avant toute écriture,
y compris dans un lot. Mettre à jour l'UID conservé plutôt que créer un nouvel UID
pour une information déjà présente. Les requêtes historiques restent archivées
dans `patch-requests/`, sans être rejouées.

Après toute écriture directe ou exécution d'un ancien script :

```sh
python scripts/pokemon_calendar_presentation.py
python scripts/sync_pokemon_global.py
python scripts/pokemon_calendar_presentation.py --check
python -m unittest discover -s scripts -p 'test_pokemon_calendar_presentation.py'
```

La synchronisation du flux global applique également la présentation. Le contrôle
GitHub Actions signale les écritures directes qui ne respectent pas cette politique.
L'application d'agenda récupère les changements à son prochain rafraîchissement
après publication sur `master` ; les événements déjà copiés manuellement ne sont
pas liés à l'abonnement.
