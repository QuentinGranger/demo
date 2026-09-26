# Veille consolidée — 26 septembre 2026

À la demande de l'utilisateur, les veilles Pokémon, Fortnite, Harry Potter et
billetterie sont regroupées dans la tâche active `Calendriers jeux — France`
(ID `6a84c4941c608191bcfb74e78a025c39`). Sa cadence reste horaire, Europe/Paris.
Pokémon, Fortnite et billetterie sont examinés à chaque passage ; le balayage
général Harry Potter reste quotidien. Les instructions métier des autres fichiers
restent applicables. Ce fichier et la politique actuelle remplacent toutes les
anciennes instructions de santé figurant dans les archives métier.

Les anciennes tâches désactivées sont retirées du dispositif ; ne pas les
réactiver ni recréer la billetterie séparée. Le regroupement respecte le quota de
cinq tâches sans toucher aux quatre autres tâches actives de l'utilisateur.
La tâche consolidée effectue la veille ; GitHub Actions conserve le contrôle
indépendant des fichiers, flux publics, état des tâches observé et fraîcheur du
heartbeat. Il ne faut pas prétendre disposer de deux tâches ChatGPT indépendantes.

À chaque passage, lire la politique, l'état et le heartbeat actuels. Observer la
tâche par automations.peek. Vérifier les chemins déclarés et les trois contrats
d'abonnement. Une fois par jour ou à une transition, actualiser le heartbeat
par lecture fraîche/SHA/compare-and-swap avec les valeurs réellement observées.
Un échec peut rafraîchir un diagnostic DEGRADED ; il ne peut jamais devenir HEALTHY
sans preuve de récupération. Ne pas inventer un run ni antidater une vérification.

Après une écriture, comparer le master courant et l'URL RAW stable. Si le cache
sert l'ancien contenu, vérifier aussi l'URL du commit immuable et le max-age HTTP
(habituellement 300 secondes). Réessayer l'URL stable après expiration ; ne pas
créer de nouvelle URL d'abonnement ni demander de réimporter le fichier. Un import
manuel crée des copies qui ne se synchronisent pas. Les abonnements global et
spécialiste se recouvrent : ne pas conseiller de les activer simultanément.

Ne pas répéter une alerte sans changement matériel. Maintenir les incidents
OPEN/ESCALATED/RECOVERED et leurs preuves. Le mode --static vérifie le dépôt ;
le mode normal et --online doivent continuer à échouer sur une surveillance
réellement périmée, manquante ou désactivée. Les contrôles sains restent silencieux.
