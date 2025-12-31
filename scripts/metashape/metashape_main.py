import Metashape
from pathlib import Path
import json

###https://agisoft.freshdesk.com/support/solutions/articles/31000148332-metashape-python-api-reference


with open(Path("config") / "config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

paths = config["paths"]
ms = config["metashape"]

cikti_root = Path(paths["cikti"])



for user_dir in cikti_root.iterdir():
    if not user_dir.is_dir():
        continue

    user_id = user_dir.name

    
    photos_dir = user_dir / "kareler_ham"
   # photos_dir=user_dir / "kareler_secilmis_manuel"
   
    if not photos_dir.exists():
        print(f"[Metashape] {user_id} | frameler yok, geçildi")
        continue

    photos = sorted(photos_dir.glob("*.jpg"))
    if not photos:
        print(f"[Metashape] {user_id} | foto yok, geçildi")
        continue

    out_dir = user_dir / "modeller_metashape"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[Metashape] {user_id} | Foto sayısı: {len(photos)}")

   
    # PROJECT
    

    doc = Metashape.Document()
    chunk = doc.addChunk()
    chunk.addPhotos([str(p) for p in photos])

  

    ap = ms["align_photos"]

    chunk.matchPhotos(
    generic_preselection=ap["generic_preselection"],
    reference_preselection=ap["reference_preselection"],
    keypoint_limit=ap["keypoint_limit"],
    tiepoint_limit=ap["tiepoint_limit"]
    )

    chunk.alignCameras()

   

    ctp = ms["clean_tie_points"]
    if ctp["enabled"]:
        f = Metashape.TiePoints.Filter()
        f.init(chunk, Metashape.TiePoints.Filter.ReprojectionError)
        f.removePoints(ctp["level"])

   

    if ms["optimize_cameras"]["enabled"]:
        chunk.optimizeCameras()

    chunk.buildDepthMaps()
    
    
    #quality eklemeyi bulmamız gerek
    
    pc = ms["build_point_cloud"]

    filtering_map = {
        "disabled": Metashape.NoFiltering,
        "mild": Metashape.MildFiltering,
        "moderate": Metashape.ModerateFiltering,
        "aggressive": Metashape.AggressiveFiltering
    }

    chunk.buildPointCloud(
        source_data=Metashape.DepthMapsData
    )

   

    chunk.buildModel(
        source_data=Metashape.PointCloudData,
        interpolation=Metashape.EnabledInterpolation
    )

    

    chunk.buildUV(
        mapping_mode=Metashape.GenericMapping
    )

    

    bt = ms["build_texture"]

    chunk.buildTexture(
        blending_mode=Metashape.MosaicBlending,
        texture_size=bt["texture_size"]
    )

  

    export_path = out_dir / f"{user_id}.obj"

    chunk.exportModel(
        path=str(export_path),
        format=Metashape.ModelFormatOBJ,
        save_texture=True,
        embed_texture=False
    )

    print(f"[Metashape] ÇIKTI → {export_path}")

print("[Metashape] TÜM İŞLEMLER TAMAMLANDI")
