"""
***************************************************************************************************************
#########################################################
Mean DN values extraction for Radiometric calibration (RGB)

Created on Fri Mar 15 16:28:21 2024
#########################################################

In this script, the image zooms in when the left mouse button is clicked. Then it maintains that zoom extent 
for entire images and allow users to draw regions of interest for extracting mean DN values and associated 
standard deviation. Mean DN values for all ROIs and all 3 channels: Red, Green, and Blue. The extracted mean
DN values are exported as .xlsx file in the same directory as the calibration images. 

Note: The script was tested on windows environment in Python 3.10.13 version only.

Package installations:
    1) roipoly  : pip install roipoly or pip install git+https://github.com/jdoepfert/roipoly.py
    2) numpy    : pip install numpy
    3) pandas   : pip install pandas
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Run Anaconda Prompt or general Terminal where you can locate the installed Python.
    c) Use the following command to run (Give complete path to where your script is located):
    
                (base) D:\MScGeomatics>python ".../SITES_UAV-RGB-DJI_MeanDN-RefPanels.py"
                
    d) Follow the instructions displayed on the Terminal screen once you run the script.
    e) Provide complete path to where the calibration images are located. And hit 'Enter'.
    f) Click on the middle part of where the calibration panel images are located. It will create zoom
       extent around that. Close the image window and it will maintain the same extent for drawing the
       region of interst.
    g) Click on New ROI button and start drawing region of interest. When drawing ROIs left click to draw 
       vertices and right click to complete the ROI. Draw ROIs for all three reflectance panels (9%, 23% 
       and 44% in this case) one by one for each band. Click 'Finish' button as soon as you are done with 
       drawing. Repeat this step for all calibration images. 
    
Limitations of the script:
    a) Script is programmed to handle DJI P4 RGB images only.
    b) Roipoly package doesn't work properly in Spyder. No issues running through the Terminal though.
    c) This script can only handle three ROIs.
    
Important information:
    a) Read more on RoiPoly package: 
       https://github.com/jdoepfert/roipoly.py
    b) Make sure to draw ROIs on similar fashion for all calibration pictures.

For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se

@author: Shangharsha.Thapa
***************************************************************************************************************
"""
###############################################################################################################
# Importing required modules
###############################################################################################################
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from roipoly import MultiRoi

###############################################################################################################
# Image path definition
###############################################################################################################
# Get path to all calibration target images
print('\n')
thePath = input('Enter the path where the reflectance panel images are located: ')

# Get list of all images within the user defined directory
imgList = sorted(glob.glob(os.path.join(thePath, '*.JPG')))

###############################################################################################################
# Automatically creating folders in the current working directory to save results 
###############################################################################################################
print('\n')
print('Creating new folders to store the results......')

# Try-except block is to pass overwrite directories if exists
folders = ['Plots', 'MeanDN']
for folder in folders:
    try:
        os.mkdir(os.path.join(thePath, folder))
    except:
        pass

print('\n')
print('Created new folder to store the results.')

###############################################################################################################

# Load your RGB image
image_path = imgList[0]
image = np.array(Image.open(image_path))

# Initialize variables to store zoomed extent
rowCol = None

# Function to handle zooming
def zoom(event):
    global rowCol
    if event.inaxes == ax:
        # Get the coordinates of the clicked point
        x, y = int(event.xdata), int(event.ydata)
        # Set the limits for zooming
        xlim = (max(0, x - 80), min(image.shape[1], x + 80))
        ylim = (max(0, y - 80), min(image.shape[0], y + 80))
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        plt.draw()
        
        # Store the zoomed extent
        rowCol = [int(event.ydata - 80), int(event.ydata + 80), int(event.xdata - 80), int(event.xdata + 80)]


# Define figure size
plt.rcParams['figure.figsize'] = (16,8)
        
# Create a subplot for drawing the image
fig, ax = plt.subplots()

