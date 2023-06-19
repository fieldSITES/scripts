"""
****************************************************************************************************************
#########################################################
Empirical line for Radiometric calibration 

Created on Fri Oct  1 13:50:44 2021
#########################################################

This Python script is used to apply empirical line correction for radiometric calibration of the multispectral
UAV orthomosaic. Finally, the reflectance map and computed Normalized Difference Vegetation Index (NDVI) layer
are exported as .TIF files to the same file path as the original orthomosaic. 

Note: The script was tested on windows environment in Python 3.7.6 version only. This script is only for the 
      internal use within SITES.

Package installation:
    a) gdal    
    b) pandas
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Change panelType based on the panels used during the flight.
    b) Run the script and follow the instructions displayed. Provide complete file path to
       multispectral UAV orthomosaic as well as to the .xlsx file containing mean DN values
       for radiometric calibration.

Limitations of the script:
    a) Script is programmed to handle UAV orthomosaics with 5 bands that follows DJI P4 specification.
    b) Fails if the computer configuration is not sufficient for handling large data.
    
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        per-ola.olsson@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha (Modified after Dr. Per-Ola Olsson)

****************************************************************************************************************
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import copy
import numpy as np
import pandas as pd
from osgeo import gdal
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

################################################################################################################
# Paths and parameters to set
################################################################################################################

# Define file path for orthophoto to be corrected for radiometry
orgImg = input("Enter full file path of the multispectral orthomosaic: ") 

# Name appended to reflectance orthophoto (after empirical line)
ReflImgExt = '_refl'

# Number of bands in reflectance image to save (5 is with spectral bands only)
nbrBands = 5

# Excel sheet with mean DN values for the reflectance panels in the orthophoto to calcualte reflectance for
reflPanValFile = input("Enter full file path of .xlsx file with mean DN values for radiometric calibration: ") 

# Sheet in the Excel with acutal mean values for the reflectance panels
ValSheet = 'EmpLineValues'

# Which reflectance panels are used: 1 = Spectralon; 2 = MosaicMill
# Change it as per the panels used.
panelType = 2

# Reflectance values for the panels (rough refelctance, "real" values derived from dictionary below)
if panelType == 1:
    reflPercentage = ['5', '20', '50'] # For Spectralon
elif panelType == 2:
    reflPercentage = ['9', '23', '44'] # For MosaicMill

# Plotting images or not
plotImages = True
verbose = True
computeNDVI = True # Set to False if you don't want NDVI computation

################################################################################################################
# Define standard reflectance values for the panels chosen and read the orthomosaic
################################################################################################################
# DJI P4 spectral bands. Included as list to ensure band order is correct. 
djiBandList = ['BLU', 'GRE', 'RED', 'REG', 'NIR']

bandProc = '' # To append names of corrected bands to file name later

# The bands and reflectance panel reflectances for 5%, 20%, 50%
if panelType == 1:
    djiBandDict = {'BLU': [0.036542424,	0.201557576, 0.481509091], 'GRE':[0.037827273, 0.213139394, 0.500790909], 
               'RED':[0.039157576, 0.222890909, 0.515169697], 'REG':[0.04050303, 0.231678788, 0.527287879], 
               'NIR':[0.04345283, 0.244384906, 0.543090566]}
    
# The bands and reflectance panel reflectances for 9%, 23%, 44%    
elif  panelType == 2:
    djiBandDict = {'BLU': [0.071864034, 0.217418623, 0.382620256], 'GRE':[0.068064604, 0.218853955, 0.45281708], 
               'RED':[0.076557511, 0.22275384, 0.43940517], 'REG':[0.084988391, 0.234725921, 0.466921599], 
               'NIR':[0.100331593, 0.251634465, 0.497430071]}        

# Reading Excel sheet as a dataframe
reflPanValues = pd.ExcelFile(reflPanValFile)
reflPanValSheet = pd.read_excel(reflPanValues, ValSheet)

model = LinearRegression()

# Reading original TIFF
orgTIFF = gdal.Open(orgImg, gdal.GA_ReadOnly)

# And creating a new "empty" tiff with the same size as original
nbrCols = orgTIFF.RasterXSize
nbrRows = orgTIFF.RasterYSize

orgImgBase, orgImgExt = orgImg.split('.')
outImgName = orgImgBase + ReflImgExt + '.' + orgImgExt

# Reading just to get data type
tempDT = orgTIFF.GetRasterBand(1)
tiffDataType = tempDT.DataType
del tempDT
# Need same driver
driver = orgTIFF.GetDriver()
# Finally creating new tiff file
outImgGDAL = driver.Create(outImgName, nbrCols, nbrRows, nbrBands, tiffDataType)
#outImgGDAL = driver.Create(outImgName, nbrCols, nbrRows, nbrBands, gdal.GDT_Float32)

if verbose:
    print(outImgGDAL)
    print(driver)
    print(gdal.GetDataTypeName(tiffDataType))
    
################################################################################################################
# Performing empirical line correction and saving the reflectance tiff
################################################################################################################
    
for idx, band in enumerate(djiBandList):
    panelRefl = np.array(djiBandDict[band])
    
    # Extracting mean reflectance for the reflectance panels in the orthophoto
    # Setting NaN for saturated panels
    orthoRefl = np.full(3, np.nan)
    nbrReflVal = 0
    for i, r in enumerate(reflPercentage):
        tempRefl = band + '_' + r
        if reflPanValSheet[tempRefl][0] > 0:
            orthoRefl[i] = reflPanValSheet[tempRefl][0]
            nbrReflVal += 1
        
        print(tempRefl)
   
    print(orthoRefl)
    
    # Finding indices of NaN to omit in regression
    nonNanIdx = ~np.isnan(orthoRefl)
    
    orthoRefl = orthoRefl[nonNanIdx].reshape(-1, 1)
    
    panelRefl = panelRefl[np.transpose(nonNanIdx)]
    
    print(panelRefl)
    
    model = LinearRegression().fit(orthoRefl, panelRefl)
    
    if verbose:    
        print('Coefficient of determination: {}'.format(model.score(orthoRefl, panelRefl)))
        print('Intercept: {}'.format(model.intercept_))
        print('Slope: {}'.format(model.coef_))
    
    tiffBand = orgTIFF.GetRasterBand(idx+1)
    tiffArray = tiffBand.ReadAsArray()
    
    if plotImages:
        plt.imshow(tiffArray)
        plt.title('Original TIFF')
        plt.show()
        
        if nbrReflVal > 1:
            bandProc  += '_' + band
            reflArray = tiffArray*model.coef_[0] + model.intercept_
        
            plt.imshow(reflArray)
            plt.title('Reflectance')
            plt.colorbar()
            plt.show()
    
    if computeNDVI:   
        # Need to make deep coppies as Python will only copy the reference otherwise
        if "RED" in band:
            NDVIRED = copy.deepcopy(reflArray)
        elif "NIR" in band:
            NDVINIR = copy.deepcopy(reflArray)
    
    # Saving reflectance to the tiff file
    # First needs to scale and convert to integer
    # and remove negative numbers (which will otherwise be max value)
    if nbrReflVal > 1:
        reflArray[reflArray<0] = 0
        reflArray *= 10000 
        reflArray = np.uint16(reflArray)
        # Need idx+1 since raster band index start at 1
        outImgGDAL.GetRasterBand(idx+1).WriteArray(reflArray)
    else:
        outImgGDAL.GetRasterBand(idx+1).WriteArray(tiffArray)

# "Closing" the driver    
outImgGDAL = None        

## Renaming image to append processed band names to file name
#curr_name = orgImgBase + ReflImgExt + '.' + orgImgExt
#new_name = orgImgBase + ReflImgExt + bandProc + '.' + orgImgExt
#os.rename(curr_name, new_name)
    
# Creating the tfw-file for the new tiff
copyTFWstring = 'copy ' + orgImgBase + '.tfw ' + orgImgBase + ReflImgExt + '.tfw'
os.popen(copyTFWstring)

################################################################################################################
# NDVI computation and export
################################################################################################################
# Handling NDVI
if computeNDVI:
    
    NDVIArray = (NDVINIR - NDVIRED)/(NDVINIR + NDVIRED)
    NDVIArray[NDVIArray<0] = 0
    NDVIArray *= 10000 
    NDVIArray = np.uint16(NDVIArray)
    
    NDVIFileName = orgImgBase + '_NDVI.' + orgImgExt
    outImgNDVI = driver.Create(NDVIFileName, nbrCols, nbrRows, 1, tiffDataType)
    outImgNDVI.GetRasterBand(1).WriteArray(NDVIArray)

    # Creating the tfw-file for the new tiff
    copyTFWstringNDVI = 'copy ' + orgImgBase + '.tfw ' + orgImgBase + '_NDVI.tfw'
    os.popen(copyTFWstringNDVI)    
    
    outImgNDVI = None # "Closing" the driver

print('\n')
print('Radiometric calibration performed successfully.')
print('Check the reflectance and NDVI image layers in .tif format in the same file path as the original data.')

################################################################################################################
################################################################################################################

