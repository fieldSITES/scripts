"""
***************************************************************************************************************
Created on Mon Jan 16 10:04:56 2023
This python script lets the user to draw their own region of interest (ROI) for generating time series
of daily averaged Green Chromatic Coordinate (GCC) and Red Chromatic Coordinate (RCC) from the time 
lapse PhenoCam images. 

The script will export the results in the same path as that of the original pictures. The time series
data are exported as .csv file with all the time series metrics within a folder 'CSV'. The plot of the
VIs are exported as a .png file within a folder called 'Graph'. The user defined ROI will be exported
as a ROI map in the same directory.

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only 
      for internal use within Swedish Infrastructure for Ecosystem Science (SITES).

Package installations:
    1) roipoly  : pip install roipoly or pip install git+https://github.com/jdoepfert/roipoly.py
    2) Open-CV  : pip install opencv-python
    3) numpy    : pip install numpy
    4) pandas   : pip install pandas

Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Images should be in .jpg format.
    c) Make sure the images are as per the SITES naming convention
    
       For example: SWE-LON-SFA-P01_20220101_001_1020.jpg
       General: Country-Station-Location-PhenoCam_YYMMDD_DOY_HHMM
       
    d) Make sure the images are of same dimensions (For eg: 3072*2048)
    e) Create a new folder named 'SnowyImage' within the image directory and move all snowy images to
       this newly created folder. In case of no snowy images in the year, skip this step.
    f) Run Anaconda Prompt or general Terminal where you can locate the installed Python.
    g) Use the following command to run (Give complete path to where your script is located):
    
                (base) D:\MScGeomatics>python ".../SITES_phenoCam.py"
                
    h) Follow the instructions displayed on the Terminal screen once you run the script.
    i) When drawing ROIs left click to draw vertices and right click to complete the ROI.

Limitations of the script:
    a) Script can only take .jpg images as input.
    b) Script is programmed to handle only one ROI at a time.
    c) Script doesn't account for the change in camera field of view
    c) Script is programmed to process only one year data at a time.
    d) Roipoly package doesn't work properly in Spyder. No issues running through the Terminal though.

Example Data:
    # Freely downloadable from SITES data portal under SITES Spectral thematic program. 
    Link to SITES data portal: https://data.fieldsites.se/portal/

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
@author: Shangharsha

***************************************************************************************************************
"""
###############################################################################################################
# Importing required modules
###############################################################################################################
import os
import cv2
import glob
import random
import calendar
import datetime
import statistics
import numpy as np
import pandas as pd
from roipoly import RoiPoly
from scipy import stats as s
from datetime import datetime as dt
from matplotlib import pyplot as plt

###############################################################################################################
# Get time now. This helps to compute total elapsed time for running the code.
###############################################################################################################
start = dt.now()

###############################################################################################################
# ROI preparation
###############################################################################################################
# Select one random image from the user defined directory
thePath = input('Enter the path where the PhenoCam images are stored: ')

# Random selection of one image from the user defined directory
roiImg = thePath + '\\' + random.choice(os.listdir(thePath))

# Extract image name, station name, year
imName = os.path.basename(roiImg)
stnName = imName.split('_')[0]
yyyy = int(imName.split('_')[1][0:4])

# Display image on which you want to draw a region of interest
im = cv2.imread(roiImg)
plt.rcParams['figure.figsize'] = (16,8)

# Display the image
fig = plt.figure()
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
plt.title("Left click: Line segment     Right click: Complete ROI", fontsize = 20)
plt.show(block=False)

# Draw a polygon within the displayed image by clicking with the left mouse button to select the 
# vertices of the polygon. To close the polygon, click with the right mouse button.
user_roi = RoiPoly(color='r', fig = fig) 

print('\n')
print('User input for region of interest (ROI) is completed.')

###############################################################################################################
# Get ROI coordinates and round off to nearest 10 and use this to extract DN values per channel
###############################################################################################################
# Get the ROI coordinates [(x1, y1), (x2, y2), …]
roi_coordinates = user_roi.get_roi_coordinates()

# Empty list to store ROI Coordinates
roiList = []

# Iterate through the list of ROI coordinates and round off to nearest 10s
for tuples in roi_coordinates:
    tempList = [int(round(x, -1)) for x in tuples]
    
    # Append the tempList values to roiList
    roiList.append(tempList)

###############################################################################################################
# Automatically creating folders in the current working directory to save results 
###############################################################################################################
# Try-except block is to pass overwrite directories if exists
folders = ['Graph','CSV']
for folder in folders:
    try:
        os.mkdir(os.path.join(thePath, folder))
    except:
        pass

