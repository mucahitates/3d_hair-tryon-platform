from pathlib import Path
import cv2
import numpy as np


def _frame_diff(prev_bgr, curr_bgr, resize_width): #iki kare arasındaki sayısal farkı hesaplamak için yazıldı
    def prep(img):
        h, w = img.shape[:2]
        if w > resize_width:
            nh = int(h * resize_width / w)  #performan iyileştirmek amaçlı görüntü yeniden boyutlandırıldı
            img = cv2.resize(img, (resize_width, nh), interpolation=cv2.INTER_AREA)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    a = prep(prev_bgr)
    b = prep(curr_bgr)
    return float(np.mean(cv2.absdiff(a, b)))  #iki kare arasındaki ortalama piksel farkı hesaplanır


def run_frame_extraction(config: dict):
    paths = config["paths"]  #klasör yolları jsondan alındı
    fe = config["frame_extraction"] #kare çıkarma değişkenleri jsondan alındı
    users_cfg = config["users"] #kabul edilen video uzantıları jsondan alındı

    girdi_dir = Path(paths["girdi"])
    cikti_dir = Path(paths["cikti"])
    video_exts = users_cfg["video_extensions"]

    for user_dir in girdi_dir.iterdir(): #her kullanıcı klasörü gezilir ve her seferinde bir path gelir
        if not user_dir.is_dir(): #path nesnesi klasör mü ?  for x in list(girdi_dir.iterdir()) optimize değil
            continue

        # video bul  list comprehension
        video_files = [
            p for p in user_dir.iterdir()
            if p.suffix.lower() in video_exts  #p.suffix  nokta değil uzantıyı verir
            ]
        
        if not video_files: #kullanıcı videosu yoksa diğer kullanıcıya geçmesi için
            continue  

        video_path = video_files[0]
        out_dir = cikti_dir / user_dir.name / "kareler_ham"
        #out_dir = os.path.join(cikti_dir, user_dir.name, "kareler_ham") import os den daha iyi
        out_dir.mkdir(parents=True, exist_ok=True)
        
        #opencv ile video açılır. Str dönüşümü c++ kökenli olduğu için 
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            continue

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0 #video fps hesapladık default 30fps dedik
        step = max(1, int(round(fps * fe["interval_sec"]))) 
        # örnek  60*0.1= 6 her 6 kareden biri alınacak
        #round tam sayıya yuvarladık
        #int dönüşümü yapıldı
        #interval_sec 0.01 gibi düşükse round 0 olabilir önlemek için min 1 
         # yazılamdan önce sonsuz döngüye girdi step=0 olduğu için
       
        prev_kept = None #son kayıt edilen kareyi tutar. ilk karede karşılaştırma olmadığı için none
        kept = 0 #toplam sayı limit kontrolü için
        idx = 0 #karenin indexi

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if idx % step != 0:
                idx += 1
                continue

            keep = True
            if prev_kept is not None:
                diff = _frame_diff(prev_kept, frame, fe["resize_width"])
                if diff < fe["diff_threshold"]:
                    keep = False
                    
            #önceki kayıt edilen kare ile işlenen kare arasındaki fark hesaplanır
            #belirlediğimiz değerden küçüse kareyi kayıt etmez

            if keep:
                kept += 1
                prev_kept = frame # kayıt edilen kare bir sonraki karşılaştırma için saklanır

                out_path = out_dir / f"frame_{kept:04d}.jpg"
                cv2.imwrite(
                    str(out_path),
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), int(fe["jpeg_quality"])]
                )

                if kept >= fe["max_frames"]:
                    break

            idx += 1

        cap.release()
        
#BU ALGORİTMA ORTALAMA PİKSEL FARKINA BAKARAK İKİ KAREYİ KARŞILAŞTIRIR
#SSIM ADINDA BİR TEKNİK VAR DENENEBİLİR
#OPTİCAL FLOW  KAMERA SABİTSE ÇOK GÜÇLÜ (MODEL HAREKET EDİYORSA)


