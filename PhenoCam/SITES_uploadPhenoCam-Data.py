"""
****************************************************************************************************************
Created on Thu May 12 15:48:09 2022

This python script helps in automatic uploading of PhenoCam data products into the SITES data portal. 
The PhenoCam data products defined within SITES are: 
    
    a) Level 0 : Raw data - Phenocamera photos
    b) Level 1 : Quality-filtered phenocamera photos
    c) Level 2 : Green Chromatic Index composites, daily
    d) Level 2 : Red Chromatic Index composites, daily
    e) Level 2 : RGB composites, daily
    f) Level 3 : Phenocam - Green and Red Chromatic Coordinates time series, daily

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for internal
      use within Swedish Infrastructure for Ecosystem Science (SITES).

Package installation:
    1) zipfile-deflate64   : pip install zipfile-deflate64
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure the .zip files are named as per the SITES standard.
    
       For example: SITES_P03-GCC_SRC_CEM03_20190101-20191231_L2_daily.zip
       General: Infrastructure_PhenocamNo-DataLevelAbbreviation_Station_Location_StartDate-EndDate_Datalevel.zip
       
    c) Make sure the .zip file contains metadata (.txt) file in UTF-8 encodings.
    d) Make sure to have data upload rights to the SITES data portal. 
    d) Make sure to have login credentials to the SITES data portal. This enables to have cookie characters which
       is necessary when uploading the data. And this can be found in the data portal 'My Account' page.
    e) Make sure the internet connection is strong and stable throughout the upload process.   
    f) Follow the instructions displayed on the screen once you run the script.
       
Limitations of the script:
    a) Script can only upload .zip files and not the indvidual data product.
    b) Script can only upload Level 1, Level 2, and Level 3 data levels. The script can handle Level 0 raw data  
       uploads once the portal is ready to host it.
    c) Cookie copied from the SITES data portal 'My Account' page is valid only for 24 hours.

Important information:    
    a) Instructions for uploading data objects: https://github.com/ICOS-Carbon-Portal/data
    b) Instuctions about data portal metadata service: https://github.com/ICOS-Carbon-Portal/meta
    c) Always good to check the log.text file after completion of running the upload script. All details together
       with curl command for each particular .zip file and PID of the uploaded file will be there if there is no 
       problem in uploading. If the internet connection is not stable, only the metadata of the data is uploaded 
       and not the data. In such case, check the log file and copy the curl command and run it in any console. 
    
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha

****************************************************************************************************************
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import glob
import json
import hashlib
import zipfile_deflate64 as zipfile
import subprocess

################################################################################################################
# List out all SITES station and ask from user which station data to upload
################################################################################################################
# Update this variable when more stations are added into SITES
rstation = ['Abisko', 'Asa', 'Grimso', 'Lonnstorp', 'Robacksdalen', 'Skogaryd', 'Svartberget', 'Tarfala']

print('\n')

# Iterate though the list of SITES station
for idx, stn in enumerate(rstation):
    
    # Print the station name and corresponding indexes
    print('{} : {}'.format(idx, stn))

print('\n')

# Select the station to upload the PhenoCam data products
chosenStn = int(input('Choose one of the SITES station (For example, 0 to upload data for Abisko): '))
print('\n')

################################################################################################################
# Get file path to the folder containing .zip files to be uploaded
################################################################################################################
filePath = input("Enter complete file path to the {} folder containing files to upload: ".format(rstation[chosenStn]))

print('\n')
print("File path is: " + filePath)

# Change the working directory
os.chdir(filePath)

# Print all the .zip files within the user input path
zipfiles = [file for file in glob.glob('*.zip')] 
print('\n')
print("List of all .zip files found within the file path: ")
print('\n')
[print(fileName) for fileName in zipfiles]

################################################################################################################
# Station specific information definition
################################################################################################################
# Predefine SITES station ID along with the station name
# Update this variable when more stations are added into SITES
stationID = {'Abisko'        : 'ANS', 
             'Asa'           : 'ASA', 
             'Grimso'        : 'GRI', 
             'Lonnstorp'     : 'LON', 
             'Robacksdalen'  : 'RBD', 
             'Skogaryd'      : 'SRC', 
             'Svartberget'   : 'SVB',
             'Tarfala'       : 'TRS'}

# Predefine data type (data object specification) for Phenocamera data products
dataType = {'L0': 'https://meta.fieldsites.se/resources/objspecs/phenocam-photos',
            'L1': 'https://meta.fieldsites.se/resources/objspecs/quality-filtered-phenocamera-photos',
            'L2': {'RGB': 'https://meta.fieldsites.se/resources/objspecs/rgb-phenocam-photos-daily', 
                   'GCC': 'https://meta.fieldsites.se/resources/objspecs/green-chromatic-index-daily',
                   'RCC': 'https://meta.fieldsites.se/resources/objspecs/red-chromatic-index-daily'},
            'L3': 'https://meta.fieldsites.se/resources/objspecs/green-red-chromatic-coordinates'}

# Predefine SITES station information
# Update this variable when more stations are added into SITES
stnName = {'ANS': 'https://meta.fieldsites.se/resources/stations/abisko', 
           'ASA': 'https://meta.fieldsites.se/resources/stations/Asa', 
           'GRI': 'https://meta.fieldsites.se/resources/stations/Grimso', 
           'LON': 'https://meta.fieldsites.se/resources/stations/Lonnstorp', 
           'RBD': 'https://meta.fieldsites.se/resources/stations/Robacksdalen', 
           'SRC': 'https://meta.fieldsites.se/resources/stations/Skogaryd', 
           'SVB': 'https://meta.fieldsites.se/resources/stations/Svartberget',
           'TRS': 'https://meta.fieldsites.se/resources/stations/Tarfala'}

# Predefine dictionary to store 'site' information
# Update this field with additional information about other station site name
siteName = {'ANS_OBS'  : 'https://meta.fieldsites.se/resources/sites/abisko-observatory',
            'ASA_NYB'  : 'https://meta.fieldsites.se/resources/sites/nybbeget-forest',
            'LON_SFA'  : 'https://meta.fieldsites.se/resources/sites/lonnstorp',
            'RBD_RBD'  : 'https://meta.fieldsites.se/resources/sites/robacksdalen-north',
            'SRC_CEM01': 'https://meta.fieldsites.se/resources/sites/umbrisol-forest',
            'SRC_CEM02': 'https://meta.fieldsites.se/resources/sites/umbrisol-forest',
            'SRC_CEM03': 'https://meta.fieldsites.se/resources/sites/umbrisol-forest',
            'SRC_STM'  : 'https://meta.fieldsites.se/resources/sites/skogaryd-stordalen-forest',
            'SVB_DEG'  : 'https://meta.fieldsites.se/resources/sites/degero-mire',
            'SVB_SVB'  : 'https://meta.fieldsites.se/resources/sites/svartberget-forest',
            'TRS_LAE'  : 'https://meta.fieldsites.se/resources/sites/laevas-grassland'}

'''
Important information:
# Users must have login credentials of SITES data portal and visit 'My Account' to get Cookie.
# Copy the cookie string and paste it when asked by the script to enter
# If you do not have one, please communicate with SITES data management committee to get one.  
'''
# Get cookie input from the user           
cookie = input("Please enter your Cookie characters: ")
print('\n')

# Empty list to store the files to be uploaded
files2upload = []

# Display the files to be uploaded
print('Files to upload: ')
print('\n')

################################################################################################################
# Check to see if the file path contains data belonging to the user defined station
################################################################################################################

# Iterate through the .zip files
for dfiles in zipfiles:
    
    # Extracting the phenocamera number and short name of station from the .zip file name
    phenocamN = dfiles.split('_')[1].split('-')[0]
    abbStn = dfiles.split('_')[2]
    
    # Check if the .zip file belongs to the chosen station 
    # To confirm we upload data to the station where it belongs
    if abbStn == stationID[rstation[chosenStn]]:
        
        # Append the files to be uploaded
        files2upload.append(dfiles)
    
    else:
        
        print('List of .zip files do not belong to the user defined station.')
        print('Run the script again with correct file path and station.')
        print('Terminating the upload program.....')
        break
    
# Print the files that will be uploaded    
[print(upfile) for upfile in files2upload]

################################################################################################################
# Initialize counter for numbering separate .json file for data uploads
# Creating log file to store the curl command and PID of the uploaded file
################################################################################################################
count = 0

# Assigning path to create text file
logPath = os.path.join(filePath + r'\log.txt')

# Opening log file for writing the upload status and associated PID of each uploads.
f1 = open(logPath, 'w')

################################################################################################################
# Extract information from the metadata and upload the .zip files in the file path
################################################################################################################
# Iterate through files2upload variable to upload all the .zip files
for file in files2upload:
    
    # Split the file names to find data levels
    splitted = file.split('_')
    
    # Define site abbreviation for given .zip file
    # This helps to select the appropriate sample point for a given dataset.
    siteAbb = splitted[2] + '_' + splitted[3]
    
    # Extract data level of the file being uploaded
    dtLevel = splitted[5]
    
    # Extract what type of Level 2 data
    typeL2 = splitted[1].split('-')[1]
    
    # Compute SHA256 hash string of a file
    sha256_hash = hashlib.sha256()
    
    # Open the .zip file 
    with open(file,"rb") as f:
            
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        
        hashSum = sha256_hash.hexdigest()
        #print(sha256_hash.hexdigest())
        print('\n')
        
        # Read metadata file in .zip file to extract specific information
        # Information extracted will be used to create .json file 
        zip = zipfile.ZipFile(file, "r")
        textFile = [text for text in zip.namelist() if text.endswith('.txt')]
        
        # Open .txt meta file to extract timestamp and geolocation information
        with zip.open(textFile[0]) as f:
            head = [next(f) for x in range(9)]
            
            # Extracting timestamp information from metadata files
            dateTime = head[2].split()
            
            # start and stop time to be included in .json file
            # By default .decode() use UTF-8 encoding and converts from bytes to string format
            start = dateTime[2].decode() + 'T' + dateTime[3].decode() + '.000Z'
            stop = dateTime[5].decode() + 'T' + dateTime[6].decode() + '.000Z'
            
            # Extract sampling point latitude and longitude information from the metadata file
            lat = float(head[6].split()[1])
            lon = float(head[7].split()[1])

        # Define all parameters to create a .json file required for data upload
        data = {
                "submitterId": "SITES_SPECTRAL",
                "hashSum": "",
                "fileName": "",
                "specificInfo": {
                    "station": "",
                    "site": "",
                    "acquisitionInterval": {
                        "start": "",
                        "stop": ""
                        },
                    "samplingPoint": {
                        "lat": 99.996675,
                        "lon": 11.885564
                        }
                    },
                "objectSpecification": ""
                }
               
        # Fill up the empty fields with necessary information to create a complete .json file
        data['hashSum'] = hashSum
        data['fileName'] = file
        data['specificInfo']['acquisitionInterval']['start'] = start
        data['specificInfo']['acquisitionInterval']['stop'] = stop
        data['specificInfo']['samplingPoint']['lat'] = lat
        data['specificInfo']['samplingPoint']['lon'] = lon
        data['specificInfo']['station'] = stnName[splitted[2]]
        data['specificInfo']['site'] = siteName[siteAbb]
        
        ################################################################################################################
        # Use correct object specification for distinct data levels
        ################################################################################################################
        if dtLevel == 'L0':
            
            data['objectSpecification'] = dataType[dtLevel]
        
        elif dtLevel == 'L1':
        
            data['objectSpecification'] = dataType[dtLevel]
        
        elif (dtLevel == 'L2') and  (typeL2 == 'RGB'):
        
            data['objectSpecification'] = dataType[dtLevel][typeL2]
        
        elif (dtLevel == 'L2') and  (typeL2 == 'GCC'):
            
            data['objectSpecification'] = dataType[dtLevel][typeL2]
        
        elif (dtLevel == 'L2') and  (typeL2 == 'RCC'):
            
            data['objectSpecification'] = dataType[dtLevel][typeL2]
            
        else:
            print('{} is not valid L2 data type.'.format(file))
            break

        ################################################################################################################
        # .json file preparation with all of the above parameters
        # Serializing json 
        ################################################################################################################
        json_object = json.dumps(data, indent = 2)
 
        # Writing to sample.json
        jsonFile = 'sample{}.json'.format(count)
        with open(jsonFile, "w") as outfile:
            outfile.write(json_object)            
        
        ################################################################################################################
        # Using curl command to upload the data into the portal.
        # Use the cookie input from user when uploading data 
        ################################################################################################################
        curlCommand = 'curl -s -H "Host: meta.fieldsites.se" -H "Content-Type: application/json" -H "Cookie: {}" -X POST -d @{} https://meta.fieldsites.se/upload'.format(cookie, jsonFile)
        
        # Use getstatusoutput to store the metadata link for use in curl command to upload data
        status, metaURL = subprocess.getstatusoutput(curlCommand)
        
        print('Uploading {} file............'.format(file))
        
        # Initiate curl command to upload the selected .zip file data into the portal
        curlData = 'curl -H "Host: data.fieldsites.se" -H "Transfer-Encoding: chunked" -H "Cookie: {}" --upload-file {} {}'.format(cookie, os.path.join(os.getcwd(), file), metaURL)
        f1.write('{}\n\n'.format(curlData))
        print('\n')
        print('\n')
        #print(curlData)
        
        # Use getstatusoutput to display the PID
        status, PID = subprocess.getstatusoutput(curlData)
        f1.write('{}\n\n'.format(PID))
        print('\n')
        print('\n')
        #print(PID)
        print('{} uploaded successfully into SITES data portal'.format(file))    
        
        # Increase the counter
        count += 1

################################################################################################################
# Close the file when done
f1.close()

# Delete all the created .json files
[os.remove(f) for f in glob.glob('*.json')]

print ('Finished uploading all .zip files within the defined path.')
print ('Check the log.txt file for upload status and PID after running the script.')
print ('It might take few hours until it is visible in the data portal.')

################################################################################################################
################################################################################################################