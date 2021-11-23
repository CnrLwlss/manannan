# Compare histograms from multipage .tiffs (scaled) with individual .tiffs
from PIL import Image
import tifffile as tf
import matplotlib.pyplot as plt
import os
import numpy as np
from skimage import exposure

def adapt(arr,clip_limit=0.03):
    arr_adapt = exposure.equalize_adapthist(arr, clip_limit=clip_limit)
    im8 = Image.fromarray(np.array(np.round(255.0*arr_adapt),dtype=np.uint8))
    im8.show()

pats = os.listdir("MultiTIFFs")
for pat in pats:
    print("")
    print(pat)
    if not os.path.exists("PreviewImages"):
        os.mkdir("PreviewImages")
    multidir = os.path.join("PreviewImages",pat)
    annotatedir = os.path.join(multidir,"geojson_annotations")
    if not os.path.exists(multidir):
        os.mkdir(multidir)
        if not os.path.exists(annotatedir):
            os.mkdir(annotatedir)
            
    fnames = []
    for root,subdir,files in os.walk(os.path.join("MultiTIFFs",pat)):
        for f in files:
            if ".tiff" in f:
                fnames.append(os.path.join(root,f))

    for multifn in fnames:
        tif = tf.TiffFile(multifn)
        images = tif.asarray()
        n = images.shape[0]
        metals = []
        labels = []
        print("LOADING METADATA")
        for page in tif.pages:
            meta = {}
            for tag in page.tags.values():
                name,value = tag.name, tag.value
                meta[name] = value
            #print(meta["PageName"])
            metals.append(meta["PageName"][meta["PageName"].find("(")+1:meta["PageName"].find(")")])
            labels.append(meta["PageName"].split("(")[0])
        print("GENERATING PREVIEW IMAGES")
        qmax = 0.95
        clip_limit = 0.5
        for i,label in enumerate(labels):
            print(label)
            arr = images[i,:,:]
            
            arr8 = np.minimum(arr/np.quantile(arr,qmax),1.0)
            quant8 = Image.fromarray(np.array(np.round(255.0*arr8),dtype=np.uint8))
            quant8.save(os.path.join(multidir,os.path.basename(multidir)+"_"+label+"_Q.jpg"),quality=90)
            
            arr_adapt = exposure.equalize_adapthist(arr, clip_limit=clip_limit)
            adapt8 = Image.fromarray(np.array(np.round(255.0*arr_adapt),dtype=np.uint8))
            adapt8.save(os.path.join(multidir,os.path.basename(multidir)+"_"+label+".jpg"),quality=90)

        #plt.hist(images.flatten(),bins = np.linspace(0,255,256))
        #plt.show()
