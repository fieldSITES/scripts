"""
***************************************************************************************************************
######################################
First step in PhenoCam data processing
Created on Wed Jul 15 13:05:54 2020
######################################

This python script renames .jpg images for stations: Abisko, Asa, Lönnstorp, Röbäcksdalen, Skogaryd, Tarfala, 
Grimsö & Svartberget. Different naming conventions are used at the stations. SITES Spectral centrally renames 
all images by following SITES naming convention. Users are encouraged to adapt the script in a way that match
with the station and SITES naming convention.
 
Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for 
      internal use within Swedish Infrastructure for Ecosystem Science (SITES).

Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Images should be in .jpg format.
    c) Uncomment only the lines for renaming images for one particular station based on how the original image 
       names looks like. 
    
Limitations of the script:
    a) Script can only take .jpg images as input.
    b) Script can rename one station image files at once.
    c) Script can rename images that are defined in specific ways only (See different cases for each station).

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha

***************************************************************************************************************
"""
###############################################################################################################
# Module declaration
###############################################################################################################
import os
import glob
import shutil
import exiftool
import datetime
from PIL import Image
from datetime import datetime as dt

###############################################################################################################
# Path definition for source images and the destination to save the renamed images
# Users are supposed to change the source image directory
###############################################################################################################
srcImgdir = input('Enter file path where the images to be renamed are stored: ')

print('\n')
print ('Renaming images.......................................................')