print('\n')
print('Created new folders to store the vegetation metrics and plots.')

###############################################################################################################
# Export ROI Map within the newly created 'Graph' folder        
###############################################################################################################   
# ROI definition for the image
pts1 = np.array(roiList) 
cv2.polylines(im, np.int32([pts1]), 1, (0, 0, 255), 5)
    
# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))

# Saving the user drawn ROI as a map in the current working directory
plt.savefig(os.path.join(thePath + r'\Graph\ROI_Map.png'), dpi = 300)

print('\n')
print('Exported user defined ROI as a ROI map in the newly created folder (i.e. Graphs).')

###############################################################################################################
# Empty lists to store the corresponding vegetation indices value
###############################################################################################################

GCC = []
RCC = []
DOY = []

# Empty dictionary to store DOY, GCC as key, value pairs
GCCdict1day = {}
RCCdict1day = {}
Reddict1day = {}
Grndict1day = {}
Bludict1day = {}
SolarAngles = {}
SElevnClass = {}
SnowdictTag = {}

###############################################################################################################
# Create a text file to save the vegetation metrics extracted from the time lapse images 
###############################################################################################################      
pathVI = os.path.join(thePath + r'\CSV\VI_allImage.txt')

# Headers definition
heading = "Image DOY Red_ROI1 Green_ROI1 Blue_ROI1 GCC_ROI1 RCC_ROI1 Snow"

# Open a file for storing image metrics
f1 = open(pathVI, 'w')

# Append header to the text file
f1.write(heading + "\n")

###############################################################################################################
# Vegetation indices calculation within user defined ROI for all valid images
###############################################################################################################
# Create a mask with 0 as background having same size like that of original image
mask = np.zeros_like(im)
    
# Fill the polygon with white colour where we want to apply the mask
cv2.fillPoly(mask, np.int32([pts1]), (255,255,255))

print('\n')
print('Reading images and computing the time series of GCC and RCC......................')

# Iterating through the images
for img in sorted(glob.glob(os.path.join(thePath, '*.jpg'))):
   
    # Reading image
    cv_img = cv2.imread(img)
    
    # Extracting image file name
    imgName = os.path.basename(img)
    
    # Splitting image name to different components
    splitted = imgName.split('_')
       
    # Image acquisition date (month, day and day of year)
    mm = int(splitted[1][4:6])
    dd = int(splitted[1][6:])
    doy = splitted[2]
    
    # Append doy to DOY empty list
    DOY.append(doy)
    
    # Apply the mask and extract the image data within mask only
    masked = cv2.bitwise_and(cv_img, mask)
    
    # Splitting RGB image into separate channels
    B, G, R = cv2.split(masked)

    # Finding out the mean DN of RGB bands within ROI 
    Rm = np.mean(np.ma.masked_equal(R, 0))
    Gm = np.mean(np.ma.masked_equal(G, 0))
    Bm = np.mean(np.ma.masked_equal(B, 0))

    # Total mean DN of ROI 
    TotalDN_ROI = Rm + Gm + Bm

    # Evaluation of visible band based vegetation indices
    # Green Chromatic Coordinate (GCC)
    g = round((Gm/(TotalDN_ROI)), 5)
    
    # Red Chromatic Coordinate
    r = round((Rm/(TotalDN_ROI)), 5)    
    
    # Snow tag
    snow = 200 # Absence of snow
    
    # Appending GCC values
    GCC.append(g)
    RCC.append(r)
    
    # Time series of vegetation indices saved as a text file
    f1.write('{} {} {} {} {} {} {} {}\n'.format(imgName, doy, Rm, Gm, Bm, g, r, snow))
    
    # Update dictionary with DOY and its associated GCC and RCC values
    if doy in GCCdict1day:
        GCCdict1day[doy].append(g)
        RCCdict1day[doy].append(r)
        Reddict1day[doy].append(Rm)
        Grndict1day[doy].append(Gm)
        Bludict1day[doy].append(Bm)
        SnowdictTag[doy].append(snow)
        
    else:
        GCCdict1day[doy] = [g]
        RCCdict1day[doy] = [r]
        Reddict1day[doy] = [Rm]
        Grndict1day[doy] = [Gm]
        Bludict1day[doy] = [Bm]
        SnowdictTag[doy] = [snow]
    