# Display the image
ax.imshow(image)
ax.set_title('Click to zoom (buffered zone of 50 pixels)')

# Connect zoom event
plt.connect('button_press_event', zoom)
plt.show()

###############################################################################################################
# Iterate through the list of calibration target images
# Extract mean and standard deviation for each panels per image
# Write the extracted information to a .csv file
###############################################################################################################
print('\n')
print('Getting ROI polygons for 3 panels from the user......')

# Get the row and column extent to plot
ymin, ymax, xmin, xmax = rowCol

# Empty dictionary to store data to be exported
meanDN_Panels = {}
stdDN_Panels  = {}

# Iterating through the images
for im in imgList:
    
    # Get image name
    imgName = os.path.basename(im).split('.')[0]
    
    # Load RGB image
    img = np.array(Image.open(im))
    
    # Create a subplot for drawing the image with the same zoom extent
    fig, ax = plt.subplots()
    
    # Display the image with the zoomed coordinates
    plt.imshow(img[ymin:ymax, xmin:xmax])
    ax.set_title('Draw regions of interest')
    ax.text(3, 5, imgName, fontsize=12, color='blue', bbox=dict(facecolor='whitesmoke', alpha=0.5))
    
    # Initialize a MultiRoi instance to store ROIs
    multi_roi = MultiRoi(fig=fig, ax=ax, roi_names=['9% Panel', '23% Panel', '44% Panel'])

    # Function to handle mouse button press event for drawing ROIs
    def on_press(event):
        if event.inaxes == ax and not multi_roi.has_been_closed():
            multi_roi.add_roi(event)
            multi_roi.display_rois()
            plt.draw()

    # Register the mouse button press event callback for drawing ROIs
    fig.canvas.mpl_connect('button_press_event', on_press)

    plt.show(block=False)
    
    # Empty list to store ROI names for displaying in the legend
    roi_names = []
    roi_means = {}
    roi_stds  = {}
    
    # After closing the plot, calculate mean and standard deviation for each ROI
    for idx, roi in multi_roi.rois.items():
        
        # Display created ROI on top of the image
        roi.display_roi()
        roi_names.append(idx)
               
        # Compute mean and standard deviation over that ROI.
        # Red Channel
        data_red = roi.get_mean_and_std(img[:,:,0][ymin:ymax, xmin:xmax])
        mean_red, std_red = data_red
        
        # Green Channel
        data_gre = roi.get_mean_and_std(img[:,:,1][ymin:ymax, xmin:xmax])
        mean_gre, std_gre = data_gre
        
        # Blue Channel
        data_blu = roi.get_mean_and_std(img[:,:,2][ymin:ymax, xmin:xmax])
        mean_blu, std_blu = data_blu
        
        # Mean DN for R, G, and B channel for user drawn ROI
        # Note user should always draw ROI on similar fashion
        # In this case, first 9%, then 23% and finally 44%
        tempMean_RGB = [mean_red, mean_gre, mean_blu]
        tempStd_RGB = [std_red, std_gre, std_blu]
                
        # Update the dictionaries with mean and standard deviation of ROI drawn by user
        roi_means[idx] = tempMean_RGB
        roi_stds[idx]  = tempStd_RGB
                                   
    meanDN_Panels[imgName] = roi_means
    stdDN_Panels[imgName] = roi_stds
       
    ax.text(3, 5, imgName, fontsize=12, color='blue', bbox=dict(facecolor='whitesmoke', alpha=0.5))
    plt.legend(roi_names, loc = 'best')
    outName = os.path.join(thePath + r'\Plots\{}.png'.format(imgName))
    fig.savefig(outName, bbox_inches='tight')
    plt.close()

###############################################################################################################
# Create an excel sheet to save the mean DN values per band for all three reflectance panels
###############################################################################################################
print('\n')
print('Exporting the mean DN values per spectral band to a .xlsx file......')

