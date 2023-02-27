##############################################################################################################
"""
Created on Tue Apr 13 13:08:10 2021

This python script allows to download satellite (S2) derived data product for research stations 
within SITES (Swedish Infrastructure for Ecosystem Science). The script once run, automatically
creates a folder named after the station chosen by the user inside which, there will be folders
created for each satellite data products related with Plant Phenology Index (PPI) and phenology 
and productivity parameters.

Note: This script is only for internal use within SITES Spectral.

To read more about the hda python package, please visit:
https://www.wekeo.eu/docs/hda-python-lib

Important information to run this script on Terminal:
    
    1) At the home directory, there should be a hidden .hdarc file with login credentials to 
       access the WEkEO data portal for downloading various satellite products.
    
    2) There should be a base .json file called 'srcSITES.json' on the same file path as this
       python script.
    
    3) Run the Terminal
    
    4) Type the following command line script on Terminal:
        
        python /projects/eko/fs1/SITES_Spectral/FTPdatabase/Satellites/download_VIvpp.py /projects/eko/fs1/SITES_Spectral/FTPdatabase/Satellites/srcSITES.json

        General form of this cmd line: python CompletePythonFilePath.py CompleteJSONFilePath.json
    
    5) Follow the instructions displayed on the screen once you run the script
    
@author: Shangharsha
"""
##############################################################################################################
# Importing required modules
import os
import sys
import json
import shutil
from hda import Client

##############################################################################################################

# Define a specific path for an interpreter to search for
# Login information to Weekeo website is kept within this interpreter
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

##############################################################################################################
# Predefine dictionary to store 'station' information
stnName = ['Abisko', 'Asa', 'Bolmen', 'Erken', 'Grimso', 'Lonnstorp', 'Robacksdalen', 
           'Skogaryd', 'Svartberget', 'Tarfala']

print('\n')

# Iterate through the list of SITES station
for idx, stn in enumerate(stnName):
    
    # Print the station name and corresponding indexes
    print('{}  : {}'.format(idx, stn))

print('\n')

# Ask from user to select the station for which to download the satellite data products   
station = int(input("Choose one of the SITES station (For example, 0 to download data for Abisko): "))

# Ask from user which year's satellite data to download
yyyy = input('Enter which year''s satellite data to download: ')
start = yyyy + '-01-01' + 'T00:00:00.000Z'
end = yyyy + '-12-31' + 'T00:00:00.000Z'
              
# List storing the satellite data product names to be downloaded
valueList = ['PPI', 'QFLAG', 'SOSD', 'EOSD', 'LENGTH', 'AMPL', 'SPROD']

# Bounding box for downloading the correct tile for each SITES station
# Note that these bounding box coordinates doesn't represent the actual spatial extent
bbox = {0: [18.792550319107576, 67.8906193667046, 19.103915986567653, 68.02178036463253],
        1: [14.713680355042431, 57.09388769367229, 14.894288111203261, 57.200643240699065],
        2: [13.568724088354003, 56.811275199509055, 13.857437562360206, 57.016236850536956],
        3: [18.480936198124386, 59.8256240563108, 18.65866502753997, 59.880300378586725],
        4: [15.323507322319273, 59.68968895767991, 15.558648051870374, 59.798696673573424], 
        5: [13.098326599390239, 55.65669984979459, 13.13343688881537, 55.67492923063878],
        6: [20.098856578228340, 63.720530206050086, 20.38627537297891, 63.8657537138816],
        7: [12.033614084706503, 58.276784892588594, 12.264560352073318, 58.42341710330686],
        8: [19.389132036157555, 64.1060313946668, 19.685746416040367, 64.23765124249282],
        9: [18.792550319107576, 67.8906193667046, 19.103915986567653, 68.02178036463253]}

# Satellite data tile ID for each of the research station
tileID = {0: '33WXR', 
          1: '33VVD',
          2: '33VVD',
          3: '34VCM',
          4: '33VWG',
          5: '33UUB',
          6: '34VDR',
          7: '33VUE',
          8: '34WDS',
          9: '33WXR'}

##############################################################################################################
# Main program to communicate with Weekeo website and download various satellite data
# product as mentioned in the .json file              
c = Client(debug=True)

# Find the .json file to be used for downloading satellite data
queries = sys.argv[1:]

if not queries:
    queries = ["sentinel.json"]

