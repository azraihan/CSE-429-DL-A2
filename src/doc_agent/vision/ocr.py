"""Stage 3 — OCR/HTR (BASELINE = pretrained foundation, fine-tuned)

REPRODUCED PUBLISHED METHOD: Nougat (Blecher et al., 2023, arXiv:2308.13418), run
through HF `transformers` rather than the unmaintained `nougat-ocr` package.

Nougat is the right foundation for this corpus specifically: it is a document-understanding
transformer trained on arXiv page images, so it emits Markdown with LaTeX for mathematics
and resolves two-column reading order internally — the two properties our data speciality
turns on. A line-level recogniser like TrOCR would need the layout stage to feed it
correctly ordered lines and would still lose every equation.

How the two stages divide the work:
  * page prose  -> ONE full-page Nougat pass (its own reading-order model does the work)
  * figure/table region -> a separate pass over the cropped region, so evidence that lives
    inside a figure becomes its own retrievable chunk instead of being flattened into the
    surrounding prose. 56.1% of this corpus's questions need exactly that.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from ..contracts import *  # noqa
from ..ingest.loader import PAGE_META
from ..logging_conf import get_logger
from .layout import REGION_META

log = get_logger(__name__)


def _looks_degenerate(text: str) -> bool:
    """Nougat's known failure mode: it falls into a repetition loop on dense tables."""
    if len(text) < 200:
        return False
    tail = text[-400:]
    for n in (12, 25, 50):
        chunk = tail[-n:]
        if chunk and tail.count(chunk) >= 4:
            return True
    words = text.split()
    if len(words) > 60:
        window = words[-60:]
        if len(set(window)) <= 4:
            return True
    return False


class Reader:
    """Model set by cfg['ocr']. Baseline: pretrained TrOCR/Donut/Tesseract."""

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg["ocr"]
        self._full = cfg
        self._model: Any = None
        self._proc: Any = None
        self._device = cfg.get("device", "cpu")

    def _load(self) -> None:
        if self._model is not None:
            return
        from transformers import NougatProcessor, VisionEncoderDecoderModel

        name = self.cfg["model"]
        log.info("loading OCR model %s on %s", name, self._device)
        self._proc = NougatProcessor.from_pretrained(name)
        # Cast after loading rather than via a dtype/torch_dtype kwarg: the two
        # transformers generations spell that argument differently, and this runs on
        # both a local CPU box and a Colab GPU.
        model = VisionEncoderDecoderModel.from_pretrained(name)
        if self._device == "cuda":
            model = model.half()
        self._model = model.to(self._device).eval()

    def _run(self, image) -> str:  # type: ignore[no-untyped-def]
        import torch

        self._load()
        assert self._proc is not None and self._model is not None
        # Call the image processor directly, not the NougatProcessor wrapper: in
        # transformers 5.x the wrapper forwards its own None defaults into a strictly
        # validated dataclass and dies on `do_crop_margin` before doing any work.
        pixel_values = self._proc.image_processor(image, return_tensors="pt").pixel_values.to(
            self._device
        )
        if self._device == "cuda":
            pixel_values = pixel_values.half()
        with torch.no_grad():
            out = self._model.generate(
                pixel_values,
                min_length=1,
                max_new_tokens=int(self.cfg.get("max_new_tokens", 3584)),
                bad_words_ids=[[self._proc.tokenizer.unk_token_id]],
            )
        text = self._proc.batch_decode(out, skip_special_tokens=True)[0]
        text = self._proc.post_process_generation(text, fix_markdown=False)
        return text.strip()

    def transcribe_page(self, page_id: str) -> str:
        """Full-page pass — Nougat resolves multi-column reading order itself."""
        from PIL import Image

        meta = PAGE_META[page_id]
        with Image.open(meta["abs_path"]) as img:
            return self._guarded(self._run(img.convert("RGB")), page_id)

    def transcribe_region(self, region: Region) -> str:  # noqa: F405
        """Crop the region and read it on its own."""
        from PIL import Image

        meta = PAGE_META[region.page_id]
        pad = int(self._full.get("ingest", {}).get("crop_padding_px", 8))
        x0, y0, x1, y1 = region.bbox
        box = (
            max(0, x0 - pad),
            max(0, y0 - pad),
            min(meta["width"], x1 + pad),
            min(meta["height"], y1 + pad),
        )
        with Image.open(meta["abs_path"]) as img:
            crop = img.convert("RGB").crop(box)
        return self._guarded(self._run(crop), f"{region.page_id}:{region.kind}")

    def _guarded(self, text: str, what: str) -> str:
        if self.cfg.get("repetition_guard", True) and _looks_degenerate(text):
            log.warning("OCR degenerated into a repetition loop on %s; truncating", what)
            return re.sub(r"\s+", " ", text[:1500]).strip()
        return text


