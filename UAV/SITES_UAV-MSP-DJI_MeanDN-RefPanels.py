"""
***************************************************************************************************************
#########################################################
Mean DN values extraction for Radiometric calibration 

Created on Fri Apr 28 09:46:51 2023
#########################################################

This Python script is used to extract mean DN values of the reflectance panels from the multispectral 
images per band. The extracted values are exported to an excel sheet. The exported excel sheet will be 
used as an input for the radiometric calibration script. Furthermore, there will be plots showing mean
DN values and standard deviation for the ROIs drawn per image.

Note: The script was tested on windows environment in Python 3.7.6 version only.

Package installations:
    1) roipoly  : pip install roipoly or pip install git+https://github.com/jdoepfert/roipoly.py
    2) Open-CV  : pip install opencv-python
    3) numpy    : pip install numpy
    4) pandas   : pip install pandas
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure the reflectance panel images are renamed as per the SITES Standard.
       For example: DJI_0011_BLU, DJI_0012_GRE, DJI_0013_RED, DJI_0014_REG, DJI_0015_NIR
    c) Check the same file path as the original images for the excel sheet with mean DN values for
       radiometric calibration.  
    d) Run Anaconda Prompt or general Terminal where you can locate the installed Python.
    e) Use the following command to run (Give complete path to where your script is located):
    
                (base) D:\MScGeomatics>python ".../SITES_extractMeanDN_RefPanels.py"
                
    f) Follow the instructions displayed on the Terminal screen once you run the script.
    g) When drawing ROIs left click to draw vertices and right click to complete the ROI. Draw ROIs for
       all three reflectance panels (9%, 23% and 44% in our case) one by one for each band.

    
Limitations of the script:
    a) Script is programmed to handle DJI P4 multispectral images only.
    b) Roipoly package doesn't work properly in Spyder. No issues running through the Terminal though.
    
Important information:
    a) Read more on RoiPoly package: 
       https://github.com/jdoepfert/roipoly.py

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
@author: Shangharsha

***************************************************************************************************************
"""
###############################################################################################################
# Importing required modules
###############################################################################################################
import os
import cv2
import glob
import logging
import pandas as pd
from roipoly import RoiPoly
from roipoly import MultiRoi
from shapely.geometry import Point
from matplotlib import pyplot as plt

logging.basicConfig(format='%(levelname)s ''%(processName)-10s : %(asctime)s '
                           '%(module)s.%(funcName)s:%(lineno)s %(message)s', level=logging.INFO)

###############################################################################################################
# Image path definition
###############################################################################################################
# Get path to all calibration target images
print('\n')
thePath = input('Enter the path where the reflectance panel images are located: ')

# Get list of all images within the user defined directory
imgList = sorted(glob.glob(os.path.join(thePath, '*.TIF')))

###############################################################################################################
# Automatically creating folders in the current working directory to save results 
###############################################################################################################
print('\n')
print('Creating new folders to store the results......')

# Try-except block is to pass overwrite directories if exists
folders = ['Plots', 'MeanDN']
for folder in folders:
    try:
        os.mkdir(os.path.join(thePath, folder))
    except:
        pass

print('\n')
print('Created new folder to store the results.')

###############################################################################################################
# User input to get the centroid location of where the panels are located.
# This is used to create a square buffer of 100 pixel distance
###############################################################################################################
print('\n')
print('Reading first reflectance panel image......')
print('Follow instructions on the user interface to continue.')

# Read first reflectance panel image 
im = cv2.imread(imgList[0])

# Define figure size
plt.rcParams['figure.figsize'] = (16,8)

# Display figure
fig = plt.figure()
plt.imshow(im)
plt.title('Left click: Mark central location of all panels  Right click: Complete', fontsize = 14)
plt.show(block=False)

# Mark a point in the central area where all 3 panels are located by clicking with the left mouse button  
# To complete this marking, click with the right mouse button.
zoomROI = RoiPoly(color='r', fig = fig) 

# Get the coordinate [(x1, y1), (x2, y2), …] of user defined centroid
imgCentre = zoomROI.get_roi_coordinates()

# Round off to nearest 10s
tempList1 = [int(round(y, -1)) for y in imgCentre[0]]

# Define point object of shapely geometry point module
squareRegion = Point(tempList1)
sqBuf = squareRegion.buffer(60, cap_style=3)

# Create arrays of x and y values
x1, y1 = sqBuf.exterior.xy

# Get extent of square buffer
ymin, ymax = (int(min(y1)), int(max(y1)))  
xmin, xmax = (int(min(x1)), int(max(x1)))

###############################################################################################################
# Iterate through the list of calibration target images
# Extract mean and standard deviation for each panels per image
# Write the extracted information to a .csv file
###############################################################################################################
print('\n')
print('Getting ROI polygons for 3 panels from the user......')

meanDN_values = []

