from rapidfuzz.distance import Levenshtein
from rapidfuzz import fuzz
from typing import List, Dict

def normalize(s: str):
    return (s or "").strip().lower()

def sim_scores(a: str, b: str):
    a_n, b_n = normalize(a), normalize(b)
    lev = 1.0 - (Levenshtein.distance(a_n, b_n) / max(1, len(b_n)))
    jw = fuzz.WRatio(a_n, b_n) / 100.0
    return lev, jw

def verify_fields(submitted: List[Dict[str, str]], observed: List[Dict[str, str]]):
    obs_map = {f["name"]: f for f in observed}
    results = []; all_ok = True
    for f in submitted:
        name = f["name"]; exp = f.get("value", "")
        obs = obs_map.get(name, {"value": ""})
        lev, jw = sim_scores(exp, obs.get("value", ""))
        ocr_conf = float(obs.get("confidence", 0.0))
        combined = 0.4 * ocr_conf + 0.6 * max(lev, jw)
        status = "match" if combined >= 0.95 else ("partial_match" if combined >= 0.80 else "mismatch")
        if status != "match": all_ok = False
        results.append({
            "name": name,
            "expected": exp,
            "observed": obs.get("value", ""),
            "status": status,
            "similarity": {"levenshtein": lev, "jaroWinklerLike": jw},
            "ocrConfidence": ocr_conf,
            "combinedScore": combined,
            "page": obs.get("page"),
            "bbox": obs.get("bbox"),
        })
    return results, all_ok

def overall_cer(submitted: List[Dict[str,str]], observed: List[Dict[str,str]]):
    obs_map = {f["name"]: f for f in observed}
    S = N = 0
    for f in submitted:
        tgt = (f.get("value") or "")
        hyp = (obs_map.get(f["name"], {}).get("value") or "")
        dist = Levenshtein.distance(tgt, hyp)
        N += len(tgt); S += dist
    return (S) / max(1, N)