def _cache_path() -> str:
    from ..ingest.loader import repo_root

    return os.path.join(repo_root(), "data", "interim", "ocr_cache.jsonl")


def _load_cache() -> dict[str, str]:
    path = _cache_path()
    if not os.path.exists(path):
        return {}
    cache: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                row = json.loads(line)
                cache[row["key"]] = row["text"]
            except (json.JSONDecodeError, KeyError):
                continue  # a half-written line from a killed run; skip it
    return cache


def transcribe(regions: list[Region], cfg: dict) -> list[Chunk]:  # noqa: F405
    """Regions -> text chunks (calls Reader).

    Every model call is cached to disk keyed by page/region, so a run that dies
    part-way — a dropped Colab session, an OOM — resumes instead of restarting. At
    seconds per page over ~1.8k pages that is the difference between a rerun costing
    minutes and costing hours.
    """
    reader = Reader(cfg)
    cache = _load_cache() if cfg.get("ocr", {}).get("cache", True) else {}
    os.makedirs(os.path.dirname(_cache_path()), exist_ok=True)
    fh_cache = open(_cache_path(), "a", encoding="utf-8")
    hits = 0

    def read(key: str, fn: Any) -> str:
        nonlocal hits
        if key in cache:
            hits += 1
            return cache[key]
        text = fn()
        cache[key] = text
        fh_cache.write(json.dumps({"key": key, "text": text}, ensure_ascii=False) + "\n")
        fh_cache.flush()
        return text

    by_page: dict[str, list[Region]] = {}  # noqa: F405
    for r in regions:
        by_page.setdefault(r.page_id, []).append(r)

    out: list[Chunk] = []  # noqa: F405
    n_region_calls = 0
    for page_id, regs in by_page.items():
        meta = PAGE_META.get(page_id, {})
        doc_id = meta.get("doc_id", page_id.split("/")[1] if "/" in page_id else page_id)

        prose = read(page_id, lambda pid=page_id: reader.transcribe_page(pid))  # type: ignore[misc]
        if prose:
            out.append(
                Chunk(  # noqa: F405
                    id=f"{page_id}#prose",
                    doc_id=doc_id,
                    text=prose,
                    page_ids=[page_id],
                )
            )

        for r in regs:
            if r.kind not in ("figure", "table"):
                continue
            order = REGION_META.get((r.page_id, r.bbox), {}).get("order", 0)
            key = f"{page_id}#r{order:02d}:{r.kind}"
            text = read(key, lambda r=r: reader.transcribe_region(r))  # type: ignore[misc]
            n_region_calls += 1
            if not text.strip():
                continue
            out.append(
                Chunk(  # noqa: F405
                    id=f"{page_id}#r{order:02d}:{r.kind}",
                    doc_id=doc_id,
                    text=f"[{r.kind}] {text}",
                    page_ids=[page_id],
                )
            )

    fh_cache.close()
    log.info(
        "ocr: %d chunks from %d pages (%d page passes, %d region crops, %d cache hits)",
        len(out),
        len(by_page),
        len(by_page),
        n_region_calls,
        hits,
    )
    return out
