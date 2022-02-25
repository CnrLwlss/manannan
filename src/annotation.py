import json
from PIL import Image, ImageDraw, ImageFont
from PIL import ImagePath
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import pandas as pd
import sys
from matplotlib.backends.backend_pdf import PdfPages

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

pixthresh = 0
font = ImageFont.truetype("LEMONMILK-Regular.otf",75)

for pat in pats:
    print(pat)

    annotationfiles = os.listdir(os.path.join("PreviewImages",pat,"geojson_annotations"))
    annotationfiles = [f for f in annotationfiles if ".geojson" in f]

    imdir = os.path.join("PreviewImages",pat)
    files = os.listdir(imdir)
    ims = [f for f in files if (".jpg" in f) and ("_Q." not in f)]

    im = Image.open(os.path.join(imdir,ims[0]))
    allblack = Image.new('L', im.size)
    imdall = ImageDraw.Draw(allblack)
    
    for annotationfile in annotationfiles:
        annroot = annotationfile.replace(".geojson","")
        anndir = os.path.join("PreviewImages",pat,annroot)
        if not os.path.exists(anndir):
            os.mkdir(anndir)
        black = Image.new('L', im.size)
        red = Image.new('L', im.size)
        with open(os.path.join("PreviewImages",pat,"geojson_annotations",annotationfile)) as f:
            data = json.load(f)
        Nann = len(data["features"])
        coordvec = []
        for f in range(0,Nann):
            blob = data["features"][f]["geometry"]
            if blob["type"] == "LineString":
                coords = blob["coordinates"]
            if blob["type"] == "Polygon":
                coords = blob["coordinates"][0]
            coordvec.append(coords)
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
            images,metals,unsorted_labels = ex.parseMultiTIFF(fnames[0])
            labdict = {lab:i for i,lab in enumerate(unsorted_labels)}
            labels = sorted(unsorted_labels, key=str.casefold)
            area = np.sum(mask)
            corrs = np.zeros((len(unsorted_labels),len(unsorted_labels)))
            fig = plt.figure(constrained_layout=True, figsize=(25*0.75, 15*0.75), dpi=100)
            
            for l,label in enumerate(labels):
                i = labdict[label]
                chanpix = images[i,:,:]
                allpix = chanpix[mask]
                qmax = 0.95
                eps = 0.5
                pixtqm = np.quantile(chanpix[mask],qmax)
                pixtqa = np.quantile(chanpix,qmax)
        
                # Write log intensity histogram to .pdf
                mlabel = "log("+label+"+0.5)"
                print("Plotting histogram: "+pat+" "+annroot+'_{:04d} '.format(f)+label)
                sp = plt.subplot(6,10,l+1)
                ldat = np.log(allpix+eps)
                n, bins, patches = plt.hist(ldat, bins = np.linspace(-1,12,131), range=[np.log(pixthresh+eps),np.max(np.log(chanpix+eps))],density=True, facecolor='g', alpha=0.75, figure=fig,log=True)
                changebin = 1+5+np.argmax(np.abs(np.diff(n[5:])))
                pixtadapt = np.exp(bins[changebin])-eps
                nadapt = n[changebin]
                l = plt.axvline(np.log(np.ceil(pixthresh+eps)),color="red",linestyle="dashed")
                l2 = plt.axvline(np.log(np.ceil(pixtadapt+eps)),color=(0,0,1,0.25),linestyle="dashed")
                l3 = plt.axvline(np.log(np.ceil(pixtqm+eps)), color="pink",linestyle="dashed")
                l4 = plt.axvline(np.log(np.ceil(pixtqa+eps)), color="orange",linestyle="dashed")
                pt = plt.xlabel(mlabel,figure=fig)
                tx = plt.text(1.05*np.log(np.ceil(pixtadapt+eps)),0.3*np.max(n),str(round(np.log(np.ceil(pixtadapt+eps)),3)),color="blue",ha="left")

                pixthresh = pixtadapt
                maskp = np.logical_and(mask,chanpix > pixthresh)
                pospix = chanpix[maskp]    
                mean = np.mean(pospix)
                median = np.median(pospix)
                mean_all = np.mean(allpix)
                median_all = np.median(allpix)
                posarea = np.sum(maskp)
                posfrac = float(posarea)/float(area)
                
                
                for l2,label2 in enumerate(labels):
                    j = labdict[label2]
                    pospix2 = images[j,:,:][maskp]
                    corrs[i,j] = np.corrcoef(pospix,pospix2)[0,1]
                summ = {
                    "image":pat,
                    "annotation_file":annotationfile,
                    "roi_number":f,
                    "label":label2,
                    "area":area,
                    "mean_intensity_pos_signal":mean,
                    "median_intensity_pos_signal":median,
                    "mean_intensity_all_pixels":mean_all,
                    "median_intensity_all_pixels":median_all,
                    "pos_area":posarea,
                    "pos_fraction":posfrac
                }
                res.append(summ)

            st = fig.suptitle(pat+" "+annroot+'_{:04d} '.format(f), fontsize=14)
            plt.savefig(os.path.join(anndir,pat+"_"+annroot+'_{:04d}.png'.format(f)),dpi=400)
            print("Writing correlation matrix to file: "+'{:04d}'.format(f))
            df = pd.DataFrame(corrs,columns=labels,index=labels)
            df.to_csv(os.path.join(anndir,pat+"_"+annroot+"_CorrelationMatrix_"+'ROI{:04d}'.format(f)+".csv"))

            # Convert to long format
            b = np.tile(df.columns, len(df.index))
            a = np.repeat(df.index, len(df.columns))
            c = df.values.ravel()

            df_long = pd.DataFrame({'label_a':a, 'label_b':b, 'correlation':c})
            df_long = df_long[df_long.label_a!=df_long.label_b]
            df_long = df_long.sort_values("correlation",ascending=False)
            df_long.to_csv(os.path.join(anndir,pat+"_"+annroot+"_CorrelationsRanked_"+'ROI{:04d}'.format(f)+".csv"), index=False)
            
        for lab in labels:
            i = labdict[lab]
            for j,coords in enumerate(coordvec):
                tups = [tuple(coord) for coord in coords]
                imdall.polygon(tups,fill="white",outline="white")
            filename = pat+"_"+lab+".jpg"
            arr = np.array(images[i,:,:])
            posim = Image.fromarray(np.array((arr>pixthresh)*255,dtype=np.uint8),mode="L")
            im = Image.open(os.path.join(imdir,filename))
            maskp = np.logical_and(mask,images[i,:,:]>pixthresh)
            imrgb = im.convert("RGB")
            R, G, B = imrgb.split()
            empty = Image.fromarray(np.zeros(posim.size[::-1],dtype=np.uint8),mode="L")
            newImage = Image.merge("RGB", (posim,empty,allblack))
            imd2 = ImageDraw.Draw(newImage)
            for j,coords in enumerate(coordvec):
                mid = np.average(coords,axis=0)
                imd2.text((int(round(mid[0])),int(round(mid[1]))),'{:04d}'.format(j),fill="white",font=font)
            newImage.save(os.path.join(anndir,annroot+"_"+filename))

outres = pd.DataFrame(res)
outres.to_csv(os.path.join("PreviewImages","ROI_summaries.csv"),index=False)