"""
###############################################################################################################
###############################################################################################################
# Iterating through the .jpg files in source directory
for img in sorted(glob.glob(os.path.join(srcImgdir, "*.jpg"))):
    
    # Extracting image file name
    oldimgName = os.path.basename(img)

    '''
    ###########################################################################################################
    # Renaming Asa Station .jpg files
    ###########################################################################################################
    
    newimgName = oldimgName.replace('Asa', 'SWE-ASA-NYB-FOR-P01')
    os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))   
    
    ###########################################################################################################
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    # Renaming Skogaryd Station .jpg files (Valid only for SWE-SRC-STD-FOR-P01)
    ###########################################################################################################

    newimgName = oldimgName.replace('Skogaryd', 'SWE-SRC-STD-FOR-P01')
    os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))   
    
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    # Renaming Skogaryd .jpg files (SWE-SRC-CEN-FOR-P01, SWE-SRC-CEN-FOR-P02, SWE-SRC-CEN-FOR-P03)
    ###########################################################################################################
    
    # Don't forget to change the first string of 'newimgName' variable as per the PhenoCam numbers.
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('_')
    yy = splitted[1].split('-')[0]
    mm = splitted[1].split('-')[1]
    dd = splitted[1].split('-')[2]
    hhmm = splitted[2].split('.')[0]
    
    # Concatenating ddmmyy for calculating day of year
    sdate = dd + '-' + mm + '-' + yy
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
       
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = 'SWE-SRC-CEN-FOR-P01' + '_' + yy + mm + dd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = 'SWE-SRC-CEN-FOR-P01' + '_' + yy + mm + dd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = 'SWE-SRC-CEN-FOR-P01' + '_' + yy + mm + dd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    ###########################################################################################################
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    # Renaming Lonnstorp .jpg files (SWE-LON-SFA-AGR-P01, SWE-LON-SFA-AGR-P02, SWE-LON-SFA-AGR-P03)
    ###########################################################################################################

    # First case
    # Example: '20180320_1603_SWE-LON-SFA-P01'
    
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('_')
    yymmdd = splitted[0]
    hhmm = splitted[1]
    baseName = splitted[2].split('.')[0]
      
    # Concatenating ddmmyy for calculating day of year
    sdate = splitted[0][6:8] + '-' + splitted[0][4:6] + '-' + splitted[0][0:4]
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################   
    '''
    '''
    ###########################################################################################################
    
    # Second case
    # Example: 'SWE-LON-SFA-AGR-P02_2019-04-08_09-00-01'
    
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('_')
    baseName = splitted[0]
    yy = splitted[1].split('-')[0]
    mm = splitted[1].split('-')[1]
    dd = splitted[1].split('-')[2]
    hh = splitted[2].split('-')[0]
    minute = splitted[2].split('-')[1]
    
    # Concatenating ddmmyy for calculating day of year
    sdate = dd + '-' + mm + '-' + yy
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yy + mm + dd + '_' + '00' + str(dayOfYear) + '_' + hh + minute + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yy + mm + dd + '_' + '0' + str(dayOfYear) + '_' + hh + minute + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yy + mm + dd + '_' + str(dayOfYear) + '_' + hh + minute + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    
    # Third case
    # Example: 'SWE-LON-SFA-AGR-P02_2020-01-28T1000'
    
    # Remove the 'T' character from original image file name
    tRemoved = oldimgName.replace('T', '_')
    
    # Splitting the image file name based on '_' character
    splitted = tRemoved.split('_')
    
    # Extract the base name
    baseName = splitted[0]
    
    # Extract year, month, day, hour, minute information
    temp = splitted[1].split('-')
    yymmdd = ''.join(temp) #Join all strings from 'temp' list
    hhmm = splitted[2].split('.')[0]
    
    # Concatenating dd-mm-yy for calculating day of year
    sdate = temp[2] + '-' + temp[1] + '-' + temp[0]
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    
    # Fourth case
    # This is the recent naming convention that the station uses.
    # Example: 'SWE-LON-SFA-AGR-P02_2020-01-28_T10-00'
    
    # Remove the 'T' character from original image file name
    tRemoved = oldimgName.replace('T', '_')
    
    # Splitting the image file name based on '_' character
    splitted = tRemoved.split('_')
    
    # Extract the base name
    baseName = splitted[0]
    
    # Extract year, month, day, hour, minute information
    temp = splitted[1].split('-')
    yymmdd = ''.join(temp) #Join all strings from 'temp' list
    hhmm = ''.join(splitted[-1].split('.')[0].split('-'))
    
    # Concatenating dd-mm-yy for calculating day of year
    sdate = temp[2] + '-' + temp[1] + '-' + temp[0]
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    ###########################################################################################################    
    '''
    '''
    ###########################################################################################################
    # Renaming Svartberget Forest location .jpg files
    ###########################################################################################################
    
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('T')
    yy = splitted[0][6:10]
    mm = splitted[0][11:13]
    dd = splitted[0][14:16]
    hhmm = splitted[1].split('.')[0]
    
    # Concatenating ddmmyy for calculating day of year
    sdate = dd + '-' + mm + '-' + yy
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = 'SWE-SVB-SVB-FOR-P01' + '_' + yy + mm + dd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = 'SWE-SVB-SVB-FOR-P01' + '_' + yy + mm + dd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = 'SWE-SVB-SVB-FOR-P01' + '_' + yy + mm + dd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    # Renaming Svartberget (Degerö) location .jpg files
    ###########################################################################################################
    
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('_')
    yy = splitted[2][0:4]
    mm = splitted[2][4:6]
    dd = splitted[2][6:8]
    hhmm = splitted[2][8:12]
    
    # Concatenating ddmmyy for calculating day of year
    sdate = dd + '-' + mm + '-' + yy
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = 'SWE-SVB-DEG-MIR-P01' + '_' + yy + mm + dd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = 'SWE-SVB-DEG-MIR-P01' + '_' + yy + mm + dd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = 'SWE-SVB-DEG-MIR-P01' + '_' + yy + mm + dd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    ###########################################################################################################    
    '''
    '''
    ###########################################################################################################
    # Renaming Tarfala station .jpg files
    ###########################################################################################################
    
    # Splitting the image file name to extract the year, month, day, hour, minute information
    splitted = oldimgName.split('_')
    yy = splitted[1].split('-')[0][0:4]
    mm = splitted[1].split('-')[0][4:6]
    dd = splitted[1].split('-')[0][6:8]
    hhmm = splitted[1].split('-')[1].split('.')[0]
    
    # Concatenating ddmmyy for calculating day of year
    sdate = dd + '-' + mm + '-' + yy
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = 'SWE-TRS-LAE-GRA-P01' + '_' + yy + mm + dd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = 'SWE-TRS-LAE-GRA-P01' + '_' + yy + mm + dd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = 'SWE-TRS-LAE-GRA-P01' + '_' + yy + mm + dd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    ###########################################################################################################    
    '''
    '''
    ###########################################################################################################
    # Renaming Robacksdalen station .jpg files
    ###########################################################################################################
    
    # First case
    # Example: 'SWE-RBD-RBD-AGR-P01_2019-04-11T1430'
    
    # Remove the 'T' character from original image file name
    tRemoved = oldimgName.replace('T', '_')
    
    # Splitting the image file name based on '_' character
    splitted = tRemoved.split('_')
    
    # Extract the base name
    baseName = splitted[0]
    
    # Extract year, month, day, hour, minute information
    temp = splitted[1].split('-')
    yymmdd = ''.join(temp) # Join all strings from 'temp' list
    hhmm = splitted[2].split('.')[0]
    
    # Concatenating dd-mm-yy for calculating day of year
    sdate = temp[2] + '-' + temp[1] + '-' + temp[0]
    
    # Converting date in string format to date format
    adate = datetime.datetime.strptime(sdate,"%d-%m-%Y")
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    '''
    '''
    ###########################################################################################################
    # Second case
    # Example: 'SWE-RBD-RBD-AGR-P01_2206130700'
    
    # Splitting the image file name based on '_' character
    splitted = oldimgName.split('_')
    
    # Extract the base name
    baseName = splitted[0]
    
    # Extract year, month, day, hour, minute information
    temp = splitted[1].split('.')
    yymmdd = '20' + temp[0][:6]
    hhmm = temp[0][6:]   
    
    # Converting date in string format to date format
    adate = dt.strptime(yymmdd, '%Y%m%d').date()
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(srcImgdir, newimgName))
    
    ###########################################################################################################
    ###########################################################################################################    
    '''
"""
###############################################################################################################
# Automatically creating folders in the current working directory to save results 
###############################################################################################################
# Try-except block is to pass overwrite directories if exists
folders = ['Renamed']
for folder in folders:
    try:
        os.mkdir(os.path.join(srcImgdir, folder))
    except:
        pass

