#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
BASE = CAL / "fortnite-taxonomy-france.json"
LORE = CAL / "fortnite-lore-taxonomy-france.json"
GRAPH = CAL / "fortnite-lore-graph-france.json"
ENGINE = CAL / "fortnite-lore-engine-france.json"
INDEX = CAL / "fortnite-lore-index-france.json"
SOURCES = CAL / "fortnite-sources-france.json"
LORE_SOURCES = CAL / "fortnite-lore-sources-france.json"

ALLOWED_TYPES = {"CHARACTER","ORGANIZATION","FACTION","POI","ISLAND","LORE_OBJECT","HISTORICAL_EVENT","REALITY","TIMELINE","LORE_CONCEPT","CHAPTER"}
ALLOWED_CANON = {"MAIN_STORY","COLLAB_CANON","GAMEPLAY_ONLY","COSMETIC_ONLY","META","UNKNOWN"}
V1_REL = {"MEMBER_OF","OPPOSES","PART_OF_ISLAND","BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER","OCCURS_IN_REALITY","OCCURS_IN_TIMELINE","INVOLVES","CENTERS_ON","LOCATED_AT","PRECEDES","SUCCESSOR_OF","SAME_ENTITY_AS_LEGACY"}
V2_REL = {"MEMBER_OF","AFFILIATED_WITH","LEADS","OPPOSES","ASSOCIATED_WITH","PART_OF_ISLAND","BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER","OCCURS_IN_REALITY","OCCURS_IN_TIMELINE","INVOLVES","CENTERS_ON","LOCATED_AT","TARGETS","USES","CREATED_BY","DESTROYED_IN","TRANSFORMED_INTO","DERIVED_FROM","SPLIT_FROM","MERGED_INTO","PRECEDES","SUCCESSOR_OF","CAUSES","SAME_ENTITY_AS_LEGACY"}
ALLOWED_ROLES = {"NPC","BOSS","QUEST_GIVER","VENDOR","ALLY","HOSTILE","NEUTRAL","LEADER","AGENT"}
CLAIM_TYPES = {"RELATION","ROLE","PARTICIPATION","LOCATION","STATE","CHRONOLOGY","LINEAGE","IDENTITY"}
CLAIM_STATUSES = {"ACTIVE","PROVISIONAL","DISPUTED","SUPERSEDED","RETRACTED"}
EVIDENCE = {"OFFICIAL_EXPLICIT","OFFICIAL_CROSS_REFERENCE","CURATED_LEGACY_OFFICIAL","DISCOVERY_ONLY","UNKNOWN"}
STRONG_EVIDENCE = {"OFFICIAL_EXPLICIT","OFFICIAL_CROSS_REFERENCE"}
PRECISIONS = {"EXACT","DATE_ONLY","SEASON_SCOPE","CHAPTER_SCOPE","EVENT_SCOPE","UNKNOWN"}
PARTICIPATION_ROLES = {"PARTICIPANT","LEADER","AGENT","ALLY","OPPONENT","TARGET","DEFENDER","ATTACKER","CREATOR","OWNER","OBSERVER","UNKNOWN"}


def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def base_refs(base):
    refs = set()
    for facet, rows in base.get("facets", {}).items():
        for row in rows:
            if row.get("id"):
                refs.add(f"{facet}:{row['id']}")
    return refs