for im in imgList:
    
    # Get image name
    imgName = os.path.basename(im).split('.')[0]
    
    # Read reflectance panel image 
    cv_mean = cv2.imread(im, cv2.IMREAD_UNCHANGED)
    cv_disp = cv2.imread(im)
    
    # Adjusting the brightness for displaying images
    cv_adjst = cv2.convertScaleAbs(cv_disp, beta = 30)
    
    # Display the calibration target images zoomed to square buffer extent
    fig = plt.figure()
    plt.imshow(cv_adjst[ymin:ymax, xmin:xmax])
    plt.title("Click on the button to add a new ROI")
    plt.text(3, 5, imgName, fontsize=12, color='blue', bbox=dict(facecolor='whitesmoke', alpha=0.5))
    
    # Draw multiple ROIs, each for the available reflectance panels in the image
    multiroi_named = MultiRoi(roi_names=['9% Panel', '23% Panel', '44% Panel'])
    
    # Draw all ROIs
    plt.imshow(cv_adjst[ymin:ymax, xmin:xmax])
    
    # Empty list to store ROI names for displaying in the legend
    roi_names = []
    roi_means = {}
    
    # Iterate through the multiple ROI object
    # Generate statistics and plot them
    for name, roi in multiroi_named.rois.items():
    
        roi.display_roi()
        roi.display_mean(cv_mean[ymin:ymax, xmin:xmax])
        roi_names.append(name)
        
        if imgName in roi_means:
            roi_means[imgName].append(roi.get_mean_and_std(cv_mean[ymin:ymax, xmin:xmax]))
        
        else:
            roi_means[imgName] = [roi.get_mean_and_std(cv_mean[ymin:ymax, xmin:xmax])]
    
    plt.text(3, 5, imgName, fontsize=12, color='blue', bbox=dict(facecolor='whitesmoke', alpha=0.5))
    plt.legend(roi_names, loc = 'best')
    outName = os.path.join(thePath + r'\Plots\{}.png'.format(imgName))
    plt.savefig(outName, bbox_inches='tight')
    plt.close()
    
    # Convert list of tuples in dictionary values to lists and update the dictionary
    # Input: [(11, 20), (13, 40), (55, 16)] ==> Output:[11, 20, 13, 40, 55, 16]
    roi_means[imgName] = [item for t in list(roi_means.values())[0] for item in t]
    
    # Convert Key-Value list Dictionary to Lists of List
    exportData = [[key] + val for key, val in roi_means.items()]

    # Appending dictionary with mean DN values of all 3 panels to an empty list
    meanDN_values.append(exportData[0])

print('\n')
print('Mean DN values for the user defined ROI polygons for all panels completed.')

###############################################################################################################
# Create an excel sheet to save the mean DN values per band for all three reflectance panels
###############################################################################################################
print('\n')
print('Exporting the mean DN values per spectral band to a .xlsx file......')

# Field name definition
heading = ['Image', 'MeanDN_9', 'Std_Dev', 'MeanDN_23', 'Std_Dev', 'MeanDN_44', 'Std_Dev']

# Spectral band definition for DJI P4 MSP
bands = ['BLU', 'GRE', 'NIR', 'RED', 'REG']

# Creating dataframe using lists of list
tempdf = pd.DataFrame(meanDN_values, columns = heading)

# Split dataframes based on spectral bands and save it as a list
splitDF_bands = [v for k, v in tempdf.groupby(tempdf.Image.str[-3:])]
      
# Create a new excel file in the path
pathDN = os.path.join(thePath + r'\MeanDN\extractedDN.xlsx')
writer = pd.ExcelWriter(pathDN, engine='xlsxwriter')

# Iterate through the list of dataframes and export to multiple sheets named after each bands
for i, frame in enumerate(splitDF_bands):
   frame.to_excel(writer, sheet_name = bands[i], index=False)

writer.save()

###############################################################################################################
# Create an excel sheet with average DN values of all reflectance panel images ready
# radiometric calibration.
###############################################################################################################
heading1 = ['BLU_9', 'BLU_23', 'BLU_44', 'GRE_9', 'GRE_23',	'GRE_44', 'RED_9', 'RED_23', 
            'RED_44', 'REG_9', 'REG_23', 'REG_44',	'NIR_9', 'NIR_23',	'NIR_44']

# Compute average DN values and export it to use for Empirical line method
avg_EMP = [frame.mean().to_list()[0:-1:2] for frame in splitDF_bands]

# Reshuffle list items in a way that follows the heading
avg2write = avg_EMP[0] + avg_EMP[1] + avg_EMP[3] + avg_EMP[-1] + avg_EMP[2]

# Replace saturated pixel values (i.e. 65535.0) with 0.0
for nbr, val in enumerate(avg2write):
    if val == 65535.0:
        avg2write[nbr] = 0.0

# Create a new excel file in the path
pathDN = os.path.join(thePath + r'\MeanDN\avg4cal.xlsx')
writer = pd.ExcelWriter(pathDN, engine='xlsxwriter')

# Convert list to dataframe
avgDF = pd.DataFrame([avg2write], columns = heading1)

# Export the dataframe to .xlsx file
writer = pd.ExcelWriter(pathDN, engine='xlsxwriter')
avgDF.to_excel(writer, sheet_name = 'EmpLineValues', index=False)
writer.save()

print('\n')
print('Exported successfully.')
print('Check the folder i.e. MeanDN for the extracted average DN values.')

###############################################################################################################