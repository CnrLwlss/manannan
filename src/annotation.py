import json
from PIL import Image, ImageDraw
from PIL import ImagePath
import os

pats = os.listdir("PreviewImages")
for pat in pats:
    print(pat)

    annotationfiles = os.listdir(os.path.join("PreviewImages",pat,"geojson_annotations"))
    annotationfiles = [f for f in annotationfiles if ".geojson" in f]

    imdir = os.path.join("PreviewImages",pat)
    files = os.listdir(imdir)
    ims = [f for f in files if (".jpg" in f) and ("_Q." not in f)]

    im = Image.open(os.path.join(imdir,ims[0]))
    black = Image.new('L', im.size)

    for annotationfile in annotationfiles:
        with open(os.path.join("PreviewImages",pat,"geojson_annotations",annotationfile)) as f:
            data = json.load(f)
        Nann = len(data["features"])
        for f in range(0,Nann):
            blob = data["features"][f]["geometry"]
            if blob["type"] == "LineString":
                coords = blob["coordinates"]
            if blob["type"] == "Polygon":
                coords = blob["coordinates"][0]
            tups = [tuple(coord) for coord in coords]
            imd = ImageDraw.Draw(black)
            imd.polygon(tups,fill="white",outline="white")

        annroot = annotationfile.replace(".geojson","")
        anndir = os.path.join("PreviewImages",pat,annroot)
        if not os.path.exists(anndir):
            os.mkdir(anndir)

        for filename in ims:
            im = Image.open(os.path.join(imdir,filename))
            imrgb = im.convert("RGB")
            R, G, B = imrgb.split()
            newImage = Image.merge("RGB", (R,G,black))
            newImage.save(os.path.join(anndir,annroot+"_"+filename))