def cycle_nodes(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
    visiting, visited = set(), set()
    def dfs(node, stack):
        if node in visiting:
            i = stack.index(node) if node in stack else 0
            return stack[i:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for nxt in graph.get(node, []):
            cyc = dfs(nxt, stack)
            if cyc:
                return cyc
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None
    for node in graph:
        cyc = dfs(node, [])
        if cyc:
            return cyc
    return []


def valid_https(url):
    if not isinstance(url, str):
        return False
    try:
        p = urlparse(url)
        return p.scheme == "https" and bool(p.netloc)
    except Exception:
        return False


def main():
    errors = []
    required = (BASE, LORE, GRAPH, ENGINE, INDEX, SOURCES, LORE_SOURCES)
    for p in required:
        if not p.exists():
            errors.append(f"missing required file: {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    base = load(BASE)
    lore = load(LORE)
    graph = load(GRAPH)
    engine = load(ENGINE)
    index = load(INDEX)
    sources = load(SOURCES)
    lore_sources = load(LORE_SOURCES)

    expected = {
        "lore taxonomy": (lore.get("version"), "FORTNITE_LORE_TAXONOMY_FR_V1"),
        "lore graph": (graph.get("version"), "FORTNITE_LORE_KNOWLEDGE_GRAPH_FR_V2"),
        "lore engine": (engine.get("version"), "FORTNITE_LORE_ENGINE_FR_V2"),
        "lore index": (index.get("version"), "FORTNITE_LORE_INDEX_FR_V2"),
        "lore source policy": (lore_sources.get("version"), "FORTNITE_LORE_SOURCE_POLICY_FR_V2")
    }
    for label, (actual, wanted) in expected.items():
        if actual != wanted:
            errors.append(f"unexpected {label} version: {actual!r}, wanted {wanted}")

    if lore_sources.get("inherits") != SOURCES.name:
        errors.append("lore source policy inherits wrong registry")
    if lore.get("base_registry") != BASE.name or engine.get("base_registry") != BASE.name:
        errors.append("base registry mismatch")
    if engine.get("lore_registry") != LORE.name:
        errors.append("lore engine registry mismatch")
    if engine.get("claim_graph") != GRAPH.name:
        errors.append("lore engine claim_graph mismatch")
    if graph.get("base_registry") != LORE.name:
        errors.append("lore graph base_registry mismatch")
    if lore_sources.get("claim_graph") != GRAPH.name:
        errors.append("lore source policy claim_graph mismatch")
    if GRAPH.name not in index.get("derived_from", []):
        errors.append("lore index does not derive from V2 claim graph")

    source_ids = {s.get("source_id") for s in sources.get("sources", []) if s.get("source_id")}
    for source_id in lore_sources.get("authority", {}).keys():
        if source_id not in source_ids:
            errors.append(f"lore source policy references unknown source_id: {source_id}")

    bref = base_refs(base)
    entities = {}
    origin = {}
    for e in lore.get("entities", []):
        eid = e.get("id")
        if not eid:
            errors.append("V1 entity without id")
            continue
        if eid in entities:
            errors.append(f"duplicate V1 entity id: {eid}")
        entities[eid] = e
        origin[eid] = "V1"
        if e.get("type") not in ALLOWED_TYPES:
            errors.append(f"invalid entity type on {eid}: {e.get('type')}")
        if e.get("canon_scope") not in ALLOWED_CANON:
            errors.append(f"invalid canon scope on {eid}: {e.get('canon_scope')}")
        if e.get("base_ref") and e["base_ref"] not in bref:
            errors.append(f"unknown base_ref on {eid}: {e['base_ref']}")
        if e.get("legacy_ref") and e["legacy_ref"] not in bref:
            errors.append(f"unknown legacy_ref on {eid}: {e['legacy_ref']}")

    for e in graph.get("entity_extensions", []):
        eid = e.get("id")
        if not eid:
            errors.append("V2 entity extension without id")
            continue
        if eid in entities:
            errors.append(f"V2 entity extension collides with existing entity id: {eid}")
            continue
        entities[eid] = e
        origin[eid] = "V2"
        if e.get("type") not in ALLOWED_TYPES:
            errors.append(f"invalid V2 entity type on {eid}: {e.get('type')}")
        if e.get("canon_scope") not in ALLOWED_CANON:
            errors.append(f"invalid V2 canon scope on {eid}: {e.get('canon_scope')}")

    # Validate V1 graph and chronology.
    timeline_edges = []
    for r in lore.get("relations", []):
        a, b, rt = r.get("source"), r.get("target"), r.get("type")
        if a not in entities or b not in entities:
            errors.append(f"V1 relation endpoint missing: {a} {rt} {b}")
            continue
        if rt not in V1_REL:
            errors.append(f"invalid V1 relation type: {rt}")
        if r.get("source_id") not in source_ids:
            errors.append(f"unknown source_id on V1 relation {a}->{b}: {r.get('source_id')}")
        at, bt = entities[a]["type"], entities[b]["type"]
        if rt == "MEMBER_OF" and not (at == "CHARACTER" and bt in {"ORGANIZATION","FACTION"}):
            errors.append(f"V1 MEMBER_OF type mismatch: {a}->{b}")
        if rt == "PART_OF_ISLAND" and bt != "ISLAND":
            errors.append(f"V1 PART_OF_ISLAND target is not ISLAND: {a}->{b}")
        if rt in {"BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER"} and bt != "CHAPTER":
            errors.append(f"V1 chapter relation target is not CHAPTER: {a}->{b}")
        if rt == "OCCURS_IN_REALITY" and bt != "REALITY":
            errors.append(f"V1 reality relation target is not REALITY: {a}->{b}")
        if rt == "OCCURS_IN_TIMELINE" and bt != "TIMELINE":
            errors.append(f"V1 timeline relation target is not TIMELINE: {a}->{b}")
        if rt == "PRECEDES":
            if at != "HISTORICAL_EVENT" or bt != "HISTORICAL_EVENT":
                errors.append(f"V1 PRECEDES must connect historical events: {a}->{b}")
            timeline_edges.append((a, b))
    cyc = cycle_nodes(timeline_edges)
    if cyc:
        errors.append("V1 timeline PRECEDES cycle: " + " -> ".join(cyc))

    # Validate V1 scoped roles.
    for a in lore.get("role_assignments", []):
        aid = a.get("assignment_id")
        eid = a.get("entity_id")
        if eid not in entities:
            errors.append(f"role assignment unknown entity: {eid}")
            continue
        if entities[eid]["type"] != "CHARACTER":
            errors.append(f"role assignment entity is not CHARACTER: {eid}")
        if a.get("role_type") not in ALLOWED_ROLES:
            errors.append(f"invalid role type: {a.get('role_type')}")
        if not a.get("scope") or not any(v is not None for v in a.get("scope", {}).values()):
            errors.append(f"role assignment lacks temporal/context scope: {aid}")
        if a.get("source_id") not in source_ids:
            errors.append(f"role assignment has unknown source: {aid}")

    # Legacy bridges remain strict.
    for bridge in lore.get("legacy_bridges", []):
        if bridge.get("legacy_ref") not in bref:
            errors.append(f"legacy bridge references unknown base id: {bridge.get('legacy_ref')}")
        if bridge.get("canonical_entity") not in entities:
            errors.append(f"legacy bridge references unknown lore id: {bridge.get('canonical_entity')}")

    # V2 claims.
    claims = {}
    supersession_edges = []
    for c in graph.get("claims", []):
        cid = c.get("claim_id")
        if not cid:
            errors.append("V2 claim without claim_id")
            continue
        if cid in claims:
            errors.append(f"duplicate claim_id: {cid}")
            continue
        claims[cid] = c
        if c.get("claim_type") not in CLAIM_TYPES:
            errors.append(f"invalid claim_type on {cid}: {c.get('claim_type')}")
        if c.get("status") not in CLAIM_STATUSES:
            errors.append(f"invalid claim status on {cid}: {c.get('status')}")
        if c.get("canon_scope") not in ALLOWED_CANON:
            errors.append(f"invalid claim canon_scope on {cid}: {c.get('canon_scope')}")
        if c.get("evidence") not in EVIDENCE:
            errors.append(f"invalid evidence on {cid}: {c.get('evidence')}")
        if c.get("source_id") not in source_ids:
            errors.append(f"unknown source_id on claim {cid}: {c.get('source_id')}")
        a, b, pred = c.get("source_entity"), c.get("target_entity"), c.get("predicate")
        if a not in entities or b not in entities:
            errors.append(f"claim endpoint missing on {cid}: {a} {pred} {b}")
            continue
        if pred not in V2_REL:
            errors.append(f"invalid predicate on {cid}: {pred}")
        if c.get("evidence") in STRONG_EVIDENCE and not valid_https(c.get("source_url")):
            errors.append(f"strong claim lacks valid HTTPS source_url: {cid}")
        if c.get("participation_role") and c.get("participation_role") not in PARTICIPATION_ROLES:
            errors.append(f"invalid participation_role on {cid}: {c.get('participation_role')}")
        validity = c.get("validity", {}) or {}
        precision = validity.get("time_precision")
        if precision and precision not in PRECISIONS:
            errors.append(f"invalid time precision on {cid}: {precision}")
        if validity.get("chapter_id") and (validity["chapter_id"] not in entities or entities[validity["chapter_id"]]["type"] != "CHAPTER"):
            errors.append(f"claim {cid} has invalid chapter_id: {validity.get('chapter_id')}")
        if validity.get("historical_event_id") and (validity["historical_event_id"] not in entities or entities[validity["historical_event_id"]]["type"] != "HISTORICAL_EVENT"):
            errors.append(f"claim {cid} has invalid historical_event_id: {validity.get('historical_event_id')}")
        if validity.get("poi_id") and (validity["poi_id"] not in entities or entities[validity["poi_id"]]["type"] != "POI"):
            errors.append(f"claim {cid} has invalid poi_id: {validity.get('poi_id')}")
        at, bt = entities[a]["type"], entities[b]["type"]
        if pred in {"MEMBER_OF","AFFILIATED_WITH","LEADS"} and not (at == "CHARACTER" and bt in {"ORGANIZATION","FACTION"}):
            errors.append(f"{pred} type mismatch on {cid}: {at}->{bt}")
        if pred == "PART_OF_ISLAND" and bt != "ISLAND":
            errors.append(f"PART_OF_ISLAND target is not ISLAND on {cid}")
        if pred in {"BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER"} and bt != "CHAPTER":
            errors.append(f"chapter predicate target is not CHAPTER on {cid}")
        if pred == "OCCURS_IN_REALITY" and bt != "REALITY":
            errors.append(f"OCCURS_IN_REALITY target is not REALITY on {cid}")
        if pred == "OCCURS_IN_TIMELINE" and bt != "TIMELINE":
            errors.append(f"OCCURS_IN_TIMELINE target is not TIMELINE on {cid}")
        if pred == "PRECEDES" and not (at == "HISTORICAL_EVENT" and bt == "HISTORICAL_EVENT"):
            errors.append(f"PRECEDES must connect historical events on {cid}")
        if pred == "CAUSES" and c.get("evidence") != "OFFICIAL_EXPLICIT":
            errors.append(f"CAUSES requires OFFICIAL_EXPLICIT evidence: {cid}")
        if c.get("claim_type") == "PARTICIPATION" and at != "HISTORICAL_EVENT":
            errors.append(f"PARTICIPATION source must be HISTORICAL_EVENT on {cid}")
        sup = c.get("supersedes_claim_id")
        if sup:
            if sup == cid:
                errors.append(f"claim supersedes itself: {cid}")
            supersession_edges.append((cid, sup))

    for cid, c in claims.items():
        sup = c.get("supersedes_claim_id")
        if sup and sup not in claims:
            errors.append(f"claim {cid} supersedes unknown claim {sup}")
    cyc = cycle_nodes(supersession_edges)
    if cyc:
        errors.append("claim supersession cycle: " + " -> ".join(cyc))

    # Engine aliases resolve against the combined entity set.
    for alias, target in engine.get("aliases", {}).items():
        if target not in entities:
            errors.append(f"alias {alias!r} points to unknown entity {target}")

    # Index entity validation.
    for typ, ids in index.get("by_type", {}).items():
        if typ not in ALLOWED_TYPES:
            errors.append(f"index unknown type: {typ}")
        if ids != sorted(set(ids)):
            errors.append(f"index by_type/{typ} is not sorted/deduplicated")
        for eid in ids:
            if eid not in entities:
                errors.append(f"index type {typ} references unknown entity {eid}")
            elif entities[eid]["type"] != typ:
                errors.append(f"index type mismatch {typ}: {eid} is {entities[eid]['type']}")

    for section in ("alias_lookup", "legacy_lookup"):
        for key, eid in index.get(section, {}).items():
            if eid not in entities:
                errors.append(f"index {section} {key!r} references unknown entity {eid}")

    for section in ("chapter_view", "entity_view", "organization_view", "reality_view", "timeline_view"):
        for key, ids in index.get(section, {}).items():
            if key not in entities:
                errors.append(f"index {section} key is unknown entity {key}")
            if ids != sorted(set(ids)):
                errors.append(f"index {section}/{key} is not sorted/deduplicated")
            for eid in ids:
                if eid not in entities:
                    errors.append(f"index {section}/{key} references unknown entity {eid}")

    for eid, cids in index.get("claims_by_entity", {}).items():
        if eid not in entities:
            errors.append(f"claims_by_entity unknown entity: {eid}")
        if cids != sorted(set(cids)):
            errors.append(f"claims_by_entity/{eid} is not sorted/deduplicated")
        for cid in cids:
            if cid not in claims:
                errors.append(f"claims_by_entity/{eid} references unknown claim {cid}")
            elif eid not in {claims[cid].get("source_entity"), claims[cid].get("target_entity")}:
                errors.append(f"claims_by_entity/{eid} references unrelated claim {cid}")

    indexed_status = {}
    for status, cids in index.get("claims_by_status", {}).items():
        if status not in CLAIM_STATUSES:
            errors.append(f"index unknown claim status: {status}")
        for cid in cids:
            if cid not in claims:
                errors.append(f"claims_by_status/{status} references unknown claim {cid}")
            elif claims[cid].get("status") != status:
                errors.append(f"claims_by_status mismatch for {cid}: index={status}, claim={claims[cid].get('status')}")
            indexed_status[cid] = status
    for cid in claims:
        if cid not in indexed_status:
            errors.append(f"claim missing from claims_by_status index: {cid}")

    overlap = set(engine.get("materialization", {}).get("query_only_relations", [])) & set(engine.get("materialization", {}).get("allowed_forward_relations", []))
    if overlap:
        errors.append("relations cannot be both query-only and materializable: " + ",".join(sorted(overlap)))

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1

    print(
        "OK: Fortnite lore graph V2 validated — "
        f"{len(entities)} entities ({sum(1 for v in origin.values() if v == 'V2')} V2 extensions), "
        f"{len(lore.get('relations', []))} V1 relations, {len(claims)} V2 claims, "
        f"{len(lore.get('role_assignments', []))} scoped roles"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
