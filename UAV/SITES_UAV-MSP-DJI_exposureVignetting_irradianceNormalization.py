"""
***************************************************************************************************************
#########################################################
Step 3:
Exposure, Vignetting and Optional Irradiance compensation 

Created on Wed Aug 18 12:07:53 2021
#########################################################

This Python Script performs exposure and vignetting compensation and optionally compensates for differences in
irradiance according to normalized sunshine sensor irradiance data from step 2. Finally, the normalized images
are exported as .TIF files and also copies the metadata from original images to the normalized images. 
Additionally, there are also image mask for the saturated pixels in each flight images. The output of 
this script i.e. both the normalized images and image masks are used for further processing into the
image processing softwares like Metashape/Pix4D or OpenDroneMap.

Note: The script was tested on windows environment in Python 3.7.6 version only. This script is only for the 
      internal use within SITES.

Package installation:
    a) gdal
    b) pandas     
    c) exiftool
    d) PyExifTool
    e) Matplotlib

Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure the flight images are renamed as per the SITES Standard.
       For example: DJI_0011_BLU, DJI_0012_GRE, DJI_0013_RED, DJI_0014_REG, DJI_0015_NIR
    c) Check the parameter setting section. Set the variables in this section to 'True' or
       'False'. Information about these variables are available there in the script.
    d) Run the script and follow the instructions displayed. Provide complete file path to
       multispectral images as well as to the .xlsx file with normalizing factor for each 
       of the images. The path to .xlsx file should be:
                ...SWE-LON-SFAB-AGR-msp-210604-U01\SWE-LON-SFAB-AGR-msp-210604-U01_seq.xlsx
                
    e) Check all the normalized images in the same file path as the original multispectral 
       images once the script is successfully completed. This images will be used for L2 & 
       L3 data creation. 
    
Limitations of the script:
    a) Script is programmed to handle DJI P4 multispectral images only.
    b) Users must have good knowledge of sunshine sensor data, radiometry, as well as the
       threshold values for the saturated pixels.
    
Important information:
    a) DJI Image Processing Guide:
       https://dl.djicdn.com/downloads/p4-multispectral/20200717/P4_Multispectral_Image_Processing_Guide_EN.pdf
       
    b) SITES Spectral - Data Quality Flagging (QFLAG) Documentation:
       https://meta.fieldsites.se/objects/yHjlJ9dsmPzMNAGPswfSlEtC
              
    c) Download and read more on Exiftool:
       https://exiftool.org/
       
    d) Download and read more on PyExifTool:
       https://github.com/sylikc/pyexiftool
       
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        per-ola.olsson@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha (Modified after Dr. Per-Ola Olsson)

"""
################################################################################################################
# Importing required modules
################################################################################################################

import os
import sys
import math
import exiftool
import numpy as np
import pandas as pd
from osgeo import gdal
import matplotlib.pyplot as plt

################################################################################################################
# Get file paths to the multispectral UAV flight images
################################################################################################################
directory = input("Enter file path to the folder containing multispectral DJI P4 images: ") 

# Path to .xlsx sheet with normalised sunshine sensor data 
sunshineSensorFittedExcel = input("Enter file path to .xlsx file containing normalizing factors: ")[1:-1]

################################################################################################################
# Paramter setting section
# This section decides how we want to run the script
################################################################################################################

adjustSunshineSensorDataFitted = False # True normalizes images based on sunshine sensor data
splTrend = False # True means the spline trend is used, False uses the polynomial trend

# True means vignetting compensation is performed
vigComp = True

# True means images are plotted, both original and adjusted
plotImages = False

# Set verbose to True for printouts of some steps
verbose = False

# Set saveAdjImg = True if saving the adjusted images
saveAdjImg = True

# Handling saturated pixels or not + threshold setting for defining saturated pixels
checkSaturated = True # Set True to save masks per image for importing in Metashape 
satThres = 64000 # This threshold values should be set with care

# Set to true to copy EXIF (and XMP) data from original to adjsuted images
copyEXIF = True # True means EXIF (and XMP) data will be copied

