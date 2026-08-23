#!/usr/bin/env python3
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "calendars"
DETECTED_AT = "2026-08-23T15:18:31Z"
ICS_STAMP = "20260823T151831Z"
UPDATE_UNTIL = "20260826T151831Z"
TM_CATEGORY_URL = "https://www.ticketmaster.be/discover/antwerpen?categoryId=KZFzniwnSyZfZ7v7nE&classificationId=KnvZfZ7vAJF&language=fr-be"
TM_EVENT_URL = "https://www.ticketmaster.be/event/451606713?brand=laa&language=en-be"
LOTTO_URL = "https://www.lotto-arena.be/en/event/fortnite-global-championship-2026-c1ed5ce1"
UID = "fortnite-fncs-global-antwerp-20260926@openai"
PHYSICAL_ID = "fortnite-physical-fncs-global-antwerp-2026"
ACCESS_ID = "fortnite-access-fncs-global-antwerp-2026"


def load(name):
    return json.loads((CAL / name).read_text(encoding="utf-8"))


def dump(name, obj):
    (CAL / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def subject_scope_key(domain, subject_key, scope_key):
    scope = scope_key or ""
    return "sub_" + sha256_text(f"{domain}|{subject_key}|{scope}")


def find_head(ledger, ssk):
    items = [c for c in ledger.get("changes", []) if c.get("subject_scope_key") == ssk]
    if not items:
        return 0, None
    head = max(items, key=lambda c: c.get("subject_revision", 0))
    return head["subject_revision"], head["change_id"]


def ensure_change(ledger, *, domain, subject_key, scope_key, change_type, materiality,
                  before, after, evidence, disposition, source_refs,
                  causal_source_change_ids=None, projection_targets=None, notes=None,
                  preferred_change_id=None, preferred_state_fingerprint=None,
                  preferred_transition_fingerprint=None, detected_at=DETECTED_AT):
    ssk = subject_scope_key(domain, subject_key, scope_key)
    state_fp = preferred_state_fingerprint or sha256_text(canon(after))
    transition_fp = preferred_transition_fingerprint or sha256_text(canon({
        "change_type": change_type,
        "material_before": before,
        "material_after": after,
        "material_evidence_state": evidence,
    }))
    for c in ledger.get("changes", []):
        if c.get("subject_scope_key") == ssk and c.get("state_fingerprint") == state_fp and c.get("change_type") == change_type:
            return c["change_id"]
    rev, parent = find_head(ledger, ssk)
    new_rev = rev + 1
    raw = f"{domain}|{subject_key}|{scope_key or ''}|{new_rev}|{parent or 'null'}|{transition_fp}"
    cid = preferred_change_id or ("chg_" + sha256_text(raw)[:24])
    record = {
        "change_id": cid,
        "domain": domain,
        "subject_scope_key": ssk,
        "subject_key": subject_key,
        "subject_revision": new_rev,
        "causal_parent_change_id": parent,
        "change_type": change_type,
        "materiality": materiality,
        "state_fingerprint": state_fp,
        "transition_fingerprint": transition_fp,
        "detected_at": detected_at,
        "source_refs": source_refs,
        "notification_disposition": disposition,
        "scope_key": scope_key,
        "material_before": before,
        "material_after": after,
        "material_evidence_state": evidence,
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2",
    }
    if causal_source_change_ids:
        record["causal_source_change_ids"] = causal_source_change_ids
    if projection_targets:
        record["projection_targets"] = projection_targets
    if notes:
        record["notes"] = notes
    ledger.setdefault("changes", []).append(record)
    return cid


def replace_or_insert(lines, prefix, value, after_prefix=None):
    for i, line in enumerate(lines):
        if line.startswith(prefix):
            lines[i] = value
            return
    if after_prefix:
        for i, line in enumerate(lines):
            if line.startswith(after_prefix):
                lines.insert(i + 1, value)
                return
    # Keep custom fields before DTSTART when possible.
    for i, line in enumerate(lines):
        if line.startswith("DTSTART"):
            lines.insert(i, value)
            return
    lines.append(value)


def unfold(lines):
    out = []
    for line in lines:
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def fold_line(line, limit=75):
    if len(line.encode("utf-8")) <= limit:
        return [line]
    chunks = []
    current = ""
    current_limit = limit
    for ch in line:
        candidate = current + ch
        if len(candidate.encode("utf-8")) > current_limit and current:
            chunks.append(current)
            current = ch
            current_limit = limit - 1
        else:
            current = candidate
    if current:
        chunks.append(current)
    return [chunks[0]] + [" " + c for c in chunks[1:]]


def escape_ics_text(value):
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def update_ics(path, ticket_change_id):
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RuntimeError(f"BOM forbidden in {path}")
    text = raw.decode("utf-8")
    physical = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    start = None
    end = None
    i = 0
    while i < len(physical):
        if physical[i] == "BEGIN:VEVENT":
            j = i + 1
            while j < len(physical) and physical[j] != "END:VEVENT":
                j += 1
            if j >= len(physical):
                raise RuntimeError(f"Unclosed VEVENT in {path}")
            logical = unfold(physical[i:j+1])
            if f"UID:{UID}" in logical:
                start, end = i, j
                break
            i = j
        i += 1
    if start is None:
        raise RuntimeError(f"Target UID missing from {path}")

    logical = unfold(physical[start:end+1])
    current_status = next((x.split(":",1)[1] for x in logical if x.startswith("X-FORTNITE-TICKET-STATUS:")), None)
    if current_status != "LOW_AVAILABILITY":
        seq_idx = next(i for i,x in enumerate(logical) if x.startswith("SEQUENCE:"))
        logical[seq_idx] = f"SEQUENCE:{int(logical[seq_idx].split(':',1)[1]) + 1}"
    replace_or_insert(logical, "DTSTAMP:", f"DTSTAMP:{ICS_STAMP}")
    replace_or_insert(logical, "LAST-MODIFIED:", f"LAST-MODIFIED:{ICS_STAMP}")
    replace_or_insert(logical, "X-FORTNITE-ACTION:", "X-FORTNITE-ACTION:BUY_TICKET")
    replace_or_insert(logical, "X-FORTNITE-TICKET-STATUS:", "X-FORTNITE-TICKET-STATUS:LOW_AVAILABILITY")
    replace_or_insert(logical, "X-FORTNITE-TICKET-LAST-TRANSITION:", "X-FORTNITE-TICKET-LAST-TRANSITION:BACK_ON_SALE", "X-FORTNITE-TICKET-STATUS:")
    replace_or_insert(logical, "X-FORTNITE-TICKET-CONFIDENCE:", "X-FORTNITE-TICKET-CONFIDENCE:HIGH", "X-FORTNITE-TICKET-LAST-TRANSITION:")
    replace_or_insert(logical, "X-FORTNITE-TICKET-SCARCITY-EVIDENCE:", "X-FORTNITE-TICKET-SCARCITY-EVIDENCE:EXPLICIT_TEXT", "X-FORTNITE-TICKET-CONFIDENCE:")
    replace_or_insert(logical, "X-FORTNITE-ACCESS-PROFILE-ID:", f"X-FORTNITE-ACCESS-PROFILE-ID:{ACCESS_ID}", "X-FORTNITE-TICKET-SCARCITY-EVIDENCE:")
    replace_or_insert(logical, "X-FORTNITE-ACCESS-STATE:", "X-FORTNITE-ACCESS-STATE:TICKET_REQUIRED", "X-FORTNITE-ACCESS-PROFILE-ID:")
    replace_or_insert(logical, "X-FORTNITE-ADMISSION-MODE:", "X-FORTNITE-ADMISSION-MODE:PAID_TICKET", "X-FORTNITE-ACCESS-STATE:")
    replace_or_insert(logical, "X-FORTNITE-LAST-CHANGE-ID:", f"X-FORTNITE-LAST-CHANGE-ID:{ticket_change_id}", "X-FORTNITE-ADMISSION-MODE:")
    replace_or_insert(logical, "X-FORTNITE-TICKET-CATEGORY;KEY=STANDARD_2_DAY;", "X-FORTNITE-TICKET-CATEGORY;KEY=STANDARD_2_DAY;STATUS=LOW_AVAILABILITY;SCARCITY-EVIDENCE=EXPLICIT_TEXT:Billet standard 2 jours")
    replace_or_insert(logical, "X-FORTNITE-TICKET-CATEGORY;KEY=ULTIMATE_LIVE_EXPERIENCE_2_DAY;", "X-FORTNITE-TICKET-CATEGORY;KEY=ULTIMATE_LIVE_EXPERIENCE_2_DAY;STATUS=AVAILABLE;PRICE-EUR=324.70:Ultimate Live Experience Package 2 jours")
    replace_or_insert(logical, "X-FORTNITE-LAST-MAJOR-UPDATE-AT:", f"X-FORTNITE-LAST-MAJOR-UPDATE-AT:{ICS_STAMP}")
    replace_or_insert(logical, "X-FORTNITE-UPDATE-UNTIL:", f"X-FORTNITE-UPDATE-UNTIL:{UPDATE_UNTIL}")
    replace_or_insert(logical, "X-FORTNITE-UPDATE-REASON:", "X-FORTNITE-UPDATE-REASON:TICKETING_BACK_ON_SALE")
    for idx, line in enumerate(logical):
        if line.startswith("SUMMARY:") and "✨" not in line:
            logical[idx] = line.replace("SUMMARY:⭐ ✅ 🆕 ", "SUMMARY:⭐ ✅ 🆕 ✨ ")
            break
    description = (
        "Priorité : ⭐ Important. Championnat global Fortnite 2026 en présentiel.\n"
        "Dates : 26 et 27 septembre 2026.\n"
        "Format : 50 duos, 12 parties sur deux jours, 2 000 000 $ de dotation annoncée par Fortnite Competitive.\n"
        "🎟️ Billetterie : retour d’inventaire après la liste d’attente. Ticketmaster Belgique affiche maintenant le pass 2 jours en « Disponibilité limitée » et propose l’accès aux tickets. La liste d’attente reste proposée en parallèle ; aucun nombre de places restantes n’est déduit. Aucun billet à la journée n’est annoncé.\n"
        "✨ Ultimate Live Experience Package : 324,70 € sur Lotto Arena ; le package reste présenté avec un accès d’achat, sans quantité restante affirmée.\n"
        "🔞 Restriction d’âge publiée : 16+.\n"
        "🕒 Lotto Arena affiche 14h00 le samedi 26 et 18h30 le dimanche 27 comme horaires salle ; ils ne sont pas traités comme horaires officiels des parties FNCS.\n"
        "📍 Lotto Arena, Schijnpoortweg 119, Anvers, Belgique.\n"
        "Rappels : J-30, J-7 et J-1.\n"
        f"Ticketmaster : {TM_CATEGORY_URL}\n"
        f"Lotto Arena : {LOTTO_URL}"
    )
    replace_or_insert(logical, "DESCRIPTION:", "DESCRIPTION:" + escape_ics_text(description))

    new_block = []
    for line in logical:
        new_block.extend(fold_line(line))
    physical[start:end+1] = new_block
    out = "\r\n".join(physical)
    if not out.endswith("\r\n"):
        out += "\r\n"
    path.write_bytes(out.encode("utf-8"))


def rebuild_consumed(outbox):
    intents = {i["intent_id"]: i for i in outbox.get("intents", [])}
    grouped = {}
    for e in outbox.get("delivery_events", []):
        grouped.setdefault(e["intent_id"], []).append(e)
    derived = {}
    for iid, events in grouped.items():
        events = sorted(events, key=lambda e: e.get("at", ""))
        latest = None
        reserved = False
        for e in events:
            if e["state"] == "RESERVED":
                reserved = True
                latest = e
            elif e["state"] in {"SENT", "UNKNOWN_DELIVERY"} and reserved:
                latest = e
        if latest and iid in intents:
            key = intents[iid]["notification_key"]
            derived[key] = {"intent_id": iid, "state": latest["state"], "last_event_id": latest["delivery_event_id"]}
    outbox["consumed_keys"] = derived


def reconcile_stale_reservations(outbox):
    now = parse_dt(DETECTED_AT)
    by_intent = {}
    for e in outbox.get("delivery_events", []):
        by_intent.setdefault(e["intent_id"], []).append(e)
    for iid, events in by_intent.items():
        states = {e["state"] for e in events}
        if "RESERVED" not in states or states.intersection({"SENT", "UNKNOWN_DELIVERY"}):
            continue
        reserved = min((e for e in events if e["state"] == "RESERVED"), key=lambda e: e["at"])
        if (now - parse_dt(reserved["at"])).total_seconds() <= 1800:
            continue
        key = reserved["notification_key"]
        eid = "nde_" + sha256_text(f"{iid}|UNKNOWN_DELIVERY|{DETECTED_AT}")[:24]
        if not any(e.get("delivery_event_id") == eid for e in outbox.get("delivery_events", [])):
            outbox.setdefault("delivery_events", []).append({
                "delivery_event_id": eid,
                "intent_id": iid,
                "notification_key": key,
                "state": "UNKNOWN_DELIVERY",
                "at": DETECTED_AT,
                "failure_class": "RESERVED_WITHOUT_SENT_ACK_AFTER_TIMEOUT",
                "note": "Reservation exceeded the 30-minute stale threshold. Key remains consumed; automatic replay is forbidden."
            })
            outbox.setdefault("history", []).append({
                "at": DETECTED_AT,
                "type": "NOTIFICATION_DELIVERY_UNKNOWN",
                "notification_key": key,
                "note": "Stale reservation reconciled conservatively; no automatic resend."
            })


def reserve_notification(outbox, change_ids):
    notice_kind = "FNCS_ANTWERP_TICKETS_BACK_ON_SALE_LIMITED"
    audience = "user"
    channel = "chat"
    ids = sorted(change_ids)
    notification_key = "ntf_" + sha256_text(f"{','.join(ids)}|{notice_kind}|{audience}|{channel}")
    rebuild_consumed(outbox)
    if notification_key in outbox.get("consumed_keys", {}):
        return notification_key
    if any(i.get("notification_key") == notification_key for i in outbox.get("intents", [])):
        return notification_key
    intent_id = "nti_" + sha256_text(notification_key)[:24]
    group_key = "grp_" + sha256_text(f"fncs-antwerp-ticketing|{','.join(ids)}|{notice_kind}|{audience}|{channel}")
    payload = "🎟️ FNCS Global Championship Anvers — des billets 2 jours sont de nouveau disponibles. Ticketmaster les affiche en « Disponibilité limitée ». La liste d’attente reste proposée, et Lotto Arena indique toujours qu’il n’y a pas de billet à la journée. Le package Ultimate Live Experience est affiché à 324,70 €."
    reservation_id = "nrs_" + uuid.uuid4().hex[:24]
    event_id = "nde_" + sha256_text(f"{intent_id}|RESERVED|1|{DETECTED_AT}|{reservation_id}")[:24]
    outbox.setdefault("intents", []).append({
        "intent_id": intent_id,
        "notification_key": notification_key,
        "change_ids": ids,
        "notice_kind": notice_kind,
        "audience_key": audience,
        "channel_key": channel,
        "payload_fingerprint": sha256_text(payload),
        "render_version": "FORTNITE_ALERT_FR_V1",
        "created_at": DETECTED_AT,
        "group_key": group_key,
        "subject_key": UID,
        "locale": "fr-FR",
        "payload_snapshot": payload,
        "condition_snapshot": {
            "ticket_status": "LOW_AVAILABILITY",
            "ticket_scope": "STANDARD_2_DAY",
            "waiting_list_available": True,
            "single_day_available": False,
            "event_date_start": "2026-09-26",
            "event_date_end": "2026-09-27"
        },
        "policy_version": "FORTNITE_CHANGE_ENGINE_FR_V2"
    })
    outbox.setdefault("delivery_events", []).append({
        "delivery_event_id": event_id,
        "intent_id": intent_id,
        "notification_key": notification_key,
        "state": "RESERVED",
        "at": DETECTED_AT,
        "reservation_id": reservation_id,
        "note": "Reserved after fresh canonical reconciliation of Ticketmaster limited inventory returning after WAITLIST. This consumes the key before user-visible emission."
    })
    outbox.setdefault("group_index", {})[group_key] = intent_id
    outbox.setdefault("history", []).append({
        "at": DETECTED_AT,
        "type": "NOTIFICATION_RESERVED",
        "notification_key": notification_key,
        "note": "One coalesced notification reserved for FNCS Antwerp tickets returning from WAITLIST with direct LIMITED_AVAILABILITY evidence."
    })
    rebuild_consumed(outbox)
    return notification_key


def rebuild_change_index(index, ledger, outbox):
    changes = ledger.get("changes", [])
    heads = {}
    by_domain = {}
    by_type = {}
    open_by_subject = {}
    for c in changes:
        cid = c["change_id"]
        ssk = c["subject_scope_key"]
        rev = c["subject_revision"]
        if ssk not in heads or rev > heads[ssk]["revision"]:
            heads[ssk] = {"revision": rev, "change_id": cid}
        by_domain.setdefault(c["domain"], []).append(cid)
        by_type.setdefault(c["change_type"], []).append(cid)
        if c.get("state", "OPEN") == "OPEN":
            open_by_subject.setdefault(ssk, []).append(cid)
    index["subject_heads"] = {k: heads[k] for k in sorted(heads)}
    index["by_domain"] = {k: sorted(v) for k,v in sorted(by_domain.items())}
    index["by_change_type"] = {k: sorted(v) for k,v in sorted(by_type.items())}
    index["open_changes_by_subject"] = {k: sorted(v) for k,v in sorted(open_by_subject.items())}
    consumed = outbox.get("consumed_keys", {})
    index["consumed_notification_keys"] = sorted(consumed)
    index["unknown_delivery_keys"] = sorted(k for k,v in consumed.items() if v.get("state") == "UNKNOWN_DELIVERY")
    index["updated_at"] = DETECTED_AT
    index["stats"] = {
        "changes": len(changes),
        "subjects": len(heads),
        "notification_intents": len(outbox.get("intents", [])),
        "consumed_notification_keys": len(consumed),
        "unknown_delivery": len(index["unknown_delivery_keys"]),
        "pending_reconciliation": len(index.get("pending_reconciliation", [])),
    }


def rebuild_physical_index(index, physical, access):
    access_by_id = {e["access_profile_id"]: e for e in access.get("entries", [])}
    events = physical.get("entries", [])
    def bucket(values):
        return {k: sorted(v) for k,v in values.items()}
    by_type = {k: [] for k in physical.get("event_types", [])}
    by_country = {}
    by_city = {}
    by_visibility = {k: [] for k in physical.get("visibility_levels", [])}
    by_comp = {k: [] for k in physical.get("operational_completeness", [])}
    by_action = {k: [] for k in physical.get("action_types", [])}
    by_travel = {k: [] for k in physical.get("travel_scopes", [])}
    by_access = {}
    by_venue = {}
    by_date = {}
    sessions_by_date = {}
    uids = {}
    for e in events:
        pid = e["physical_event_id"]
        by_type.setdefault(e["event_type"], []).append(pid)
        by_country.setdefault(e["country_code"], []).append(pid)
        by_city.setdefault(e["city"], []).append(pid)
        by_visibility.setdefault(e["visibility"], []).append(pid)
        by_comp.setdefault(e["operational_completeness"], []).append(pid)
        by_action.setdefault(e["primary_action"], []).append(pid)
        by_travel.setdefault(e["travel_scope"], []).append(pid)
        if e.get("venue_id"):
            by_venue.setdefault(e["venue_id"], []).append(pid)
        by_date.setdefault(e["start_date"], []).append(pid)
        if e.get("event_uid"):
            uids[pid] = e["event_uid"]
        ap = access_by_id.get(e.get("access_profile_id"))
        access_state = ap.get("access_state") if ap else e.get("current_admission_state", "UNKNOWN")
        by_access.setdefault(access_state or "UNKNOWN", []).append(pid)
        for s in e.get("public_sessions", []):
            if s.get("start_at"):
                d = s["start_at"][:10]
                sessions_by_date.setdefault(d, []).append(f"{pid}:{s['session_id']}")
    index["updated_at"] = DETECTED_AT
    index["by_type"] = bucket(by_type)
    index["by_country"] = bucket(by_country)
    index["by_city"] = bucket(by_city)
    index["by_visibility"] = bucket(by_visibility)
    index["by_operational_completeness"] = bucket(by_comp)
    index["by_primary_action"] = bucket(by_action)
    index["by_travel_scope"] = bucket(by_travel)
    index["by_access_state"] = bucket(by_access)
    index["by_venue"] = bucket(by_venue)
    index["by_date"] = bucket(by_date)
    index["public_sessions_by_date"] = bucket(sessions_by_date)
    index["calendar_uids"] = {k: uids[k] for k in sorted(uids)}


def main():
    ticketing = load("fortnite-ticketing-france.json")
    access = load("fortnite-physical-access-france.json")
    physical = load("fortnite-physical-events-france.json")
    pindex = load("fortnite-physical-events-index-france.json")
    ledger = load("fortnite-change-ledger.json")
    outbox = load("fortnite-notification-outbox-france.json")
    cindex = load("fortnite-change-index-france.json")

    # First, finish a previously recorded ledger-only reconciliation, if still pending.
    remaining = []
    for rec in cindex.get("pending_reconciliation", []):
        if rec.get("reconciliation_id") == "rec_performance_eval_20260823":
            ensure_change(
                ledger,
                domain="COMPETITIVE",
                subject_key=rec["subject_key"],
                scope_key=None,
                change_type=rec["expected_change_type"],
                materiality=rec["expected_materiality"],
                before=None,
                after={
                    "competition_id": "performance-evaluation-eu-2026",
                    "visibility": "LEDGER_ONLY",
                    "season_id": "C7S4",
                    "ruleset": "BUILD",
                    "team_format": "DUOS",
                    "first_eu_sessions": ["2026-08-23T16:00:00+02:00", "2026-08-23T19:00:00+02:00"],
                    "qualification": "TOP_50_TO_ROUND_2"
                },
                evidence="OFFICIAL_FORTNITE_COMPETITIVE_EU",
                disposition=rec["expected_notification_disposition"],
                source_refs=["https://www.fortnite.com/competitive/events/S42_PerformanceEvaluation/?region=EU", "https://www.fortnite.com/competitive/schedule?lang=en-US&region=EU"],
                notes="Reconciled from the derived pending queue. Performance Evaluation remains ledger-only and notification-silent.",
                preferred_change_id=rec.get("expected_change_id"),
                preferred_state_fingerprint=rec.get("state_fingerprint"),
                preferred_transition_fingerprint=rec.get("transition_fingerprint"),
                detected_at=rec.get("detected_at", DETECTED_AT),
            )
        else:
            remaining.append(rec)
    cindex["pending_reconciliation"] = remaining

    tentry = next(e for e in ticketing["entries"] if e["event_uid"] == UID)
    # Out-of-order guard: never overwrite a newer material ticketing transition.
    if tentry.get("last_changed_at") and parse_dt(tentry["last_changed_at"]) > parse_dt(DETECTED_AT) and tentry.get("status") != "LOW_AVAILABILITY":
        raise RuntimeError("A newer Antwerp ticketing transition exists; refusing to overwrite it with this observation.")

    ticket_before = {"status": tentry.get("status"), "category_key": "STANDARD_2_DAY", "waiting_list_available": bool(tentry.get("waiting_list_available"))}
    ticket_after = {"status": "LOW_AVAILABILITY", "category_key": "STANDARD_2_DAY", "waiting_list_available": True, "acquisition_action": "BUY_TICKET"}
    ticket_evidence = {"confidence": "HIGH", "scarcity_evidence": "EXPLICIT_TEXT", "source_semantics": "TICKETMASTER_LIMITED_AVAILABILITY"}
    ticket_change_id = ensure_change(
        ledger,
        domain="TICKETING",
        subject_key=f"{UID}|lotto_arena|STANDARD_2_DAY",
        scope_key="lotto_arena|STANDARD_2_DAY",
        change_type="BACK_ON_SALE",
        materiality="NOTIFY",
        before=ticket_before,
        after=ticket_after,
        evidence=ticket_evidence,
        disposition="ELIGIBLE_NOW",
        source_refs=[TM_CATEGORY_URL, TM_EVENT_URL, LOTTO_URL],
        projection_targets=["calendars/fortnite-competitive-france.ics", "calendars/fortnite-paris.ics"],
        notes="Direct Ticketmaster category listing changed the two-day product from waiting-list-only semantics to LIMITED_AVAILABILITY with a live ticket CTA. Waiting list remains available as a fallback; no remaining quantity is inferred."
    )

    if tentry.get("status") != "LOW_AVAILABILITY":
        old_status = tentry.get("status")
        tentry["previous_status"] = old_status
        tentry["status"] = "LOW_AVAILABILITY"
        tentry["status_origin"] = "DIRECT_VERIFIED"
        tentry["confidence"] = "HIGH"
        tentry["scarcity_evidence"] = "EXPLICIT_TEXT"
        tentry["waiting_list_available"] = True
        tentry["last_verified_at"] = DETECTED_AT
        tentry["last_changed_at"] = DETECTED_AT
        for s in tentry.get("session_states", []):
            s["status"] = "LOW_AVAILABILITY"
            s["confidence"] = "MEDIUM"
            s["scarcity_evidence"] = "EXPLICIT_TEXT"
        for c in tentry.get("category_states", []):
            if c.get("category_key") == "STANDARD_2_DAY":
                c["status"] = "LOW_AVAILABILITY"
                c["scarcity_evidence"] = "EXPLICIT_TEXT"
                c["confidence"] = "HIGH"
                c["source"] = "Ticketmaster Belgium direct — LIMITED_AVAILABILITY"
            elif c.get("category_key") == "ULTIMATE_LIVE_EXPERIENCE_2_DAY":
                c["status"] = "AVAILABLE"
                c["scarcity_evidence"] = "UNKNOWN"
                c["confidence"] = "HIGH"
                c["source"] = "Lotto Arena direct purchase listing; exact remaining quantity not published"
        tentry.setdefault("history", []).append({
            "at": DETECTED_AT,
            "type": "BACK_ON_SALE",
            "from": old_status,
            "to": "LOW_AVAILABILITY",
            "source": TM_CATEGORY_URL,
            "confidence": "HIGH",
            "scarcity_evidence": "EXPLICIT_TEXT",
            "note": "Ticketmaster Belgium now displays 'Disponibilité limitée' with a ticket CTA for the 2-day Fortnite Global Championship product. Waiting list remains offered; no ticket count is inferred."
        })
        ticketing["updated_at"] = DETECTED_AT

    aentry = next(e for e in access["entries"] if e["access_profile_id"] == ACCESS_ID)
    access_before = {"access_state": aentry.get("access_state"), "admission_mode": aentry.get("admission_mode")}
    access_after = {"access_state": "TICKET_REQUIRED", "admission_mode": "PAID_TICKET", "acquisition_action": "BUY_TICKET", "ticket_inventory_state": "LOW_AVAILABILITY"}
    access_change_id = ensure_change(
        ledger,
        domain="PHYSICAL_ACCESS",
        subject_key=ACCESS_ID,
        scope_key=None,
        change_type="ACCESS_CHANGED",
        materiality="CALENDAR",
        before=access_before,
        after=access_after,
        evidence={"confidence": "HIGH", "source_semantics": "TICKETMASTER_LIMITED_AVAILABILITY"},
        disposition="NOT_APPLICABLE",
        source_refs=[TM_CATEGORY_URL, LOTTO_URL],
        causal_source_change_ids=[ticket_change_id],
        projection_targets=["calendars/fortnite-competitive-france.ics", "calendars/fortnite-paris.ics"],
        notes="Mirror access transition only; user notification collapses to the underlying ticketing BACK_ON_SALE effect."
    )
    if aentry.get("access_state") != "TICKET_REQUIRED" or aentry.get("admission_mode") != "PAID_TICKET":
        aentry["access_state"] = "TICKET_REQUIRED"
        aentry["admission_mode"] = "PAID_TICKET"
        aentry["source_url"] = TM_CATEGORY_URL
        aentry.setdefault("history", []).append({
            "at": DETECTED_AT,
            "type": "ACCESS_CHANGED",
            "from": "WAITLIST_ONLY",
            "to": "TICKET_REQUIRED",
            "source_url": TM_CATEGORY_URL,
            "note": "Direct 2-day ticket inventory is actionable again with LIMITED_AVAILABILITY. Admission still requires a valid ticket; no ID, re-entry, bag, queue or capacity rule is inferred."
        })
        access["updated_at"] = DETECTED_AT

    pentry = next(e for e in physical["entries"] if e["physical_event_id"] == PHYSICAL_ID)
    physical_before = {"status": pentry.get("status"), "current_ticket_state": pentry.get("current_ticket_state"), "current_admission_state": pentry.get("current_admission_state"), "primary_action": pentry.get("primary_action")}
    physical_after = {"status": "TICKETS_ON_SALE", "current_ticket_state": "LOW_AVAILABILITY", "current_admission_state": "TICKET_REQUIRED", "primary_action": "BUY_TICKET"}
    physical_change_id = ensure_change(
        ledger,
        domain="PHYSICAL_EVENT",
        subject_key=PHYSICAL_ID,
        scope_key=None,
        change_type="ACCESS_CHANGED",
        materiality="CALENDAR",
        before=physical_before,
        after=physical_after,
        evidence="DIRECT_TICKETING_BACK_ON_SALE",
        disposition="NOT_APPLICABLE",
        source_refs=[TM_CATEGORY_URL, LOTTO_URL],
        causal_source_change_ids=[ticket_change_id, access_change_id],
        projection_targets=["calendars/fortnite-competitive-france.ics", "calendars/fortnite-paris.ics"],
        notes="Physical-event summary mirrors the ticketing/access truth and does not create a second user effect."
    )
    if pentry.get("current_ticket_state") != "LOW_AVAILABILITY" or pentry.get("primary_action") != "BUY_TICKET":
        pentry["status"] = "TICKETS_ON_SALE"
        pentry["current_ticket_state"] = "LOW_AVAILABILITY"
        pentry["current_admission_state"] = "TICKET_REQUIRED"
        pentry["primary_action"] = "BUY_TICKET"
        pentry.setdefault("history", []).append({
            "at": DETECTED_AT,
            "type": "TICKETING_BRIDGE_TRANSITION",
            "from": "WAITLIST",
            "to": "LOW_AVAILABILITY",
            "primary_action": "BUY_TICKET",
            "note": "Ticketmaster limited inventory returned after waitlist; physical planning now has an actionable purchase path."
        })
        physical["updated_at"] = DETECTED_AT

    # Calendar business projections stay synchronized on the same UID/SEQUENCE.
    update_ics(CAL / "fortnite-paris.ics", ticket_change_id)
    update_ics(CAL / "fortnite-competitive-france.ics", ticket_change_id)

    # Conservative outbox reconciliation, then reserve the new user effect exactly once.
    reconcile_stale_reservations(outbox)
    notification_key = reserve_notification(outbox, [ticket_change_id, access_change_id, physical_change_id])
    outbox["updated_at"] = DETECTED_AT

    ledger["updated_at"] = DETECTED_AT
    ledger.setdefault("history", []).append({
        "at": DETECTED_AT,
        "type": "MATERIAL_FNCS_ANTWERP_BACK_ON_SALE",
        "note": "Ticketmaster Belgium now exposes LIMITED_AVAILABILITY for the 2-day Global Championship product after the prior WAITLIST state. Access and physical-event mirrors are linked to the single ticketing user effect."
    })

    rebuild_consumed(outbox)
    rebuild_change_index(cindex, ledger, outbox)
    rebuild_physical_index(pindex, physical, access)

    dump("fortnite-ticketing-france.json", ticketing)
    dump("fortnite-physical-access-france.json", access)
    dump("fortnite-physical-events-france.json", physical)
    (CAL / "fortnite-physical-events-index-france.json").write_text(json.dumps(pindex, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dump("fortnite-change-ledger.json", ledger)
    dump("fortnite-notification-outbox-france.json", outbox)
    dump("fortnite-change-index-france.json", cindex)

    print(f"Reconciled Antwerp back-on-sale; notification key={notification_key}")


if __name__ == "__main__":
    main()