###############################################################################################################
# Script handles the computation of snow covered PhenoCam images separately.
# The script runs without any problem if there are no any snow covered images
###############################################################################################################     
# Empty list to store snow covered image GCC and its respective DOY
doySnow = []
gccSnow = []
rccSnow = []
solSnow = []

# Folder path definition for snow covered images        
snowImg = thePath + r'\SnowyImage'

# Iterating through snow covered images
for img in sorted(glob.glob(os.path.join(snowImg, '*.jpg'))):
    
    # Reading image
    cv_img = cv2.imread(img)
    
    # Extracting image file name
    imgName = os.path.basename(img)
    
    # Splitting image name to different components
    splitted = imgName.split('_')
       
    # Image acquisition date (month, day and day of year)
    mm = int(splitted[1][4:6])
    dd = int(splitted[1][6:])
    doy = splitted[2]
    
    # Append doy to DOY empty list
    DOY.append(doy)
        
    # Apply the mask and extract the image data within mask only
    masked = cv2.bitwise_and(cv_img, mask)
    
    # Splitting RGB image into separate channels
    B, G, R = cv2.split(masked)

    # Finding out mean DN of RGB bands within ROI 
    Rm = np.mean(np.ma.masked_equal(R, 0))
    Gm = np.mean(np.ma.masked_equal(G, 0))
    Bm = np.mean(np.ma.masked_equal(B, 0))

    # Total mean DN of ROI 
    TotalDN_ROI = Rm + Gm + Bm

    # Evaluation of visible band based vegetation indices
    # Green Chromatic Coordinate (GCC)
    g = round((Gm/(TotalDN_ROI)), 5)
    
    # Red Chromatic Coordinate
    r = round((Rm/(TotalDN_ROI)), 5)
    
    # Snow tag
    snow = 100 # Presence of snow
    
    # Appending values
    doySnow.append(doy)
    gccSnow.append(g)
    rccSnow.append(r)
       
    # Appending GCC and RCC values for the snowy images
    GCC.append(g)
    RCC.append(r)
    
    # Time series of vegetation indices saved as a text file
    f1.write('{} {} {} {} {} {} {} {}\n'.format(imgName, doy, Rm, Gm, Bm, g, r, snow))
    
    # Update dictionary with DOY and its associated GCC and RCC values
    if doy in GCCdict1day:
        GCCdict1day[doy].append(g)
        RCCdict1day[doy].append(r)
        Reddict1day[doy].append(Rm)
        Grndict1day[doy].append(Gm)
        Bludict1day[doy].append(Bm)
        SnowdictTag[doy].append(snow)
        
    else:
        GCCdict1day[doy] = [g]
        RCCdict1day[doy] = [r]
        Reddict1day[doy] = [Rm]
        Grndict1day[doy] = [Gm]
        Bludict1day[doy] = [Bm]
        SnowdictTag[doy] = [snow]        

#Close the file when done 
f1.close()        

print('\n')
print('Time series of GCC and RCC computation completed.')

###############################################################################################################
# Export .txt file as .csv file with all the information   
###############################################################################################################
# Read the .txt file as a dataframe 
df = pd.read_table(pathVI, delim_whitespace = True)

# Sort the dataframe in ascending order of DOY
sortedDF = df.sort_values('Image')

# Export the dataframe as a .csv file
fileName = os.path.join(thePath + r'\CSV\{}_{}_allImages.csv'.format(stnName, yyyy))
sortedDF.to_csv(fileName, index=False)

print('\n')
print('Exported time series data to {} file in original timestamp.'.format(os.path.basename(fileName)))

###############################################################################################################
# Finding daily mean VI values for a given DOY
###############################################################################################################   
# Dictionaries to store daily mean VIs (Excluding NAN values for a DOY)
avgGCC = {}
avgRCC = {}
avgR = {}
avgG = {}
avgB = {}
sTag = {}
stdGCC = {}
stdRCC = {}
nbrImgAvg = {}

# Path definition to create new text file for storing daily averaged indices values
path_avgGCC = os.path.join(thePath + r'\CSV\avgGCC1Day.txt')

# Header definition
header1 = "TIMESTAMP DOY RED_ROI_1 GREEN_ROI_1 BLUE_ROI_1 GCC_ROI_1 GCC_STD_1 RCC_ROI_1 RCC_STD_1 NO._IMG_AVG"

