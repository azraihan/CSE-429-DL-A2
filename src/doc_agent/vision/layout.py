"""Stage 2 — layout detection / segmentation

DATA-SPECIALITY ENHANCEMENT (E2: multi-column / table-figure reading order).

The hard property of this corpus is that reading order is not visual order: 42.5% of
pages are two-column, and 56.1% of questions have their evidence inside a figure or
table rather than in prose. A detector that returns an unordered pile of boxes is
useless here — scrambled column order is exactly the failure this stage exists to
prevent. So `detect()` returns regions **in reading order**, and that list order is the
contract every later stage relies on.

Two region sources, in priority order:
  1. the corpus's own evidence annotations (figure/table boxes with a type), and
  2. a morphological block detector over the page image for everything else.

`contracts.Region` is FIXED at (page_id, bbox, kind), so reading-order index and region
provenance live in the REGION_META sidecar.
"""
from __future__ import annotations

import os
from collections import defaultdict

from ..contracts import *  # noqa
from ..ingest.loader import PAGE_META, load_qa
from ..logging_conf import get_logger

log = get_logger(__name__)

# (page_id, bbox) -> {"order": int, "source": "dataset"|"heuristic", "column": int}
REGION_META: dict[tuple[str, tuple[int, int, int, int]], dict] = {}

_WORK_W = 850  # detector works on a downscaled copy; boxes are scaled back up


def _evidence_boxes(cfg: dict) -> dict[str, list[tuple[tuple[int, int, int, int], str]]]:
    """page_id -> [(bbox_px, kind)] from the corpus's own annotations."""
    out: dict[str, list[tuple[tuple[int, int, int, int], str]]] = defaultdict(list)
    seen: set[tuple[str, tuple[int, int, int, int]]] = set()
    for row in load_qa(cfg):
        for ev in row.get("evidence", []):
            pid = ev["page_id"]
            meta = PAGE_META.get(pid)
            if not meta:
                continue
            for i, rel in enumerate(ev.get("rel_boxes", [])):
                # rel_bbox is normalised to a 1000x1000 grid, so it is the only
                # coordinate form that survives this corpus's mixed page geometry.
                x0 = int(rel[0] / 1000.0 * meta["width"])
                y0 = int(rel[1] / 1000.0 * meta["height"])
                x1 = int(rel[2] / 1000.0 * meta["width"])
                y1 = int(rel[3] / 1000.0 * meta["height"])
                box = (max(0, x0), max(0, y0), min(meta["width"], x1), min(meta["height"], y1))
                if box[2] <= box[0] or box[3] <= box[1]:
                    continue
                types = ev.get("types", [])
                raw = types[i] if i < len(types) else (types[0] if types else "text")
                kind = {"image": "figure", "table": "table"}.get(raw, "text")
                key = (pid, box)
                if key in seen:
                    continue
                seen.add(key)
                out[pid].append((box, kind))
    return out


def _gutter(binv) -> tuple[int, int] | None:  # type: ignore[no-untyped-def]
    """Find the vertical whitespace channel separating two text columns.

    A projection profile is the right tool here rather than morphology: the column gap
    on these pages is only ~12px at working resolution, narrower than the kernel needed
    to join words into lines, so any purely morphological pass bridges the gutter and
    welds the two columns into one block — which is precisely the reading-order failure
    this stage has to prevent.
    """
    import numpy as np

    h, w = binv.shape
    ink = binv > 0
    lo, hi = int(0.30 * w), int(0.70 * w)
    gw = max(4, int(0.012 * w))
    bh, st = int(0.20 * h), max(1, int(0.10 * h))

    def widest_gap(col: "np.ndarray", thr: float) -> tuple[int, int] | None:
        best: tuple[int, int] | None = None
        start = None
        for x in range(lo, hi + 1):
            gap = x < hi and col[x] <= thr
            if gap and start is None:
                start = x
            elif not gap and start is not None:
                if best is None or (x - start) > (best[1] - best[0]):
                    best = (start, x)
                start = None
        return best

    # Scan horizontal bands, not the whole page: a wide figure above two columns closes
    # the gutter in a whole-page projection and hides the columns underneath it.
    text_bands, found = 0, []
    for y in range(0, max(1, h - bh + 1), st):
        band = ink[y : y + bh]
        if band.sum() < 0.010 * bh * w:
            continue
        col = band.sum(axis=0).astype(np.float32)
        if col[:lo].sum() == 0 or col[hi:].sum() == 0:
            continue
        text_bands += 1
        g = widest_gap(col, max(1.0, 0.02 * bh))
        if g and (g[1] - g[0]) >= gw:
            found.append(g)

    # One band with a gap is a coincidence; a real two-column page keeps it open.
    if text_bands < 2 or len(found) / text_bands < 0.5:
        return None
    return (
        int(np.median([g[0] for g in found])),
        int(np.median([g[1] for g in found])),
    )


