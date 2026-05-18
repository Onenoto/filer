from __future__ import annotations

import io
import tempfile
from dataclasses import dataclass


@dataclass(frozen=True)
class OcrResult:
    text: str


def run_tesseract(image_bytes: bytes, *, tesseract_cmd: str | None = None) -> OcrResult:
    import pytesseract

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        from PIL import Image, ImageEnhance, ImageOps

        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        img = img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(1.8)
        img = ImageEnhance.Sharpness(img).enhance(1.2)
        text = pytesseract.image_to_string(img, lang="eng")
    except Exception:
        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            f.write(image_bytes)
            f.flush()
            text = pytesseract.image_to_string(f.name, lang="eng")
    return OcrResult(text=text.strip())
