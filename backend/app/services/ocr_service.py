"""OCR service: EasyOCR primary, Tesseract fallback.

Both engines are imported lazily so the app (and tests) boot without the heavy
torch/EasyOCR model download. The EasyOCR reader is cached process-wide.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_easyocr_reader = None  # lazily-initialised, cached singleton


@dataclass
class OCRResult:
    text: str
    confidence: float
    engine: str


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr  # heavy import, deferred

        logger.info("Initialising EasyOCR reader (languages=%s)", settings.ocr_language_list)
        _easyocr_reader = easyocr.Reader(settings.ocr_language_list, gpu=False)
    return _easyocr_reader


def _easyocr(image_bytes: bytes) -> OCRResult:
    reader = _get_easyocr_reader()
    # detail=1 → list of (bbox, text, confidence)
    results = reader.readtext(image_bytes, detail=1, paragraph=False)
    if not results:
        return OCRResult(text="", confidence=0.0, engine="easyocr")
    lines = [r[1] for r in results]
    confidences = [float(r[2]) for r in results if r[2] is not None]
    mean_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return OCRResult(text="\n".join(lines), confidence=mean_conf, engine="easyocr")


def _tesseract(image_bytes: bytes) -> OCRResult:
    import io

    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(image_bytes))
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    words, confs = [], []
    for word, conf in zip(data["text"], data["conf"], strict=False):
        if word.strip():
            words.append(word)
            try:
                c = float(conf)
            except (TypeError, ValueError):
                c = -1.0
            if c >= 0:
                confs.append(c / 100.0)
    mean_conf = sum(confs) / len(confs) if confs else 0.0
    return OCRResult(text=" ".join(words), confidence=mean_conf, engine="tesseract")


def run_ocr(image_bytes: bytes) -> OCRResult:
    """Run OCR with the configured primary engine; fall back to the other on
    failure or low confidence."""
    primary, fallback = (
        (_easyocr, _tesseract)
        if settings.OCR_ENGINE == "easyocr"
        else (_tesseract, _easyocr)
    )

    try:
        result = primary(image_bytes)
    except Exception as exc:  # noqa: BLE001 — engine import/runtime failure
        logger.warning("Primary OCR engine failed (%s); trying fallback", exc)
        result = OCRResult(text="", confidence=0.0, engine="none")

    if result.confidence >= settings.OCR_CONFIDENCE_THRESHOLD and result.text.strip():
        return result

    logger.info(
        "OCR confidence %.2f below threshold %.2f — trying fallback engine",
        result.confidence,
        settings.OCR_CONFIDENCE_THRESHOLD,
    )
    try:
        fallback_result = fallback(image_bytes)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Fallback OCR engine failed (%s)", exc)
        return result

    # Keep whichever produced the higher confidence.
    return max(result, fallback_result, key=lambda r: r.confidence)
