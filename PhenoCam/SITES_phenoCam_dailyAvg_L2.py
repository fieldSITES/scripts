"""
***************************************************************************************************************
######################################
Third step in PhenoCam data processing

Level 2 (L2) data creation
Created on Sat Aug 1 13:12:23 2020
######################################

This python script computes daily average from quality filtered phenoCam images (L1) and store it to a user 
defined path. The daily average images are saved to folders defined by the L2 product names. For example:
    
    a) Daily averaged RGB: SITES_P01-RGB_RBD_RBD_20220613-20220925_L2_daily
    b) Daily averaged GCC: SITES_P01-GCC_RBD_RBD_20220613-20220925_L2_daily
    c) Daily averaged RCC: SITES_P01-RCC_RBD_RBD_20220613-20220925_L2_daily
    
The daily averaed L2 image products are RGB, GCC, and RCC and they are exported as a grayscale image in the 
corresponding folders as shown in the example above.  

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for 
      internal use within Swedish Infrastructure for Ecosystem Science (SITES).
      
      GCC and RCC images are exported as 8 bit images. So in order to get pixel values in physical range 
      of GCC-RCC, scale factor of 1/255 should be used. Some precision is lost while exporting as 8 bit 
      images but they are not significant.

Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Images should be in .jpg format.
    c) Make sure the L1 images are as per the SITES naming convention
    d) Run the script and provide path to folder where L1 images are stored.
    e) Daily average of RGB, GCC, and RCC are computed and stored within the same file path.
    
Limitations of the script:
    a) Script can only take .jpg images as input.
    b) Script is programmed to process only one year data at a time..
    c) Script doesn't account for the change in camera field of view (FOV).
    d) Script doesn't take into account the different image sizes if there are any.
    
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se

@author: Shangharsha

***************************************************************************************************************
"""
###############################################################################################################
# Moduel Declaration
###############################################################################################################
import os
import cv2
import glob
import shutil
import numpy as np
from datetime import datetime
from PIL import Image

###############################################################################################################

###############################################################################################################
# Get time now. This helps to compute total elapsed time for running the code.
###############################################################################################################
start = datetime.now()

# Empty list to store the DOY information
doy = []

# Ask from user to enter file path of L1 datasets
imgSrc = input("Enter file path to the folder containing L1 data: ")

# Get the first and last image from the file path
imgList = sorted(glob.glob(os.path.join(imgSrc, '*.jpg')))
img1st = os.path.basename(imgList[0]).split('_')[1]
imglst = os.path.basename(imgList[-1]).split('_')[1]

# Get station and phenoCam information
tempImg = os.path.basename(imgList[0]).split('-')
phenCam = tempImg[-1].split('_')[0]
stn = tempImg[1] + '_' + tempImg[2] + '_'

# Naming convention of folders storing L2 daily data
dgcc = 'SITES_' + phenCam + '-GCC_' + stn + img1st + '-' + imglst + '_L2_daily'
drcc = 'SITES_' + phenCam + '-RCC_' + stn + img1st + '-' + imglst + '_L2_daily'
drgb = 'SITES_' + phenCam + '-RGB_' + stn + img1st + '-' + imglst + '_L2_daily'

###############################################################################################################
# Automatically creating folders in the directory to save results into
###############################################################################################################

# Try-except block is to pass overwrite directories if exists
folders = ['Temp', drgb, dgcc, drcc]
for folder in folders:
    try:
        os.mkdir(os.path.join(imgSrc, folder))
    except:
        pass

# Path definition for intermediate file storage    
baseDst = imgSrc + '\Temp'

###############################################################################################################
###############################################################################################################

# 1st Part
# Automatically copy all images and store them in a folder named after DOY  
# Iterating all images
for img in sorted(glob.glob(os.path.join(imgSrc, '*.jpg'))):
    
    # Extracting image file name
    imgName = os.path.basename(img)
    
    # Day of Year information (DOY) extraction from image file name
    dayOfYear = int(imgName.split('_')[2])
    
    # Check if current DOY is in the list
    if dayOfYear not in doy:
        
        # Append the day of year in empty list DOY
        doy.append(dayOfYear)
        
        # Make a new folder in the given path with the 'doy' as folder name
        thePath = baseDst
        folders = [str(dayOfYear)]
        
        # Iterating the folders list to create each DOY as a new folder in given path
        for folder in folders:
            # Try-except block is to pass overwrite directories if exists
            try:
                os.mkdir(os.path.join(thePath, folder))
            except:
                pass
        
        # Copy the image from the source to destination folder
        imgDst = baseDst + '\\' + folders[0]
    
    # If DOY exists in the doy list, copy the source image to the same folder
    shutil.copy(img, imgDst)
    
