import subprocess, numpy as np, json, sys, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, M, out = sys.argv[1], sys.argv[2], sys.argv[3]
X0,Y0,W,H=560,160,800,800; SC=1.0
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=M+"/face_landmarker.task"), running_mode=vision.RunningMode.VIDEO, num_faces=2, min_face_detection_confidence=0.3, min_tracking_confidence=0.3))
fd = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=BaseOptions(model_asset_path=M+"/blaze_face_short_range.tflite"), running_mode=vision.RunningMode.VIDEO, min_detection_confidence=0.3))
p=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-vf",f"crop={W}:{H}:{X0}:{Y0}","-pix_fmt","rgb24","-f","rawvideo","-"],stdout=subprocess.PIPE)
res=[]; i=0
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    img=mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(np.frombuffer(b,np.uint8).reshape(H,W,3)))
    ts=int(i*1000/30)
    r=lm.detect_for_video(img,ts); boxes=[]
    for f in r.face_landmarks:
        xs=[p_.x for p_ in f]; ys=[p_.y for p_ in f]
        boxes.append(["lm",X0+min(xs)*W,Y0+min(ys)*H,X0+max(xs)*W,Y0+max(ys)*H])
    d=fd.detect_for_video(img,ts)
    for det in d.detections:
        bb=det.bounding_box
        boxes.append(["fd",X0+bb.origin_x,Y0+bb.origin_y,X0+bb.origin_x+bb.width,Y0+bb.origin_y+bb.height])
    res.append(boxes); i+=1
    if i%1000==0: print(i,boxes,flush=True)
json.dump(res,open(out,"w"))
print("frames",i,flush=True); import os; os._exit(0)
