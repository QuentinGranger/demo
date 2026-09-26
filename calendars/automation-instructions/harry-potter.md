# Instructions métier : Calendriers Harry Potter France & Paris

Les règles de surveillance technique dans `shared-health.md` et la politique courante du dépôt remplacent toute ancienne référence de santé ci-dessous. Exécuter Pokémon et Fortnite à chaque passage ; Harry Potter général une fois par jour. Les tâches séparées ont été regroupées à la demande de l'utilisateur le 26 septembre 2026.

Surveille quotidiennement Harry Potter / Wizarding World pour la France, priorité Paris/Île-de-France, et maintiens sans doublon : calendars/harry-potter-paris.ics, calendars/harry-potter-releases-france.ics, calendars/harry-potter-events-france-paris.ics.

ORCHESTRATION PERSISTANTE V7 — lis obligatoirement avant toute décision :
- calendars/harry-potter-sources-france.json = OFFICIAL_SOURCE_REGISTRY_FR_V3
- calendars/harry-potter-watchlist-france.json = CANDIDATE_QUEUE_FR_V1
- calendars/harry-potter-retailers-france.json = RETAILER_REGISTRY_FR_V2
- calendars/harry-potter-retailer-offers-france.json = RETAILER_OFFER_LEDGER_FR_V1
- calendars/harry-potter-taxonomy-france.json = WIZARDING_TAXONOMY_FR_V1 (registre de base et assignments)
- calendars/harry-potter-taxonomy-engine-france.json = WIZARDING_TAXONOMY_ENGINE_FR_V2 (overlay non cassant, aliases, relations, filtres, extensions)
- calendars/harry-potter-taxonomy-index-france.json = index inversé dérivé
- calendars/harry-potter-ticketing-france.json = TICKETING_INTELLIGENCE_FR_V2
- calendars/harry-potter-ticketing-providers-france.json = TICKETING_PROVIDER_REGISTRY_FR_V1
- calendars/harry-potter-end-reminders-france.json = DEADLINE_INTELLIGENCE_FR_V2
Les ledgers spécialisés priment sur une donnée plus ancienne du .ics. Préserve toutes les politiques X-HARRYPOTTER-* déjà présentes dans les calendriers.

ANTI-RUMEUR ABSOLU : aucun leak, rumeur, post anonyme, datamining, spéculation ou fan account non sourcé dans les calendriers. Un VEVENT exige une date/heure/période/action exploitable + une source identifiable suffisamment crédible. Les signaux faibles vont en watchlist. Applique authority, territory, can_confirm/cannot_confirm et field_rules du registre officiel. Une source globale ne confirme jamais automatiquement un champ France.

FIABILITÉ / PRIORITÉ : source autorisée grade A pour le champ précis => ✅ CONFIRMED ; B => 🟠 TENTATIVE ; retailer/spécialiste C => 🟡 TENTATIVE. 🟡 jamais 🔥. 🔥 PRIORITY:1 pour action très urgente/rare/limitée ; ⭐ PRIORITY:5 pour grosse sortie/collector/média/événement ; ℹ️ PRIORITY:9 standard/secondaire.

CANDIDATS : WATCHING -> SIGNAL_FOUND -> READY -> CALENDAR_ADDED -> RESOLVED/REJECTED. READY seulement avec preuve et date/action exploitable. Le VEVENT créé garde X-HARRYPOTTER-CANDIDATE-ID et un UID stable. Ne recrée jamais un candidat connu sous un autre UID.

TAXONOMIE V2 — MODÈLE BASE + ENGINE : le registre V1 conserve les IDs/assignments existants ; le moteur V2 est un overlay non cassant et doit être appliqué pour toutes les nouvelles classifications. Résous les entités avec base + extensions du moteur. Les alias FR/EN servent uniquement à la recherche ; l'output utilise toujours l'ID canonique. Si un nouvel ID est requis, ajoute-le au registre ou à l'overlay avec ID ASCII stable, labels FR/EN, relations vérifiées et provenance. Ne réutilise jamais un ID pour un autre concept.

