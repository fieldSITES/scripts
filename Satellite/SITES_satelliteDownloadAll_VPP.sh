#!/bin/bash

set +x # Supress the progress messages

# Get the full functionality of the Anaconda environment 
module load Anaconda3
source config_conda.sh

# Run the python script
python /projects/eko/fs1/SITES_Spectral/FTPdatabase/Satellites/SITES_satelliteDownloadAll_VPP.py /projects/eko/fs1/SITES_Spectral/FTPdatabase/Satellites/vpp.json

