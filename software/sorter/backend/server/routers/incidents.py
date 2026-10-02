from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IncidentDebugPiece(BaseModel):
    track_id: Optional[int] = None
    uuid: Optional[str] = None
    part_id: Optional[str] = None
    classification_status: Optional[str] = None
    zone: Optional[str] = None
    placed: Optional[bool] = None
    capture_done: Optional[bool] = None


class IncidentDebugSnapshot(BaseModel):
    captured_at: Optional[float] = None
    cameras: Dict[str, str] = {}
    pieces: Optional[List[IncidentDebugPiece]] = None


class IncidentDetailResponse(BaseModel):
    id: int
    kind: str
    source: Optional[str] = None
    source_kind: Optional[str] = None
    severity: Optional[str] = None
    scope: Optional[str] = None
    channel: Optional[str] = None
    role: Optional[str] = None
    channel_label: Optional[str] = None
    piece_uuid: Optional[str] = None
    track_id: Optional[int] = None
    reason: Optional[str] = None
    rule: Optional[str] = None
    resolution_hint: Optional[str] = None
    operator_message: Optional[str] = None
    status: str
    triggered_at: float
    updated_at: Optional[float] = None
    resolved_at: Optional[float] = None
    resolved_by: Optional[str] = None
    duration_s: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    debug_before: Optional[IncidentDebugSnapshot] = None
    debug_after: Optional[IncidentDebugSnapshot] = None


class IncidentSummaryRow(BaseModel):
    id: int
    kind: str
    source: Optional[str] = None
    source_kind: Optional[str] = None
    severity: Optional[str] = None
    scope: Optional[str] = None
    channel: Optional[str] = None
    role: Optional[str] = None
    channel_label: Optional[str] = None
    piece_uuid: Optional[str] = None
    track_id: Optional[int] = None
    reason: Optional[str] = None
    operator_message: Optional[str] = None
    status: str
    triggered_at: float
    resolved_at: Optional[float] = None
    resolved_by: Optional[str] = None
    duration_s: Optional[float] = None


class IncidentsListResponse(BaseModel):
    items: List[IncidentSummaryRow]
    next_cursor: Optional[str]
    total: int


class IncidentKindSummary(BaseModel):
    kind: str
    count: int
    avg_duration_s: Optional[float] = None
    operator_resolved: int = 0
    auto_resolved: int = 0


class IncidentDaySummary(BaseModel):
    date: str
    count: int


class IncidentChannelSummary(BaseModel):
    channel: str
    count: int


class IncidentsSummaryResponse(BaseModel):
    total: int
    active: int
    by_kind: List[IncidentKindSummary]
    by_day: List[IncidentDaySummary]
    by_channel: List[IncidentChannelSummary]


def _parseCursor(cursor: Optional[str]) -> Optional[int]:
    if cursor is None:
        return None
    try:
        return int(cursor)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid cursor")


@router.get("/api/incidents/summary", response_model=IncidentsSummaryResponse)
def getIncidentsSummary(
    date_from: Optional[float] = None,
    date_to: Optional[float] = None,
) -> IncidentsSummaryResponse:
    import incident_records

    return IncidentsSummaryResponse(
        **incident_records.incidentSummary(date_from=date_from, date_to=date_to)
    )


@router.get("/api/incidents", response_model=IncidentsListResponse)
def listIncidents(
    limit: int = 100,
    cursor: Optional[str] = None,
    kind: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[float] = None,
    date_to: Optional[float] = None,
) -> IncidentsListResponse:
    import incident_records

    result = incident_records.listIncidents(
        limit=limit,
        cursor=_parseCursor(cursor),
        kind=kind,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    return IncidentsListResponse(
        items=[IncidentSummaryRow(**item) for item in result["items"]],
        next_cursor=result["next_cursor"],
        total=result["total"],
    )


class IncidentActionBody(BaseModel):
    action: str


@router.post("/api/incidents/action")
def incident_action(body: IncidentActionBody) -> dict:
    """Run one of the open incident's card buttons (see incidents.actions)."""
    import incidents
    from server import shared_state

    gc = shared_state.gc_ref
    if gc is None or getattr(gc, "runtime_stats", None) is None:
        raise HTTPException(status_code=503, detail="The machine is not running.")
    try:
        return incidents.act(gc, body.action)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# Literal paths above (summary, list) MUST stay declared before this path-param
# route — same convention as /api/pieces/{uuid} in server/routers/pieces.py.
@router.get("/api/incidents/{incident_id}", response_model=IncidentDetailResponse)
def getIncidentDetail(incident_id: int) -> IncidentDetailResponse:
    import json

    import incident_records

    row = incident_records.getIncident(incident_id)
    if row is None:
        raise HTTPException(status_code=404, detail="incident not found")

    details_json = row.pop("details_json", None)
    details: Optional[Dict[str, Any]] = None
    if isinstance(details_json, str) and details_json:
        try:
            details = json.loads(details_json)
        except (TypeError, ValueError):
            details = None

    # getIncident() already resolved debug_before_json/debug_after_json into
    # row["debug_before"]/row["debug_after"] (parsed dicts or None) — leave
    # them in row for the **row unpack below rather than re-passing them.
    return IncidentDetailResponse(**row, details=details)