def _blocks_in(binv, x0: int, x1: int, y0: int, y1: int):  # type: ignore[no-untyped-def]
    """Morphological block detection restricted to one column strip."""
    import cv2

    strip = binv[y0:y1, x0:x1]
    if strip.size == 0:
        return []
    lines = cv2.morphologyEx(
        strip, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    )
    blocks = cv2.morphologyEx(
        lines, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 21))
    )
    cnts = cv2.findContours(blocks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    out = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w < 25 or h < 10 or w * h < 900:
            continue
        out.append((x0 + x, y0 + y, x0 + x + w, y0 + y + h))
    return out


def _analyse(
    image_path: str, width: int, height: int
) -> tuple[list[tuple[int, int, int, int]], int | None, list[tuple[int, int, bool]]]:
    """Return (text blocks, gutter mid-x, bands) in FULL-RESOLUTION coordinates.

    A band is a horizontal slice of the page tagged with whether its ink crosses the
    gutter. Spanning bands hold titles, wide figures and wide tables; the rest hold the
    two-column flow. Bands plus the gutter are what let every region — detected or
    annotated — be ordered by one consistent rule in `detect()`.
    """
    import cv2
    import numpy as np

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return [], None, []
    scale = _WORK_W / img.shape[1]
    small = cv2.resize(img, (_WORK_W, int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA)
    binv = cv2.threshold(small, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    h, w = binv.shape
    inv = 1.0 / scale

    def up(b: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        return (
            max(0, int(b[0] * inv)),
            max(0, int(b[1] * inv)),
            min(width, int(b[2] * inv)),
            min(height, int(b[3] * inv)),
        )

    gut = _gutter(binv)
    if gut is None:
        blocks = [up(b) for b in _blocks_in(binv, 0, w, 0, h)]
        return blocks, None, [(0, height, True)]

    gx0, gx1 = gut
    spans = (binv[:, gx0:gx1] > 0).sum(axis=1) > max(1, 0.35 * (gx1 - gx0))

    def _runs(mask: "np.ndarray") -> list[tuple[int, int, bool]]:
        out: list[tuple[int, int, bool]] = []
        y = 0
        while y < len(mask):
            v = bool(mask[y])
            y2 = y
            while y2 < len(mask) and bool(mask[y2]) == v:
                y2 += 1
            out.append((y, y2, v))
            y = y2
        return out

    # Clean the mask by run length rather than by smoothing: a stray descender poking
    # into the gutter must not promote a whole two-column band to full width, and a
    # blank line inside a wide figure must not split it. Smoothing does both wrongly.
    min_true, min_false = max(4, int(0.020 * h)), max(4, int(0.012 * h))
    for _ in range(2):
        for y0, y1, v in _runs(spans):
            if v and (y1 - y0) < min_true:
                spans[y0:y1] = False
        for y0, y1, v in _runs(spans):
            if not v and (y1 - y0) < min_false:
                spans[y0:y1] = True

    bands: list[tuple[int, int, bool]] = [
        (int(y0 * inv), int(y1 * inv), v) for y0, y1, v in _runs(spans) if y1 - y0 >= 4
    ]

    blocks: list[tuple[int, int, int, int]] = []
    for by0, by1, spanning in bands:
        sy0, sy1 = int(by0 * scale), int(by1 * scale)
        if spanning:
            blocks += [up(b) for b in _blocks_in(binv, 0, w, sy0, sy1)]
        else:
            blocks += [up(b) for b in _blocks_in(binv, 0, gx0, sy0, sy1)]
            blocks += [up(b) for b in _blocks_in(binv, gx1, w, sy0, sy1)]

    return blocks, int(((gx0 + gx1) / 2) * inv), bands


def _overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    """Fraction of `a` covered by `b`."""
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    area = max(1, (a[2] - a[0]) * (a[3] - a[1]))
    return ix * iy / area


def detect(pages: list[Page], cfg: dict) -> list[Region]:
    """Detect text/table/figure/heading regions, returned in READING ORDER."""
    lay = cfg.get("layout", {})
    use_dataset = bool(lay.get("use_dataset_bboxes", True))
    evidence = _evidence_boxes(cfg) if use_dataset else {}

    regions: list[Region] = []  # noqa: F405
    REGION_META.clear()
    n_dataset = n_heur = 0

    for page in pages:
        meta = PAGE_META.get(page.id, {})
        width = int(meta.get("width", 0)) or 2550
        height = int(meta.get("height", 0)) or 3300
        annotated = evidence.get(page.id, [])
        blocks, gutter, bands = _analyse(page.image_path, width, height)

        # a detected block swallowed by an annotated figure/table is that region's
        # internals, not prose — the annotated box already covers it
        candidates: list[tuple[tuple[int, int, int, int], str]] = [
            (b, "text") for b in blocks if not any(_overlap(b, ann) > 0.6 for ann, _ in annotated)
        ]
        candidates += annotated

        def band_of(box: tuple[int, int, int, int]) -> tuple[int, bool]:
            centre = (box[1] + box[3]) / 2.0
            for i, (by0, by1, spanning) in enumerate(bands):
                if by0 <= centre < by1:
                    return i, spanning
            return len(bands), True

        # ONE ordering rule for detected and annotated regions alike: band top-to-bottom,
        # then left column before right column, then vertical position. Ordering the two
        # sources separately is what puts a right-column figure ahead of a left-column one.
        flow: list[tuple[tuple[int, int, int, int], str, int]] = []
        for box, kind in candidates:
            bi, spanning = band_of(box)
            wide = (box[2] - box[0]) > 0.62 * width
            if spanning or wide or gutter is None:
                col = -1
            else:
                col = 0 if (box[0] + box[2]) / 2.0 < gutter else 1
            flow.append((box, kind, col))
        flow.sort(key=lambda item: (band_of(item[0])[0], item[2], item[0][1], item[0][0]))

        text_h = sorted(b[3] - b[1] for b, k, _ in flow if k == "text")
        line_h = text_h[len(text_h) // 2] if text_h else 0
        text_w = max((b[2] - b[0] for b, k, _ in flow if k == "text"), default=1)

        for order, (box, kind, column) in enumerate(flow):
            # a short, narrow text block that is not a full paragraph reads as a heading
            if (
                kind == "text"
                and len(flow) > 2
                and line_h
                and (box[3] - box[1]) <= 1.4 * line_h
                and (box[2] - box[0]) <= 0.75 * text_w
            ):
                kind = "heading"
            src = "dataset" if kind in ("figure", "table") else "heuristic"
            n_dataset += src == "dataset"
            n_heur += src == "heuristic"
            regions.append(Region(page_id=page.id, bbox=box, kind=kind))  # noqa: F405
            REGION_META[(page.id, box)] = {"order": order, "source": src, "column": column}

    kinds: dict[str, int] = defaultdict(int)
    for r in regions:
        kinds[r.kind] += 1
    log.info(
        "layout: %d regions over %d pages (%s) dataset=%d heuristic=%d",
        len(regions),
        len(pages),
        dict(kinds),
        n_dataset,
        n_heur,
    )
    return regions