# Define destination path where the renamed images should be saved
destPath = os.path.join(srcImgdir, folder)

"""
###############################################################################################################
# Renaming Grimsö station .jpg files
###############################################################################################################

# First case
# Example: 'GRIMSO1-2020-03-03T0900'

# Iterating through the .jpg files in source directory
for img in sorted(glob.glob(os.path.join(srcImgdir, "*.jpg"))):
    
    # Extracting image file name
    oldimgName = os.path.basename(img)
    
    # Splitting the image file name based on '_' character
    splitted = oldimgName.split('-')
    
    # Basename definition
    baseName = 'SWE-GRI-GRI-FOR-P01'
    
    # Timestamp information
    yymmdd = splitted[1] + splitted[2] + splitted[3].split('.')[0][:2] 
    hhmm = splitted[3].split('.')[0][3:]  
    
    # Converting date in string format to date format
    adate = dt.strptime(yymmdd, '%Y%m%d').date()
    
    # Computing day of year information for each image based on date it was acquired
    dayOfYear = adate.timetuple().tm_yday
    
    if dayOfYear < 10:
        # Concatenating all variables to define the new file name for the images
        newimgName = baseName + '_' + yymmdd + '_' + '00' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(destPath, newimgName))
        
    elif dayOfYear >= 10 and dayOfYear < 100:
        newimgName = baseName + '_' + yymmdd + '_' + '0' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(destPath, newimgName))
        
    else:
        newimgName = baseName + '_' + yymmdd + '_' + str(dayOfYear) + '_' + hhmm + '.jpg'
        os.rename(os.path.join(srcImgdir, oldimgName), os.path.join(destPath, newimgName))
"""
"""    
###############################################################################################################

# Second case
# This is the recent naming convention that the station uses.
# Example: E00000'
    
# Iterate filePath and search for each and every directory
for subdir, dirs, files in os.walk(srcImgdir):
       
    for file in files:
        
        # Only rename the valid image i.e. 'E00000.jpg'
        if not (file == 'INFO.jpg'):
            
            # Implement exiftool to extract the required metadata
            # Check wwhat EXIF metadata exists for the image and change it accordingly 
            # For eg: 'DateTimeOriginal'
            with exiftool.ExifTool() as et:
                metadata = et.get_tag('FileModifyDate', os.path.join(subdir, file))
            
            # Extracting various information required to rename the images
            datetimeOnly = metadata.split('+')[0]
            doy = dt.strptime(datetimeOnly, "%Y:%m:%d %H:%M:%S").timetuple().tm_yday
            yymmdd = "".join(datetimeOnly.split(' ')[0].split(':'))
            hhmm = datetimeOnly.split(' ')[1].split(':')[0] + datetimeOnly.split(' ')[1].split(':')[1]
                        
            # New name for the image
            newimgName = 'SWE-GRI-GRI-FOR-P01_' + yymmdd + '_' + str(doy) + '_' + hhmm + '.jpg'
            
            # Rename the images in the defined directory
            try:
                os.rename(os.path.join(subdir, file), os.path.join(destPath, newimgName))
            
            except WindowsError:
                os.remove(os.path.join(destPath, newimgName))
                os.rename(os.path.join(subdir, file), os.path.join(destPath, newimgName))
"""
###############################################################################################################
###############################################################################################################
'''
###############################################################################################################
# Renaming Abisko station .jpg files
###############################################################################################################
#Counting number of images that will be moved.
count = 0

# Iterating through the .jpg files in source directory
for img in glob.iglob(os.path.join(srcImgdir, "*.jpg")):
    
    #Moving the .jpg file to the destination directory
    shutil.copy(img, destPath)
    
    #Incrementing count
    count += 1

print ('Finished moving {} .jpg files to destination folder'.format(count))

# Iterating through the .jpg files in source directory
for subdir, dirs, files in os.walk(destPath):
    
    for file in files:
        
        imgPath = os.path.join(subdir, file)
        
        # Access the complete path of the image
        with Image.open(imgPath) as test:
        
            # Read EXIF metadata for each image
            exif = test.getexif()
        
        # Extract date when image is captured
        date_created = exif.get(36867)
        
        # Extracting year, month, day, hour, minute and second information 
        yyyy = date_created[0:4]
        month = date_created[5:7]
        day = date_created[8:10]
        hh = date_created[11:13]
        mm = date_created[14:16]
        
        # Concatenating ddmmyy for calculating day of year
        sdate = day + '-' + month + '-' + yyyy
    
        # Converting date in string to date format
        adate = datetime.datetime.strptime(sdate, "%d-%m-%Y")
    
        # Computing day of year information for each image 
        doy = adate.timetuple().tm_yday
        
        # Conditions to append day of year information in image file name
        if doy < 10:
            # Concatenating all variables to define the new file name for the images
            newimgName = 'SWE-ANS-ANS-FOR-P01_' + yyyy + month + day + '_' + '00' + str(doy) + '_' + hh + mm + '.jpg'
            os.rename(os.path.join(subdir, file), os.path.join(subdir, newimgName))
        
        elif doy >= 10 and doy < 100:
            newimgName = 'SWE-ANS-ANS-FOR-P01_' + yyyy + month + day + '_' + '0' + str(doy) + '_' + hh + mm + '.jpg'
            os.rename(os.path.join(subdir, file), os.path.join(subdir, newimgName))
        
        else:
            newimgName = 'SWE-ANS-ANS-FOR-P01_' + yyyy + month + day + '_' + str(doy) + '_' + hh + mm + '.jpg'
            os.rename(os.path.join(subdir, file), os.path.join(subdir, newimgName))
'''
###############################################################################################################
            
print ('\n')
print ('Images are renamed successfully as per the standards of SITES Spectral.')
print ('Check the destination path for renamed images.')

###############################################################################################################
###############################################################################################################