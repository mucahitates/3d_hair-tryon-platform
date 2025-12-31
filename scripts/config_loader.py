# -*- coding: utf-8 -*-

import json

from pathlib import Path


def load_config():
    config_path = Path("config") / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config dosyası bulunamadı: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


#json formatı ek kütüphane gerektirmediği için seçildi