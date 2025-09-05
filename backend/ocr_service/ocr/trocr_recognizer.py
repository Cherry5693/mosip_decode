import cv2


class TrOCRRecognizer:
    """Resilient TrOCR wrapper.

    If required transformer/tokenizer packages or model files are missing,
    the recognizer becomes unavailable and methods return safe defaults.
    """
    def __init__(self, model_id="microsoft/trocr-small-printed"):
        self.model_id = model_id
        self.available = False
        self.device = "cpu"
        # Delay heavy imports and model loading. Try to load, but catch any
        # exception and mark unavailable instead of raising.
        try:
            import torch
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel

            self.torch = torch
            self.processor = TrOCRProcessor.from_pretrained(model_id)
            self.model = VisionEncoderDecoderModel.from_pretrained(model_id)
            self.model.to(self.device)
            self.available = True
        except Exception as e:
            # Keep the recognizer available flag false and log the error.
            try:
                # avoid raising during import-time in server logs
                print(f"TrOCRRecognizer init failed: {e}")
            except Exception:
                pass

    def recognize(self, crop_bgr):
        if not self.available:
            return "", 0.0
        if crop_bgr is None:
            return "", 0.0
        try:
            rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
            inputs = self.processor(images=rgb, return_tensors="pt")
            # move tensors to device if necessary
            if hasattr(self.torch, "device"):
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with self.torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_length=128)
            text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
            conf = 0.95 if text else 0.0
            return text[0].strip(), conf
        except Exception as e:
            try:
                print(f"TrOCRRecognizer recognize failed: {e}")
            except Exception:
                pass
            return "", 0.0