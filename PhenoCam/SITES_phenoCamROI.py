"""
***************************************************************************************************************
###########################################
ROI coordinate for PhenoCam data processing
Created on Tue Jul 21 09:59:58 2020
###########################################

This python script contains predefined ROI polygon coordinates for the SITES stations (Asa, Abisko, Skogaryd,
Röbäcksdalen, Lönnstorp, Tarfala, and Svartberget). All time series L3 products available in SITES data portal 
are generated using the ROI coordinate defined here. In addition, the script allows to visualize each ROIs for
all the phenoCam operated within SITES.  
Uncomment line of codes for each station to visualize the ROI on top of one of the images from the phenoCamera 
at each station. If needed, one can modify the ROI coordinates here and use the finalized ROI coordinates in 
the main python script that computes daily average VIs (i.e. SITES_phenoCam_dailyAvgCSV_L3.py).

Note: The script was tested on Windows environment in Python 3.7.6 version only. This script is only 
      for internal use within Swedish Infrastructure for Ecosystem Science (SITES).
      
Package installations:
    1) numpy    : pip install numpy
    2) Open-CV  : pip install opencv-python
    
Instructions for running the script:
    a) Make sure all the required modules are installed.
    b) Make sure you have access to sample image for which you want to overlay the ROIs.
    c) Give full path to sample image when asked. 

Limitations of the script:
    a) This predefined ROIs might be off the target in case there is change in camera field of view (FOV). We
       suggest using modified ROI coordinates in case of shift.
    b) Users need to comment/uncomment ROI coordinate definition line of code based on the size of the image.
       Better to check if the image size is consistent over the years. If not, use ROI coordinates that fits.
    
For enquiries, please send an email to: shangharsha.thapa@nateko.lu.se
                                        lars.eklundh@nateko.lu.se
                                        
@author: Shangharsha
***************************************************************************************************************
"""
################################################################################################################
# Module Declaration
################################################################################################################
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

################################################################################################################
# Region of Interest (ROI) for Abisko  
################################################################################################################

# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[100, 1800], [2700, 1550], [2500, 2700], [100, 2700]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 255, 0), 7)

# Second ROI polygon
pts2 = np.array([[100, 930], [3700, 1050], [3700, 1200], [100, 1400]]) 
cv2.polylines(img, np.int32([pts2]), 1, (0, 0, 255), 7)

# Third ROI polygon
pts3 = np.array([[750, 600], [3700, 650], [3500, 950], [100, 830]]) 
cv2.polylines(img, np.int32([pts3]), 1, (255, 0, 0), 7)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='g', marker='s',  label='ROI 1'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='r', marker='s',  label='ROI 2'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='b', marker='s',  label='ROI 3')]
  
plt.legend(handles=handles, fontsize = 20, loc = 'lower right')

