# Jeux & collection — Calendriers

Calendriers Pokémon, Fortnite et Harry Potter pour la France, avec une vue
interactive et des flux d’abonnement iCalendar.

## Ouvrir le calendrier

Télécharger [`calendar.html`](calendar.html) et l’ouvrir dans un navigateur récent.
Le fichier est autonome : aucune installation, compilation ou clé d’accès.
Une connexion internet est nécessaire pour charger les trois flux publics depuis
la branche `master` de ce dépôt. Le fichier peut aussi être servi par un serveur
statique (`python -m http.server 8000`, puis `http://localhost:8000/calendar.html`).

- Vue mensuelle et vue agenda, adaptée au mobile.
- Navigation entre les mois et retour à aujourd’hui.
- Recherche dans le mois affiché, y compris lieux et descriptions, sans distinction d’accents.
- Filtres cumulables par univers, type et statut ; option « À venir uniquement ».
- Deux événements maximum par case, puis accès à la liste complète de la journée.
- Périodes longues regroupées ; dates de fin exclusives correctement interprétées.
- Détails, heures de Paris, adresse, lien source et recherche du lieu.
- Liens d’abonnement à copier ou ouvrir dans une application d’agenda.
- Actualisation manuelle avec conservation des données déjà chargées si un flux échoue.

La vue charge un seul flux global par univers pour éviter le cumul de calendriers
spécialistes et de leur miroir. L’abonnement Pokémon proposé conserve le chemin
canonique existant `pokemon-tcg-france.ics`. La vue globale comprend aussi les
salons de `pokemon-events-france-paris.ics` ; cela est indiqué dans le dialogue
d’abonnement. Ne pas ajouter plusieurs abonnements Pokémon pour actualiser.

Les filtres ne modifient pas les abonnements. Les statuts reflètent les données
du dépôt, sans nouvelle vérification éditoriale. Le bouton « Actualiser » recharge
la vue, pas l’application d’agenda externe. Aucun hébergement web n’est configuré
par ce fichier : GitHub affiche son code, pas l’interface en ligne.

## Vérification

```sh
node --test tests/calendar-core.test.cjs
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/pokemon_calendar_presentation.py --check
python scripts/validate_calendar_health.py --static
```

Le lecteur couvre les événements non récurrents présents dans les trois flux.
Une récurrence ou un format non pris en charge est signalé dans la vue et doit être
consulté dans l’application d’agenda abonnée ; il n’est pas affiché comme une
occurrence unique trompeuse. Le contrôle GitHub vérifie la compatibilité des flux.

Voir [`calendars/README.md`](calendars/README.md) pour les règles d’import,
la présentation, la déduplication et la surveillance.
