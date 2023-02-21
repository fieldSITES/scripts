"""
***************************************************************************************************************
######################################
Third step in PhenoCam data processing

Level 2 (L2) data creation
Created on Sat Aug 1 13:12:23 2020
######################################

This python script computes daily average from quality filtered phenoCam images (L1) and store it to a user 
defined path (i.e. average images are exported to .jpg image in a folder called 'RGB'. Furthermore, it also 
computes daily GCC, RCC average as a grayscale image in a folder called 'GCC' and 'RCC' respectively. 
Folders are created in the source image directory assigned by the user. 

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for 
      internal use within Swedish Infrastructure for Ecosystem Science (SITES).
      
      GCC and RCC images are exported as 8 bit images. So in order to get pixel values in physical range 
      of GCC-RCC, scale factor of 1/255 should be used.

@author: Shangharsha


***************************************************************************************************************

"""
#################################################################################################
#Importing required modules
import glob
import os
import shutil
import cv2
import numpy as np
from datetime import datetime
from PIL import Image

#################################################################################################

#################################################################################################
#Get time now. This helps to compute total elapsed time for running the code.
#################################################################################################
start = datetime.now()

#Empty list to store the DOY information
doy = []

#Ask from user to enter file path of L1 datasets
imgSrc = input("Enter file path to the folder containing L1 data: ")

#################################################################################################
#Automatically creating folders in the directory to save results into
#################################################################################################

#Try-except block is to pass overwrite directories if exists
folders = ['Temp','RGB', 'GCC', 'RCC']
for folder in folders:
    try:
        os.mkdir(os.path.join(imgSrc, folder))
    except:
        pass

#Path definition for intermediate file storage    
baseDst = imgSrc + '\Temp'

#################################################################################################
#################################################################################################

#1st Part
#Line of codes to automatically copy all valid images and store them in a folder named after DOY  
#Iterating all images
for img in sorted(glob.glob(os.path.join(imgSrc, '*.jpg'))):
    
    #Extracting image file name
    imgName = os.path.basename(img)
    
    #Day of Year information (DOY) extraction from image file name
    dayOfYear = int(imgName.split('_')[2])
    
    #Check if current DOY is in the list
    if dayOfYear not in doy:
        
        #Append the day of year in empty list DOY
        doy.append(dayOfYear)
        
        #Make a new folder in the given path with the 'doy' as folder name
        thePath = baseDst
        folders = [str(dayOfYear)]
        
        #Iterating the folders list to create each DOY as a new folder in given path
        for folder in folders:
            #Try-except block is to pass overwrite directories if exists
            try:
                os.mkdir(os.path.join(thePath, folder))
            except:
                pass
        
        #Copy the image from the source to destination folder
        imgDst = baseDst + '\\' + folders[0]
        #shutil.copy(img, imgDst)
    
    #If DOY exists in the doy list, copy the source image to the same folder
    shutil.copy(img, imgDst)
    
print ('\n')  
print ('Finished copying images to respective DOY folders.')
   
#################################################################################################
#################################################################################################

print ('\n')
print ('Computing daily average images...')

#2nd part
#Line of codes to compute daily average from all valid images and save it as a .jpg file

#Save average image
imgSave = imgSrc + '\RGB'

for subdir in os.listdir(baseDst): 
    
    imgDir = baseDst + '\\' + subdir

    #Read all files in a directory as a numpy array
    #cv2.cvtColor for converting image from BGR to RGB
    images = [cv2.cvtColor(cv2.imread(file), cv2.COLOR_BGR2RGB) for file in glob.glob(os.path.join(imgDir, '*.jpg'))]
    
    #Compute element wise daily average
    avgImg = np.mean(images, axis = 0)
    
    #Converting float64 type ndarray to uint8
    intImage = np.around(avgImg).astype(np.uint8) #Round first and then convert to integer
    
    #Saving the daily average as image
    im = Image.fromarray(intImage)
    
    #Define path for saving image with given file name 
    saveDst = imgSave + '\\' + "_".join(os.listdir(imgDir)[0].split("_")[:3]) + '_RGB_L2_daily.jpg'
    
    #Save image in the defined path
    im.save(saveDst)
    
print ('\n')
print ('Daily averaged RGB images are computed and stored successfully.')

#################################################################################################
#################################################################################################
    
#3rd part
#Line of code to delete pre-created DOY folders and files after finishing the processing  
shutil.rmtree(baseDst)

#################################################################################################
#################################################################################################

print ('\n')
print ('Computing daily GCC and RCC images...')

#4th part
#Line of code to generate daily GCC and RCC as an image

#Save daily GCC and RCC image
gccSave = imgSrc + '\GCC'
rccSave = imgSrc + '\RCC'

#Iterating all daily average images to compute GCC and RCC on a pixel by pixel basis
for img in sorted(glob.glob(os.path.join(imgSave, '*.jpg'))):
    
    #Extracting image file name
    imgName = os.path.basename(img)

    #Reading image one by one
    cv_img = cv2.imread(img)
    
    #Extracting RGB bands as a separate numpy array
    B = cv_img[:,:,0]
    G = cv_img[:,:,1]
    R = cv_img[:,:,2]
      
    #Element wise addition of BGR array to calculate Total DN values in RGB band (i.e. R+G+B) 
    DNtotal = cv_img.sum(axis = 2)
    
    #Compute pixel wise GCC and RCC from daily average
    gcc = np.divide(G, DNtotal)
    rcc = np.divide(R, DNtotal)
    
    # PIL only supports float 32 (mode = 'F').
    gccImgF = np.float32(gcc)
    rccImgF = np.float32(rcc)
    
    #Creating the image to save.
    gccImSave = Image.fromarray(gccImgF, mode="F")
    rccImSave = Image.fromarray(rccImgF, mode="F")
    
    #Define path for saving image with given file name 
    saveDst1 = gccSave + '\\' + imgName.replace('RGB','GCC') + '.tif'
    saveDst2 = rccSave + '\\' + imgName.replace('RGB','RCC') + '.tif'
    
    #Save in the defined path as a Grayscale image
    gccImSave.save(saveDst1)
    rccImSave.save(saveDst2)
    
print ('\n')
print ('Daily averaged GCC and RCC images are computed and stored successfully.')
    
#################################################################################################
#Find out the total elapsed time and print out on the screen
#################################################################################################

end = datetime.now()
time_taken = end - start

print ('\n')
print ('Time elapsed: {}'.format(time_taken)) 

#################################################################################################
   