'''
###############################################################################################################
Variables description
TIMESTAMP       : Date in [YYYY-MM-DD]
DOY             : Day of the Year (dimensionless), Sequential day number starting with day 1 on January 1st
RED_ROI_1       : Daily averaged value of Red Channel for ROI number '1' (dimensionless)
GREEN_ROI_1     : Daily averaged value of Green Channel for ROI number '1' (dimensionless)
BLUE_ROI_1      : Daily averaged value of Blue Channel for ROI number '1' (dimensionless)
GCC_ROI_1       : Daily averaged Green Chromatic Coordinate (GCC) for ROI number '1' (dimensionless)
GCC_STD_1       : Standard deviation of the corresponding daily averaged GCC (dimensionless)
RCC_ROI_1       : Daily averaged Red Chromatic Coordinate (RCC) for ROI number '1' (dimensionless)
RCC_STD_1       : Standard deviation of the corresponding daily averaged RCC (dimensionless)
NO._IMG_AVG     : Number of images used to compute the daily average (dimensionless)

###############################################################################################################    
'''
# Open a file for writing the corresponding DOY and VIs
f4 = open(path_avgGCC, 'w')

# Append header to the text file
f4.write(header1 + "\n")

print('\n')
print('Computing daily average of GCC and RCC.....................................')

# Iterating over all dictionary keys, value pairs and average the items
for (k, v), (k1, v1), (k2, v2), (k3, v3), (k4, v4), (k5, v5) in zip(sorted(GCCdict1day.items()), \
    sorted(RCCdict1day.items()), sorted(Reddict1day.items()), sorted(Grndict1day.items()), \
    sorted(Bludict1day.items()), sorted(SnowdictTag.items())):
    
    # Updating the dictionary with computed metrics
    avgGCC[k] = round(sum(v)/len(v), 5)
    stdGCC[k] = round(statistics.pstdev(v), 5)
    nbrImgAvg[k] = len(v)
    avgRCC[k1] = round(sum(v1)/len(v1), 5)
    stdRCC[k1] = round(statistics.pstdev(v1), 5)
    avgR[k2] = round(sum(v2)/len(v2), 3)
    avgG[k3] = round(sum(v3)/len(v3), 3)
    avgB[k4] = round(sum(v4)/len(v4), 3) 
    sTag[k5] = int(s.mode(v5)[0])
                
    # Extracting timestamp information from day of year and year for the dataset
    yyyy_doy = str(yyyy) + '+' + k
    timeStamp = datetime.datetime.strptime(yyyy_doy, "%Y+%j").strftime('%Y-%m-%d')
    
    # Time series of daily average VIs saved as a text file in the given directory
    f4.write('{} {} {} {} {} {} {} {} {} {}\n'.format(timeStamp, k, avgR[k2], avgG[k3], \
    avgB[k4], avgGCC[k], stdGCC[k], avgRCC[k1], stdRCC[k1], nbrImgAvg[k]))

# Check if it is a leap year
if calendar.isleap(yyyy):
    nbrDays = 366
else:
    nbrDays = 365

print('\n')
print('Checking if there are any missing data for the year.......................')
print('All missing day of year (DOYs) will be filled with NaN.')
    
# Check if there are complete annual data. Write 'NaN' if there are any missing DOYs
if len(avgGCC) < nbrDays:
    
    # Find out the missing DOYs
    currentDOY = [int(j) for j in sorted(avgGCC.keys())]
    
    tempA = [x+1 for x in range(int(datetime.date.max.replace(year = yyyy).strftime('%j')))]
    currentDOY = set(currentDOY)
    missedDOY = list(currentDOY ^ set(tempA))

    # Update the dictionary with missed DOYs as NaN
    for mdoy in missedDOY:
        
        avgGCC[str(mdoy)]       = np.float64('nan')
        stdGCC[str(mdoy)]       = np.float64('nan')
        nbrImgAvg[str(mdoy)]    = np.float64('nan')
        avgRCC[str(mdoy)]       = np.float64('nan')
        stdRCC[str(mdoy)]       = np.float64('nan')
        avgR[str(mdoy)]         = np.float64('nan')
        avgG[str(mdoy)]         = np.float64('nan')
        avgB[str(mdoy)]         = np.float64('nan')
                
        # Extracting timestamp information from day of year and year for the dataset
        yyyy_doy = str(yyyy) + '+' + str(mdoy)
        timeStamp = datetime.datetime.strptime(yyyy_doy, "%Y+%j").strftime('%Y-%m-%d')
        
        # Time series of daily average VIs saved as a text file in the given directory
        f4.write('{} {} {} {} {} {} {} {} {} {}\n'.format(timeStamp, str(mdoy), avgR[str(mdoy)], \
        avgG[str(mdoy)], avgB[str(mdoy)], avgGCC[str(mdoy)], stdGCC[str(mdoy)], avgRCC[str(mdoy)], \
        stdRCC[str(mdoy)], nbrImgAvg[str(mdoy)]))

