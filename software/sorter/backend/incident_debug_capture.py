from __future__ import annotations

import base64
import time
from typing import Any

import cv2

# Debug-capture snapshots (incident_records.debug_before_json/debug_after_json,
# gated on toml_config.debugIncidentsEnabled()) are for a human eyeballing why
# an incident fired, not for the classifier — keep them noticeably smaller
# than classification_channel.running.DROP_SNAPSHOT_MAX_EDGE_PX (1024px/q78)
# since a single incident can pull one frame per camera, twice.
_MAX_EDGE_PX = 800
_JPEG_QUALITY = 70


def _encodeFrame(raw: Any) -> str | None:
    try:
        import numpy as np

        if raw is None or not isinstance(raw, np.ndarray) or raw.size == 0:
            return None
        frame = raw
        h, w = frame.shape[:2]
        longest = max(h, w)
        if longest > _MAX_EDGE_PX:
            scale = _MAX_EDGE_PX / float(longest)
            frame = cv2.resize(
                frame,
                (max(1, int(round(w * scale))), max(1, int(round(h * scale)))),
                interpolation=cv2.INTER_AREA,
            )
        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, _JPEG_QUALITY])
        if not ok:
            return None
        return base64.b64encode(buffer).decode("utf-8")
    except Exception:
        return None


def captureCameraSnapshots() -> dict[str, str]:
    """Grab the current frame from every live camera, JPEG-encoded (base64).

    Mirrors sample_collector.py's SampleCollector._captureOnce: the same
    zero-extra-I/O accessor (camera_service.get_capture_thread_for_role(role)
    .latest_frame.raw) it already uses to snapshot every configured camera on
    a cadence. Roles with no live frame yet are skipped, never raise."""
    from server import shared_state

    camera_service = shared_state.camera_service
    if camera_service is None:
        return {}
    feeds = getattr(camera_service, "feeds", None) or {}
    out: dict[str, str] = {}
    for role in sorted(feeds.keys()):
        try:
            capture = camera_service.get_capture_thread_for_role(role)
            frame = getattr(capture, "latest_frame", None) if capture is not None else None
            raw = getattr(frame, "raw", None) if frame is not None else None
            encoded = _encodeFrame(raw)
            if encoded is not None:
                out[role] = encoded
        except Exception:
            continue
    return out


_ZONE_LABELS = {0: "gap", 1: "drop", 2: "exit", 3: "precise"}


def captureClassificationChannelPieces() -> list[dict[str, Any]]:
    """Snapshot every piece currently tracked on the classification channel.

    Two-piece mode (this is the only mode with a real ordered queue — see
    subsystems/classification_channel/two_piece.py) reads the live
    TwoPieceClassificationChannel._pieces dict directly. Simple-mode / no
    controller yet -> best-effort single-piece fallback via PieceTransport.
    Never raises; returns [] on anything unexpected."""
    from server import shared_state

    controller = shared_state.controller_ref
    coordinator = getattr(controller, "coordinator", None) if controller is not None else None
    classification = getattr(coordinator, "classification", None) if coordinator is not None else None
    if classification is None:
        return []

    two_piece = getattr(classification, "_two_piece", None)
    if two_piece is not None:
        out: list[dict[str, Any]] = []
        try:
            pieces = dict(getattr(two_piece, "_pieces", {}) or {})
        except Exception:
            pieces = {}
        for track_id, tp in pieces.items():
            try:
                obj = tp.known_object
                out.append(
                    {
                        "track_id": int(track_id),
                        "uuid": getattr(obj, "uuid", None),
                        "part_id": getattr(obj, "part_id", None),
                        "classification_status": getattr(
                            getattr(obj, "classification_status", None), "value", None
                        ),
                        "zone": _ZONE_LABELS.get(int(getattr(tp, "zone", 0)), "unknown"),
                        "placed": bool(getattr(tp, "placed", False)),
                        "capture_done": bool(getattr(tp, "capture_done", False)),
                    }
                )
            except Exception:
                continue
        return out

    # Simple-mode fallback: whatever single piece the transport currently owns.
    transport = getattr(classification, "transport", None)
    out = []
    for getter in ("getPieceAtClassification", "getPieceForDistributionPositioning"):
        try:
            obj = getattr(transport, getter, lambda: None)()
        except Exception:
            obj = None
        if obj is None:
            continue
        try:
            out.append(
                {
                    "track_id": getattr(obj, "tracked_global_id", None),
                    "uuid": getattr(obj, "uuid", None),
                    "part_id": getattr(obj, "part_id", None),
                    "classification_status": getattr(
                        getattr(obj, "classification_status", None), "value", None
                    ),
                    "zone": getter,
                }
            )
        except Exception:
            continue
    return out


def captureIncidentDebugSnapshot(*, include_pieces: bool) -> dict[str, Any]:
    """Bundle the debug-capture payload stored on an incident's db row.

    ``include_pieces=True`` for the open-time ("before") capture; False for
    the resolve-time ("after") capture, which is camera-only per the plan
    (the piece list only matters at the moment the incident fired)."""
    snapshot: dict[str, Any] = {
        "captured_at": time.time(),
        "cameras": captureCameraSnapshots(),
    }
    if include_pieces:
        snapshot["pieces"] = captureClassificationChannelPieces()
    return snapshot
