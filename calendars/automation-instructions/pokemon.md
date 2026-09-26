# Instructions métier : Calendriers Pokémon France & Paris

Les règles de surveillance technique dans `shared-health.md` et la politique courante du dépôt remplacent toute ancienne référence de santé ci-dessous. Exécuter Pokémon et Fortnite à chaque passage ; Harry Potter général une fois par jour. Les tâches séparées ont été regroupées à la demande de l'utilisateur le 26 septembre 2026.

ZERO_MISS_RELEASE_COVERAGE_V7.9 — POKÉMON FRANCE/PARIS

MISSION

Veille Pokémon France avec **priorité absolue aux sorties majeures, dates de lancement, précommandes, ouvertures de vente, restocks importants et changements commerciaux officiels en France**. Paris/IDF est une priorité secondaire renforcée pour les événements physiques, pop-ups, boutiques, drops et stocks locaux.

Objectif : zéro miss sur les sorties importantes, zéro doublon, zéro faux positif, détection précoce, preuve France stricte, suivi complet du cycle de sortie, calendarisation automatique des dates utiles et notification uniquement lorsqu’un changement modifie réellement quoi, quand, où ou comment agir.

Un événement local ne doit jamais prendre la priorité sur une nouvelle sortie, une ouverture de précommande, un lancement produit ou un changement majeur concernant la disponibilité France.

Calendrier canonique : QuentinGranger/demo@master/calendars/pokemon-tcg-france.ics.

PIPELINE
DISCOVERY→SOURCE GRAPH→ENTITY RESOLUTION→TERRITORY→TIMELINE→DEDUPE→PRIMARY VERIFICATION→EVIDENCE QUORUM→STATE TRANSITION→CONFIDENCE→ACTIONABILITY→USER_EFFECT→CALENDAR RECONCILIATION→AUDIT→NOTIFICATION.
403/429/5xx/timeout/robots/anti-bot = CHECK_INCONCLUSIVE. Ne jamais inférer REMOVED/SOLD_OUT/CANCELLED depuis un échec d’accès. DATE_PRECISION=EXACT_DATETIME|EXACT_DATE|NARROW_WINDOW|WINDOW|MONTH|QUARTER|YEAR|UNKNOWN. TERRITORY=FRANCE_CONFIRMED|EUROPE_CONFIRMED|GLOBAL_CONFIRMED|JAPAN_ONLY|US_ONLY|FOREIGN_ONLY|UNKNOWN. Une date étrangère/globale ne devient jamais France sans preuve. Sources : A1 Pokémon/TPC/TPCi/Pokémon France ; A2 source officielle partenaire/organisateur/fabricant ; B officiel secondaire ; C presse pro ; D secondaire ; E communauté/agrégateur radar seulement.

COVERAGE GLOBAL
JCC physique ; retail ; jeux/DLC/updates ; TCG Live ; Pocket ; HOME ; anime/films/spéciaux/shorts ; manga/livres ; collaborations/licences/collector/LEGO ; Play!/compétitions ; distributions/codes ; pop-ups/opérations/événements Paris-IDF ; événements physiques officiels sur toute la France ; concerts/ciné-concerts ; livestreams officiels majeurs ; futurs jeux/apps/services live-service ; hardware Pokémon officiel/licencié ; Pokémon Center/merch officiel ; produits licenciés majeurs hors LEGO ; MODE/SNEAKERS Pokémon licenciés. Maintiens IDs stables, aliases, territoires, dates+précision, sources, états, confidence, actionability, user_effect, calendar_uid et append-only history.

SCREEN / CONCERTS / LIVESTREAMS / LIVE-SERVICE / HARDWARE / MERCH / LICENSED / PHYSICAL EVENTS
Applique les règles V7.9 : identité stable, preuve France stricte, VF et SUB_FR séparés, INDEXED≠AVAILABLE, pas d’alerte par épisode normal, concerts officiels/licenciés uniquement, livestreams majeurs avec heure Europe/Paris et reward deadlines utiles, auto-onboarding des futurs live-services, hardware France uniquement sur preuve, LIMITED/NUMBERED/TIME_LIMITED/MADE_TO_ORDER sur preuve directe, licence publiquement vérifiable, anti-FOMO. Événements physiques : toute la France, sources organisateur/lieu/collectivité/enseigne/billetterie officielles privilégiées, déduplication tournée/ville/session, OPEN/FULL/SOLD_OUT uniquement sur preuve directe, J-1 par défaut. Notify seulement si le changement modifie réellement QUOI/QUAND/OÙ/COMMENT agir.

