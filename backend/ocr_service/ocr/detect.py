from .tesseract_recognizer import TessRecognizer


class Detector:
    """Lightweight Detector that uses Tesseract as a fallback.

    This avoids the heavy PaddleOCR dependency and works in environments
    without Paddle installed. It presents the same .recognize(img, lang)
    interface and returns token dicts with text, confidence and bbox.
    """
    def __init__(self):
        self.tess = TessRecognizer()

    def recognize(self, img, lang="en"):
        # Map language code to tesseract code
        tess_lang = "eng" if lang == "en" else lang
        try:
            tokens = self.tess.recognize(img, lang=tess_lang)
        except Exception:
            # On any tesseract error return empty list to avoid crashing app
            tokens = []
        if lang != "en":
            tokens = self._rtl_line_reorder(tokens)
        return tokens

    def _rtl_line_reorder(self, tokens):
        if not tokens:
            return tokens
        tokens_sorted = sorted(tokens, key=lambda t: (t["bbox"][1], -t["bbox"][0]))
        return tokens_sorted