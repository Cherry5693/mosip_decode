import re, json
from typing import Dict, List, Any

def load_templates(path):
    templates = {}
    if path.exists():
        for f in path.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fh:
                templates[f.stem] = json.load(fh)
    return templates

class FieldMapper:
    def __init__(self, template: Dict[str, Any], lang="eng"):
        self.template = template or {}
        self.lang = lang

    def extract_fields(self, pages_tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fields = []
        for fname, spec in self.template.get("fields", {}).items():
            anchors = spec.get("anchors", [])
            pattern = spec.get("regex")
            value, conf, bbox, page_no = "", 0.0, None, 1
            for p in pages_tokens:
                page = p["page"]; tokens = p["tokens"]
                if pattern:
                    mtxt = " ".join(t["text"] for t in tokens)
                    m = re.search(pattern, mtxt)
                    if m:
                        value = m.group(1) if m.groups() else m.group(0)
                        conf = 0.9; page_no = page; break
                for i, t in enumerate(tokens):
                    if any(a.lower() in t["text"].lower() for a in anchors):
                        candidates = tokens[i+1:i+6]
                        value = " ".join(c["text"] for c in candidates if c["text"].strip())
                        conf = sum(c.get("confidence", 0.7) for c in candidates)/max(1,len(candidates)) if candidates else 0.7
                        bbox = candidates[-1]["bbox"] if candidates else t["bbox"]
                        page_no = page; break
                if value: break
            fields.append({"name": fname, "value": value.strip(), "confidence": float(conf), "page": page_no, "bbox": bbox})
        if self.template.get("allowPartial", True):
            seen = set(f["name"] for f in fields)
            for p in pages_tokens:
                tokens = p["tokens"]
                for i, t in enumerate(tokens):
                    if t["text"].endswith(":") and i+1 < len(tokens):
                        key = t["text"].strip(":").lower().replace(" ", "_")
                        if key not in seen:
                            val = tokens[i+1]["text"]
                            fields.append({"name": key, "value": val, "confidence": tokens[i+1].get("confidence", 0.7), "page": p["page"], "bbox": tokens[i+1]["bbox"]})
        return fields