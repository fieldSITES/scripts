"""
***************************************************************************************************************
######################################
Final step in PhenoCam data processing

Level 3 (L3) data creation
Created on Fri Feb 21 21:34:13 2020
######################################

This python script uses the predefined regions of interest (ROIs) for generating time series of daily averaged
Green Chromatic Coordinate (GCC) and Red Chromatic Coordinate (RCC) for defined ROIs from the quality filtered 
L1 phenoCam images. 
The script exports the time series of GCC and RCC as .csv file in the same file path as the original pictures. 
The .csv file can be found within a folder 'CSV' and contains all time series metrics. Furthermore, the plots 
of daily averaged GCC and RCC are exported as a .png file within a folder called 'Graph'. The user defined ROI 
will be exported as a ROI map in the same directory.

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only 
      for internal use within Swedish Infrastructure for Ecosystem Science (SITES).

Package installations:
    1) astral   : pip install astral 
    2) Open-CV  : pip install opencv-python
    3) numpy    : pip install numpy
    4) pandas   : pip install pandas

Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Input images should be L1 and in .jpg format.
    c) Make sure the images are as per the SITES naming convention
    
       For example: SWE-LON-SFA-P01_20220101_001_1020.jpg
       General: Country-Station-Location-PhenoCam_YYMMDD_DOY_HHMM
       
    d) Make sure the images are of same dimensions (For eg: 3072*2048)
    e) Create a new folder named 'SnowyImage' within the image directory and move all snowy 
       images to it. In case of no snowy images in the year, skip this step.
    f) Define correct ROI coordinate for the chosen phenoCam location and station.                
    h) Change ROI number in the headings of the time series data if there are ROI more than one.

Limitations of the script:
    a) Script can only take .jpg images as input.
    b) Script is programmed to handle only one ROI at a time.
    c) Script doesn't account for the change in camera field of view
    c) Script is programmed to process only one year data at a time.

Example Data:
    # Freely downloadable from SITES data portal under SITES Spectral thematic program.
    One example data:  https://meta.fieldsites.se/objects/Y156yelfNlRX21Ny8XWERQnY
    Find more data in the SITES data portal: https://data.fieldsites.se/portal/

Important information:    
    a) Solar elevation angle computation is based on:
       https://forum.developer.parrot.com/t/suns-elevation-and-azimuth-calculation/5573
       
    b) SITES Spectral – Data Quality Flagging (QFLAG) Documentation
       https://hdl.handle.net/11676.1/yHjlJ9dsmPzMNAGPswfSlEtC

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se

@author: Shangharsha

***************************************************************************************************************
"""
################################################################################################################
# Module Declaration
################################################################################################################
import os
import cv2
import glob
import pytz
import random
import calendar
import datetime
import statistics
import numpy as np
import pandas as pd
from pytz import timezone
from astral import Astral
from scipy import stats as s
import matplotlib.pyplot as plt

# Time zone definition
timezone_name = 'Europe/Stockholm'

# Geolocation definition for each phenoCam location
#lat, lon = (68.353729, 18.816522)  # Abisko
#lat, lon = (57.149750, 14.738164) # Asa
#lat, lon = (64.182032, 19.556545) # Degerö
#lat, lon = (64.256110, 19.774500) # SVB-Forest
#lat, lon = (63.806340, 20.232638) # SWE-RBD-RBD-AGR-P01
#lat, lon = (63.809446, 20.241503)  # SWE-RBD-RBD-AGR-P02
#lat, lon = (55.668106, 13.108658) # Lönnstorp-P03, P02, P01
lat, lon = (68.041889, 18.959309) # Tarfala-P01
#lat, lon = (58.363846, 12.149787) # Skogaryd-CEM-P01
#lat, lon = (58.363718, 12.149494) # Skogaryd-CEM-P02
#lat, lon = (58.363555, 12.149921) # Skogaryd-CEM-P03
#lat, lon = (58.381368, 12.146208) # Skogaryd-STD-P01
#lat, lon = (59.72868, 15.47249)   # Grimsö
 