FACETTES : SUBFRANCHISE, WORK, HOUSE, CHARACTER, PLACE, ERA, THEME, ARTIFACT, CANON_SCOPE. Basis autorisées : DIRECT, INHERITED, DERIVED, UMBRELLA. Confidence : EXPLICIT, RELATION_VERIFIED, INHERITED_VERIFIED, AMBIGUOUS. AMBIGUOUS n'est jamais matérialisé en ICS ni indexé en STRICT.

STRICT / EXPANDED / CANON_ONLY / COLLECTOR : STRICT = DIRECT seulement. EXPANDED = DIRECT+INHERITED+DERIVED+UMBRELLA et traverse uniquement les relations autorisées du moteur, profondeur maximale 2. CANON_ONLY exclut merchandising/expérience/parodie/meta. COLLECTOR combine taxonomie + champs COLLECTOR-INTEREST/LIMITED du VEVENT ; un thème COLLECTING seul ne prouve jamais qu'un produit est limité.

INFÉRENCES : applique uniquement les relations typées du moteur. Character -> House, Work -> Era, Work -> Subfranchise, Place -> Parent sont forward-only. THEMATIC_EQUIVALENT sert au filtre, pas à créer un fait narratif. Interdictions absolues : HOUSE_TO_CHARACTER, PLACE_TO_WORK, THEME_TO_CHARACTER, ARTIFACT_TO_WORK sans règle explicite, produit licencié -> fait canonique, texte marketing -> relation personnage. Exemple : Luna DIRECT => RAVENCLAW DERIVED en EXPANDED ; RAVENCLAW ne permet jamais d'inférer Luna.

HÉRITAGE : TICKET_ONSALE/PREORDER_OPEN héritent du parent avec INHERITED. SAME_TOUR/SAME_CAMPAIGN héritent œuvre/sous-franchise/thèmes centraux seulement ; ne dupliquent jamais un lieu fictif ou personnage non central. Une prolongation conserve l'assignment du même UID.

INDEX TAXONOMIQUE : harry-potter-taxonomy-index-france.json est dérivé et jetable. Il sert uniquement à accélérer facet/id -> UIDs. Le registre base + moteur restent source de vérité. Régénère l'index seulement après ASSIGNMENT_ADD/REMOVE/CHANGE, RELATION_CHANGE, INHERITANCE_CHANGE ou ENTITY_DEPRECATION. Ne commit jamais un index logiquement identique. Vérifie avant écriture : aucun UID orphelin, aucun ID inconnu, listes triées/dédupliquées. Si index et registre divergent, reconstruis l'index depuis les sources de vérité, ne modifie jamais le registre pour satisfaire l'index.

INDEX MODES : STRICT contient uniquement les tags DIRECT résolus (avec héritage seulement si la requête demande explicitement le parent logique). EXPANDED contient les ajouts dérivés autorisés, notamment house de personnage, era/subfranchise d'œuvre et parents de lieux. Ne pré-calculer aucune relation interdite.

ICS TAXONOMIE : lors d'une vraie modification métier du VEVENT, ajoute si pertinent X-HARRYPOTTER-SUBFRANCHISE, WORK, HOUSE, CHARACTER, PLACE, ERA, THEME, ARTIFACT, CANON-SCOPE et TAG-BASIS. Ajoute X-HARRYPOTTER-TAXONOMY-VERSION:WIZARDING_TAXONOMY_FR_V2. Au VCALENDAR, utiliser lors d'une prochaine vraie écriture : X-HARRYPOTTER-TAXONOMY-POLICY:WIZARDING_TAXONOMY_FR_V2 ; X-HARRYPOTTER-TAXONOMY-REGISTRY:harry-potter-taxonomy-france.json ; X-HARRYPOTTER-TAXONOMY-ENGINE:harry-potter-taxonomy-engine-france.json ; X-HARRYPOTTER-TAXONOMY-INDEX:harry-potter-taxonomy-index-france.json. Ne change jamais SEQUENCE uniquement pour taxonomie/header/index.

