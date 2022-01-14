import json
from PIL import Image, ImageDraw
from PIL import ImagePath
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr

import explore as ex

def get_font(fontsize=40):
    """Attempts to retrieve a reasonably-looking TTF font from the system.

    We don't make much of an effort, but it's what we can reasonably do without
    incorporating additional dependencies for this task.
    """
    if sys.platform == 'win32':
        font_names = ['Arial']
    elif sys.platform in ['linux', 'linux2']:
        font_names = ['DejaVuSans-Bold', 'DroidSans-Bold']
    elif sys.platform == 'darwin':
        font_names = ['Menlo', 'Helvetica']

    font = None
    for font_name in font_names:
        try:
            font = ImageFont.truetype(font_name,fontsize)
            break
        except IOError:
            continue

    return font

def makeMask(size,tups):
    black = Image.new('1', im.size)
    imd = ImageDraw.Draw(black)
    imd.polygon(tups,fill="white",outline="white")
    return(np.array(black))

pats = os.listdir("PreviewImages")
for pat in pats:
    print(pat)

    annotationfiles = os.listdir(os.path.join("PreviewImages",pat,"geojson_annotations"))
    annotationfiles = [f for f in annotationfiles if ".geojson" in f]

    imdir = os.path.join("PreviewImages",pat)
    files = os.listdir(imdir)
    ims = [f for f in files if (".jpg" in f) and ("_Q." not in f)]

    im = Image.open(os.path.join(imdir,ims[0]))
    

    for annotationfile in annotationfiles:
        black = Image.new('L', im.size)
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
            mask = makeMask(im.size,tups)
            # Let's have a look at raw data in multipage tiff files
            fnames = []
            for root,subdir,files in os.walk(os.path.join("MultiTIFFs",pat)):
                for f in files:
                    if ".tiff" in f:
                    fnames.append(os.path.join(root,f))
            if len(fnames)>1:
                print("Error: More than one .tiff file found for "+pat)
                break
            images,metals,labels = ex.parseMultiTIFF(fnames[0])
            imax = np.quantile(images,0.95)
            res={}
            area = np.sum(mask)
            corrs = np.zeros((len(labels),len(labels)))
            for i in range(0,len(labels)):
                maskp = np.logical_and(mask,images[i,:,:]>0.0)
                nonzeros = images[i,:,:][maskp]
                mean = np.mean(nonzeros)
                median = np.median(nonzeros)
                posarea = np.sum(maskp)
                posfrac = float(posarea)/float(area)
                #n, bins, patches = plt.hist(nonzeros, bins = 200, range=[0,np.max(nonzeros)],density=True, facecolor='g', alpha=0.75)
                #t = plt.title(labels[i])
                #plt.show()
                for j in range(0,len(labels)):
                    nonzeros2 = images[j,:,:][maskp]
                    corrs[i,j] = np.corrcoef(nonzeros,nonzeros2)[0,1]
            
            imd = ImageDraw.Draw(black)
            imd.polygon(tups,fill="white",outline="white")
            mid = np.average(coords,axis=0)
            font = get_font(40)
            imd.text((int(round(mid[0])),int(round(mid[1]))),f,font,fill=(255,0,0,255))

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
