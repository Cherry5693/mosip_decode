import torch
import cv2
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

class TrOCRRecognizer:
    def __init__(self, model_id="microsoft/trocr-small-printed"):
        self.processor = TrOCRProcessor.from_pretrained(model_id)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id)
        self.device = "cpu"
        self.model.to(self.device)

    def recognize(self, crop_bgr):
        if crop_bgr is None:
            return "", 0.0
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        inputs = self.processor(images=rgb, return_tensors="pt").to(self.device)
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_length=128)
        text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        conf = 0.95 if text else 0.0
        return text[0].strip(), conf