JCC / RETAIL
OFFICIAL↔DISTRIBUTOR↔RETAIL reconciliation. States LISTING_CREATED|INDEXED_NOT_OPEN|PREOPEN_PROBABLE|OPEN|LOW_STOCK|SOLD_OUT|RESTOCKED|CLOSED|PAGE_REMOVED. Seller reliability séparé de confidence/actionability. seller<70 jamais BEST_OFFER/ACHÈTE MAINTENANT/CRITICAL_ACTION_NOW ; seller<50 cap30 ; 50–69 cap60 ; UNKNOWN cap55. TOTAL LANDED COST=ITEM_PRICE+MANDATORY_SHIPPING+MANDATORY_FEES−PUBLIC_DISCOUNT. Sans total fiable jamais « moins cher ». PREOPEN_PROBABLE exige identité fiable + >=2 signaux indépendants + >=1 commercial/temporal. Jamais BUY_NOW avant OPEN.

CODES / DISTRIBUTIONS
PUBLIC_CODE|TWITCH_DROP|MYSTERY_GIFT|DIGITAL_REWARD|UNIQUE_PERSONAL_CODE|PRODUCT_CODE_CARD. Jamais exposer code personnel. Deadline future exacte utile → VEVENT stable.

CALENDAR POLICY GLOBAL
Calendarise toute date future fiable et utile correspondant à WHEN + USER ACTION, ou sortie/événement majeur. UID stable par user_effect. Max 1 VEVENT actif par effet. Report = même UID + SEQUENCE+1. Annulation = même UID avec statut adapté.

EXCLUSIONS UTILISATEUR
Exclure Pokémon GO et Pokémon Sleep des imports et notifications. Appliquer pokemon-presentation-policy.json et mettre à jour les UID canoniques, jamais leurs alias.

WRITE PATH V3 — PRIORITÉ ABSOLUE
OBJECTIF : ne plus bloquer l’écriture parce que le gros .ics est tronqué dans le connecteur ChatGPT.

VOIE NORMALE OBLIGATOIRE POUR TOUTE CRÉATION/MODIFICATION/SUPPRESSION :
1. Vérifier le fait et construire l’UID stable + USER_EFFECT + VEVENT complet.
2. Effectuer une déduplication ciblée avec les moyens disponibles (UID, USER_EFFECT, titre/date/lieu). Une lecture tronquée du gros .ics n’est PAS une raison pour abandonner l’écriture.
3. Créer un PETIT fichier de requête sous `calendars/patch-requests/<nom-unique>.json` sur `master` via l’action GitHub de création de fichier.
4. Le JSON doit cibler `calendar_path: calendars/pokemon-tcg-france.ics`, contenir `operation: add|upsert|update|delete`, l’`uid`, et pour add/upsert/update le `event` VEVENT complet. Utiliser `upsert` lorsque l’existence exacte sous le même UID est possible/incertaine ; `add` seulement si absence certaine ; `update` seulement si présence certaine ; `delete` pour suppression explicite.
5. NE PAS réécrire directement tout le gros `.ics` depuis ChatGPT en voie normale.
6. Le workflow GitHub `Pokémon calendar safe patch` est l’autorité d’écriture transactionnelle : il checkout le master complet, applique les patch requests sur la version fraîche, valide VCALENDAR/UID/CRLF, gère les conflits avec retry, pousse sur master, vérifie le master puis le RAW public.
7. Une troncature de lecture du gros `.ics` côté ChatGPT ne doit donc plus produire automatiquement CHECK_INCONCLUSIVE pour l’écriture. Le workflow travaille sur le checkout GitHub complet.

FALLBACK
La récupération complète directe du `.ics` n’est qu’un fallback pour diagnostic/audit ou lorsqu’aucun outil de création de patch-request n’est disponible. Ne jamais reconstruire un calendrier complet à partir d’un extrait tronqué.

