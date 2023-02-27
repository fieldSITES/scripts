#!/bin/bash

set +x # Supress the progress messages

# Get the full functionality of the Anaconda environment 
module load Anaconda3
source config_conda.sh

# Load the GDAL module
module load GCC/9.3.0  OpenMPI/4.0.3 GDAL/3.0.4-Python-3.8.2
#/sw/easybuild/software/GDAL/3.0.4-foss-2020a-Python-3.8.2/bin/gdalwarp

# Run the python script
python3 SITES_satelliteData_harmonize.py
