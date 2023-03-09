"""
***************************************************************************************************************
#########################################################
Step 1:
EXIF/XMP Metadata extraction for Multispectral UAV Images 

Created on Wed Apr 28 16:12:17 2021
#########################################################

This Python script reads EXIF-data from Phantom 4 Multispectral sensor acquired images and saves to Excel. The
sunshine sensor onboard UAV gives an idea about the consistency of light conditions throughout the flight. So,
it's necessary to check the variation of sunshine sensor irradiance data before processing them. And this code
helps to extract key metadata parameters such as image name, geolocation information, irradiance data recorded
by sunshine sensor and roll, yaw and pitch angle.

Note: The script was tested on windows environment in Python 3.7.6 version only. This script is only for 
      the internal use within SITES.

Package installation:
    a) exiftool     
    b) xlsxwriter
    c) PyExifTool
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure the flight images are renamed as per the SITES Standard.
       For example: DJI_0011_BLU, DJI_0012_GRE, DJI_0013_RED, DJI_0014_REG, DJI_0015_NIR
           
    b) Run the script and follow the instructions displayed.
    c) Once finished, there should be a .xlsx sheet with irradiance data per band for the flight.
    
Limitations of the script:
    a) Script works only with DJI P4 Multispectral images and is programmed to extract only fews EXIF data.
    
Important information:
    a) DJI Image Processing Guide:
       https://dl.djicdn.com/downloads/p4-multispectral/20200717/P4_Multispectral_Image_Processing_Guide_EN.pdf
       
    b) Download and read more on Exiftool:
       https://exiftool.org/
       
    c) Download and read more on PyExifTool:
       https://github.com/sylikc/pyexiftool
       

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
      
@author: Shangharsha
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import exiftool
import xlsxwriter

################################################################################################################  
# Creating and writing data to excel sheet  
# Data to write to the sheet is handled when the actual writing is performed.  
################################################################################################################
# Get file paths to the multispectral UAV flight images 
directory = input("Enter file path to the folder containing multispectral DJI P4 images: ")
print ('\n')

# Base folder name of data
original = os.path.basename(directory)

# Define name for excel sheet
xlsSheet = os.path.join(directory, original + '_seq.xlsx')
   
# Create a new Excel file and add a worksheet. 
# Need to open here to add sunshine sensor irradiance data for all bands
workbook = xlsxwriter.Workbook(xlsSheet)
################################################################################################################

################################################################################################################
# Creating variables for tags and placing tags of interest in a list
# Adjust the tags in the list 'tags' to decide which tags to extract
################################################################################################################
yaw_tag   = 'XMP:FlightYawDegree'
roll_tag  = 'XMP:FlightRollDegree'
pitch_tag = 'XMP:FlightPitchDegree'

irr_tag   = 'XMP:Irradiance'
lat_tag   = 'XMP:GpsLatitude'
lon_tag   = 'XMP:GpsLongitude'
alt_tag   = 'XMP:AbsoluteAltitude'

bandName_tag = 'XMP:BandName'
      
# Define which tags to read
# Modify this if interested in other EXIF metadata tags
mtags = [bandName_tag, irr_tag, lat_tag, lon_tag, alt_tag, roll_tag, yaw_tag, pitch_tag]

################################################################################################################

# Get list of all files in the directory
fileList = os.listdir(directory)
fileList.sort(key = lambda x: int(x.split('_')[1]))

# Select only image (.TIF) files
arr = []
for f in fileList:
    if 'TIF' in f:
        arr.append(f)

# Complete file path to each .TIF files
pathFileList = [os.path.join(directory, f) for f in arr]
  
files = pathFileList
  
################################################################################################################
# Creating lists for appending the EXIF data of interest
# Check that the exif tags are included in the list 'tags'
# NB! the lists must be initiated inside the loop to clear data from previous bands
################################################################################################################

irrBandDict = {band:[] for band in ['Blue', 'Green', 'Red', 'RedEdge', 'NIR']}

with exiftool.ExifTool() as et:
    # Gets metadata as a list of dictionaries
    metadata = et.get_tags_batch(mtags, files)
    
    for idx, file_metadata in enumerate(metadata):

        irrData = [fileList[idx], file_metadata[irr_tag], file_metadata[lat_tag], file_metadata[lon_tag], 
                   float(file_metadata[alt_tag]), float(file_metadata[roll_tag]), float(file_metadata[yaw_tag]), 
                   float(file_metadata[pitch_tag])]
        irrBandDict[file_metadata[bandName_tag]].append(irrData)

################################################################################################################ 
# Writing to Excel sheet     
# Adjust to get the data of interest
################################################################################################################

for band in ['Blue', 'Green', 'Red', 'RedEdge', 'NIR']:
    worksheet = workbook.add_worksheet(band)
    
    tempIrrList = irrBandDict[band]
    
    # Header definition for the excel sheet
    exifData = ['Img', 'Irradiance', 'Latitude', 'Longitude', 'Altitude', 'Roll', 'Yaw', 'Pitch']

    # Adding all headings
    for col, heading in enumerate(exifData):
        # writing at row = 0, col = col and title from exifData
        worksheet.write(0, col, heading)
        
    for row, valList in enumerate(tempIrrList):
        for col, val in enumerate(valList):
            worksheet.write(row+1, col, val)

# Closing the Excel sheet   
workbook.close()

print ('Finished extracting defined EXIF metadata tags for the images.')
print ('Check the {} for information about the extracted EXIF metadata.'.format(xlsSheet))

################################################################################################################
################################################################################################################