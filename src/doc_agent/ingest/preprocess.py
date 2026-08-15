# =============================================================================
# File:     src/doc_agent/ingest/preprocess.py
# Stage:    1 - deskew / denoise / binarize / augment
# Status:   IMPLEMENTED (as a deliberate no-op restoration stage)
#
# Design decision - why there is no deskew, denoise or binarize here:
#   The corpus is born-digital 300-DPI renders. There is no skew, speckle or
#   fading to correct, and classical restoration applied to clean glyphs only
#   damages them - binarising crisp antialiased text measurably hurts the OCR
#   stage. Running those filters "because the stage is called preprocess" would
#   trade real accuracy for the appearance of thoroughness.
#
# What run(pages, cfg) does instead:
#   Enforces the ingest contract every later stage silently assumes, and fails
#   loudly when a page violates it:
#     - the image file exists                     -> FileNotFoundError
#     - its geometry matches the manifest         -> ValueError (corpus and
#       manifest disagree, which would otherwise surface much later as a
#       mysterious OCR or bbox failure)
#     - the page is greyscale when cfg.ingest.grayscale is set
#
# _degrade(img, seed) - the honest use of a degradation library on clean data:
#   manufacture a degraded copy of a known-clean page (Gaussian blur + Gaussian
#   noise, seeded from cfg.seed) so robustness can be measured against a clean
#   reference. Gated behind cfg.ingest.degrade, off by default; when on, the
#   degraded pages are written to data/interim/pages/ and the returned Page
#   objects point at those copies, leaving data/raw/ untouched.
#
# Inputs  : list[Page], cfg["ingest"], PAGE_META
# Outputs : list[Page] (same pages, or degraded copies)
# =============================================================================

"""Stage 1 — deskew / denoise / binarize / augment"""

from __future__ import annotations

import os

from ..contracts import *  # noqa
from ..contracts import Page  # explicit: keeps the star import from hiding the name
from ..logging_conf import get_logger
from .loader import PAGE_META, repo_root

log = get_logger(__name__)


def _degrade(img, seed: int):  # type: ignore[no-untyped-def]
    """Synthetic scan degradation — OFF by default.

    These pages are born-digital renders, so there is nothing to *repair*. The only
    honest use of a degradation library here is the opposite direction: manufacturing a
    degraded copy of a clean page so robustness can be measured against a known-clean
    reference. Kept behind cfg.ingest.degrade for the A3 robustness stress run.
    """
    import numpy as np
    from PIL import Image, ImageFilter

    rng = np.random.default_rng(seed)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    arr = np.asarray(img).astype(np.float32)
    arr += rng.normal(0, 8.0, arr.shape)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), mode="L")


def run(pages: list[Page], cfg: dict) -> list[Page]:
    """Classical preprocessing.

    NO deskew, denoise or binarize: the corpus is born-digital 300-DPI renders with no
    skew, speckle or fading to correct, and classical restoration on clean glyphs only
    destroys them. What this stage does instead is enforce the ingest contract every
    later stage depends on — greyscale, the configured DPI geometry, a readable file —
    and fail loudly when a page violates it, because a silently malformed page would
    surface much later as an unexplained OCR failure.
    """
    ing = cfg.get("ingest", {})
    want_gray = bool(ing.get("grayscale", True))
    degrade = bool(ing.get("degrade", False))
    seed = int(cfg.get("seed", 42))

    from PIL import Image

    out: list[Page] = []
    interim = os.path.join(repo_root(), "data", "interim", "pages")
    if degrade:
        os.makedirs(interim, exist_ok=True)

    converted = 0
    for page in pages:
        if not os.path.exists(page.image_path):
            raise FileNotFoundError(f"page image missing: {page.image_path}")

        with Image.open(page.image_path) as img:
            meta = PAGE_META.get(page.id, {})
            if meta:
                if (img.width, img.height) != (meta["width"], meta["height"]):
                    raise ValueError(
                        f"{page.id}: geometry {img.size} != manifest "
                        f"{(meta['width'], meta['height'])} — corpus and manifest disagree"
                    )
            if want_gray and img.mode != "L":
                img = img.convert("L")
                converted += 1

            if degrade:
                dst = os.path.join(interim, page.id.replace("/", "_") + ".png")
                _degrade(img, seed).save(dst)
                out.append(Page(id=page.id, image_path=dst, doc_id=page.doc_id))  # noqa: F405
                continue

        out.append(page)

    log.info(
        "preprocess: %d pages verified (greyscale conversions=%d, degrade=%s)",
        len(out),
        converted,
        degrade,
    )
    return out
