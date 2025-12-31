from pathlib import Path
import cv2
import numpy as np
from scripts.user_log import write_log

#gemini tarafından yazıldı fakat belirgin bir işe yarama olmadı

def _score_sharpness(gray: np.ndarray) -> float:
    v = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(np.clip(v / 1000.0, 0.0, 1.0))


def _score_lighting(gray: np.ndarray) -> float:
    m = float(np.mean(gray) / 255.0)
    return float(1.0 - abs(m - 0.5) * 2.0)  # 0..1


def _score_pose_simple(gray: np.ndarray) -> float:
    # Basit simetri: 1'e yakınsa "daha frontal"
    h, w = gray.shape
    left = gray[:, :w // 2]
    right = cv2.flip(gray[:, w // 2:], 1)
    diff = float(np.mean(cv2.absdiff(left, right)) / 255.0)
    return float(1.0 - np.clip(diff * 2.0, 0.0, 1.0))


def run_scoring(config: dict):
    paths = config["paths"]
    scoring = config["scoring"]

    cikti_dir = Path(paths["cikti"])

    for user_dir in cikti_dir.iterdir():
        if not user_dir.is_dir():
            continue

        user_id = user_dir.name
        kareler_ham = user_dir / "kareler_ham"
        if not kareler_ham.exists():
            continue

        secilmis_dir = user_dir / "kareler_secilmis"
        secilmis_dir.mkdir(parents=True, exist_ok=True)

        # Önceki çalıştırmadan kalanları temizle (tutarlılık için)
        for old in secilmis_dir.glob("sel_*.jpg"):
            old.unlink()

        weights = scoring["weights"]
        thr = scoring["thresholds"]
        max_n = scoring["selection"]["max_selected_frames"]

        all_frames = []
        selected = []

        for img_path in sorted(kareler_ham.glob("*.jpg")):
            img = cv2.imread(str(img_path))
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            s = _score_sharpness(gray)
            l = _score_lighting(gray)
            p = _score_pose_simple(gray)

            total = (
                s * weights["sharpness"] +
                l * weights["lighting"] +
                p * weights["pose"]
            )

            rec = {
                "filename": img_path.name,
                "sharpness": s,
                "lighting": l,
                "pose": p,
                "total_score": total,
                "passes_threshold": bool(
                    (s >= thr["min_sharpness"]) and
                    (l >= thr["min_lighting"]) and
                    (p >= thr.get("min_pose", 0.0)) and
                    (total >= thr.get("min_total_score", 0.0))
                )
            }
            all_frames.append(rec)

        # Eşik üstünü al
        selected = [r for r in all_frames if r["passes_threshold"]]

        # Çok seçilirse: en iyi total_score ile kırp
        selected.sort(key=lambda x: x["total_score"], reverse=True)
        selected = selected[:max_n]

        # Seçileni yaz
        for i, r in enumerate(selected, start=1):
            src = kareler_ham / r["filename"]
            dst = secilmis_dir / f"sel_{i:03d}.jpg"
            img = cv2.imread(str(src))
            if img is not None:
                cv2.imwrite(str(dst), img)

        # Logla (hepsi + seçilenler)
        write_log(
            config=config,
            user_id=user_id,
            log_name="scoring",
            data={
                "total_raw_frames": len(list(kareler_ham.glob("*.jpg"))),
                "total_scored_frames": len(all_frames),
                "total_selected_frames": len(selected),
                "thresholds_used": thr,
                "weights_used": weights,
                "all_frames": all_frames, #Hocaya gösterdikten sonra silinecen şişmemesi için
                "selected_frames": selected # Opsiyonel kalabilir.
            }
        )