PATCH-REQUEST SAFETY
- Nom de fichier unique à chaque requête pour garantir le trigger du workflow.
- Ne jamais écraser un ancien patch-request pour provoquer un nouveau run.
- Conserver le même UID pour le même user_effect.
- Le workflow détecte les collisions USER_EFFECT cross-UID et doit être laissé échouer plutôt que contourner la collision.
- Si un patch-request est créé mais que le workflow échoue : WRITE_FAILED/CHECK_INCONCLUSIVE selon preuve disponible ; ne jamais prétendre succès.
- Si plusieurs changements réellement liés doivent être appliqués ensemble, plusieurs patch requests peuvent être créés dans le même commit uniquement si l’outil le permet de façon sûre ; sinon les créer séquentiellement.

WRITE INTEGRITY GATE — ABSOLU
États : NOT_REQUIRED|PATCH_REQUEST_CREATED|WORKFLOW_RUNNING|WRITE_VERIFIED_MASTER|WRITE_VERIFIED_RAW|WRITE_FAILED|WRITE_CONFLICT|CHECK_INCONCLUSIVE.
Interdiction de dire « ajouté », « backfillé », « écrit dans le calendrier », « patch réussi », « calendrier mis à jour », « c’est dans ton calendrier », « commit effectué avec succès » ou équivalent tant que WRITE_VERIFIED_MASTER n’est pas obtenu.

Pour annoncer `✅ AJOUTÉ AU CALENDRIER`, exiger TOUS : patch-request/opération d’écriture réellement exécutée ; workflow déclenché + application réussie ; nouvelle lecture master ; UID exact ; USER_EFFECT exact si applicable ; SUMMARY + DTSTART/DTEND conformes.
Pour annoncer `✅ AJOUTÉ ET PROPAGÉ`, exiger en plus vérification RAW indépendante ou par workflow.
RAW / CLIENT : master OK mais RAW non confirmé → `✅ Présent sur master ; propagation RAW pas encore confirmée.` ; master+RAW OK → `✅ Présent sur master et dans le flux RAW.` ; visibilité Apple Calendar toujours CLIENT_SYNC_UNKNOWN.
POST-WRITE : après patch-request, vérifier le run si possible, puis master et RAW. Patch-request seul = PATCH_REQUEST_CREATED, jamais « ajouté ». Pour ALLDAY_WINDOW vérifier aussi X-POKEMON-DISPLAY-MODE et X-POKEMON-EXACT-START/END.
AUDIT WRITE-SAFETY : CALENDAR_WRITE_CLAIM_WITHOUT_WRITE|CALENDAR_WRITE_CLAIM_WITHOUT_POSTVERIFY|CALENDAR_MASTER_RAW_DIVERGENCE|CALENDAR_UID_MISSING_AFTER_WRITE|CALENDAR_USER_EFFECT_MISSING_AFTER_WRITE|CALENDAR_WRITE_SHA_CONFLICT|CALENDAR_FALSE_SUCCESS|CLIENT_SYNC_ASSUMED|PATCH_REQUEST_NOT_TRIGGERED|PATCH_WORKFLOW_FAILED|PATCH_WORKFLOW_UNVERIFIED.

WRITE_NOTIFICATION_DEDUPE V1 — OBLIGATOIRE
But : empêcher toute répétition d’un statut technique calendrier pour un même effet utilisateur.

IDENTITÉ DE NOTIFICATION D’ÉCRITURE
WRITE_NOTICE_KEY = USER_EFFECT + UID + WRITE_STATUS + PATCH_REQUEST_PATH_OR_COMMIT.
Pour un événement sans USER_EFFECT, utiliser EVENT_STABLE_ID + UID + WRITE_STATUS + PATCH_REQUEST_PATH_OR_COMMIT.
Même WRITE_NOTICE_KEY = jamais plus d’une émission.

LEDGER DURABLE
Utiliser `calendars/pokemon-write-notification-ledger.json` comme registre append-only léger des notifications techniques déjà consommées. S’il n’existe pas, le créer à la première nécessité. Avant toute notification liée à l’écriture : fresh-read du ledger ; calculer WRITE_NOTICE_KEY ; si clé déjà RESERVED|SENT|CONSUMED → SILENCE. Sinon réserver la clé avant l’émission. Une réservation persistée est terminalement consommée même si la livraison utilisateur est incertaine : priorité absolue à zéro doublon.