# Close file when everything is written
f4.close()

print('\n')
print('Daily average of GCC and RCC computation completed.')
       
###############################################################################################################
# Export .txt file as .csv file with all the information   
###############################################################################################################
# Read the .txt file as a dataframe 
df = pd.read_table(path_avgGCC, delim_whitespace=True)

# Export the dataframe as a .csv file
fileName = os.path.join(thePath + r'\CSV\{}_{}_L3_daily.csv'.format(stnName, yyyy))
pd.concat([df[:1], df.iloc[1:].sort_values(by = 'TIMESTAMP')], ignore_index = True, \
          axis = 0).to_csv(fileName, index=False, na_rep='NaN', date_format='%Y-%m-%d')

print('\n')
print('Exported the daily averaged GCC and RCC data to {} file.'.format(os.path.basename(fileName)))

###############################################################################################################
# Remove all .txt file in the directory   
###############################################################################################################
dir_name = os.path.join(thePath + r'\CSV')
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".txt"):
        os.remove(os.path.join(dir_name, item))

print('\n')
print('Plotting time series of GCC and RCC.........................................')

###############################################################################################################
# Time series of daily averaged vegetation indices plotted against corresponding DOY   
###############################################################################################################
# Plotting time series of GCC vegetation index
plt.figure(1)
plt.rcParams['figure.figsize'] = (16,8)
plt.ylim([0.3, 0.45]) 
plt.plot([int(i) for i in DOY], GCC, 'o', color = 'grey', markersize = 4, alpha = 0.1, 
         label = 'All image GCC')
plt.plot([int(i) for i in doySnow], gccSnow, 'o', color = 'cornflowerblue', markersize = 4, alpha = 0.5, 
         label = 'Snowy image GCC') 
plt.plot([int(j) for j in sorted(avgGCC.keys())], [avgGCC[x] for x in sorted(avgGCC.keys())], 
         'r^', markersize = 6, mfc = 'none', label = 'Daily Average')
plt.xticks(range(0, 365, 10), rotation = 45, fontsize = 16)
plt.yticks(fontsize = 16) 
plt.grid(True, alpha = 0.3)
plt.xlabel('Day of Year (DOY)', fontsize = 20)
plt.ylabel('Green Chromatic Coordinate (GCC)', fontsize = 20)
plt.legend(loc = 'upper left', fontsize = 18)
plt.savefig(os.path.join(thePath + r'\Graph\GCC_daily.jpg'))

# Plotting time series of RCC vegetation index
plt.figure(2)
plt.rcParams['figure.figsize'] = (16,8)
plt.ylim([0.3, 0.45]) 
plt.plot([int(i) for i in DOY], RCC, 'o', color = 'grey', markersize = 4, alpha = 0.1, 
         label = 'All image RCC')
plt.plot([int(i) for i in doySnow], rccSnow, 'o', color = 'cornflowerblue', markersize = 4, alpha = 0.5, 
         label = 'Snowy image RCC')
plt.plot([int(j) for j in sorted(avgRCC.keys())], [avgRCC[x] for x in sorted(avgRCC.keys())], 
         'ro', markersize = 6, mfc = 'none', label = 'Daily Average')
plt.xticks(range(0, 365, 10), rotation = 45, fontsize = 16)
plt.yticks(fontsize = 16) 
plt.grid(True, alpha = 0.3)
plt.xlabel('Day of Year (DOY)', fontsize = 20)
plt.ylabel('Red Chromatic Coordinate (RCC)', fontsize = 20)
plt.legend(loc = 'upper left', fontsize = 18)
plt.savefig(os.path.join(thePath + r'\Graph\RCC_daily.jpg'))

print('\n')
print('Exported GCC and RCC time series data plots to (Graphs) folder in the image directory.')

print('\n')
print('Successfully completed processing the images.')
print('Check the image directory to see the derived products.')

###############################################################################################################
# Total elapsed time 
###############################################################################################################
end = dt.now()
time_taken = end - start

# Print out the total elapsed time
print ('\n')
print ('Total time elapsed: {}'.format(time_taken))
print ('\n') 

###############################################################################################################
###############################################################################################################
