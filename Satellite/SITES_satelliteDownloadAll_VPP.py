"""
***************************************************************************************************************
#######################################
First step in Satellite data processing

Download all HRVPP product 
Created on Wed Oct 19 09:39:43 2022
######################################

This python script downloads satellite (S2) derived all 14 HRVPP data product from WEkEO data portal for user
defined satellite tile ID. The script once run, creates new folder automatically which is named after defined
satellite tile ID.There will be folders inside named after each of the HRVPP data products. Data products are
related with TIMESAT processed high resolution vegetation seasonality. 

Note: The script was tested on LINUX environment (i.e. LUNARC AURORA) in Python 3.9.12 version only. 
      This script is only for the internal use within SITES.

Instructions for running the script:
    1) At the home directory, there should be a hidden .hdarc file with login credentials to 
       access the WEkEO data portal for downloading various satellite products.
    2) There should be a base .json file called 'vpp.json' on the same file path as this python script.
    3) The script can be run in two ways:
    
            1st way (Fully automated):
            ##########################
                
            Users are supposed to run the executable bash file (SITES_satelliteDownloadAll_VPP.sh) directly 
            and follow the instructions displayed on the screen. No need to load anything separately
            in the Terminal.
        
            Don't forget to change the path to python script and vpp.json file in the executable bash file 
            before running.
    
            2nd way (Semi-automated):
            #########################
       
            a) Run the Terminal on AURORA.
            b) Load Anaconda3 module running the following command lines one by one on the Terminal:
    
               module load Anaconda3
               source config_conda.sh
           
            c) Run this python script on terminal:
        
               python .../SITES_satelliteDownloadAll_VPP.py .../vpp.json
               General form: python CompletePythonFilePath.py CompleteJSONFilePath.json
        
    4) Follow the instructions displayed on the Terminal screen once you run the script

Limitations of the script:
    a) Script cannot directly download data for defined spatial extent only but rather downloads 
       whole tile which can later be reprojected or clipped accordingly.
    
Important information:
    a) Read more about the hda python package:
       https://www.wekeo.eu/docs/hda-python-lib
       
    b) Read more about the HRVPP data products:
       https://land.copernicus.eu/user-corner/technical-library/product-user-manual-of-seasonal-trajectories/
       
    c) Read more about Anaconda3 module running on LUNARC:
       https://lunarc-documentation.readthedocs.io/en/latest/Python/
       
    d) Read more about the WEkEO data service documentation:
       https://www.wekeo.eu/docs 
       
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
    
@author: Shangharsha
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import sys
import json
import shutil
from hda import Client

################################################################################################################
# Define a specific path for an interpreter to search for
# Login information to Weekeo website is kept within this interpreter
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
################################################################################################################

################################################################################################################
# Predefine dictionary to store 'station' information
################################################################################################################
folderName = ['HRVPP_Data']

print('\n')

# Ask from user which year's satellite data to download
yyyy = input('Enter which year''s satellite data to download: ')
start = yyyy + '-01-01' + 'T00:00:00.000Z'
end = yyyy + '-12-31' + 'T00:00:00.000Z'
              
# List storing the satellite data product names to be downloaded
valueList = ['SOSD', 'SOSV', 'EOSD', 'EOSV', 'LENGTH', 'AMPL', 'SPROD', 'TPROD', 'MAXD', 'MAXV', 'MINV', 
             'LSLOPE', 'RSLOPE', 'QFLAG']

# Satellite data tile ID for each of the research station
tileID = input('Enter S2 Tile ID to download: ')
    
################################################################################################################
# Main program to communicate with Weekeo website and download various satellite data
# product as mentioned in the .json file  
################################################################################################################
            
c = Client(debug=True)

# Find the .json file to be used for downloading satellite data
queries = sys.argv[1:]

if not queries:
    queries = ["sentinel.json"]

# Create a copy of the original .json file
# Newly created copy will be used to modify and use
dst = os.path.dirname(queries[0]) + '/copy_vpp.json'
shutil.copy2(queries[0], dst)

################################################################################################################
# Automatically creating folders in the directory to save results into
################################################################################################################

# Try-except block is to pass overwrite directories if exists
folders = [folderName[0]]

# Create a folder named 'HRVPP_Data' as a base folder
for folder in folders:
    try:
        os.mkdir(os.path.join(os.path.dirname(queries[0]), folder))
    except:
        pass

# Create sub-folders within the base folder named after TileID
childPath = os.path.dirname(dst) + '/' + folders[0] + '/'

try:
    os.mkdir(os.path.join(childPath, tileID))
except:
    pass

# Update file path where sub-folders named after each of the VPP parameters are to be downloaded    
rootPath = os.path.join(childPath, tileID)

# Sub-folders to create within the TileID folder
subFolders = ['SOSD', 'SOSV', 'EOSD', 'EOSV', 'LENGTH', 'AMPL', 'SPROD', 'TPROD', 'MAXD', 
              'MAXV', 'MINV', 'LSLOPE', 'RSLOPE', 'QFLAG']

# Loop over this list to create them as a subfolder    
for items in subFolders:
    try:
        
        # Temporary path creation to the subfolder items
        tempPath = os.path.join(rootPath, items)
        
        # Create new folders within the temporary path
        os.mkdir(tempPath)
    except:
        pass
       
################################################################################################################
# Iterate through the product list to be downloaded
################################################################################################################
for prod in valueList:
    
    # Read, update the tags and modify the .json file
    with open(dst, 'r+') as f:
        
        # Returns a JSON object as a dictionary
        data = json.load(f)
        
        # Update the sample .json file with new user defined parameters   
        # Date interval 
        data['dateRangeSelectValues'][0]['start'] = start
        data['dateRangeSelectValues'][0]['end'] = end
        
        # Tile ID
        data['stringInputValues'][0]['value'] = tileID
        
        # Update the .json file with season number i.e. s1 or s2
        # Number of seasons
        season = ['s1', 's2']

        # Set counter
        count = 0
    
        # Iterate through seasons to download data for both seasons
        for nseasons in season:
            dictSeason = {'name':'productGroupId', 'value':nseasons}
            data['datasetId'] = 'EO:EEA:DAT:CLMS_HRVPP_VPP'
            
            # Check conditions to see if the dictSeason is to be appended or modified
            if (count == 0) and (len(data['stringChoiceValues']) < 2):
                # Data product
                data['stringChoiceValues'].append(dictSeason) 
            else:
                # Data product
                data['stringChoiceValues'][1] = dictSeason
                
            # Update the .json file with the product type to download
            data['stringChoiceValues'][0]['value'] = prod
            
            # Should reset the file position to the beginning
            f.seek(0)
        
            # Write the updated information in the original .json file
            json.dump(data, f, indent=4)
            
            # Remove any data beyond the data you've written
            # If not truncated, .json will add additional '}' leading to cause JSON decode error
            f.truncate()
            
            # Increment the counter
            count+= 1
            
            # Opening and loading the updated .json file
            with open(dst) as f1:
                query = json.loads(f1.read())
            
            print('Downloading {} {} : {}.......'.format(nseasons, data['datasetId'], prod))
            
            # Change the working directory
            os.chdir(os.path.join(rootPath, prod))
            
            # Search in data portal with the .json tags
            matches = c.search(query)
            print('\n')
            print(matches)
            print('\n')
            
            # Download the matched dataset
            matches.download()
            print('\n')
            
            print('Successfully downloaded {} {} data for {}.'.format(yyyy, prod, tileID))
            print('\n')
                
print('Sucessfully downloaded all satellite data products.')
print('Check the file path containing .json file to see the downloaded data.')
print('\n')

# Remove the copy version of .json file
os.remove(dst)

################################################################################################################
################################################################################################################