RETAILERS / OFFRES : retailer_id est canonique et immuable. Marketplace != seller tiers. Offre persistante = retailer_id + exact_product_key (SKU > EAN > product_id > titre/édition/langue normalisés). Distingue PAGE_LISTING, FIRST_STOCK, RESTOCK. Pas un VEVENT par boutique standard ; fiche séparée seulement si précommande importante, exclusivité, stock/restock majeur, collector urgent ou avantage concret. Les prix retailers restent distincts du prix officiel.

PRIX : prix officiel FR uniquement depuis une source explicitement autorisée PRICE_FR pour le SKU exact. Jamais conversion USD/GBP. Sans prix officiel FR : « meilleur prix vérifié parmi les offres suivies », jamais « remise officielle ».

PÉRIMÈTRE : livres/éditions FR, illustrés/collector, audiobooks, jeux Warner/Portkey, HBO/Max, Warner Bros France, LEGO, MinaLima, Noble Collection, Cinereplicas, Funko/Loungefly, ressorties cinéma, expos, pop-ups, conventions, spectacles, ciné-concerts, dédicaces, rencontres, petits événements régionaux, boutiques et opérations locales. Ne transforme pas chaque produit dérivé banal en VEVENT : date/action exploitable ou réel intérêt collection/planification requis.

ANTI-BAZAR : série HBO = fiche première/fenêtre de saison, pas par épisode sauf demande explicite. Ressortie cinéma multi-jours même réseau/lieu = une fiche de période. Saison spectacle = production+ville+lieu+période. Tournée = une fiche par ville importante. Séances rapprochées même lieu = une fiche run avec SESSION-*.

BILLETTERIE / DEADLINES : pour disponibilité, séances, catégories, sold-out, nouvelles séances et prix ticket, le ticketing ledger horaire est prioritaire. Pour fin/dernière chance, le deadline ledger est prioritaire. La veille quotidienne ne doit jamais écraser un état plus récent de ces ledgers. Une proximité de fin ne prouve jamais une rareté de billets.

COLLECTOR / COLLECTIONS : COLLECTOR-INTEREST HIGH|MEDIUM|LOW et LIMITED YES|NO|UNKNOWN ; LIMITED:YES exige preuve directe. Une vraie collection commerciale + même date peut être regroupée avec COLLECTION-ID ; ne fusionne jamais seulement parce que les dates coïncident.

LIEUX / TEMPS : LOCATION complète ; GEO seulement fiable ; aucun GEO inventé. Ne fabrique jamais DTEND : fin calculée = ESTIMATED, inconnue = UNKNOWN.

FRAÎCHEUR / CHANGEMENTS : conserve NEW5D_UPDATE3D_V3 et UID_STABLE_AUDIT_V2. Nouvel UID = 🆕 5 jours ; grosse mise à jour = ✨ 3 jours ; expiration silencieuse. Report/annulation/réactivation gardent le même UID et historique. Report sans nouvelle date => aucune alarme future. Annulation => STATUS:CANCELLED, jamais suppression.

RAPPELS : conserve TYPE_FIRST_V2 et les rappels de fin DEADLINE_INTELLIGENCE_FR_V2. Aucun rappel passé ou doublon. Ne modifie pas les alarmes billetterie/deadline sans lire leurs ledgers spécialisés.

SYNCHRONISATION : même UID dans global/spécialiste = mêmes données métier, taxonomie, UID, SEQUENCE, fraîcheur, evidence, source_id, candidate_id, retailer_id, relations et statut. SEQUENCE+1 seulement si le VEVENT change réellement.

ANTI-COMMIT-BRUIT : aucun commit juste pour recheck, checked_at sans changement, ajout de header, expiration de badge ou régénération identique. Les corrections taxonomiques seules restent silencieuses sauf si elles sont nécessaires à un flux filtré explicitement demandé.

NOTIFICATIONS : uniquement changement utile : nouvel événement/sortie, candidat devenu actionnable, précommande/billetterie importante, date/heure officielle, FIRST_STOCK/RESTOCK utile, exclusivité, stock critique, disponibilité Paris/IDF pertinente, report, annulation/réactivation ou transition deadline/ticketing prévue. Ajout/correction de taxonomie ou régénération d'index seuls = silencieux.

