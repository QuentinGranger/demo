# Calendriers Pokémon

Ce dépôt publie des abonnements iCalendar, sans interface web. L'affichage
(couleurs, disposition mensuelle, etc.) dépend de l'application d'agenda.

Le flux abonné reste `pokemon-tcg-france.ics` : aucune réinscription nécessaire.
Les chemins et noms des calendriers existants sont conservés.

## Présentation

- Titres sans accumulation de pictogrammes de priorité, de nouveauté ou de statut.
- Mention textuelle `[À confirmer]` pour les dates incertaines.
- Dates réelles, horaires, sources et rappels conservés ; repères visuels explicitement distingués des périodes complètes.
- Événements informatifs marqués « disponible » : ils ne bloquent pas l'agenda personnel.
- Pokémon GO et Pokémon Sleep exclus des trois flux publics concernés.
- Doublons identifiés regroupés sous leur UID existant ; alias rejetés à l'import.

Les cinq périodes longues identifiées dans `compact_periods` sont affichées comme
des repères de début (une journée, ou quinze minutes pour une heure précise).
Les dates réelles restent dans la description et `X-POKEMON-PERIOD-START/END`.
Un repère « Fenêtre T4 » n'est pas une date de sortie confirmée. Les fenêtres
avec récurrence ou alarme relative à leur fin ne sont pas raccourcies.
Les vraies sessions, dates et produits distincts restent séparés.

Les doublons sont archivés dans `archive/pokemon-duplicates-20260926.json`.
L'import vérifie aussi l'identité métier et les sessions identiques, même sous
un nouvel UID. Un lot contenant un doublon est refusé avant toute écriture.

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

La voie safe-patch synchronise le flux global dans la même transaction, y compris
pour les écritures du bot. La synchronisation applique également la présentation. Le contrôle
GitHub Actions signale les écritures directes qui ne respectent pas cette politique.
L'application d'agenda récupère les changements à son prochain rafraîchissement
après publication sur `master` ; les événements déjà copiés manuellement ne sont
pas liés à l'abonnement.
Une cadence de rafraîchissement d'une heure est suggérée aux clients. Le cache
RAW GitHub annonce généralement 300 secondes ; aucun outil ne permet de forcer
le rafraîchissement de l'agenda de l'utilisateur. Un seul abonnement Pokémon
doit être affiché : le global et le spécialiste contiennent volontairement des
événements communs. Ne pas ajouter un second abonnement ou importer le fichier
manuellement pour « actualiser ».

## Contrôle de santé du dépôt

La politique V4 déclare huit chemins surveillés. `pokemon-paris.ics` reste un
miroir de compatibilité ; l'abonnement Pokémon canonique est `pokemon-tcg-france.ics`.

`python scripts/validate_calendar_health.py --static` vérifie les contrats du
dépôt dans les pull requests : schéma, chemins, noms, structure ICS, manifeste
et cohérence du diagnostic. Les incidents des tâches externes sont affichés
séparément et ne certifient jamais un service sain.

Sans option (et avec `--online` sur master), le contrôle exige aussi une
surveillance active et récente. Une tâche absente, désactivée, périmée ou une
redondance insuffisante restent des échecs. Le contrôle planifié et son suivi
d'incident GitHub restent actifs.

Le heartbeat est une observation datée, y compris quand elle est `DEGRADED`.
Un observateur actif peut l'actualiser quotidiennement avec les résultats réels.
Il ne doit ni recopier un ancien état `HEALTHY`, ni inventer une exécution, ni
réactiver une tâche mise en pause sans demande de l'utilisateur.

Le 26 septembre 2026, l'utilisateur a choisi de regrouper les veilles pour
respecter sa limite de cinq tâches actives. La tâche `Calendriers jeux — France`
couvre Pokémon, Fortnite et la billetterie Harry Potter chaque heure, avec un
balayage général Harry Potter quotidien. Ses instructions métier complètes sont
versionnées dans `automation-instructions/`. Les anciens moniteurs sont retirés
de la politique ; leur historique est conservé. GitHub Actions reste un contrôle
indépendant. Il ne s'agit pas de deux tâches de découverte indépendantes.
