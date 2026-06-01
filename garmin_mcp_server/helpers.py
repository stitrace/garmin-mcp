"""Small, dependency-free helpers shared across the server."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REL_RE = re.compile(r"^([+-]?\d+)$")


def resolve_date(value: str | None) -> str:
    """Normalise a user-supplied date into ``YYYY-MM-DD``.

    Accepts:
      * ``None`` or ``""``           -> today
      * ``"today"`` / ``"yesterday"`` / ``"tomorrow"``
      * a relative day offset such as ``"-7"`` (7 days ago) or ``"3"``
      * an ISO date ``"2024-01-31"``
    """
    if value is None:
        return date.today().isoformat()

    raw = value.strip().lower()
    if raw in ("", "today", "now"):
        return date.today().isoformat()
    if raw == "yesterday":
        return (date.today() - timedelta(days=1)).isoformat()
    if raw == "tomorrow":
        return (date.today() + timedelta(days=1)).isoformat()

    rel = _REL_RE.match(raw)
    if rel:
        return (date.today() + timedelta(days=int(rel.group(1)))).isoformat()

    if _ISO_RE.match(raw):
        datetime.strptime(raw, "%Y-%m-%d")  # validate it is a real calendar date
        return raw

    raise ValueError(
        f"Invalid date {value!r}. Use 'YYYY-MM-DD', 'today', 'yesterday', "
        f"or a relative offset like '-7'."
    )


def resolve_range(start: str | None, end: str | None, default_days: int = 7) -> tuple[str, str]:
    """Resolve a ``(start, end)`` date range.

    If ``end`` is omitted it defaults to today. If ``start`` is omitted it
    defaults to ``default_days`` before ``end``.
    """
    end_d = resolve_date(end) if end else date.today().isoformat()
    if start:
        start_d = resolve_date(start)
    else:
        end_dt = datetime.strptime(end_d, "%Y-%m-%d").date()
        start_d = (end_dt - timedelta(days=default_days)).isoformat()
    if start_d > end_d:
        start_d, end_d = end_d, start_d
    return start_d, end_d


def trim(data: Any, max_items: int = 50, max_str: int = 4000) -> Any:
    """Recursively trim very large structures so responses stay readable.

    Garmin detail endpoints can return tens of thousands of per-second samples.
    This keeps payloads informative without flooding the model's context window.
    """
    if isinstance(data, dict):
        return {k: trim(v, max_items, max_str) for k, v in data.items()}
    if isinstance(data, list):
        if len(data) > max_items:
            head = [trim(x, max_items, max_str) for x in data[:max_items]]
            head.append(
                {"_truncated": f"{len(data) - max_items} more items omitted (total {len(data)})"}
            )
            return head
        return [trim(x, max_items, max_str) for x in data]
    if isinstance(data, str) and len(data) > max_str:
        return data[:max_str] + f"... [truncated {len(data) - max_str} chars]"
    return data