################################################################################################################
# Empty lists and dictionaries to store the corresponding vegetation indices value
################################################################################################################
GCC = []
RCC = []
SOL = []
DOY = []

# Define file path of L1 quality filtered images
thePath = input('Enter the path where L1 phenoCam images are stored: ')

# Empty dictionary to store DOY and GCC as Key, value pair 
GCCdict1day = {}
RCCdict1day = {}
Reddict1day = {}
Grndict1day = {}
Bludict1day = {}
SolarAngles = {}
SElevnClass = {}
SnowdictTag = {}

################################################################################################################
# Display Region of Interest (ROI) selection in the image  
################################################################################################################

# Random selection of one image from the image folder to show the extent of ROI
imgDir = thePath + '\\' + random.choice(os.listdir(thePath))

# Extract image name, station name, year
imName = os.path.basename(imgDir)
stnName = imName.split('_')[0]
yyyy = int(imName.split('_')[1][0:4])

# Reading randomly selected image 
img = cv2.imread(imgDir)

# Define right ROI for the phenoCam data being processed.
# ROI used in SITES are available in a python script i.e. SITES_phenoCamROI.py 
pts1 = np.array([[200, 1750], [200, 550], [2900, 550], [2900, 1750]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

################################################################################################################
# Overlay defined ROI on top of image to give visual representation of ROI 
################################################################################################################

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

################################################################################################################
# Automatically creating folders in the directory to save results
################################################################################################################

# Try-except block is to pass overwrite directories if exists
folders = ['Graph','CSV']
for folder in folders:
    try:
        os.mkdir(os.path.join(thePath, folder))
    except:
        pass

################################################################################################################
# Text file to store the mean image metrics
################################################################################################################       
# Define path for the text file
pathVI = os.path.join(thePath + r'\CSV\VI_allImage.txt')

# Header defintion
heading = "Image DOY Red_ROI1 Green_ROI1 Blue_ROI1 GCC_ROI1 RCC_ROI1 Snow Solar_Angle Solar_Angle_Class"

# Open a file for writing the image name, corresponding DOY and vegetation indices
f1 = open(pathVI, 'w')

# Append header to the text file
f1.write(heading + "\n")

################################################################################################################
# Vegetation indices calculation for all available images for defined ROI
################################################################################################################

# Create a mask with 0 as background having same size like original image
mask = np.zeros_like(img)
    
# Fill the polygon with white colour in the area where the mask will be applied
cv2.fillPoly(mask, np.int32([pts1]), (255,255,255))

# Iterating all images
for img in sorted(glob.glob(os.path.join(thePath, '*.jpg'))):
   
    # Reading image
    cv_img = cv2.imread(img)
    
    # Image file name
    imgName = os.path.basename(img)
    
    # Splitting the image name to extract date and time information
    splitted = imgName.split('_')
       
    # Date when the image was acquired
    mm = int(splitted[1][4:6])
    dd = int(splitted[1][6:])
    doy = splitted[2]
    
    # Day of Year information (DOY) extraction from image file name
    DOY.append(doy)
    
    # Extract time
    time = splitted[-1].split('.')[0]
    hh = int(time[:2])
    mint = int(time[2:4])

    # Returns sun elevation for a given position (lat, long) at a given date and time    
    dt = datetime.datetime(yyyy, mm, dd, hh, mint, 0)
    utc_dt = pytz.timezone('UTC').localize(dt)
    info_timezone = timezone(timezone_name)
    info_dt = utc_dt.astimezone(info_timezone)
    
    astral = Astral()
    sun_elevation = round(astral.solar_elevation(info_dt, lat, lon), 2)
    
    # Categorize the solar angles into 3 classes based on their values
    # Read more about this here: SITES Spectral – Data Quality Flagging (QFLAG) Documentation
    if sun_elevation < 20:
        solClass = 1
    elif 20 <= sun_elevation <= 30:
        solClass = 2
    else:
        solClass = 3
    
    # Apply the mask and extract the image data within mask only
    masked = cv2.bitwise_and(cv_img, mask)
    
    # Splitting RGB image into separate bands
    B, G, R = cv2.split(masked)

    # Finding out the mean DN of RGB bands within ROI 
    Rm = np.mean(np.ma.masked_equal(R, 0))
    Gm = np.mean(np.ma.masked_equal(G, 0))
    Bm = np.mean(np.ma.masked_equal(B, 0))

    # Total mean DN of ROI 
    TotalDN_ROI = Rm + Gm + Bm

    # Evaluation of visible band based vegetation indices
    # Green Chromatic Coordinate 
    g = round((Gm/(TotalDN_ROI)), 5)
    
    # Red chromatic Coordinate
    r = round((Rm/(TotalDN_ROI)), 5)    
    
    snow = 2 # Absence of snow
    
    # Appending GCC values for the images to the empty list created before
    GCC.append(g)
    RCC.append(r)
    SOL.append(sun_elevation)
    
    # Writing computed time series metrics for defined ROIs to the text file created earlier
    f1.write('{} {} {} {} {} {} {} {} {} {}\n'.format(imgName, doy, Rm, Gm, Bm, g, r, snow, sun_elevation, solClass))
    
    # Update dictionary with corresponding key value pairs
    if doy in GCCdict1day:
        GCCdict1day[doy].append(g)
        RCCdict1day[doy].append(r)
        Reddict1day[doy].append(Rm)
        Grndict1day[doy].append(Gm)
        Bludict1day[doy].append(Bm)
        SolarAngles[doy].append(sun_elevation)
        SElevnClass[doy].append(solClass)
        SnowdictTag[doy].append(snow)
        
    else:
        GCCdict1day[doy] = [g]
        RCCdict1day[doy] = [r]
        Reddict1day[doy] = [Rm]
        Grndict1day[doy] = [Gm]
        Bludict1day[doy] = [Bm]
        SolarAngles[doy] = [sun_elevation]
        SElevnClass[doy] = [solClass]
        SnowdictTag[doy] = [snow]
    
################################################################################################################
# Lines of code to take into account the snow covered images stored in 'SnowyImage' folder.
# Script works if there is no 'SnowyImage' folder in the directory        
################################################################################################################       

# Empty list to store similar VIs for snow covered image and its respective DOY
doySnow = []
gccSnow = []
rccSnow = []
solSnow = []

# Define file path of snow covered images        
snowImg = thePath + '\SnowyImage'

# Iterating through snow covered images
for img in sorted(glob.glob(os.path.join(snowImg, '*.jpg'))):
    
    # Reading image
    cv_img = cv2.imread(img)
    
    # Extracting image file name
    imgName = os.path.basename(img)
    
    # Splitting the image name to extract date and time information
    splitted = imgName.split('_')
       
    # Date when the image was acquired
    mm = int(splitted[1][4:6])
    dd = int(splitted[1][6:])
    doy = splitted[2]
    
    # DOY extraction from image file name
    DOY.append(doy)
    
    # Extract time
    time = splitted[-1].split('.')[0]
    hh = int(time[:2])
    min = int(time[2:4])

    # Returns sun elevation for a given position (lat, long) at a given date and time    
    dt = datetime.datetime(yyyy, mm, dd, hh, min, 0)
    utc_dt = pytz.timezone('UTC').localize(dt)
    info_timezone = timezone(timezone_name)
    info_dt = utc_dt.astimezone(info_timezone)
    
    astral = Astral()
    sun_elevation = round(astral.solar_elevation(info_dt, lat, lon), 2)
    
    # Categorize the solar angles into 3 classes based on their values
    # Read more about this here: SITES Spectral – Data Quality Flagging (QFLAG) Documentation
    if sun_elevation < 20:
        solClass = 1
    elif 20 <= sun_elevation <= 30:
        solClass = 2
    else:
        solClass = 3
        
    # Apply the mask and extract the image data within mask only
    masked = cv2.bitwise_and(cv_img, mask)
    
    # Splitting RGB image into separate bands
    B, G, R = cv2.split(masked)

    # Finding out mean DN of RGB bands within ROI 
    Rm = np.mean(np.ma.masked_equal(R, 0))
    Gm = np.mean(np.ma.masked_equal(G, 0))
    Bm = np.mean(np.ma.masked_equal(B, 0))

    # Total mean DN of ROI 
    TotalDN_ROI = Rm + Gm + Bm

    # Evaluation of visible band based vegetation indices
    # Green Chromatic Coordinate
    g = round((Gm/(TotalDN_ROI)), 5)
    
    # Red chromatic Coordinate
    r = round((Rm/(TotalDN_ROI)), 5)
    
    snow = 1 # Presence of snow
    
    # Appending GCC values for the snow covered images to the empty list created before
    doySnow.append(doy)
    gccSnow.append(g)
    rccSnow.append(r)
    solSnow.append(sun_elevation)
       
    # Appending GCC and RCC values for the images
    GCC.append(g)
    RCC.append(r)
    SOL.append(sun_elevation)
    
    # Writing computed time series metrics for defined ROIs to the text file created earlier
    f1.write('{} {} {} {} {} {} {} {} {} {}\n'.format(imgName, doy, Rm, Gm, Bm, g, r, snow, sun_elevation, solClass))
    
    # Update dictionary with corresponding key value pairs
    if doy in GCCdict1day:
        GCCdict1day[doy].append(g)
        RCCdict1day[doy].append(r)
        Reddict1day[doy].append(Rm)
        Grndict1day[doy].append(Gm)
        Bludict1day[doy].append(Bm)
        SolarAngles[doy].append(sun_elevation)
        SElevnClass[doy].append(solClass)
        SnowdictTag[doy].append(snow)
        
    else:
        GCCdict1day[doy] = [g]
        RCCdict1day[doy] = [r]
        Reddict1day[doy] = [Rm]
        Grndict1day[doy] = [Gm]
        Bludict1day[doy] = [Bm]
        SolarAngles[doy] = [sun_elevation]
        SElevnClass[doy] = [solClass]
        SnowdictTag[doy] = [snow]        

# Close the file
f1.close()

################################################################################################################
# Export .txt file as .csv file with all the information   
################################################################################################################

# Read .txt file as a dataframe 
df = pd.read_table(pathVI, delim_whitespace = True)

# Sort the dataframe in increasing DOY order
sortedDF = df.sort_values('Image')

# Export the dataframe as a .csv file
fileName = os.path.join(thePath + r'\CSV\{}_{}_allImages.csv'.format(stnName, yyyy))
sortedDF.to_csv(fileName, index=False)

################################################################################################################
# Finding mean vegetation indices values from all valid images within a given DOY
################################################################################################################
        
# Dictionaries to store mean indices per day (Excluding no data values for a DOY)
avgGCC = {}
avgRCC = {}
avgR = {}
avgG = {}
avgB = {}
sTag = {}
solC = {}
sElv = {}
stdGCC = {}
stdRCC = {}
nbrImgAvg = {}
QFLAG = {}

# Define path for new text file to store the daily averaged time series metrics
path_avgGCC = os.path.join(thePath + r'\CSV\avgGCC1Day.txt')

# Multiple line header defintion
header1 = "TIMESTAMP DOY RED_ROI_1 GREEN_ROI_1 BLUE_ROI_1 GCC_ROI_1 GCC_STD_1 RCC_ROI_1 RCC_STD_1 NO._IMG_AVG AGL_SUN_MAX QFLAG_ROI_1"
header2 = "YYYY-MM-DD None DN DN DN Fraction None Fraction None Count Degree Class"

# Open a file for writing the corresponding DOY and vegetation indices
f4 = open(path_avgGCC, 'w')

# Append header to the text file
f4.write(header1 + "\n")
f4.write(header2 + "\n")

# Iterating over all dictionary key-value pairs and average the items
for (k, v), (k1, v1), (k2, v2), (k3, v3), (k4, v4), (k5, v5), (k6, v6), (k7, v7) in zip(sorted(GCCdict1day.items()), \
    sorted(RCCdict1day.items()), sorted(Reddict1day.items()), sorted(Grndict1day.items()), sorted(Bludict1day.items()), \
    sorted(SnowdictTag.items()), sorted(SElevnClass.items()), sorted(SolarAngles.items())):
    
    # v, v1, v2, etc is the lists of GCC & RCC values on that DOY
    avgGCC[k] = round(sum(v)/len(v), 5)
    stdGCC[k] = round(statistics.pstdev(v), 5)
    nbrImgAvg[k] = len(v)
    avgRCC[k1] = round(sum(v1)/len(v1), 5)
    stdRCC[k1] = round(statistics.pstdev(v1), 5)
    avgR[k2] = round(sum(v2)/len(v2), 3)
    avgG[k3] = round(sum(v3)/len(v3), 3)
    avgB[k4] = round(sum(v4)/len(v4), 3) 
    sTag[k5] = int(s.mode(v5)[0])
    solC[k6] = max(v6)
    sElv[k7] = max(v7)
    
    ############################################################################################################
    '''
    Defining quality flagging scheme for each DOY based on number of images for computing daily average, 
    presence or absence of snow and solar elevation angle
    '''
    ############################################################################################################
    
    if sTag[k5] == 1:
        QFLAG[k] = 100
    
    ############################################################################################################
    # Valid only for half hourly temporal resolution
    ############################################################################################################  
    elif (nbrImgAvg[k] < 3) and (solC[k6] == 1):
        QFLAG[k] = 211
        
    elif (nbrImgAvg[k] < 3) and (solC[k6] == 2):
        QFLAG[k] = 212
    
    elif (nbrImgAvg[k] < 3) and (solC[k6] == 3):
        QFLAG[k] = 213
    
    elif ((nbrImgAvg[k] >= 3) and (nbrImgAvg[k] < 6)) and (solC[k6] == 1):
        QFLAG[k] = 221
    
    elif ((nbrImgAvg[k] >= 3) and (nbrImgAvg[k] < 6)) and (solC[k6] == 2):
        QFLAG[k] = 222
        
    elif ((nbrImgAvg[k] >= 3) and (nbrImgAvg[k] < 6)) and (solC[k6] == 3):
        QFLAG[k] = 223
        
    elif (nbrImgAvg[k] >= 6) and (solC[k6] == 1):
        QFLAG[k] = 231
    
    elif (nbrImgAvg[k] >= 6) and (solC[k6] == 2):
        QFLAG[k] = 232     
    
    elif (nbrImgAvg[k] >= 6) and (solC[k6] == 3):
        QFLAG[k] = 233 
    
    '''
    ############################################################################################################
    # Valid only for hourly temporal resolution
    ############################################################################################################
    elif (nbrImgAvg[k] < 2) and (solC[k6] == 1):
        QFLAG[k] = 211
        
    elif (nbrImgAvg[k] < 2) and (solC[k6] == 2):
        QFLAG[k] = 212
    
    elif (nbrImgAvg[k] < 2) and (solC[k6] == 3):
        QFLAG[k] = 213
    
    elif ((nbrImgAvg[k] >= 2) and (nbrImgAvg[k] < 4)) and (solC[k6] == 1):
        QFLAG[k] = 221
    
    elif ((nbrImgAvg[k] >= 2) and (nbrImgAvg[k] < 4)) and (solC[k6] == 2):
        QFLAG[k] = 222
        
    elif ((nbrImgAvg[k] >= 2) and (nbrImgAvg[k] < 4)) and (solC[k6] == 3):
        QFLAG[k] = 223
        
    elif (nbrImgAvg[k] >= 4) and (solC[k6] == 1):
        QFLAG[k] = 231
    
    elif (nbrImgAvg[k] >= 4) and (solC[k6] == 2):
        QFLAG[k] = 232     
    
    elif (nbrImgAvg[k] >= 4) and (solC[k6] == 3):
        QFLAG[k] = 233     
        
    ############################################################################################################
    '''
    ############################################################################################################
    ############################################################################################################
        
    # Derive timestamp information from DOY and year
    yyyy_doy = str(yyyy) + '+' + k
    timeStamp = datetime.datetime.strptime(yyyy_doy, "%Y+%j").strftime('%Y-%m-%d')
    
    # Writing daily averaged time series metrics for defined ROIs to the text file created earlier
    f4.write('{} {} {} {} {} {} {} {} {} {} {} {}\n'.format(timeStamp, k, avgR[k2], avgG[k3], \
    avgB[k4], avgGCC[k], stdGCC[k], avgRCC[k1], stdRCC[k1], nbrImgAvg[k], sElv[k7], QFLAG[k]))

# Check if it is a leap year
if calendar.isleap(yyyy):
    nbrDays = 366
else:
    nbrDays = 365
    
# Check if there are complete annual data. 
# Write 'NaN' if there are any missing DOYs
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
        solC[str(mdoy)]         = np.float64('nan')
        sElv[str(mdoy)]         = np.float64('nan')
        
        # For all no data DOYs update QFLAG with 'NaN'
        QFLAG[str(mdoy)]        = np.float64('nan')
        
        # Derive timestamp information from DOY and year
        yyyy_doy = str(yyyy) + '+' + str(mdoy)
        timeStamp = datetime.datetime.strptime(yyyy_doy, "%Y+%j").strftime('%Y-%m-%d')
        
        # Writing daily averaged time series metrics for defined ROIs to the text file created earlier
        f4.write('{} {} {} {} {} {} {} {} {} {} {} {}\n'.format(timeStamp, str(mdoy), avgR[str(mdoy)], \
        avgG[str(mdoy)], avgB[str(mdoy)], avgGCC[str(mdoy)], stdGCC[str(mdoy)], avgRCC[str(mdoy)], \
        stdRCC[str(mdoy)], nbrImgAvg[str(mdoy)], sElv[str(mdoy)], QFLAG[str(mdoy)]))

# Close the file
f4.close()
       
################################################################################################################
# Export .txt file as .csv file with all the information   
################################################################################################################

# Read the .txt file as a dataframe 
df = pd.read_table(path_avgGCC, delim_whitespace=True)

# Export the dataframe as a .csv file
fileName = os.path.join(thePath + r'\CSV\{}_{}_L3_daily.csv'.format(stnName, yyyy))
pd.concat([df[:1], df.iloc[1:].sort_values(by = 'TIMESTAMP')], ignore_index = True, \
          axis = 0).to_csv(fileName, index=False, na_rep='NaN', date_format='%Y-%m-%d')

################################################################################################################
# Remove all .txt file in the directory   
################################################################################################################
dir_name = os.path.join(thePath + r'\CSV')
test = os.listdir(dir_name)

for item in test:
    if item.endswith(".txt"):
        os.remove(os.path.join(dir_name, item))

################################################################################################################
# Plotting time series of daily averaged vegetation indices   
################################################################################################################

# Plotting time series of GCC vegetation index
plt.figure(1)
plt.rcParams['figure.figsize'] = (16,8)
plt.ylim([0.3, 0.50 ]) 
plt.plot([int(i) for i in DOY], GCC, 'o', color = 'grey', markersize = 4, alpha = 0.1, label = 'All image GCC')
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
plt.savefig(os.path.join(thePath + r'\Graph\GCC_1Day.jpg'))

# Plotting time series of RCC vegetation index
plt.figure(2)
plt.rcParams['figure.figsize'] = (16,8)
#plt.ylim([0.31, 0.38 ]) 
plt.plot([int(i) for i in DOY], RCC, 'o', color = 'grey', markersize = 4, alpha = 0.1, label = 'All image RCC')
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
plt.savefig(os.path.join(thePath + r'\Graph\RCC_1Day.jpg'))

################################################################################################################
################################################################################################################
