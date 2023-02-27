##############################################################################################################
"""
Created on Thu May  5 11:44:51 2022

This python script uses command line GDAL tools for reprojecting the satellite
data (S2) products to SWEREF99_TM (EPSG:3006). Further, the re-projected data
are clipped to the spatial extent defined within SITES. 

To know more about the GDAL command line tools:
    
    https://gdal.org/programs/gdalwarp.html#gdalwarp
    https://gdal.org/programs/gdal_calc.html#gdal-calc
    
To know more about the Anaconda3 module running on Terminal, check LUNARC 
documentation: https://lunarc-documentation.readthedocs.io/en/latest/Python/

To know more about the satellite data products:
    
    https://land.copernicus.eu/user-corner/technical-library/product-user-manual-of-seasonal-trajectories/
    
Note: This script is only for internal use within SITES Spectral.

Important information to run this script:
    
    1) Run the Terminal on AURORA.
    2) Load Anaconda3 module running the following command lines on Terminal:
    
        module load Anaconda3
        source config_conda.sh
    
    3) Load the GDAL module on terminal
    
        module load GCC/9.3.0  OpenMPI/4.0.3 GDAL/3.0.4-Python-3.8.2
        
    4) Run this python script on terminal:
        
        python /projects/eko/fs1/SITES_Spectral/FTPdatabase/Satellites/satDataPrepare.py
        
        General form: python Complete path of python script
    
    5) Follow the instructions displayed on the Terminal screen once you run the script
   
@author: Shangharsha
"""
##############################################################################################################
# Importing required modules
import os
import glob
import shutil

##############################################################################################################
# Predefine dictionary to store 'station' information
stnName = ['Abisko', 'Asa', 'Bolmen', 'Erken', 'Grimso', 'Lonnstorp', 'Robacksdalen', 
           'Skogaryd', 'Svartberget', 'Tarfala']

print('\n')

# Iterate through the list of SITES station
for idx, stn in enumerate(stnName):
    
    # Print the station name and corresponding indexes
    print('{}  : {}'.format(idx, stn))

print('\n')

# Ask from user to select the station for which to prepare the satellite data products   
station = int(input("Choose one of the SITES station (For example, 0 to prepare data for Abisko): "))

print('\n')

# Define spatial extent for each SITES station
# This spatial extent is precomputed in SWEREF99_TM (EPSG:3006) and will be 
# used for clipping the satellite tiles
spExtent = {0  : '639000 7564500 674000 7599500',
            1  : '478000 6324000 498000 6344000',
            2  : '401000 6291000 441000 6331000',
            3  : '690000 6630000 710000 6650000',
            4  : '514000 6610000 534000 6630000', 
            5  : '375000 6162000 395000 6182000',
            6  : '746500 7074500 766500 7094500',
            7  : '323000 6463000 343000 6483000',
            8  : '716500 7118000 736500 7138000',
            9  : '650000 7527000 680000 7557000'}

# Get the directory of the Python script
script = os.path.realpath(__file__)

# Get the base directory of this Python script
basePath = os.path.dirname(script)

# Join the path to the folder for the station chosen by the user
stnPath = os.path.join(basePath, stnName[station])

# List storing the names of the folders within each station
# All the data within these folders will be reprojected and clipped
folders = ['PPI', 'SOSD', 'EOSD', 'LENGTH', 'AMPL', 'SPROD']

##############################################################################################################