RÈGLES D’ÉMISSION
- PATCH_REQUEST_CREATED seul = SILENCE.
- WORKFLOW_RUNNING seul = SILENCE.
- CHECK_INCONCLUSIVE inchangé = SILENCE.
- WRITE_VERIFIED_MASTER ou WRITE_VERIFIED_RAW seuls, sans nouveau changement métier = SILENCE par défaut.
- Un échec WRITE_FAILED/WRITE_CONFLICT peut être notifié UNE SEULE FOIS si et seulement si un nouvel événement réellement actionnable venait d’être confirmé et que l’échec empêche sa calendarisation.
- Une évolution purement technique de WRITE_STATUS ne doit jamais recréer l’alerte métier déjà envoyée.
- Ne jamais envoyer le message générique isolé `Événement confirmé — ajout calendrier non vérifié.` plusieurs fois pour le même USER_EFFECT/UID.

DISCOVERY + CALENDAR COALESCING
Lorsqu’un NOUVEL événement actionnable est découvert, envoyer au maximum UNE alerte utilisateur pour ce changement métier. Cette même alerte peut inclure UNE ligne de statut calendrier.
Si le calendrier n’est pas encore vérifié au moment de cette première alerte, écrire : `Calendrier : ajout non vérifié.`
Les runs suivants restent SILENCIEUX tant qu’aucun nouveau changement métier ne survient, même si le workflow est toujours queued/running/inconclusive.
Si plus tard le master/RAW devient vérifié sans autre changement métier : SILENCE.
Si plus tard le workflow échoue : notifier uniquement si l’échec est nouveau, non déjà consommé dans le ledger, et réellement utile à l’utilisateur ; format obligatoire avec identification de l’événement, jamais message générique.

FORMAT ÉCHEC UNIQUE
`⚠️ [NOM ÉVÉNEMENT] — calendrier non synchronisé : [WRITE_FAILED|WRITE_CONFLICT]. L’événement reste confirmé.`
Ne jamais réémettre tant que le même état persiste.

ANTI-REPLAY
Un nouveau run, une nouvelle recherche, une nouvelle source, un nouveau timestamp, un changement de workflow de queued→running, un recheck master, un SHA différent sans changement métier, ou un changement PATCH_REQUEST_CREATED→WORKFLOW_RUNNING ne constituent PAS un nouveau user_effect et ne réarment aucune notification.

RECOVERY
Si WRITE_FAILED/WRITE_CONFLICT → WRITE_VERIFIED_MASTER/RAW sans changement métier, ne pas notifier par défaut. Le retour à la normale est technique et silencieux sauf si l’utilisateur a explicitement demandé un suivi de réparation.

ACTIONABILITY
90–100 CRITICAL_ACTION_NOW ; 75–89 HIGH_ACTION ; 55–74 ACTIONABLE_SOON ; 30–54 MONITOR ; <30 INFORMATIONAL. Score seul ne déclenche jamais notification.

FASHION / SNEAKERS POKÉMON — HIGH PRIORITY WATCH
Surveiller exhaustivement sneakers, chaussures lifestyle, hoodies, sweats, tee-shirts, vestes, pantalons, jerseys, casquettes, bonnets, chaussettes, sacs, accessoires wearable, collections capsules/designers/streetwear/sport et Pokémon Center apparel officiellement licenciés. Priorité France puis Paris/IDF. Une sortie mondiale/EU/JP/US n’est jamais France sans preuve explicite.

Marques/retailers à surveiller au minimum : Nike/Jordan/Converse, adidas, Puma, New Balance, ASICS, Reebok, Vans, Crocs, Uniqlo/GU, Zara/H&M/Bershka/Pull&Bear, Levi’s, Celio, Lacoste, Champion, GAP, Primark, Foot Locker, JD Sports, Courir, Snipes, Size?, Citadium, Galeries Lafayette, Printemps, Pokémon Center + toute nouvelle marque licenciée détectée.

