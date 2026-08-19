#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
BASE = CAL / "fortnite-taxonomy-france.json"
LORE = CAL / "fortnite-lore-taxonomy-france.json"
ENGINE = CAL / "fortnite-lore-engine-france.json"
INDEX = CAL / "fortnite-lore-index-france.json"
SOURCES = CAL / "fortnite-sources-france.json"
LORE_SOURCES = CAL / "fortnite-lore-sources-france.json"

ALLOWED_TYPES = {"CHARACTER","ORGANIZATION","FACTION","POI","ISLAND","LORE_OBJECT","HISTORICAL_EVENT","REALITY","TIMELINE","LORE_CONCEPT","CHAPTER"}
ALLOWED_CANON = {"MAIN_STORY","COLLAB_CANON","GAMEPLAY_ONLY","COSMETIC_ONLY","META","UNKNOWN"}
ALLOWED_REL = {"MEMBER_OF","OPPOSES","PART_OF_ISLAND","BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER","OCCURS_IN_REALITY","OCCURS_IN_TIMELINE","INVOLVES","CENTERS_ON","LOCATED_AT","PRECEDES","SUCCESSOR_OF","SAME_ENTITY_AS_LEGACY"}
ALLOWED_ROLES = {"NPC","BOSS","QUEST_GIVER","VENDOR","ALLY","HOSTILE","NEUTRAL"}


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
    cycle = []
    def dfs(node, stack):
        if node in visiting:
            i = stack.index(node) if node in stack else 0
            cycle.extend(stack[i:] + [node])
            return True
        if node in visited:
            return False
        visiting.add(node)
        stack.append(node)
        for nxt in graph.get(node, []):
            if dfs(nxt, stack):
                return True
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return False
    for node in graph:
        if dfs(node, []):
            return cycle
    return []


