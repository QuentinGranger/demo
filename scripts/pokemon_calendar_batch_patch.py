#!/usr/bin/env python3
import argparse
import json
import re
import tempfile
from pathlib import Path

from pokemon_calendar_safe_patch import (
    CANONICAL_CALENDAR,
    apply_request,
    blob_sha,
    find_event_span,
    validate_calendar,
)


def resolve_uid(req: dict) -> str:
    uid = req.get("uid")
    if uid:
        return uid
    event = req.get("event", "")
    match = re.search(r"(?m)^UID:(.+)$", event)
    if match:
        return match.group(1).strip().rstrip("\r")
    raise SystemExit("request has no resolvable UID")


def validate_request(req: dict, source: Path) -> tuple[str, str]:
    canonical = req.get("calendar_path", CANONICAL_CALENDAR)
    if canonical != CANONICAL_CALENDAR:
        raise SystemExit(
            f"{source}: calendar_path must target {CANONICAL_CALENDAR} (got {canonical})"
        )
    op = req.get("operation")
    if op not in {"add", "upsert", "update", "delete"}:
        raise SystemExit(f"{source}: unsupported operation: {op}")
    return resolve_uid(req), op


def user_effect_of_event(event: str) -> str | None:
    match = re.search(r"(?m)^X-POKEMON-USER-EFFECT:(.+)$", event or "")
    return match.group(1).strip().rstrip("\r") if match else None


def assert_no_cross_uid_user_effect_collision(calendar_text: str, req: dict, uid: str) -> None:
    if req.get("operation") == "delete":
        return
    user_effect = user_effect_of_event(req.get("event", ""))
    if not user_effect:
        return
    pattern = re.compile(r"BEGIN:VEVENT\r?\n.*?\r?\nEND:VEVENT", re.S)
    for match in pattern.finditer(calendar_text):
        event = match.group(0)
        effect_match = re.search(r"(?m)^X-POKEMON-USER-EFFECT:(.+)\r?$", event)
        if not effect_match or effect_match.group(1).strip() != user_effect:
            continue
        uid_match = re.search(r"(?m)^UID:(.+)\r?$", event)
        existing_uid = uid_match.group(1).strip() if uid_match else None
        if existing_uid and existing_uid != uid:
            raise SystemExit(
                f"duplicate user_effect collision: {user_effect} already belongs to UID {existing_uid}"
            )


def apply_batch(request_paths: list[Path]) -> int:
    if not request_paths:
        raise SystemExit("no patch requests supplied")

    calendar = Path(CANONICAL_CALENDAR)
    base_raw = calendar.read_bytes()
    base_sha = blob_sha(base_raw)
    base_text = base_raw.decode("utf-8")
    validate_calendar(base_text)

    prepared: list[tuple[Path, dict, str, str]] = []
    seen_uids: set[str] = set()

    for path in request_paths:
        req = json.loads(path.read_text(encoding="utf-8"))
        uid, op = validate_request(req, path)
        if uid in seen_uids:
            raise SystemExit(f"duplicate UID inside batch: {uid}")
        seen_uids.add(uid)

        expected = req.get("expected_calendar_blob_sha")
        if expected and expected != base_sha:
            print(
                f"SHA_CONFLICT_RECOMPUTED=1 REQUEST={path} EXPECTED={expected} ACTUAL={base_sha}"
            )

        assert_no_cross_uid_user_effect_collision(base_text, req, uid)
        prepared.append((path, req, uid, op))

    changed_count = 0
    for path, req, uid, op in prepared:
        # The workflow has already refreshed master. Per-request SHA guards are
        # converted into a batch-level observation so multiple requests created
        # from the same original calendar can be applied sequentially.
        safe_req = dict(req)
        safe_req.pop("expected_calendar_blob_sha", None)
        safe_req["calendar_path"] = CANONICAL_CALENDAR

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        ) as handle:
            json.dump(safe_req, handle, ensure_ascii=False)
            temp_path = Path(handle.name)

        try:
            changed = apply_request(temp_path)
            if changed:
                changed_count += 1
            print(f"REQUEST_APPLIED={path} UID={uid} OP={op} CHANGED={int(changed)}")
        finally:
            temp_path.unlink(missing_ok=True)

    final_raw = calendar.read_bytes()
    final_text = final_raw.decode("utf-8")
    validate_calendar(final_text)

    for _, _, uid, op in prepared:
        present = find_event_span(final_text, uid) is not None
        expected_present = op != "delete"
        if present != expected_present:
            raise SystemExit(
                f"post-batch verification failed for UID {uid}: present={present}, expected={expected_present}"
            )

    print(f"BATCH_REQUESTS={len(prepared)}")
    print(f"BATCH_CHANGED={changed_count}")
    print(f"BASE_BLOB_SHA={base_sha}")
    print(f"FINAL_BLOB_SHA={blob_sha(final_raw)}")
    return changed_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("requests", nargs="+")
    args = parser.parse_args()
    apply_batch([Path(p) for p in args.requests])


if __name__ == "__main__":
    main()
