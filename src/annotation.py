import json
from PIL import Image, ImageDraw, ImageFont
from PIL import ImagePath
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import pandas as pd
import sys

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

res = []
pats = os.listdir("PreviewImages")
pats = [pat for pat in pats if "." not in pat]

for pat in pats:
    print(pat)

    annotationfiles = os.listdir(os.path.join("PreviewImages",pat,"geojson_annotations"))
    annotationfiles = [f for f in annotationfiles if ".geojson" in f]

    imdir = os.path.join("PreviewImages",pat)
    files = os.listdir(imdir)
    ims = [f for f in files if (".jpg" in f) and ("_Q." not in f)]

    im = Image.open(os.path.join(imdir,ims[0]))
    
    for annotationfile in annotationfiles:
        annroot = annotationfile.replace(".geojson","")
        anndir = os.path.join("PreviewImages",pat,annroot)
        black = Image.new('L', im.size)
        red = Image.new('L', im.size)
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
                for fnm in files:
                    if ".tiff" in fnm:
                        fnames.append(os.path.join(root,fnm))
            if len(fnames)>1:
                print("Error: More than one .tiff file found for "+pat)
                break
            images,metals,labels = ex.parseMultiTIFF(fnames[0])
            imax = np.quantile(images,0.95)
            area = np.sum(mask)
            corrs = np.zeros((len(labels),len(labels)))
            for i in range(0,len(labels)):
                maskp = np.logical_and(mask,images[i,:,:]>0.0)
                nonzeros = images[i,:,:][maskp]
                allpix = images[i,:,:][mask]
                mean = np.mean(nonzeros)
                median = np.median(nonzeros)
                mean_all = np.mean(allpix)
                median_all = np.median(allpix)
                posarea = np.sum(maskp)
                posfrac = float(posarea)/float(area)
                #n, bins, patches = plt.hist(nonzeros, bins = 200, range=[0,np.max(nonzeros)],density=True, facecolor='g', alpha=0.75)
                #t = plt.title(labels[i])
                #plt.show()
                for j in range(0,len(labels)):
                    nonzeros2 = images[j,:,:][maskp]
                    corrs[i,j] = np.corrcoef(nonzeros,nonzeros2)[0,1]
                summ = {
                    "image":pat,
                    "annotation_file":annotationfile,
                    "roi_number":f,
                    "label":labels[i],
                    "area":area,
                    "mean_intensity_pos_signal":mean,
                    "median_intensity_pos_signal":median,
                    "mean_intensity_all_pixels":mean_all,
                    "median_intensity_all_pixels":median_all,
                    "pos_area":posarea,
                    "pos_fraction":posfrac
                }
                res.append(summ)
            print("Writing correlation matrix to file: "+'{:04d}'.format(f))
            df = pd.DataFrame(corrs,columns=labels,index=labels)
            df.to_csv(os.path.join(anndir,pat+"_"+annroot+"_CorrelationMatrix_"+'ROI{:04d}'.format(f)+".csv"))

            # Convert to long format
            b = np.tile(df.columns, len(df.index))
            a = np.repeat(df.index, len(df.columns))
            c = df.values.ravel()

            df_long = pd.DataFrame({'label_a':a, 'label_b':b, 'correlation':c})
            df_long = df_long[df_long.label_a!=df_long.label_b]
            df_long.sort_values("correlation",ascending=False)
            df_long.to_csv(os.path.join(anndir,pat+"_"+annroot+"_CorrelationsRanked_"+'ROI{:04d}'.format(f)+".csv"))

            imd = ImageDraw.Draw(black)
            imd_red = ImageDraw.Draw(red)
            imd.polygon(tups,fill="white",outline="white")
            
            mid = np.average(coords,axis=0)
            font = ImageFont.truetype("LEMONMILK-Regular.otf",75)
            imd_red.text((int(round(mid[0])),int(round(mid[1]))),'{:04d}'.format(f),fill="white",font=font)

        annroot = annotationfile.replace(".geojson","")
        anndir = os.path.join("PreviewImages",pat,annroot)
        if not os.path.exists(anndir):
            os.mkdir(anndir)

        for filename in ims:
            im = Image.open(os.path.join(imdir,filename))
            imrgb = im.convert("RGB")
            R, G, B = imrgb.split()
            newImage = Image.merge("RGB", (red,G,black))
            newImage.save(os.path.join(anndir,annroot+"_"+filename))

outres = pd.DataFrame(res)
outres.to_csv(os.path.join("PreviewImages","ROI_summaries.csv"))