def main():
    errors = []
    for p in (BASE, LORE, ENGINE, INDEX, SOURCES, LORE_SOURCES):
        if not p.exists():
            errors.append(f"missing required file: {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        return 1

    base = load(BASE)
    lore = load(LORE)
    engine = load(ENGINE)
    index = load(INDEX)
    sources = load(SOURCES)
    lore_sources = load(LORE_SOURCES)

    if lore.get("version") != "FORTNITE_LORE_TAXONOMY_FR_V1":
        errors.append("unexpected lore taxonomy version")
    if engine.get("version") != "FORTNITE_LORE_ENGINE_FR_V1":
        errors.append("unexpected lore engine version")
    if index.get("version") != "FORTNITE_LORE_INDEX_FR_V1":
        errors.append("unexpected lore index version")
    if lore_sources.get("version") != "FORTNITE_LORE_SOURCE_POLICY_FR_V1":
        errors.append("unexpected lore source policy version")
    if lore_sources.get("inherits") != SOURCES.name:
        errors.append("lore source policy inherits wrong registry")
    if lore.get("base_registry") != BASE.name or engine.get("base_registry") != BASE.name:
        errors.append("base registry mismatch")
    if engine.get("lore_registry") != LORE.name:
        errors.append("lore engine registry mismatch")

    source_ids = {s.get("source_id") for s in sources.get("sources", []) if s.get("source_id")}
    for source_id in lore_sources.get("authority", {}).keys():
        if source_id not in source_ids:
            errors.append(f"lore source policy references unknown source_id: {source_id}")

    bref = base_refs(base)
    entities = {}
    for e in lore.get("entities", []):
        eid = e.get("id")
        if not eid:
            errors.append("entity without id")
            continue
        if eid in entities:
            errors.append(f"duplicate entity id: {eid}")
        entities[eid] = e
        if e.get("type") not in ALLOWED_TYPES:
            errors.append(f"invalid entity type on {eid}: {e.get('type')}")
        if e.get("canon_scope") not in ALLOWED_CANON:
            errors.append(f"invalid canon scope on {eid}: {e.get('canon_scope')}")
        if e.get("base_ref") and e["base_ref"] not in bref:
            errors.append(f"unknown base_ref on {eid}: {e['base_ref']}")
        if e.get("legacy_ref") and e["legacy_ref"] not in bref:
            errors.append(f"unknown legacy_ref on {eid}: {e['legacy_ref']}")

    timeline_edges = []
    for r in lore.get("relations", []):
        a, b, rt = r.get("source"), r.get("target"), r.get("type")
        if a not in entities or b not in entities:
            errors.append(f"relation endpoint missing: {a} {rt} {b}")
            continue
        if rt not in ALLOWED_REL:
            errors.append(f"invalid relation type: {rt}")
        if r.get("source_id") not in source_ids:
            errors.append(f"unknown source_id on relation {a}->{b}: {r.get('source_id')}")
        at, bt = entities[a]["type"], entities[b]["type"]
        if rt == "MEMBER_OF" and not (at == "CHARACTER" and bt in {"ORGANIZATION","FACTION"}):
            errors.append(f"MEMBER_OF type mismatch: {a}->{b}")
        if rt == "PART_OF_ISLAND" and bt != "ISLAND":
            errors.append(f"PART_OF_ISLAND target is not ISLAND: {a}->{b}")
        if rt in {"BELONGS_TO_CHAPTER","OCCURS_IN_CHAPTER"} and bt != "CHAPTER":
            errors.append(f"chapter relation target is not CHAPTER: {a}->{b}")
        if rt == "OCCURS_IN_REALITY" and bt != "REALITY":
            errors.append(f"reality relation target is not REALITY: {a}->{b}")
        if rt == "OCCURS_IN_TIMELINE" and bt != "TIMELINE":
            errors.append(f"timeline relation target is not TIMELINE: {a}->{b}")
        if rt == "PRECEDES":
            if at != "HISTORICAL_EVENT" or bt != "HISTORICAL_EVENT":
                errors.append(f"PRECEDES must connect historical events: {a}->{b}")
            timeline_edges.append((a, b))

    cyc = cycle_nodes(timeline_edges)
    if cyc:
        errors.append("timeline PRECEDES cycle: " + " -> ".join(cyc))

    for a in lore.get("role_assignments", []):
        if a.get("entity_id") not in entities:
            errors.append(f"role assignment unknown entity: {a.get('entity_id')}")
            continue
        if entities[a["entity_id"]]["type"] != "CHARACTER":
            errors.append(f"role assignment entity is not CHARACTER: {a.get('entity_id')}")
        if a.get("role_type") not in ALLOWED_ROLES:
            errors.append(f"invalid role type: {a.get('role_type')}")
        if not a.get("scope") or not any(v is not None for v in a.get("scope", {}).values()):
            errors.append(f"role assignment lacks temporal/context scope: {a.get('assignment_id')}")
        if a.get("source_id") not in source_ids:
            errors.append(f"role assignment has unknown source: {a.get('assignment_id')}")

    for bridge in lore.get("legacy_bridges", []):
        if bridge.get("legacy_ref") not in bref:
            errors.append(f"legacy bridge references unknown base id: {bridge.get('legacy_ref')}")
        if bridge.get("canonical_entity") not in entities:
            errors.append(f"legacy bridge references unknown lore id: {bridge.get('canonical_entity')}")

    for alias, target in engine.get("aliases", {}).items():
        if target not in entities:
            errors.append(f"alias {alias!r} points to unknown entity {target}")

    for typ, ids in index.get("by_type", {}).items():
        if typ not in ALLOWED_TYPES:
            errors.append(f"index unknown type: {typ}")
        for eid in ids:
            if eid not in entities:
                errors.append(f"index type {typ} references unknown entity {eid}")
            elif entities[eid]["type"] != typ:
                errors.append(f"index type mismatch {typ}: {eid} is {entities[eid]['type']}")

    for section in ("alias_lookup", "legacy_lookup"):
        for key, eid in index.get(section, {}).items():
            if eid not in entities:
                errors.append(f"index {section} {key!r} references unknown entity {eid}")
    for section in ("chapter_view", "entity_view", "timeline_view"):
        for key, ids in index.get(section, {}).items():
            if key not in entities:
                errors.append(f"index {section} key is unknown entity {key}")
            for eid in ids:
                if eid not in entities:
                    errors.append(f"index {section}/{key} references unknown entity {eid}")

    overlap = set(engine.get("materialization", {}).get("query_only_relations", [])) & set(engine.get("materialization", {}).get("allowed_forward_relations", []))
    if overlap:
        errors.append("relations cannot be both query-only and materializable: " + ",".join(sorted(overlap)))

    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print(f"OK: Fortnite lore taxonomy validated — {len(entities)} entities, {len(lore.get('relations', []))} relations, {len(lore.get('role_assignments', []))} scoped roles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
