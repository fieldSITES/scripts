"""
***************************************************************************************************************
###############################################
UAV flight metadata extraction from KOBOToolbox

Created on Wed Apr 28 16:12:17 2021
###############################################

This Python script uses a package KoboExtractor that provides a wrapper around part of the KoBoToolbox API, with
the main goal being to ease the downloading of survey responses of UAV flights carried out at each SITES station.
The script is adapted from the KoboExtractor documentation page. 

Note: The script was tested on windows environment in Python 3.7.6 version only. KoboExtractor requires a Python
      version of 3.6+. This script is only for the internal use within SITES.

Instructions for running the script:
    a) Users are supposed to provide the API key token to KoboToolbox.
    b) The KOBOToolbox API key can be found inside Account settings of KOBOToolbox platform.
      
Important information:
    a) Full documentation of KoboExtractor:
       https://koboextractor.readthedocs.io

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import sys
import subprocess
import pandas as pd

# Check if a module required to run this script is installed
try:
    from koboextractor import KoboExtractor
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'koboextractor'])
finally:
    from koboextractor import KoboExtractor
    
################################################################################################################
# Ask from user the API token from account settings
################################################################################################################
KOBO_TOKEN = input("Enter API Token: ")

# Initialise the KoboExtractor
kobo = KoboExtractor(KOBO_TOKEN, 'https://kf.kobotoolbox.org/api/v2')

# Lists all surveys in the KoBoToolbox account
assets = kobo.list_assets()

# Get the unique ID of the first asset in your KoBoToolbox account
asset_uid = assets['results'][0]['uid'] #0 refers to first survey form in the system

# Ask from user specific date from which to start downloading rows
date = input("Enter a date from which you want to download data (yyyy-mm-dd): ")
 
# Gets all information on an asset (survey) in the associated KoBoToolbox account
new_data = kobo.get_data(asset_uid, submitted_after = date)

print('\n')
print('{} records are found in the KOBO toolbox survey form.'.format(new_data['count']))

################################################################################################################
# Exporting all the downloaded results to .xlsx file
################################################################################################################
print('\n')
print('Exporting all the records into a {}.xlsx file.'.format(''.join(assets['results'][0]['name'].split())))

# Extract 'results' from 'new_data' which stores the records that we are looking for
records = new_data['results']

# Converting list of dictionaries to dataframe
extractedData = pd.DataFrame(records)

# Get the current working directory
cwd = os.getcwd()

# Save the file into current working directory as:
savePath = cwd + '\\' + ''.join(assets['results'][0]['name'].split()) + '.xlsx'

# Convert the dataframe into excel file
extractedData.to_excel(savePath, sheet_name='KOBO survey')

print('\n')
print('{}.xlsx exported successfully.'.format(''.join(assets['results'][0]['name'].split())))
print('\n')
print('Check current working directory to retrieve the exported file.')

################################################################################################################
################################################################################################################