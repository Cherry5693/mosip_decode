from paddleocr import PaddleOCR

class Detector:
    def __init__(self):
        self.detector = PaddleOCR(det=True, rec=False, cls=True, use_angle_cls=True, use_gpu=False)

    def recognize(self, img, lang="en"):
        ocr = PaddleOCR(det=True, rec=True, cls=True, use_angle_cls=True, lang="en" if lang=="en" else "ar", use_gpu=False)
        result = ocr.ocr(img, cls=True)
        tokens = []
        for res in result:
            for line in res:
                ((x1,y1),(x2,y2),(x3,y3),(x4,y4)), (text, conf) = line
                x_min = int(min(x1, x2, x3, x4)); x_max = int(max(x1, x2, x3, x4))
                y_min = int(min(y1, y2, y3, y4)); y_max = int(max(y1, y2, y3, y4))
                tokens.append({"text": text, "confidence": float(conf), "bbox": [x_min, y_min, x_max, y_max]})
        if lang != "en":
            tokens = self._rtl_line_reorder(tokens)
        return tokens

    def _rtl_line_reorder(self, tokens):
        if not tokens:
            return tokens
        tokens_sorted = sorted(tokens, key=lambda t: (t["bbox"][1], -t["bbox"][0]))
        return tokens_sorted