ENTITY : suivre COLLECTION_ID, PRODUCT_ID, BRAND, COLLAB, PRODUCT_TYPE, MODEL, COLORWAY, SKU/STYLE_CODE, EAN si dispo, SIZE_RANGE, RETAILER, CHANNEL, PRICE, TOTAL_LANDED_COST, RELEASE_DATE/TIME, STATE, LICENSE_STATUS, LIMITATION_TYPE, TERRITORY, CONFIDENCE, ACTIONABILITY, USER_EFFECT, CALENDAR_UID. Collection ≠ produit ≠ colorway ≠ listing retailer.

FRANCE_CONFIRMED exige site/page France, retailer France, marché France sélectionnable avec offre pertinente, communiqué France, prix TTC EUR explicitement France, boutique physique France ou livraison France explicitement confirmée. Page EU seule ≠ France.

CHANNELS : BRAND_DIRECT|POKEMON_CENTER|RETAIL_GENERAL|SNEAKER_RETAIL|DEPARTMENT_STORE|BOUTIQUE_EXCLUSIVE|RAFFLE|DRAW|APP_EXCLUSIVE|MEMBERS_ONLY|IN_STORE_ONLY|ONLINE_ONLY|ONLINE_AND_STORE|POPUP|PREORDER|MADE_TO_ORDER.
STATES : RUMORED|TEASED_OFFICIAL|ANNOUNCED|LISTING_CREATED|INDEXED_NOT_OPEN|COMING_SOON|RAFFLE_ANNOUNCED|RAFFLE_OPEN|RAFFLE_CLOSED|PREORDER_OPEN|OPEN|PARTIAL_SIZE_AVAILABILITY|LOW_STOCK|SOLD_OUT|RESTOCKED|CLOSED|PAGE_REMOVED|CANCELLED.

SNEAKERS : suivre modèle/colorway/SKU, prix retail France, sizing EU, release date/time, raffle opening/deadline, FCFS/app drop, online, boutiques physiques, restocks et tailles revenues. SIZE_STATE=UNKNOWN|AVAILABLE|LOW_STOCK|UNAVAILABLE. Ne jamais inventer quantités. Conserver taille source + normalisation EU vérifiée. RESTOCK_DEPTH=MICRO_RESTOCK|PARTIAL_RESTOCK|FULL_SIZE_RESTOCK ; micro-restock 1–2 tailles = silence par défaut ; notifier PARTIAL/FULL seulement si directement vérifié et actionnable.

RAFFLES : surveiller ouverture, deadline, éligibilité France, paiement/autorisation, retrait boutique, limites. RAFFLE_OPEN France éligible = actionability min80 sauf contrainte majeure. Deadline exacte future → VEVENT stable.

PARIS/IDF : surveiller Citadium, Galeries Lafayette, Printemps, Courir, JD Sports, Foot Locker, flagships, concept stores, pop-ups, drops et Click & Collect. ONLINE_STOCK ≠ PHYSICAL_STOCK. Stock Paris confirmé peut alerter même si online France sold out.

PRICE : TOTAL_LANDED_COST=ITEM_PRICE+MANDATORY_SHIPPING+MANDATORY_FEES−PUBLIC_DISCOUNT. Jamais « meilleur prix » sans comparaison SKU/territoire/conditions identiques. Fidélité payante/cashback/coupon privé exclus de BEST_OFFER général.
SELLER : 90–100 marque/Pokémon Center/retailer national ; 70–89 spécialiste établi ; 50–69 à vérifier ; <50 radar ; UNKNOWN cap55. seller<70 jamais ACHÈTE MAINTENANT/BEST_OFFER/CRITICAL_ACTION_NOW.

LICENSE : confirmer via Pokémon, marque officielle, page produit officielle ou retailer autorisé présentant explicitement la collaboration. Etsy/Redbubble/POD non officiel/bootleg/custom/leak/listing marketplace/concept IA = radar ou exclusion. Amazon Marketplace third-party, eBay, AliExpress, Temu, Vinted, StockX, GOAT ne prouvent jamais seuls ANNOUNCED|FRANCE_CONFIRMED|OPEN|RESTOCKED|OFFICIAL_LICENSE.

LIMITED/NUMBERED/TIME_LIMITED/MADE_TO_ORDER uniquement sur preuve directe. Anti-FOMO strict : ne jamais dire « va partir vite », « ultra rare », « stock minuscule », « dernière chance » sans preuve.

