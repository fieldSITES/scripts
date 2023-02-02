# a.	In this file you can change certain thresholds for given parameters. As of now only the ones shown in the file are able to be controlled for. Keep in mind that all values above or below the thresholds you set will be deleted later. Make sure to account for extreme events in the past and to revisit this step every time you use the script to adjust the thresholds. 
# b.	The thresholds are either in groups of 12 (For each month, starting from January) or one value that is general for the whole year
# c.	Save and close the “parameters.R” file


MaxTotalRad <- c(350.0,520.0,750.0,900.0,990.0,1020.0,990.0,910.0,760.0,580.0,390.0,290.0) #Watts/m2
MinTotalRad <- c(-10.0) #Values below 0 and above the Min-Threshold are set to 0

MaxPAR <- c(650.0,850.0,1230.0,1520.0,1720.0,1840.0,1790.0,1590.0,1300.0,950.0,720.0,630.0) #micro mole/m2/s
MinPAR <- c(-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0,-12.0) #Values below 0 and above the Min-Threshold are set to 0

MaxWtemp <- c(10.0,9.0,10.0,14.0,23.0,27.0,30.0,29.0,28.0,22.0,15.0,12.0) #Degree Celsius
MinWtemp <- c(-1.0,-1.0,-1.0,-1.0,-1.0,6.0,11.0,11.0,6.0,1.0,-1.0,-1.0)

MaxAirTemp <- c(14.0,14.0,18.0,26.0,30.0,35.0,39.0,37.0,31.0,24.0,18.0,15.0) #Degree Celsius
MinAirTemp <- c(-30.0,-26.0,-22.0,-11.0,-5.0,0.0,4.0,3.0,-2.0,-8.0,-14.0,-25.0)

MaxWind <- 35.0 #m/s
MinWind <- 0.0

MaxWindDir <- 360.0 #Direction in degrees
MinWindDir <- 0.0

MaxLev <- 10.7 #Water level
MinLev <- 9.0

MinHum <- 10.0 # Humidity
MaxHum <- 100.0

MaxAirPress <- 1060 #in hPa, Be aware that SITES is using Pa
MinAirPress <- 940