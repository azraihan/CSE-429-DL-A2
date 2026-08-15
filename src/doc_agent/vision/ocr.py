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
from typing import Any

from ..contracts import *  # noqa
from ..ingest.loader import PAGE_META
from ..logging_conf import get_logger
from .layout import REGION_META

log = get_logger(__name__)


def _repetition_cut(text: str, n: int = 8, max_repeats: int = 4) -> int | None:
    """Index where a repeated n-gram takes over, or None if the text is healthy.

    Nougat's documented failure is falling into a loop ("Let C be a finite graph and let
    C be a finite graph. Let ..."). An earlier version of this check only inspected the
    last 400 characters, which misses the common case where the loop starts near the top
    of the page and runs the whole way down. This scans the whole page and returns the
    position where the looping began, so the healthy prefix can be kept.
    """
    words = text.split()
    if len(words) < n * 3:
        return None
    seen: dict[tuple[str, ...], int] = {}
    counts: dict[tuple[str, ...], int] = {}
    for i in range(len(words) - n + 1):
        gram = tuple(words[i : i + n])
        counts[gram] = counts.get(gram, 0) + 1
        seen.setdefault(gram, i)
        if counts[gram] > max_repeats:
            # rebuild the character offset of the first occurrence of this n-gram
            return len(" ".join(words[: seen[gram]]))
    return None


