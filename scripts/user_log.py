# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime


def _get_user_log_dir(config: dict, user_id: str) -> Path:
    log_root = Path(config["paths"]["loglar"])
    user_dir = log_root / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def write_log(
    *,
    config: dict,
    user_id: str,
    log_name: str,
    data: dict
):
    """
    log_name örn: 'scoring', 'frame_extraction', 'metashape'
    """
    user_dir = _get_user_log_dir(config, user_id)

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "log_type": log_name,
        "data": data
    }

    out_path = user_dir / f"{log_name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)  