# Field name definition
heading = ['Image', 'MeanDN_9', 'Std_Dev', 'MeanDN_23', 'Std_Dev', 'MeanDN_44', 'Std_Dev']

# Spectral band definition for DJI P4 MSP
bands = ['RED', 'GRE', 'BLU']

red = []
gre = []
blu = []

# Iterate over the dictionary
j = 0
for bName in bands:
    
    for k in meanDN_Panels.keys():
        
        tmpMeanDict = meanDN_Panels[k]
        tmpStdvDict = stdDN_Panels[k]
        
        meanDN_9 = tmpMeanDict['9% Panel'][j]
        stdDVn_9 = tmpStdvDict['9% Panel'][j]
        
        meanDN_23 = tmpMeanDict['23% Panel'][j]
        stdDVn_23 = tmpStdvDict['23% Panel'][j]
    
        meanDN_44 = tmpMeanDict['44% Panel'][j]
        stdDVn_44 = tmpStdvDict['44% Panel'][j]
    
        data2store = [k, meanDN_9, stdDVn_9, meanDN_23, stdDVn_23, meanDN_44, stdDVn_44]
        
        if bName == 'RED':
            red.append(data2store)
        
        elif bName == 'GRE':
            gre.append(data2store)
        
        else:
            blu.append(data2store)
            
    j += 1

# Creating dataframe using lists of list
tempRdf = pd.DataFrame(red, columns = heading)
tempBdf = pd.DataFrame(gre, columns = heading)
tempGdf = pd.DataFrame(blu, columns = heading)

# create a excel writer object
pathDN = os.path.join(thePath + r'\MeanDN\extractedDN.xlsx')

with pd.ExcelWriter(pathDN, engine="xlsxwriter") as writer:
   
    # use to_excel function and specify the sheet_name and index 
    # to store the dataframe in specified sheet
    tempRdf.to_excel(writer, sheet_name="RED", index=False)
    tempBdf.to_excel(writer, sheet_name="GREEN", index=False)
    tempGdf.to_excel(writer, sheet_name="BLUE", index=False)
  
###############################################################################################################
# Create excel sheet with average DN values of all reflectance panel images ready for radiometric calibration.
###############################################################################################################
heading1 = ['RED_9', 'RED_23', 'RED_44', 'GRE_9', 'GRE_23',	'GRE_44', 'BLU_9', 'BLU_23', 'BLU_44']

# Read individual sheets as separate dataframes
redMeanDF = pd.read_excel(pathDN, sheet_name='RED')
greMeanDF = pd.read_excel(pathDN, sheet_name='GREEN')
bluMeanDF = pd.read_excel(pathDN, sheet_name='BLUE')

# Iterate over the dataframe columns 
# Compute column averages for all dataframes
cols = list(redMeanDF.columns)

avgRedDN = []
avgGreDN = []
avgBluDN = []

for colnbr in range(1, len(cols), 2):
    tempRedDN = redMeanDF[cols[colnbr]].mean()
    tempGreDN = greMeanDF[cols[colnbr]].mean()
    tempBluDN = bluMeanDF[cols[colnbr]].mean()
    
    avgRedDN.append(tempRedDN)
    avgGreDN.append(tempGreDN)
    avgBluDN.append(tempBluDN)

# Merge all three lists
mergedDN = avgRedDN + avgGreDN + avgBluDN

# Convert list to dataframe
avgDF = pd.DataFrame([mergedDN], columns = heading1)

# Create a new excel file in the path
avgPathDN = os.path.join(thePath + r'\MeanDN\avg4cal.xlsx')

# Export the dataframe to .xlsx file
with pd.ExcelWriter(avgPathDN, engine='xlsxwriter') as writer:
    
    avgDF.to_excel(writer, sheet_name = 'EmpLineValues', index=False)

print('\n')
print('Exported successfully.')
print('Check the folder i.e. MeanDN for the extracted average DN values.')
###############################################################################################################