'''
################################################################################################################
# Region of Interest (ROI) for Skogaryd-P03  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[500, 500], [2500, 500], [2500, 1750], [500,1750]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Skogaryd-P02  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[2550, 700], [2550, 1850], [700, 1850], [700, 700]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Skogaryd-P01  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[300, 1800], [300, 400], [2700, 400], [2700, 1200], [2400, 1400], [2200, 1800]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# Second ROI polygon
pts1 = np.array([[2600, 1950], [2600, 1680], [2950, 1680], [2950, 1950]]) 
cv2.polylines(img, np.int32([pts1]), 1, (255, 0, 0), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='blue', marker='s', label='ROI 2')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Skogaryd SWE-SRC-STD-FOR-P01 (Clear-cut) 
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[200, 1350], [200, 400], [1850, 400], [1850, 1350]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Svartberget Forest 
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[300, 1500], [300, 600], [2800, 600], [2800, 1500]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Svartberget Degerö  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[100, 400], [280, 800], [1200, 800], [900, 350]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# ROI polygon (Valid only for half of the images of 2016)
# pts1 = np.array([[100, 250], [280, 700], [950, 700], [800, 250]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Lönnstorp-P01  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

################################################################################################################
# Create a polygon for region of interest
# Valid only for all images of 2018 (800*600) and 2019 (Size1)

# # First ROI polygon
# pts1 = np.array([[30, 550], [30, 250], [450, 210], [770, 350], [770, 550]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (255, 255, 255), 3)

# # Second ROI polygon
# pts2 = np.array([[10, 200], [10, 180], [300, 155], [380, 170]]) 
# cv2.polylines(img, np.int32([pts2]), 1, (255, 0, 0), 2)

# # Third ROI Polygon
# pts3 = np.array([[10, 160], [10, 165], [270, 140], [250, 138]]) 
# cv2.polylines(img, np.int32([pts3]), 1, (0, 0, 255), 2)

# # Fourth ROI Polygon
# pts4 = np.array([[10, 150], [10, 145], [220, 125], [235, 130]]) 
# cv2.polylines(img, np.int32([pts4]), 1, (0, 255, 255), 2)

# # Fifth ROI Polygon
# pts5 = np.array([[10, 135], [10, 132], [190, 115], [200, 118]]) 
# cv2.polylines(img, np.int32([pts5]), 1, (0, 255, 0), 2)

# # Sixth ROI Polygon
# pts6 = np.array([[335, 108], [500, 110], [780, 160], [780, 210]]) 
# cv2.polylines(img, np.int32([pts6]), 1, (255, 0, 255), 2)

################################################################################################################

################################################################################################################
# Create a polygon for region of interest
# Valid for all images of 2019 (Size2) and all images from 2020 onwards (2048*3072)

# First ROI polygon
pts1 = np.array([[100, 2000], [100, 900], [1600, 750], [3000, 1350], [3000, 2000]]) 
cv2.polylines(img, np.int32([pts1]), 1, (255, 0, 0), 5)

# Second ROI polygon
pts2 = np.array([[50, 810], [50, 720], [1200, 615], [1400, 670]]) 
cv2.polylines(img, np.int32([pts2]), 1, (0, 255, 0), 5)

# Third ROI Polygon
pts3 = np.array([[50, 660], [50, 630], [1000, 545], [1140, 560]]) 
cv2.polylines(img, np.int32([pts3]), 1, (0, 0, 255), 5)

# Fourth ROI Polygon
pts4 = np.array([[50, 600], [50, 590], [870, 510], [980, 515]]) 
cv2.polylines(img, np.int32([pts4]), 1, (255, 255, 0), 5)

# Fifth ROI Polygon
pts5 = np.array([[50, 558], [50, 545], [800, 468], [900, 470]]) 
cv2.polylines(img, np.int32([pts5]), 1, (255, 0, 255), 5)

# Sixth ROI Polygon
pts6 = np.array([[1380, 460], [1850, 450], [3000, 655], [3000, 850]]) 
cv2.polylines(img, np.int32([pts6]), 1, (0, 0, 0), 5)

################################################################################################################

plt.rcParams['figure.figsize'] = (16,8)
plt.figure(1)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='b', marker='s', label='ROI1'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='g', marker='s', label='ROI2'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='r', marker='s', label='ROI3'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='c', marker='s', label='ROI4'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='m', marker='s', label='ROI5'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='k', marker='s', label='ROI6')]
  
plt.legend(handles=handles, fontsize = 20, loc = 'lower right')
'''
'''
################################################################################################################
# Region of Interest (ROI) for Lönnstorp-P02  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

################################################################################################################
# Create a polygon for region of interest
# Valid only for all images of 2018

# # First ROI polygon
# pts1 = np.array([[30, 280], [100, 210], [210, 200], [250, 260]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 2)

# # Second ROI polygon
# pts2 = np.array([[300, 260], [250, 200], [410, 190], [570, 240]]) 
# cv2.polylines(img, np.int32([pts2]), 1, (0, 255, 0), 2)

# # Third ROI polygon
# pts3 = np.array([[650, 240], [450, 180], [570, 180], [785, 235]]) 
# cv2.polylines(img, np.int32([pts3]), 1, (255, 0, 0), 2)

# # Fourth ROI polygon
# pts4 = np.array([[615, 175], [720, 180], [790, 200], [790, 215]])
# cv2.polylines(img, np.int32([pts4]), 1, (255, 0, 255), 2)

################################################################################################################

################################################################################################################
# Create a polygon for region of interest
# Valid for all images from 2019 onwards

# First ROI polygon
pts1 = np.array([[100, 950], [350, 720], [820, 670], [950, 880]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 5)

# Second ROI polygon
pts2 = np.array([[1100, 880], [930, 650], [1450, 630], [2000, 830]]) 
cv2.polylines(img, np.int32([pts2]), 1, (0, 255, 0), 5)

# Third ROI Polygon
pts3 = np.array([[2150, 800], [1630, 620], [2000, 615], [2700, 790]]) 
cv2.polylines(img, np.int32([pts3]), 1, (255, 0, 0), 5)

# Fourth ROI Polygon
pts4 = np.array([[2150, 600], [2400, 600], [3035, 740], [2950, 780]]) 
cv2.polylines(img, np.int32([pts4]), 1, (0, 0, 0), 5)

################################################################################################################

plt.rcParams['figure.figsize'] = (16,8)
plt.figure(1)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s',  label='ROI1'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='lime', marker='s', label='ROI2'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='blue', marker='s', label='ROI3'),
           Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='black', marker='s',label='ROI4')]
  
plt.legend(handles=handles, fontsize = 20, loc = 'lower right')
'''
'''
################################################################################################################
# Region of Interest (ROI) for Lönnstorp-P03  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

################################################################################################################
# Create a polygon for region of interest
# Valid only for all the images of 2018

# # First ROI polygon
# pts1 = np.array([[30, 550], [30, 270], [120, 230], [700, 230], [770, 300], [770, 550]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 3)

################################################################################################################

################################################################################################################
# Create a polygon for region of interest
# Valid for all the images from 2019 onwards

# First ROI polygon
pts1 = np.array([[250, 1800], [250, 900], [2850, 900], [2850, 1800]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

################################################################################################################

plt.rcParams['figure.figsize'] = (16,8)
plt.figure(1)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s',  label='ROI1')]  
plt.legend(handles=handles, fontsize = 20, loc = 'lower right')
'''
'''
################################################################################################################
# Region of Interest (ROI) for Tarfala  
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[200, 1750], [200, 550], [2900, 550], [2900, 1750]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s',  label='ROI 1')]
plt.legend(handles=handles, fontsize = 20, loc = 'lower right')
'''
'''
################################################################################################################
# Region of Interest (ROI) for Asa 
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon
pts1 = np.array([[100, 1200], [100, 400], [2500, 400], [2500, 1200]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Röbacksdalen- P01 
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon (Until 2021)
# pts1 = np.array([[500, 1700], [200, 1250], [200, 500], [1000, 350], [2900, 400], [2900, 1700]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# ROI polygon (From 2022)
pts1 = np.array([[50, 120], [50, 500], [750, 500], [750, 120]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 5)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
'''
################################################################################################################
# Region of Interest (ROI) for Röbacksdalen- P02 
################################################################################################################
# Define complete file path of sample image to visualize the ROI extent
# Example: 'H:\Phenocam\Skogaryd\SWE-SRC-STM-FOR-P01\L1\2021\SWE-SRC-STD-FOR-P01_20210527_147_1300.jpg'
imgDir = input('Enter the path where your sample image is located: ')[1:-1]

# Reading image
img = cv2.imread(imgDir)

# Create a polygon for region of interest
# First ROI polygon (Until 2021)
# pts1 = np.array([[200, 1800], [200, 750], [2900, 750], [2900, 1800]]) 
# cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 10)

# ROI polygon (From 2022)
pts1 = np.array([[100, 200], [100, 500], [700, 500], [700, 200]]) 
cv2.polylines(img, np.int32([pts1]), 1, (0, 0, 255), 5)

# OpenCV represents image in reverse order BGR; so convert it to appear in RGB mode and plot it
plt.rcParams['figure.figsize'] = (16,8)
plt.figure(0)
plt.axis('on')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

handles = [Line2D([0], [0], linestyle='none', markersize=20, mfc='none', mec='red', marker='s', label='ROI 1')]
plt.legend(handles=handles, fontsize = 20)
'''
################################################################################################################
################################################################################################################
