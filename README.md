# manannan
Manual annotation and quantification of IMC pseudoimages

See [Manannán mac Lir](https://en.wikipedia.org/wiki/Manann%C3%A1n_mac_Lir)

## Installation
1. Install the [latest version of Python](https://www.python.org/downloads/), **taking care to ADD PYTHON TO PATH**
1. Open a command prompt (e.g. Start->cmd in windows)
1. Use Python package installer to install some packages:
```pip install numpy matplotlib json pillow tifffile scikit-image```
1. Navigate to src directory

## Set up image directories
1. Within src directory create two subdirectories: MCDs and MultiTIFFs
1. Copy all .mcd files into MCDs directory
1. Open each one using Fluidigm's [MCD viewer](https://www.fluidigm.com/FluidigmSite_Assets/PrdSrv_Software/Software-Packages/MCD_Viewer/MCDViewer_V1.0.560.6_InstallationPack.zip)
1. Export contents of each .mcd file as a scaled, 16bit, multi-page .tiff file, into the MultiTIFFs directory

## Generate image previews from multipage TIFFs
1. Navigate to src directory
1. Execute ```explore.py```
1. This will create a new directory in src: PreviewImages
1. This will create subdirectories corresponding to each multipage TIFF in MultiTIFFS
1. This will write 8bit, compressed preview images, derived from multipage TIFF files found in MultiTIFFs, to subdirectories in PreviewImages
1. This will also create sub-directories named geojson_annotations within each PreviewImages directory, to store any annotations

## Annotate with QuPath
1. Download and install [QuPath](https://qupath.github.io/)
2. Open one of the preview images
3. Generate some ROIs
4. Export the ROIs into the relevant geojson_annotations directory

## Generate annotation preview images
1. Navigate to src directory
2. Execute ```annotate.py```