# Extension of the directory to save the adjusted images
# Naming convention:
# _irrGDAL_SAT_XX_NO_SSensor
# SAT : handles saturated pixels
# _XX_ : saturation threshold
# NO states if SSensor (sunshine sensor data are used to normalize for changing light conditions)
# VIG states if vignetting compensation is done
outDirExt = '_irrGDAL' + '_SAT'*checkSaturated + '_'*checkSaturated + str(satThres/1000)*checkSaturated + \
            '_NO'*(adjustSunshineSensorDataFitted==False) + '_SSensor' + '_VIG'*vigComp + '_v2'
outDirExtMask = outDirExt  + '_mask'
        
################################################################################################################
# Creating variables for tags and placing tags of interest in a list
# Adjust the tags in the list 'tags' to decide which tags to extract
################################################################################################################
imgName_tag = 'EXIF:FileName'
sensorGain  = 'XMP:SensorGain'                       # Image sensor gain for each band
irradiance  = 'XMP:Irradiance'                       # Calibrated sunshine sensor value
blackLevel  = 'EXIF:BlackLevel'

opticalCenterRelX = 'XMP:RelativeOpticalCenterX'    # Disparity on X-direction relative to NIR band
opticalCenterRelY = 'XMP:RelativeOpticalCenterY'    # Disparity on Y-direction relative to NIR band
calOpticalCenterX = 'XMP:CalibratedOpticalCenterX'  # X-axis coordinate of the designed position of optical center
calOpticalCenterY = 'XMP:CalibratedOpticalCenterY'  # Y-axis coordinate of the designed position of optical center
sensorGainAdjustment = 'XMP:SensorGainAdjustment'   # Parameter for individual difference correction

vignettingList = 'XMP:VignettingData'               # Coefficients for vignetting calibration
exposureTime   = 'XMP:ExposureTime'                 # Exposure time for each band

# Tags to read from the EXIF
tags = [irradiance, imgName_tag, opticalCenterRelX, opticalCenterRelY, calOpticalCenterX, calOpticalCenterY, 
        blackLevel, vignettingList, sensorGain, exposureTime, sensorGainAdjustment]

################################################################################################################
# Creating path of directory for output
outDir = directory + outDirExt + '\\'

if saveAdjImg:
    # Creating directory if it does not exist
    if not os.path.isdir(outDir):
        os.mkdir(outDir)
    else:
        sys.exit('Warning: Directory {} exists. Make sure you are not overwriting files in output directory'.format(outDir))

if checkSaturated:   
    # Directory for masks    
    outDirMask = directory + outDirExtMask + '\\'   
    if not os.path.isdir(outDirMask):
        os.mkdir(outDirMask)
    else:
        sys.exit('Warning: Directory {} exists. Make sure you are not overwriting files in output directory'.format(outDirMask))

# Opening file with trend if compensating for changing light conditions
if adjustSunshineSensorDataFitted:
    sunshineSensorTrend = pd.ExcelFile(sunshineSensorFittedExcel)
    
################################################################################################################
# Getting a list of the files in the directory
fileList = os.listdir(directory)
fileList.sort(key = lambda x: int(x.split('_')[1])) #Sort based on image number in image name string

# Bands of the camera to extract EXIF data for
djiBandList = ['Blue', 'Green', 'Red', 'RedEdge', 'NIR']

# Band abbreviation for each individual band
djiBandAbb = {'Blue': 'BLU', 'Green': 'GRE', 'Red': 'RED', 'RedEdge': 'REG', 'NIR': 'NIR'}

# Empty dictionary for saving max reflectance per band
reflMaxDict = {} 

################################################################################################################
# Exposure compensation, Vignetting Correction and Irradiance Normalization
################################################################################################################
    
