"""
***************************************************************************************************************
#######################################
Second step in PhenoCam data processing

Level 1 (L1) data creation
Created on Fri Feb 21 16:07:04 2020
#######################################

This python script uses data after renaming, following the first step of PhenoCam data processing i.e. L0 raw 
data from SITES stations: Abisko, Asa, Lönnstorp, Röbäcksdalen, Skogaryd, Tarfala, Grimsö & Svartberget. The 
script uses the predefined time threshold for filtering out the PhenoCam images. Currently, the images between
10:00 - 14:00 throughout the year are filtered out and are used for further analysis. Time threshold can be 
modified as required.
 
After running the script, the time filtered images will be copied in a folder named after the year the data was
collected, in the same directory where the L0 raw data are stored. Copy and move the folder to where the L1
data for given stations are stored. Then, users are supposed to remove low quality pictures from the filtered
data. Low quality refers to images containing a lot of noises such as solar glare, disorientated, blurry, foggy, 
birds obstacle, very dark, and stripes.

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for 
      internal use within Swedish Infrastructure for Ecosystem Science (SITES).
      
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Images should be in .jpg format and in SITES L0 standard.
    
Limitations of the script:
    a) Script can only take .jpg images as input.
    b) Script filters out the image based on timestamp information available in image names.
    c) Low quality images are to be filtered out manually. 
    
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha

***************************************************************************************************************
"""
###############################################################################################################
# Module Declaration
###############################################################################################################
import os
import glob
import shutil
import random
from datetime import datetime

###############################################################################################################
# Get time now. This computes total elapsed time for running the code.
###############################################################################################################
start = datetime.now()

# Path definition for source images
imgSrc = input('Enter file path where L0 raw images are stored: ')

###############################################################################################################
# Automatic folder creation, path definition for copying and pasting images 
###############################################################################################################
# Read one random image from path where L0 images are stored
samImg = imgSrc + '\\' + random.choice(os.listdir(imgSrc))

# Extract the year the data was acquired
imgName = os.path.basename(samImg)
yyyy = imgName.split('_')[1][:4]

# Try-except block is to pass overwrite directories if exists
folders = [yyyy]
for folder in folders:
    try:
        os.mkdir(os.path.join(imgSrc, folder))
    except:
        pass

# Path definition for saving filtered images 
dest = imgSrc + '\\{}'.format(yyyy)

###############################################################################################################
# Filter out phenoCam images within user defined time frame
# Modify the time filter if needed
###############################################################################################################
print ('\n')
print ('Filtering out images acquired between 10:00 - 14:00..................')
print ('This might take between 5-10 minutes depending on the temporal resolution of the data.')

# Iterating all images and copying it to a new folder
for img in sorted(glob.glob(os.path.join(imgSrc, '*.jpg'))):
    
    # Extracting image file name
    dt_info = os.path.basename(img)
     
    # Day of Year information (DOY) extraction from image file name
    ymdt = dt_info.split('_')[-1]
    
    # TimeStamp information extraction from file name
    hour = int(ymdt.split('.')[0][:2])

    # Condition to check the time of image acquisition for a given image
    if (hour >= 10) and (hour <= 14):
        
        # Copy the images to destination folder
        shutil.copy(img, dest)
       
###############################################################################################################
# Find out the total elapsed time and print out on the screen
###############################################################################################################

end = datetime.now()
time_taken = end - start

print ('\n')
print ('Time elapsed: {}'.format(time_taken)) 
print ('Images between user defined time thresholds are filtered successfully.')
print ('Remove all low quality images before uploading it to the data portal.')

###############################################################################################################
###############################################################################################################
