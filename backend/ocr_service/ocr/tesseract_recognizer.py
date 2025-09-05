import pytesseract

class TessRecognizer:
    def recognize(self, img_bgr, lang="eng"):
        cfg = "--psm 6"
        data = pytesseract.image_to_data(img_bgr, lang=lang, config=cfg, output_type=pytesseract.Output.DICT)
        tokens = []
        n = len(data["text"])
        for i in range(n):
            txt = (data["text"][i] or "").strip()
            if not txt:
                continue
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            conf = float(data["conf"][i]) / 100.0 if str(data["conf"][i]).isdigit() else 0.0
            tokens.append({"text": txt, "confidence": conf, "bbox": [x, y, x+w, y+h]})
        return tokens