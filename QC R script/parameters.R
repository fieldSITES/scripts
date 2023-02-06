# a.	Exchange the variables in the brackets (“EXAMPLE”) with the name of the corresponding variable in your raw data. Not used parameters can be left empty (“”). At the moment only the parameters shown in this file can be used in the QC script. Be aware that R is case-sensitive!
# b.	Scroll down in the file to adjust the parameters that should be used for the “Repeat” step. You can delete the ones you do not want to check. Make sure that the first line does not contain the “rbind” command.
# c.	Save and close the “parameters.R” file


# State how your variable for Time is called within the quotation marks 
var_time <- as.character("TMSTAMP")

# State how your variable for RAD is called within the quotation marks#
var_rad <- as.character("SW_Rad_Avg")

# State how your variable for PAR is called within the quotation marks
var_par <- as.character("PAR_Rad_Avg")

# State how your variable for Water temp. (1m) is called within the quotation marks 
var_Wtmp1 <- as.character("Water_Temp_1m_Avg")

# State how your variable for Water temp. (3m) is called within the quotation marks 
var_Wtmp3 <- as.character("Water_Temp_3m_Avg")

# State how your variable for Water temp. (15m) is called within the quotation marks 
var_Wtmp15 <- as.character("Water_Temp_15m_Avg")

# State how your variable for "Air temp. from the humidity sensor" is called within the quotation marks 
var_Htmp <- as.character("Air_Temp_HS_Avg")

# State how your variable for Air temp. is called within the quotation marks 
var_tmp <- as.character("Air_Temp_AS_Avg")

# State how your variable for Wind speed is called within the quotation marks 
var_wspd <- as.character("MeanWS")

# State how your variable for Wind direction is called within the quotation marks 
var_wdir <- as.character("WindDir")

# State how your variable for Water level is called within the quotation marks 
var_lvl <- as.character("Water_Level_Avg")

# State how your variable for Humidity is called within the quotation marks 
var_hum <- as.character("RelHumidity_Avg")

# State how your variable for Air pressure is called within the quotation marks 
var_pre <- as.character("AirPressure_hPa_Avg")


#### The following parameters will be used to look for repeated sequences. Add or remove the ones you want to use
column_names <- var_Wtmp1                    # Water Temp 1m. !NO RBIND HERE AS THE LIST WILL BE CREATED HERE!
column_names <- rbind(column_names,var_Wtmp3) # Water Temp 3m.
column_names <- rbind(column_names,var_Wtmp15) # Water Temp 15m.
column_names <- rbind(column_names,var_Htmp) # Air temp. Humidity sensor
column_names <- rbind(column_names,var_tmp)  # Air temp.
column_names <- rbind(column_names,var_wspd) # Wind speed
column_names <- rbind(column_names,var_wdir) # Wind direction
column_names <- rbind(column_names,var_hum)  # Humidity
column_names <- rbind(column_names,var_pre)  # Air pressure

