"""
***************************************************************************************************************
#########################################################
Step 2:
Irradiance trend and normalization 

Created on Tue Aug 17 14:51:02 2021
#########################################################

This Python script reads the extracted irradiance data from Step 1 and plots the raw irradiance data along with
the fitted irradiance data using either spline or polynomial of degree 'n' based on the nature of the data. The
order of polynomial needs to be adjusted in a way that best fits the irradiance data. This step is preferred if 
the irradiance data matches with Case 9 (See: SITES Spectral - Data Quality Flagging (QFLAG) Documentation). 
The script optionally saves the fitted polynomial to import and use for irradiance compensation of images
together with exposure compensation and vignetting correction in Step 3.

Note: The script was tested on windows environment in Python 3.7.6 version only. This script is only for the 
      internal use within SITES.

Package installation:
    a) xlsxwriter     
    b) SciPy
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Change the order of polynomial and spline fit. An ideal way is to start with a lower order
       and go to higher order if needed based on the nature of the data.
    c) Set 'saveTrend' variable to False at the beginning. 
    d) Run the script and follow the instructions displayed until the best fit polynomial/spline
       is achieved. Set 'saveTrend' to True and run the script again. When defining the path it 
       should be something like: 
                ...SWE-LON-SFAB-AGR-msp-210604-U01\SWE-LON-SFAB-AGR-msp-210604-U01_seq.xlsx
    e) Check .xlsx sheet with irradiance normalization factor for both polynomial and spline fit
       once the script is successfully completed.
    
Limitations of the script:
    a) Defining order of polynomial to fit the irradiance data demands very good knowledge of the 
       radiometry and normalization technique.
    
Important information:
    a) SITES Spectral - Data Quality Flagging (QFLAG) Documentation:
       https://meta.fieldsites.se/objects/yHjlJ9dsmPzMNAGPswfSlEtC
              
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se

@author: Shangharsha (Modified after Dr. Per-Ola Olsson)
"""
################################################################################################################
# Importing required modules
################################################################################################################
import os
import xlsxwriter
import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt

################################################################################################################
# Get complete file path of .xlsx sheet from Step 1
# This excel sheet contains the extracted sunshine sensor irradiance data for a multispectral flight
fp = input("Enter complete file path to the raw irradiance data (.xlsx from Step 1): ")

################################################################################################################
# Define order for a polynomial and spline fit
# Spline smoothing: lower number => closer to data
################################################################################################################  
polyOrder = 5
splOrder = 5
splSmooth = 3000

# Reading excel sheet
exifData = pd.ExcelFile(fp)

# Saving trend or not
# Set True to save
saveTrend = False

################################################################################################################   
if saveTrend:
    # Creating new Excel for saving the fitted polynomials
    fb = fp.split('.')[0]
    
    # Define file name for excel sheet to save the normalized irradiance data 
    newExcel = fb + '_TREND' + '_order_' + str(polyOrder) + '_Spl_' + str(splOrder) + '_' 
    + str(splSmooth) + '.xlsx'
    
    # Create a new excel file and add a worksheet. 
    # Need to open here to add normalization factor for all bands
    workbook = xlsxwriter.Workbook(newExcel)

################################################################################################################   
# List with bands (Excel sheets to read)
seqBandList = ['Blue', 'Green', 'Red', 'RedEdge', 'NIR']

for idx, band in enumerate(seqBandList):
    
    bandSheet = pd.read_excel(exifData, band)
    
    irr = bandSheet['Irradiance']
    img = bandSheet['Img']
    
    x = range(1,len(irr)+1)
    coeffs = np.polyfit(x, irr, polyOrder)
    irrFit = np.polyval(coeffs, x)
    
    print(fp + ',\nBand: ' + band)
    print('PolyOrder: ' + str(polyOrder))
    plt.plot(irr)
    plt.plot(irrFit)
    plt.show()
    
    # Normalising polynomial trend
    tm = np.mean(irrFit)
    normTrend = irrFit/tm
    
    ############################################################################################################
    # Testing with splines
    
    xIn = range(1,len(irr)+1)    
     
    # UnivariateSpline
    # k is the order. default = 3, max = 5
    # s is smoothing factor. default = None => len of data. s=0 => pass all points    
    spl = interpolate.UnivariateSpline(xIn, irr, k=splOrder, s=splSmooth)
        
    xOut = np.arange(1, len(irr)+1)
    splFit = spl(xOut)
    
    # Normalising spline trend
    splm = np.mean(splFit)
    splNormTrend = splFit/splm
    
    plt.plot(xOut, splFit, color='orange')
    plt.plot(xIn, irr, 'b')
    plt.show()
    
    ############################################################################################################
    if saveTrend:
        worksheet = workbook.add_worksheet(band)
        
        # Add headings
        worksheet.write(0, 0, 'Img')
        worksheet.write(0, 1, 'Poly trend')
        worksheet.write(0, 2, 'Poly norm')
        worksheet.write(0, 3, 'Spline trend')
        worksheet.write(0, 4, 'Spline norm')
        
        # Add data
        # Want row to start at 1 since row = 0 is for heading
        for row in range(1,len(irrFit)+1):
            worksheet.write(row, 0, img[row-1])
            worksheet.write(row, 1, irrFit[row-1])
            worksheet.write(row, 2, normTrend[row-1])
            worksheet.write(row, 3, splFit[row-1])
            worksheet.write(row, 4, splNormTrend[row-1])
    
if saveTrend:
    # Closing the Excel sheet   
    workbook.close()    

    print ('Finished normalizing the irradiance data.')
    print ('Check the newly created {} file for information about the normalized irradiance data.'
           .format(os.path.basename(newExcel)))
 
################################################################################################################
################################################################################################################