# Create a copy of the original .json file
# Newly created copy will be used to modify and use
dst = os.path.dirname(queries[0]) + '/copysrcSITES.json'
shutil.copy2(queries[0], dst)

###############################################################################################################
# Automatically creating folders in the directory to save results into
###############################################################################################################

# Try-except block is to pass overwrite directories if exists
folders = [stnName[station]]

for folder in folders:
    try:
        os.mkdir(os.path.join(os.path.dirname(queries[0]), folder))
    except:
        pass

# Create sub-folders within the station folder, each for the satellite data products
rootPath = os.path.dirname(dst) + '/' + folders[0]

# Sub-folders to create within the station folder
subFolders = ['PPI', 'SOSD', 'EOSD', 'LENGTH', 'AMPL', 'SPROD']

# Loop over this list to create them as a subfolder    
for items in subFolders:
    try:
        
        # Temporary path creation to the subfolder items
        tempPath = os.path.join(rootPath, items)
        
        # Create new folders within the temporary path
        os.mkdir(tempPath)
    except:
        pass
        
##############################################################################################################       
# Iterate through the product list to be downloaded
for prod in valueList:
    
    # Check condition for downloading PPI and its QFLAG layer
    if (prod == 'PPI' or prod == 'QFLAG'):
    
        # Read, update the tags and modify the .json file
        with open(dst, 'r+') as f:
            
            # Returns a JSON object as a dictionary
            data = json.load(f)
            
            # Update the sample .json file with new user defined parameters   
            # Date interval 
            data['dateRangeSelectValues'][0]['start'] = start
            data['dateRangeSelectValues'][0]['end'] = end
            
            # Tile ID
            data['stringInputValues'][0]['value'] = tileID[station]
            
            # Bounding box
            data['boundingBoxValues'][0]['bbox'] = bbox[station]
        
            # Update the .json file with the product type to download
            data['stringChoiceValues'][0]['value'] = prod
        
            # Should reset the file position to the beginning
            f.seek(0)        
        
            # Write the updated information in the original .json file
            json.dump(data, f, indent=4)
                   
            # Remove any data beyond the data you've written
            # If not truncated, .json will add additional '}' leading to cause JSON decode error
            f.truncate()
    
            # Opening and loading the updated .json file
            with open(dst) as f:
                query = json.loads(f.read())
            
            print('Downloading {} : {}.......'.format(data['datasetId'], prod))
            
            # Change the working directory
            os.chdir(os.path.join(rootPath, subFolders[0]))
            
            # Search in the data portal with .json tags
            matches = c.search(query)
            print('\n')
            print(matches)
            print('\n')
    
            # Download the matched dataset
            matches.download()           
            
            print('\n')
            print('Successfully downloaded {} {} data for the {} research station.'.format(yyyy, prod, stnName[station]))
            print('\n')
            
    else:
        
        # Read, update the tags and modify the .json file
        with open(dst, 'r+') as f:
            
            # Returns a JSON object as a dictionary
            data = json.load(f)
            
            # Update the sample .json file with new user defined parameters   
            # Date interval 
            data['dateRangeSelectValues'][0]['start'] = start
            data['dateRangeSelectValues'][0]['end'] = end
            
            # Tile ID
            data['stringInputValues'][0]['value'] = tileID[station]
            
            # Bounding box
            data['boundingBoxValues'][0]['bbox'] = bbox[station]

            # Update the .json file with season number i.e. s1 or s2
            # Number of seasons
            season = ['s1', 's2']

            # Set counter
            count = 0
        
            # Iterate through seasons to download data for both seasons
            for nseasons in season:
                dictSeason = {'name':'productGroupId', 'value':nseasons}
                data['datasetId'] = 'EO:EO:EEA:DAT:CLMS_HRVPP_VPP'
                
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
                
                print('Successfully downloaded {} {} data for the {} research station.'.format(yyyy, prod, stnName[station]))
                print('\n')
                
print('Sucessfully downloaded all satellite data products.')
print('Check the file path containing .json file to see the downloaded data.')
print('\n')

# Remove the copy version of .json file
os.remove(dst)

##############################################################################################################
# Download Vegetation Phenology and Productivity Quality Flag (VPP-QFLAG)
# For more information:
'''
https://land.copernicus.eu/user-corner/technical-library/product-user-manual-of-seasonal-trajectories/
'''


