# -*- coding: utf-8 -*-

#Metashape yi çağırmak için headless mod

import subprocess
from pathlib import Path


def run_metashape_headless():
    metashape_exe = r"C:\Program Files\Agisoft\Metashape Pro\metashape.exe"
    script = Path("scripts/metashape/metashape_main.py")

    subprocess.run(
        [metashape_exe, "-r", str(script)],
        check=True
    )


#raw string windows yol hatalarını önler
# Metashape API kendi içinde çalıştığı için subprocess kullanmamız gerekti
#import edilemiyor
#script i metashape.exe de çalıştırmamız gerekiyor