for djiBand in djiBandList:

    if verbose:
        print ('Currently handling band: {}'.format(djiBand))
        
    if adjustSunshineSensorDataFitted:
        # Reading the normalised trend (and also image names for safety)
        bandSheet = pd.read_excel(sunshineSensorTrend, djiBand)
        if splTrend:
            irrTrendNorm = bandSheet['Spline norm']
            imgTrendName = bandSheet['Img']
        else:            
            irrTrendNorm = bandSheet['Norm trend']
            imgTrendName = bandSheet['Img']
    
    # Empty list for saving file names    
    files = []     
    
    maxRefl = 0 # To save max reflectance for a band to convert to uint16 later
    
    # Removing files that are not image files and selecting files per band
    arr = []
    for f in fileList:
        if ('TIF' in f) and djiBandAbb[djiBand] in f and not '.enp' in f: # checking not enp (Envi file)
            arr.append(f)
    
    files = [os.path.join(directory, f) for f in arr] 

    ############################################################################################################
    # Reading EXIF data from the image
    ############################################################################################################
    with exiftool.ExifTool() as et:
        metadata_ALL = et.get_tags_batch(tags, files)
                          
    ############################################################################################################
    # Extract various metadata tags for vignetting correction
    ############################################################################################################ 
    # Polynomial coefficients are defined as a unicode string of six coefficients separated by comma.
    poly_coeff = [float(unicodeVal) for unicodeVal in metadata_ALL[0]['XMP:VignettingData'].split(u',')]

    # Define variables for polynomial coefficients
    k0, k1, k2, k3, k4, k5 = poly_coeff
    
    # Extract black level tag
    black_level = metadata_ALL[0]['EXIF:BlackLevel']
    
    # Extract the X and Y coordinates of center of vignette in pixels
    CenterX = metadata_ALL[0]['XMP:CalibratedOpticalCenterX']
    CenterY = metadata_ALL[0]['XMP:CalibratedOpticalCenterY']
    
    # Iterate through metadata of all images per band
    for idx, metadata in enumerate(metadata_ALL):
        
        # Read image as a numpy array
        imarray = plt.imread(files[idx]) 
        
        # Get the size of the image
        nrows, ncols = np.shape(imarray) 
        
        #print np.max(imarray)
        # Normalized raw pixel value and normalized black level value.
        # Normalization here is to simply divide the original number by 65535 as P4 multispectral images are 16bit.
        Ix = imarray/65535.0
        Ibl = black_level/65535.0
        
        # Subtract the normalized raw pixelvalue from normalized dark level value
        imgAdj = Ix - Ibl
        
        # Get the basename of the images from a given path
        imgName = os.path.basename(files[idx])
                
        # Irradiance normalization of the images using sunshine sensor fitted data
        if adjustSunshineSensorDataFitted:
            assert imgTrendName[idx] == imgName
            imgAdj = imgAdj/irrTrendNorm[idx]
                
        ############################################################################################################
        # Sets saturated pixels to np.nan
        # Saturated pixels are assigned the value 65535
        ############################################################################################################
                
        if checkSaturated:
            # Gives a binary matrix with saturated values = 0 and
            # all other values = 1
            imarray[imarray < satThres] = 255
            imarray[imarray > satThres] = 0 
            
            # Saves the mask for import in Agisoft
            driver = gdal.GetDriverByName('Gtiff')
            # uint8 not available with the driver byte but gives 0-255
            dataset = driver.Create(outDirMask + imgName.split('.')[0] +'_mask.tif', ncols, nrows, 1, gdal.GDT_Byte)
            dataset.GetRasterBand(1).WriteArray(imarray)
            dataset = None # "Closing" the driver
            
            # Setting saturated pixels to nan in the adjusted image.
            # When saved to tiff nan are replaced with max value of uint16
            imarray[imarray > 0] = 1
            imgAdj = imgAdj*imarray
            imgAdj[imgAdj == 0] = np.nan 
        
        if plotImages:        
            plt.imshow(imgAdj)
            plt.colorbar()
            plt.title('Before vignetting')
            plt.show()
            
        ############################################################################################################
        # Vignetting and Exposure Correction
        ############################################################################################################
        # Empty matrix with vignetting factor for each pixels (x,y)
        r = np.ones((nrows, ncols), dtype=np.float32)
        
        # Compute distance between pixel (x, y) and the center of the vignette in pixels
        for y in range(0, nrows):
            for x in range(0, ncols):
                # Equation 9 from the referred document
                r[y, x] = math.sqrt(pow((x - CenterX), 2) + pow((y - CenterY), 2))  
        
        # Computing vignetting factor for each image
        correction = k5*r**6 + k4*r**5 + k3*r**4 + k2*r**3 + k1*r**2 + k0*r + 1.0
        
        # Extract sensor gain setting and camera exposure time for each image
        valGain = metadata['XMP:SensorGain']
        valExptime = metadata['XMP:ExposureTime']
        
        # Normalized camera value for each band. X refers to each band (e.g. NIR, Red, Red Edge, Green, Blue)
        # Equation 7 from the referred document
        Xcamera = imgAdj * correction / (valGain * (valExptime/1e6))   
        
        # To get max reflectance to convert to uint16 later
        if np.amax(Xcamera[~np.isnan(Xcamera)]) > maxRefl:
            maxRefl = np.amax(Xcamera[~np.isnan(Xcamera)])
                
        ############################################################################################################
        # Export the corrected images
        ############################################################################################################              
        if saveAdjImg:
            # Define name of output file. 
            # Removing .TIF extension since matplotlib does not handle 1-band tiffs
            fn = files[idx].split('\\')[-1].split('.')[0]
            outImg = outDir + fn
        
            # Matplotlib imsave gives 3-band tiffs.
            # Instead saving temporary as npy files.
            # NB, since the stretch must be performed before converting to
            # uint16 all images must be handled first i.e. it is not possible
            # to save final version already here

            np.save(outImg, Xcamera)
                
        if plotImages:
            plt.imshow(Xcamera)
            plt.colorbar()
            plt.show()
    
    # Store maximum reflectance per band
    reflMaxDict[djiBand] = maxRefl