print ('\n')  
print ('Finished copying images to respective DOY folders.')
   
###############################################################################################################
###############################################################################################################

print ('\n')
print ('Computing daily average images................................................')

# 2nd part
# Compute daily average from all available images for each DOY and export it as a .jpg file

# Path definition to save the daily averaged image 
imgSave = imgSrc + '\{}'.format(drgb)

for subdir in os.listdir(baseDst): 
    
    imgDir = baseDst + '\\' + subdir

    # Read all files in a directory as a numpy array
    # cv2.cvtColor for converting image from BGR to RGB
    images = [cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB) for file in glob.glob(os.path.join(imgDir, '*.jpg'))]
    
    # Compute element wise daily average
    avgImg = np.mean(images, axis = 0)
    
    # Converting float64 type ndarray to uint8
    intImage = np.around(avgImg).astype(np.uint8) # Round first and then convert to integer
    
    # Saving the daily average as image
    im = Image.fromarray(intImage)
    
    # Define path for saving image with given file name 
    saveDst = imgSave + '\\' + "_".join(os.listdir(imgDir)[0].split("_")[:3]) + '_RGB_L2_daily.jpg'
    
    # Save image in the defined path
    im.save(saveDst)
    
print ('\n')
print ('Daily averaged RGB images are computed and stored successfully.')

###############################################################################################################
###############################################################################################################
    
# 3rd part
# Delete pre-created DOY folders and files after finishing the processing  
shutil.rmtree(baseDst)

print ('\n')
print ('Computing daily GCC and RCC images...')

###############################################################################################################
###############################################################################################################

# 4th part
# Code to generate daily GCC and RCC as an image

# Save daily GCC and RCC image
gccSave = imgSrc + '\{}'.format(dgcc)
rccSave = imgSrc + '\{}'.format(drcc)

# Iterating all daily average images to compute GCC and RCC on a pixel by pixel basis
for img in sorted(glob.glob(os.path.join(imgSave, '*.jpg'))):
    
    # Extracting image file name
    imgName = os.path.basename(img)

    # Reading image one by one
    cv_img = cv2.imread(img)
    
    # Extracting RGB bands as a separate numpy array
    B = cv_img[:,:,0]
    G = cv_img[:,:,1]
    R = cv_img[:,:,2]
      
    # Element wise addition of BGR array to calculate Total DN values in RGB band (i.e. R+G+B) 
    DNtotal = cv_img.sum(axis = 2)
    
    # Compute pixel wise GCC and RCC from daily average images
    gcc = np.divide(G, DNtotal)
    rcc = np.divide(R, DNtotal)
    
    # Convert NAN to zero
    arr1 = np.nan_to_num(gcc, copy=False)
    arr2 = np.nan_to_num(rcc, copy=False)
    
    # Converting GCC and RCC to smoothly range from 0 - 255 as 'uint8' data type from 'float64'
    intImage1 = (arr1 * 255).astype(np.uint8) 
    intImage2 = (arr2 * 255).astype(np.uint8)
    
    # Define path for saving image with given file name 
    saveGCC = gccSave + '\\' + imgName.replace('RGB','GCC')
    saveRCC = rccSave + '\\' + imgName.replace('RGB','RCC')
    
    # Save in the defined path as a grayscale image
    cv2.imwrite(saveGCC, intImage1)  
    cv2.imwrite(saveRCC, intImage2)
        
print ('\n')
print ('Daily averaged GCC and RCC images are computed and stored successfully.')
print ('Check the image directory to see the derived products.')
    
###############################################################################################################
# Display total elapsed time
###############################################################################################################

end = datetime.now()
time_taken = end - start

print ('\n')
print ('Time elapsed: {}'.format(time_taken)) 

###############################################################################################################
###############################################################################################################
   