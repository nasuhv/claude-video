import numpy as np, subprocess, sys, mediapipe as mp, os
from mediapipe.tasks.python import vision, BaseOptions
S=sys.argv[1]; X0,Y0,CW,CH=480,140,960,940
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=S+"/assets/models/selfie_multiclass.tflite"),output_confidence_masks=True))
wins=[(36.6,39.9),(131.5,134.1),(187.2,190.1),(207.0,209.6),(224.9,227.3)]
for a,b in wins:
    n0,n1=int(a*30),int(b*30)+1
    p=subprocess.Popen(["ffmpeg","-v","error","-ss","%.3f"%(n0/30),"-i",S+"/src/raw.mov","-frames:v",str(n1-n0),"-vf","crop=%d:%d:%d:%d"%(CW,CH,X0,Y0),"-pix_fmt","rgb24","-f","rawvideo","-"],stdout=subprocess.PIPE)
    n=n0
    while True:
        bb=p.stdout.read(CW*CH*3)
        if len(bb)<CW*CH*3: break
        fr=np.ascontiguousarray(np.frombuffer(bb,np.uint8).reshape(CH,CW,3))
        r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=fr))
        m=1-np.squeeze(r.confidence_masks[0].numpy_view())
        np.save(S+"/work/masks/%05d.npy"%n,(np.clip(m,0,1)*255).astype(np.uint8)); n+=1
    print("window",a,b,"frames",n-n0,flush=True)
os._exit(0)