################################################################################################################
# Converting images from float to uint16 and stretching to get full range
# NB!!!! GDAL sets float values <0 to max in uint16
################################################################################################################
# To get conversion factor from float -> uint16
for key in reflMaxDict:
    # Rounding down to nearest ones
    reflMaxDict[key] = math.floor(satThres/(reflMaxDict[key]*1.0))*1
       
imgFileList = os.listdir(outDir)
imgFileList.sort(key = lambda x: int(x.split('_')[1]))

for im in imgFileList:
    
    # Reading and converting image to uint16
    imarray = np.load(outDir + im) 
    tempExt = im.split('.')[0].split('_')[-1] # To get band (BLU, GRE, RED, REG, NIR)
    
    # Need to remove negative values otherwise GDAL sets them to max. 
    imarray = imarray * reflMaxDict[list(djiBandAbb.keys())[list(djiBandAbb.values()).index(tempExt)]]
    imarray[np.isnan(imarray)] = 65535 # uint cannot handle nan so setting to max value
    imarray[imarray < 0] = 0
    imarray = imarray.astype(np.uint16)
    
    os.remove(outDir + im) # Removing old version of file
    im = im.split('.')[0]  # To remove the .npy extension
    
    # GDAL version saving directly to tiff
    nrows, ncols = np.shape(imarray)
    
    driver = gdal.GetDriverByName('Gtiff')
    dataset = driver.Create(outDir + im +'.tif', ncols, nrows, 1, gdal.GDT_UInt16)

    dataset.GetRasterBand(1).WriteArray(imarray)
    
    dataset = None # "Closing" the driver
        
################################################################################################################
# Copy the EXIF file from original to adjusted images   
################################################################################################################         
if copyEXIF:
    # Exiftool commands
    exifArgEXIF = 'exiftool -tagsFromFile ' + directory + '\\' + '%f.tif' + ' -all:all ' + outDir
    exifArgXMP = 'exiftool -tagsFromFile ' + directory + '\\' + '%f.tif' + ' -xmp ' + outDir
    
    exifArgEXIFList = ['exiftool', '-tagsFromFile', directory + '\\' + '%f.tif', '-all:all ' + outDir]
    exifArgXMPList = ['exiftool', '-tagsFromFile', directory + '\\' + '%f.tif', '-xmp ' + outDir]
    
    # Run the command line scripts in the terminal
    os.system(exifArgEXIF)
    os.system(exifArgXMP)  

print ('Finished exposure, vignetting compensation and irradiance normalization (optionally).')
print ('Check the newly created folders with normalized images and image mask for saturated pixels.')
       
################################################################################################################
################################################################################################################