##############################################################################################################
# Iterate through the folders
for folder in folders:
    
    # Join the station path to the sub-folders within it
    subPath = os.path.join(stnPath, folder)
    
    # Create a new folder inside the sub-folders to store the reprojected images
    try:
        tempPath1 = os.path.join(subPath, 'Reprojected')
        os.mkdir(tempPath1)
    
    except:
        pass
    
    # Find all .tif files within each of the sub-folders
    fileList = glob.glob(subPath + '/*.tif')
    
    # Iterate through the .tif files within each sub-folders
    for file in fileList:
        
        # Check condition to see the product type and apply the right resampling algorithm during reprojection
        # Lines to reproject PPI tiles
        if '_PPI.tif' in file:
            
            # Define output path to store the reprojected satellite tiles
            # Save the reprojected satellite tile with the same name as original
            dstPath = os.path.join(tempPath1, os.path.basename(file))
            
            print('Reprojecting {} to SWEREF99_TM'.format(file))
            print ('\n')
            
            # Command line GDAL tool implementation
            cmdReproject = 'gdalwarp -t_srs EPSG:3006 -dstnodata -32768.0 -ot Float32 -r bilinear {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(file, dstPath)
            
            # Run the command line tools for reprojection to SWEREF99_TM
            os.system(cmdReproject)
                        
        # Lines to reproject QFLAG tiles    
        elif '_QFLAG.tif' in file:
            
            # Define output path to store the reprojected QFLAG tiles
            # Save the reprojected QFLAG tile with the same name as original
            dstPath = os.path.join(tempPath1, os.path.basename(file))
            
            print('Reprojecting {} to SWEREF99_TM'.format(file))
            print ('\n')
            
            # Command line GDAL tool implementation
            cmdReproject = 'gdalwarp -t_srs EPSG:3006 -dstnodata 0 -ot Byte -r near {} -co COMPRESS=DEFLATE -co PREDICTOR=2 {}'.format(file, dstPath)
            
            # Run the command line tools for reprojection to SWEREF99_TM
            os.system(cmdReproject)
            print ('\n')
        
        # Lines to reproject AMPL tiles for both seasons
        elif '_AMPL.tif' in file:
            # Define output path to store the reprojected AMPL tiles
            # Save the reprojected AMPL tiles with the same name as original
            dstPath = os.path.join(tempPath1, os.path.basename(file))
            
            print('Reprojecting {} to SWEREF99_TM'.format(file))
            print ('\n')
            
            # Command line GDAL tool implementation
            cmdReproject = 'gdalwarp -t_srs EPSG:3006 -dstnodata -32768.0 -ot Float32 -r bilinear {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(file, dstPath)
            
            # Run the command line tools for reprojection to SWEREF99_TM
            os.system(cmdReproject)
            print ('\n')
        
        # Lines to reproject SPROD tiles for both seasons
        elif '_SPROD.tif' in file:
            
            # Define output path to store the reprojected SPROD tiles for both seasons
            # Save the reprojected SPROD tiles with the same name as original
            dstPath = os.path.join(tempPath1, os.path.basename(file))
            
            print('Reprojecting {} to SWEREF99_TM'.format(file))
            print ('\n')
            
            # Command line GDAL tool implementation
            cmdReproject = 'gdalwarp -t_srs EPSG:3006 -dstnodata 65535 -ot Float32 -r bilinear {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(file, dstPath)
            
            # Run the command line tools for reprojection to SWEREF99_TM
            os.system(cmdReproject)
            print ('\n')
        
        # Lines to reproject SOSD, EOSD, LENGTH tiles for both seasons    
        else:
            
            # Define output path to store the reprojected vegetation phenology and productivity tiles
            # Save the reprojected phenology tiles with the same name as original
            dstPath = os.path.join(tempPath1, os.path.basename(file))
            
            print('Reprojecting {} to SWEREF99_TM'.format(file))
            print ('\n')
            
            # Command line GDAL tool implementation
            cmdReproject = 'gdalwarp -t_srs EPSG:3006 -dstnodata 0 -ot Int16 -r near {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(file, dstPath)
            
            # Run the command line tools for reprojection to SWEREF99_TM
            os.system(cmdReproject)
            print ('\n')
            
    print('Successfully reprojected all {} data to SWEREF99_TM'.format(folder))
    print('\n')
    
    ##############################################################################################################
    # Create a new folder inside the sub-folders to store the clipped images
    try:
        tempPath2 = os.path.join(subPath, 'Clipped')
        os.mkdir(tempPath2)
    
    except:
        pass
    
    # Find all .tif files within each of the sub-folders
    repList = glob.glob(tempPath1 + '/*.tif')
    
    # Iterate through the .tif files within 'Reprojected' folder
    for rfile in repList:
        
        # Define output path to store the clipped satellite tiles
        # Save the clipped satellite tile with the same name as original ??
        clipPath = os.path.join(tempPath2, os.path.basename(rfile))
        
        print('Clipping the reprojected tile {} to {} extent'.format(rfile, spExtent[station]))
        print ('\n')
        
        # Check conditions to apply the GDAL command line script to clip the satellite tiles with data specific parameters
        if '_PPI.tif' in rfile:
        
            # Command line GDAL tool implementation
            cmdClip = 'gdalwarp -te {} -dstnodata -32768 -tr 10 10 -ot Float32 {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(spExtent[station], rfile, clipPath)
            
            # Run the command line tools for clipping the satellite tiles
            os.system(cmdClip)
            print ('\n')
            
            # Command line raster calculator with numpy syntax
            # Reprojection with gdalwarp destroys the scale factor information
            # Rescaling the clipped layers to display the pixel values as the original file
            cmdRescale = 'gdal_calc.py -A {} --outfile={} --calc=A*0.0001 --NoDataValue=-32767.0 --type=Float32 --overwrite --quiet --co COMPRESS=DEFLATE --co TFW=YES'.format(clipPath, clipPath)
            os.system(cmdRescale)
            print ('\n')
            
        elif '_QFLAG.tif' in rfile:
            
            # Command line GDAL tool implementation
            cmdClip = 'gdalwarp -te {} -dstnodata 0 -tr 10 10 -ot Byte {} {}'.format(spExtent[station], rfile, clipPath)
            
            # Run the command line tools for clipping the satellite tiles
            os.system(cmdClip)
            print ('\n')
            
        elif '_AMPL.tif' in rfile:
            
            # Command line GDAL tool implementation
            cmdClip = 'gdalwarp -te {} -dstnodata -32768 -tr 10 10 -ot Float32 {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(spExtent[station], rfile, clipPath)
            
            # Run the command line tools for clipping the satellite tiles
            os.system(cmdClip)
            print ('\n')
            
            # Command line raster calculator with numpy syntax
            # Reprojection with gdalwarp destroys the scale factor information
            # Rescaling the clipped layers to display the pixel values as the original file
            cmdRescale = 'gdal_calc.py -A {} --outfile={} --calc=A*0.0001 --NoDataValue=-32768.0 --type=Float32 --overwrite --quiet --co COMPRESS=DEFLATE --co TFW=YES'.format(clipPath, clipPath)
            os.system(cmdRescale)
            print ('\n')
            
        elif '_SPROD.tif' in rfile:
            
            # Command line GDAL tool implementation
            cmdClip = 'gdalwarp -te {} -dstnodata 65535 -tr 10 10 -ot Float32 {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(spExtent[station], rfile, clipPath)
            
            # Run the command line tools for clipping the satellite tiles
            os.system(cmdClip)
            print ('\n')
            
            # Command line raster calculator with numpy syntax
            # Reprojection with gdalwarp destroys the scale factor information
            # Rescaling the clipped layers to display the pixel values as the original file
            cmdRescale = 'gdal_calc.py -A {} --outfile={} --calc=A*0.1 --NoDataValue=65535 --type=Float32 --overwrite --quiet --co COMPRESS=DEFLATE --co TFW=YES'.format(clipPath, clipPath)
            os.system(cmdRescale)
            print ('\n')
            
        else:
            # Command line GDAL tool implementation
            cmdClip = 'gdalwarp -te {} -dstnodata 0 -tr 10 10 -ot Int16 {} -co COMPRESS=DEFLATE -co PREDICTOR=2 -co TFW=YES {}'.format(spExtent[station], rfile, clipPath)
            
            # Run the command line tools for clipping the satellite tiles
            os.system(cmdClip)
            print ('\n')
            
    print('Successfully clipped all {} data to defined spatial extent'.format(folder))
    print('\n')
    
    ##############################################################################################################
    # Remove the 'Reprojected' folder from the directory
    shutil.rmtree(tempPath1, ignore_errors = False) #Making ignore_errors = True will not raise a FileNotFoundError

print('Sucessfully reprojected and clipped all satellite data products for the selected SITES station')
print('Check the station folder file path to see the final data.')
print('\n')
    
##################################################################################################################

    
