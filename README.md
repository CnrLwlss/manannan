# manannan
Manual annotation and quantification of IMC pseudoimages

See [Manannán mac Lir](https://en.wikipedia.org/wiki/Manann%C3%A1n_mac_Lir)

## Installation
1. Install the [latest version of Python](https://www.python.org/downloads/), **taking care to ADD PYTHON TO PATH**
2. If not already installed you will need to install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (warning 6.7Gb!)
    * Video showing installation [here](https://www.youtube.com/watch?v=rcI1_e38BWs).
4. Open a command prompt (e.g. Start->cmd in windows)
5. Use Python package installer to install some packages:
    * ```pip install numpy matplotlib json pillow tifffile scikit-image```
7. Navigate to src directory

## Set up image directories
1. Within src directory create two subdirectories: MCDs and MultiTIFFs
1. Copy all .mcd files into MCDs directory
1. Open each one using Fluidigm's [MCD viewer](https://www.fluidigm.com/FluidigmSite_Assets/PrdSrv_Software/Software-Packages/MCD_Viewer/MCDViewer_V1.0.560.6_InstallationPack.zip)
1. Export contents of each .mcd file as a scaled, 16bit, multi-page .tiff file, into the MultiTIFFs directory

## Generate image previews from multipage TIFFs
1. Navigate to src directory
1. Execute ```explore.py``` (e.g. by double-clicking on ```explore.py```)
1. Will create a new directory in src: PreviewImages
1. Will also create subdirectories corresponding to each multipage TIFF in MultiTIFFS
1. Will also write two types of 8bit, compressed preview images, derived from multipage TIFF files found in MultiTIFFs, to subdirectories in PreviewImages
     * Files named e.g. PATID_laminin_Q.jpg are contrast stretched by stretching histogram to truncate the intensity of the brightest 5% pixels
     * Files named e.g. PATID_laminin.jpg are contrast stretched by [adaptive equalization](https://scikit-image.org/docs/dev/auto_examples/color_exposure/plot_equalize.html)
3. Will also create sub-directories named geojson_annotations within each PreviewImages directory, to store any annotations

## Annotate images  with QuPath
1. Download and install [QuPath](https://qupath.github.io/)
2. Open one of the preview images
3. Generate some annotations
4. Export the annotations into the relevant geojson_annotations directory
  * File->Object data->Export as GeoJSON...  
  * Choose "All objects" in the Export dropdown menu 
  * OK -> Write file to the relevant geojson_annotations directory

## Generate annotation preview images
1. Navigate to src directory
2. Execute ```annotate.py``` (e.g. by double-clicking on ```annotate.py```)
3. Will generate further versions of preview images highlighting annotated areas (calculated from .geojson files)