def _looks_degenerate(text: str) -> bool:
    """True if the transcription collapsed into a repetition loop."""
    return len(text) >= 200 and _repetition_cut(text) is not None


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

    def batch_size(self) -> int:
        """How many pages to generate at once.

        `auto` sizes from free VRAM so the same config runs on a 4 GB laptop card, a
        16 GB T4 and a 96 GB workstation card without editing anything. Generation is
        the whole cost of this stage, and unbatched generation leaves a large GPU almost
        idle, so this is the single knob that decides whether the corpus takes 20
        minutes or three hours.
        """
        want = self.cfg.get("batch_size", "auto")
        if isinstance(want, int) and want > 0:
            return want
        if self._device != "cuda":
            return 1
        import torch

        gb = torch.cuda.get_device_properties(0).total_memory / 2**30
        return max(1, min(32, int(gb // 6)))

    def _run_batch(self, images: list) -> list[str]:  # type: ignore[type-arg]
        import torch

        self._load()
        assert self._proc is not None and self._model is not None
        # Call the image processor directly, not the NougatProcessor wrapper: in
        # transformers 5.x the wrapper forwards its own None defaults into a strictly
        # validated dataclass and dies on `do_crop_margin` before doing any work.
        pixel_values = self._proc.image_processor(images, return_tensors="pt").pixel_values.to(
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
        decoded = self._proc.batch_decode(out, skip_special_tokens=True)
        return [self._post_process(t) for t in decoded]

    def _post_process(self, text: str) -> str:
        """Nougat's own post-processing, where the installed transformers still has it.

        It moved behind a tokenizer backend that dropped the method in newer releases
        (`TokenizersBackend has no attribute post_process_generation`), so it is treated
        as optional: it only tidies Markdown artifacts and trims repetitions, and our own
        `_looks_degenerate` guard already covers the failure that actually matters.
        """
        fn = getattr(self._proc, "post_process_generation", None)
        if fn is None:
            return text.strip()
        try:
            return fn(text, fix_markdown=False).strip()
        except (AttributeError, ImportError, TypeError):
            return text.strip()

    def _run(self, image) -> str:  # type: ignore[no-untyped-def]
        return self._run_batch([image])[0]

    def page_image(self, page_id: str):  # type: ignore[no-untyped-def]
        """The full page, as the reader sees it."""
        from PIL import Image

        with Image.open(PAGE_META[page_id]["abs_path"]) as img:
            return img.convert("RGB")

    def region_image(self, region: Region):  # type: ignore[no-untyped-def]  # noqa: F405
        """The padded crop of one region — padding stops tight boxes clipping subscripts."""
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
            return img.convert("RGB").crop(box)

    def transcribe_page(self, page_id: str) -> str:
        """Full-page pass — Nougat resolves multi-column reading order itself."""
        return self._guarded(self._run(self.page_image(page_id)), page_id)

    def transcribe_region(self, region: Region) -> str:  # noqa: F405
        """Crop the region and read it on its own."""
        return self._guarded(
            self._run(self.region_image(region)), f"{region.page_id}:{region.kind}"
        )

    def _guarded(self, text: str, what: str) -> str:
        if not self.cfg.get("repetition_guard", True) or len(text) < 200:
            return text
        cut = _repetition_cut(text)
        if cut is None:
            return text
        kept = text[:cut].strip()
        log.warning(
            "OCR degenerated into a repetition loop on %s; keeping the %d chars "
            "before the loop, discarding %d",
            what,
            len(kept),
            len(text) - len(kept),
        )
        return kept


def _cache_path() -> str:
    from ..ingest.loader import repo_root

    return os.path.join(repo_root(), "data", "interim", "ocr_cache.jsonl")


def _load_cache(guard: bool = True) -> dict[str, str]:
    """Read the resume cache, re-applying the repetition guard on the way in.

    Guarding on read as well as on write makes the cache self-healing: a transcription
    stored by an older, weaker guard is cleaned when it is next used, so a corpus that
    took hours of GPU time does not have to be regenerated to benefit from a fix here.
    """
    path = _cache_path()
    if not os.path.exists(path):
        return {}
    cache: dict[str, str] = {}
    cleaned = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                row = json.loads(line)
                text = row["text"]
            except (json.JSONDecodeError, KeyError):
                continue  # a half-written line from a killed run; skip it
            if guard and len(text) >= 200:
                cut = _repetition_cut(text)
                if cut is not None:
                    text = text[:cut].strip()
                    cleaned += 1
            cache[row["key"]] = text
    if cleaned:
        log.info("ocr cache: repetition guard cleaned %d stored transcriptions", cleaned)
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

    by_page: dict[str, list[Region]] = {}  # noqa: F405
    for r in regions:
        by_page.setdefault(r.page_id, []).append(r)

    # 1. enumerate every unit of work, page prose and region crops alike -------------
    jobs: list[tuple[str, str, Any]] = []  # (cache key, "page"|"region", payload)
    n_region_calls = 0
    for page_id, regs in by_page.items():
        jobs.append((page_id, "page", page_id))
        for r in regs:
            if r.kind not in ("figure", "table"):
                continue
            order = REGION_META.get((r.page_id, r.bbox), {}).get("order", 0)
            jobs.append((f"{page_id}#r{order:02d}:{r.kind}", "region", r))
            n_region_calls += 1

    todo = [j for j in jobs if j[0] not in cache]
    hits = len(jobs) - len(todo)
    bs = reader.batch_size()
    if todo:
        log.info("ocr: %d to transcribe, %d cached, batch_size=%d", len(todo), hits, bs)

    # 2. generate in batches, flushing each result to the resume cache ---------------
    os.makedirs(os.path.dirname(_cache_path()), exist_ok=True)
    with open(_cache_path(), "a", encoding="utf-8") as fh_cache:
        for start in range(0, len(todo), bs):
            batch = todo[start : start + bs]
            images = [
                reader.page_image(payload) if kind == "page" else reader.region_image(payload)
                for _, kind, payload in batch
            ]
            try:
                texts = reader._run_batch(images)
            except RuntimeError as exc:  # OOM on an over-large batch: fall back per item
                if "out of memory" not in str(exc).lower() or len(batch) == 1:
                    raise
                log.warning("OCR batch of %d hit OOM; retrying one at a time", len(batch))
                import torch

                torch.cuda.empty_cache()
                texts = [reader._run_batch([img])[0] for img in images]

            for (key, _, _), text in zip(batch, texts, strict=True):
                text = reader._guarded(text, key)
                cache[key] = text
                fh_cache.write(json.dumps({"key": key, "text": text}, ensure_ascii=False) + "\n")
            fh_cache.flush()
            if start and start % (bs * 20) == 0:
                log.info("ocr: %d/%d transcribed", start, len(todo))

    # 3. assemble chunks from the cache ---------------------------------------------
    out: list[Chunk] = []  # noqa: F405
    for key, kind, payload in jobs:
        text = cache.get(key, "")
        if not text.strip():
            continue
        page_id = payload if kind == "page" else payload.page_id
        meta = PAGE_META.get(page_id, {})
        doc_id = meta.get("doc_id", page_id.split("/")[1] if "/" in page_id else page_id)
        if kind == "page":
            out.append(
                Chunk(  # noqa: F405
                    id=f"{page_id}#prose",
                    doc_id=doc_id,
                    text=text,
                    page_ids=[page_id],
                )
            )
        else:
            out.append(
                Chunk(  # noqa: F405
                    id=key,
                    doc_id=doc_id,
                    text=f"[{payload.kind}] {text}",
                    page_ids=[page_id],
                )
            )

    log.info(
        "ocr: %d chunks from %d pages (%d page passes, %d region crops, %d cache hits)",
        len(out),
        len(by_page),
        len(by_page),
        n_region_calls,
        hits,
    )
    return out