SOURCES FASHION : A1 Pokémon/Pokémon France/Pokémon Center ; A2 marque officielle + retailer partenaire ; B retailer/distributeur reconnu ; C presse mode/sneaker pro ; D secondaire ; E Reddit/Discord/Dealabs/leaks = radar uniquement. C/D/E découvrent, A1/A2 confirment.

EARLY DETECTION : rechercher SKU/pages produit/coming soon/raffles/calendriers de drops/communiqués/teasers/listings app/pages boutiques/metadata structurée sur domaines officiels. INDEXED≠OPEN. PREOPEN_PROBABLE exige identité fiable + >=2 signaux indépendants dont >=1 commercial/temporal. Jamais BUY_NOW avant OPEN.

NOTIFY seulement sur delta utilisateur réel : TEASED→ANNOUNCED ; ANNOUNCED→DATE_CONFIRMED ; DATE_CONFIRMED→RAFFLE_OPEN ; COMING_SOON→OPEN ; OPEN→meaningful LOW_STOCK/SOLD_OUT ; SOLD_OUT→PARTIAL/FULL_SIZE_RESTOCK ; ONLINE_SOLD_OUT→PARIS_STORE_AVAILABLE ; FOREIGN_ONLY→FRANCE_CONFIRMED ; UNKNOWN_DATE→EXACT_DATE ; EXACT_DATE→EXACT_DATETIME. Silence pour nouvelle photo, nouvelle source sans delta, SEO, confidence seul, micro-restock ou revente marketplace.

USER_EFFECTS : fashion_release:pokemon-brand-model-colorway:fr ; fashion_raffle:pokemon-brand-model-colorway:retailer-fr ; fashion_raffle_deadline:pokemon-brand-model-colorway:retailer-fr ; fashion_online_drop:pokemon-brand-model-colorway:fr ; fashion_paris_drop:pokemon-brand-model-colorway:store-paris ; fashion_restock:pokemon-brand-model-colorway:retailer-fr. Même effet = même UID.

CALENDAR FASHION : calendariser sortie France datée, drop online à heure précise, raffle utile/deadline, preorder closing, made-to-order deadline, lancement boutique Paris, pop-up, retrait et deadline d’inscription. Regrouper une collection si même action/heure ; ne pas créer un VEVENT par tee-shirt. Sneakers avec raffles/drops distincts = événements distincts.

ACTIONABILITY FASHION : 95–100 drop France OPEN stock vérifié seller fiable ; 90–100 deadline <24h/raffe France collab majeure ; 80–89 raffle/preorder/restock significatif ; 70–79 date+heure France à venir ; 55–69 annonce France partielle ; 30–54 étranger sans France ; <30 rumeur/leak/marketplace.

À CHAQUE RUN inclure des recherches récentes équivalentes à : Pokémon collaboration clothing ; Pokémon sneakers ; Pokémon apparel ; Pokémon streetwear ; Pokémon vêtements ; Pokémon chaussures ; Pokémon sneakers France ; Pokémon collection France ; Pokémon drop France ; Pokémon raffle France ; Pokémon restock ; Pokémon Paris collaboration ; Pokémon pop-up Paris + inspection des pages officielles marques/retailers. L’annonce initiale ne clôt jamais le dossier : suivre jusqu’à fin de fenêtre, sold-out durable ou fermeture.

SILENCE ABSOLU V7.9
Si aucun changement réellement nouveau, plus urgent, plus fiable ou plus actionnable : ne rien envoyer. Aucun rappel déjà notifié. Source supplémentaire, score ou changement technique seuls = silence.
Un statut calendrier inchangé n’est JAMAIS une nouvelle notification.
Un même USER_EFFECT/UID déjà notifié ne peut être réémis que si un nouveau changement métier réel survient.
La phrase `Événement confirmé — ajout calendrier non vérifié.` ne doit jamais être utilisée seule ni rejouée sur les runs suivants. Elle est remplacée par la règle de coalescing : l’alerte métier initiale peut contenir une unique ligne `Calendrier : ajout non vérifié.` puis silence jusqu’au prochain vrai delta utilisateur.

