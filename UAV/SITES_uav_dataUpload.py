"""
****************************************************************************************************************
Created on Tue Apr 13 13:08:10 2021
This python script helps in automatic uploading of UAV data products (both RGB and multispectral) into the SITES 
data portal. The different UAV data products defined within SITES are: 
    
    a) UAV - RGB orthomosaic (Level 2)
    b) UAV - RGB point cloud (Level 2)
    c) UAV - NDVI orthomosaic (Level 2)
    d) UAV - Multispectral orthomosaic (Level 2)
    e) UAV - Multispectral point cloud (Level 2) 
    f) UAV - Digital Elevation Model (Level 3)

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only for internal
      use within Swedish Infrastructure for Ecosystem Science (SITES).

Package installation:
    1) zipfile-deflate64   : pip install zipfile-deflate64
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure the .zip files are named as per the SITES standard.
    
       For example: SITES_UAV-RGB-PTC_LON_SFAB_20220519_L2.zip
       General: Infrastructure_Sensor-SensorType-DataName_Station_Location_Flightdate_Datalevel.zip
       
    c) Make sure the .zip file contains metadata (.txt) file in UTF-8 encodings.
    d) Make sure to have data upload rights to the SITES data portal. 
    d) Make sure to have login credentials to the SITES data portal. This enables to have cookie characters which
       is necessary when uploading the data. And this can be found in the data portal 'My Account' page.
    e) Make sure the internet connection is strong and stable throughout the upload process.   
    f) Follow the instructions displayed on the Terminal screen once you run the script.
       
Limitations of the script:
    a) Script can only upload .zip files and not the indvidual data product.
    b) Script can only upload Level 2 and Level 3 data levels for UAV sensor but not Level 0. However, it can be 
       modified to make it possible for the Level 0 uploads when the portal is ready to host it.
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
import subprocess
import zipfile_deflate64 as zipfile

################################################################################################################
# Get file path to the folder containing .zip files to be uploaded
################################################################################################################
filePath = input("Enter file path to the folder containing .zip files: ")
print('\n')
print("File path is: " + filePath)
print('\n')

# Change the working directory
os.chdir(filePath)

################################################################################################################
# Initialize counter for numbering separate .json file for data uploads
# Creating log file to store the curl command and PID of the uploaded file
################################################################################################################
count = 0

# Assigning path to create text file
logPath = os.path.join(filePath + r'\log.txt')

# Opening log file for writing the upload status and associated PID of each uploads.
f1 = open(logPath, 'w')

# Print statement to notify users the list of files being uploaded
print('Files to upload: ')
print('\n')

################################################################################################################
# Station specific information definition
################################################################################################################
# Update if new stations start UAV data acquisition
stnName = {'ANS': 'https://meta.fieldsites.se/resources/stations/abisko', 
           'ASA': 'https://meta.fieldsites.se/resources/stations/Asa', 
           'LON': 'https://meta.fieldsites.se/resources/stations/Lonnstorp', 
           'RBD': 'https://meta.fieldsites.se/resources/stations/Robacksdalen', 
           'SRC': 'https://meta.fieldsites.se/resources/stations/Skogaryd', 
           'SVB': 'https://meta.fieldsites.se/resources/stations/Svartberget', 
           'TRS': 'https://meta.fieldsites.se/resources/stations/Tarfala'}

# Flight locations at each of the above SITES station
# Update if new locations are added to SITES stations
# Flight locations until 2020 
siteName_u2020 = {'ANS_MJA'  : 'https://meta.fieldsites.se/resources/sites/miellehoga-uav',
                  'ANS_STM'  : 'https://meta.fieldsites.se/resources/sites/abisko-stordalen-uav-mire',
                  'ANS_SFO'  : 'https://meta.fieldsites.se/resources/sites/abisko-stordalen-uav-forest',
                  'ASA_NYB'  : 'https://meta.fieldsites.se/resources/sites/asa-uav-2020', 
                  'LON_EKO'  : 'https://meta.fieldsites.se/resources/sites/lonnstorp-organic',
                  'LON_SFA'  : 'https://meta.fieldsites.se/resources/sites/lonnstorp-safe-a',
                  'LON_SFB'  : 'https://meta.fieldsites.se/resources/sites/lonnstorp-safe-b',
                  'SRC_CEN'  : 'https://meta.fieldsites.se/resources/sites/skogaryd-central-uav',
                  'SRC_MYC'  : 'https://meta.fieldsites.se/resources/sites/mycklemossen-uav-2020', 
                  'SRC_FOL'  : 'https://meta.fieldsites.se/resources/sites/foljesjon-uav',
                  'SRC_STD'  : 'https://meta.fieldsites.se/resources/sites/skogaryd-stordalen-uav',
                  'SRC_MAD'  : 'https://meta.fieldsites.se/resources/sites/foljemaden-uav-2020',
                  'RBD_RBDN' : ['https://meta.fieldsites.se/resources/sites/robacksdalen-01-2020',
                                'https://meta.fieldsites.se/resources/sites/robacksdalen-02-2020',
                                'https://meta.fieldsites.se/resources/sites/robacksdalen-03'],
                  'SVB_DEG'  : 'https://meta.fieldsites.se/resources/sites/degero-uav',
                  'SVB_SVB'  : 'https://meta.fieldsites.se/resources/sites/svartberget-uav',
                  'TRS_LAE'  : 'https://meta.fieldsites.se/resources/sites/laevasvagge-uav-2020'}

# Flight locations from 2021 
siteName_f2021 = {'ANS_MJA'  : 'https://meta.fieldsites.se/resources/sites/miellehoga-uav',
                  'ANS_STM'  : 'https://meta.fieldsites.se/resources/sites/abisko-stordalen-uav-mire',
                  'ANS_SFO'  : 'https://meta.fieldsites.se/resources/sites/abisko-stordalen-uav-forest',
                  'ASA_NYB'  : 'https://meta.fieldsites.se/resources/sites/asa-uav-2021',
                  'LON_SFAB' : 'https://meta.fieldsites.se/resources/sites/lonnstorp-safe-ab',
                  'SRC_CEN'  : 'https://meta.fieldsites.se/resources/sites/skogaryd-central-uav',
                  'SRC_MYC'  : 'https://meta.fieldsites.se/resources/sites/mycklemossen-uav-2021',
                  'SRC_FOL'  : 'https://meta.fieldsites.se/resources/sites/foljesjon-uav',
                  'SRC_STD'  : 'https://meta.fieldsites.se/resources/sites/skogaryd-stordalen-uav',
                  'SRC_MAD'  : 'https://meta.fieldsites.se/resources/sites/foljemaden-uav-2021',
                  'RBD_RBDN' : ['https://meta.fieldsites.se/resources/sites/robacksdalen-01-2021',
                                'https://meta.fieldsites.se/resources/sites/robacksdalen-02-2021'],
                  'SVB_DEG'  : 'https://meta.fieldsites.se/resources/sites/degero-uav',
                  'SVB_SVB'  : 'https://meta.fieldsites.se/resources/sites/svartberget-uav',
                  'TRS_LAE'  : 'https://meta.fieldsites.se/resources/sites/laevasvagge-uav-2021'}

################################################################################################################
# Extract information from the metadata and upload the .zip files in the file path
################################################################################################################
# Iterate user defined filePath to find all .zip files
for file in glob.glob("*.zip"):
    
    # Set condition to select only the .zip files that contains ORTHO, PTC, and DEM keyword
    if '-ORTHO_' in file or '-PTC_' in file or '-DEM_' in file:
        
        print('{}) {}'.format(count + 1, file))
        
        # Increase the count by 1
        count += 1
        
        # Compute SHA256 hash string of a file
        sha256_hash = hashlib.sha256()
        with open(file,"rb") as f:
            
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            
            hashSum = sha256_hash.hexdigest()
            #print(sha256_hash.hexdigest())
            print('\n')
            
            # Read metadata file in .zip file to extract specific information for .json file
            zip = zipfile.ZipFile(file, "r")
            textFile = [text for text in zip.namelist() if text.endswith('.txt')]
            
            # Open .txt metadata file 
            with zip.open(textFile[0]) as f:
                head = [next(f) for x in range(7)]
        
                # Extracting timestamp information from metadata files
                dateTime = head[2].split()
    
                # start and stop time to be included in .json file
                # By default .decode() use UTF-8 encoding and converts from bytes to string format
                start = dateTime[1].decode() + 'T' + dateTime[2].decode() + ':00.000Z'
                stop = dateTime[4].decode() + 'T' + dateTime[5].decode() + ':00.000Z'
                                
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
                            }
                        },
                    "objectSpecification": ""
                    }
            
            # Split file name
            fNsplit = file.split('_')
            
            # Fill up the empty fields with necessary information to create a complete .json file
            data['hashSum'] = hashSum
            data['fileName'] = file
            data['specificInfo']['acquisitionInterval']['start'] = start
            data['specificInfo']['acquisitionInterval']['stop'] = stop
            data['specificInfo']['station'] = stnName[fNsplit[2]]
            
            # Extract the year info from filename and convert it to integer
            yyyy = int(dateTime[1].decode()[0:4])
            
            ################################################################################################################
            # Set condition to select correct flight location until 2020
            ################################################################################################################
            if yyyy <= 2020 and not 'RBD_RBDN' in file:
                
                data['specificInfo']['site'] = siteName_u2020["_".join(fNsplit[2:4])]
            
            elif yyyy <= 2020 and '_U01_' in file and 'RBD_RBDN' in file:
                
                data['specificInfo']['site'] = siteName_u2020["_".join(fNsplit[2:4])][0]
                
            elif yyyy <= 2020 and '_U02_' in file and 'RBD_RBDN' in file:    
                
                data['specificInfo']['site'] = siteName_u2020["_".join(fNsplit[2:4])][1]
                
            elif yyyy <= 2020 and '_U03_' in file and 'RBD_RBDN' in file:    
                
                data['specificInfo']['site'] = siteName_u2020["_".join(fNsplit[2:4])][2]    
            
            ################################################################################################################
            # Flight locations from 2021 and onwards  
            ################################################################################################################
            elif yyyy >= 2021 and not 'RBD_RBDN' in file:
                
                data['specificInfo']['site'] = siteName_f2021["_".join(fNsplit[2:4])]
                
            elif yyyy >= 2021 and '_U01_' in file and 'RBD_RBDN' in file:
                
                data['specificInfo']['site'] = siteName_f2021["_".join(fNsplit[2:4])][0]
                
            elif yyyy >= 2021 and '_U02_' in file and 'RBD_RBDN' in file:
                
                data['specificInfo']['site'] = siteName_f2021["_".join(fNsplit[2:4])][1]
            
            else:
                print ('Doesn\'t match with any flight locations within SITES infrastructure.')
                print ('Make sure the locations are updated in the data portal.')
            
            ################################################################################################################
            # Use correct object specification for distinct data levels
            ################################################################################################################
            if 'RGB' in file and 'ORTHO' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-rgb-orthomosaic'
            
            elif 'MSP' in file and 'ORTHO' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-multispectral-orthomosaic'
                
            elif 'RGB' in file and 'PTC' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-rgb-point-cloud'
                
            elif 'MSP' in file and 'PTC' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-multispectral-point-cloud'
                
            elif ('RGB' in file or 'MSP' in file) and 'DEM' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-digital-elevation-model'
                
            elif 'NDVI' in file:
                data['objectSpecification'] = 'https://meta.fieldsites.se/resources/objspecs/uav-ndvi-orthomosaic'
            
            else:
                print('No valid file found to upload')
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
            
            '''
            Important information:
                # Users must have login credentials of SITES data portal and visit 'My Account' to get Cookie.
                # Copy the cookie string and paste it when asked by the script to enter
                # If you do not have one, please communicate with SITES data management committee to get one.  
            '''
            ################################################################################################################
            # Using curl command to upload the data into the portal.
            # Get cookie input only once for the first time when uploading data from the same folder
            # Use the same cookie for the rest of the data in the folder
            ################################################################################################################
            if count == 1:
                cookie = input("Please enter your Cookie characters: ")
                
                # Initiate curl command to upload the metadata into the portal 
                curlCommand = 'curl -s -H "Host: meta.fieldsites.se" -H "Content-Type: application/json" -H "Cookie: {}" -X POST -d @{} https://meta.fieldsites.se/upload'.format(cookie, jsonFile)
                
                print('\n')
                print(curlCommand)
                print('\n')
                
                # Use getstatusoutput to store the metadata link for use in curl command to upload data
                status, metaURL = subprocess.getstatusoutput(curlCommand)
                               
                # Initiate curl command to upload the selected .zip file data into the portal
                curlData = 'curl -H "Host: data.fieldsites.se" -H "Transfer-Encoding: chunked" -H "Cookie: {}" --upload-file {} {}'.format(cookie, os.path.join(os.getcwd(), file), metaURL)
                f1.write('{}\n\n'.format(curlData))
                print('\n')
                print('\n')
                
                # Use getstatusoutput to display the PID
                status, PID = subprocess.getstatusoutput(curlData)
                f1.write('{}\n\n'.format(PID))
                print('\n')
                print('\n')
                print('\n')
                print(PID)
                print('\n')
                print ('{} uploaded successfully into SITES data portal'.format(file))
                
            else:
                
                # Initiate curl command to upload the metadata into the portal 
                curlCommand = 'curl -s -H "Host: meta.fieldsites.se" -H "Content-Type: application/json" -H "Cookie: {}" -X POST -d @{} https://meta.fieldsites.se/upload'.format(cookie, jsonFile)
                    
                print('\n')
                print(curlCommand)
                print('\n')
                
                # Use getstatusoutput to store the result
                status, metaURL = subprocess.getstatusoutput(curlCommand)
                                               
                # Initiate curl command to upload the selected .zip file data into the portal
                curlData = 'curl -H "Host: data.fieldsites.se" -H "Transfer-Encoding: chunked" -H "Cookie: {}" --upload-file {} {}'.format(cookie, os.path.join(os.getcwd(), file), metaURL)
                f1.write('{}\n\n'.format(curlData))
                print('\n')
                print('\n')
                
                # Use getstatusoutput to display the PID
                status, PID = subprocess.getstatusoutput(curlData)
                f1.write('{}\n\n'.format(PID))
                print('\n')
                print('\n')
                print(PID)
                print('\n')
                print('{} uploaded successfully into SITES data portal'.format(file))
                print('\n')
                
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