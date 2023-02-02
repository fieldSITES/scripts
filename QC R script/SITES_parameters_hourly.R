### This is used to change the parameters from each station to the respective SITES guideline
###
###


#Change column names from the Erken standard to SITES standard

#Example: 
#names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'NAME OF YOUR PARAMETER in your datasheet'] <- 'SITES SPECIFIC NAME FOR PARAMETER'


#TMSTAMP to TIMESTAMP
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'TMSTAMP'] <- 'TIMESTAMP'
#Air_Temp_HS_Avg to TA_1_SHIELD
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Air_Temp_HS_Avg'] <- 'TA_1_SHIELD'
#Air_Temp_AS_Avg to TA_2_VENT 
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Air_Temp_AS_Avg'] <- 'TA_2_VENT'
#RelHumidity_Avg to RH_SHIELD
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'RelHumidity_Avg'] <- 'RH_SHIELD'
#Vapor_Pressure_Avg to VP_SHIELD
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Vapor_Pressure_Avg'] <- 'VP_SHIELD'
#SW_Rad_Avg to SW_IN
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'SW_Rad_Avg'] <- 'SW_IN'
#PAR_Rad_Avg to PPFD
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'PAR_Rad_Avg'] <- 'PPFD'
#MeanWS to WS
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'MeanWS'] <- 'WS'
#WindVector to WV
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'WindVector'] <- 'WV'
#WindDir to WD 
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'WindDir'] <- 'WD'
#StdDevWindDir to WD_STD
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'StdDevWindDir'] <- 'WD_STD'
#WindSpeed_Max to WS_MAX
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'WindSpeed_Max'] <- 'WS_MAX'
#WindSpeed_TMx to TIME_WS_MAX
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'WindSpeed_TMx'] <- 'TIME_WS_MAX'
#WindSpeed3_Avg to WS_CUBED
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'WindSpeed3_Avg'] <- 'WS_CUBED'
#Rain_Tot to P
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Rain_Tot'] <- 'P'
#Water Temp. -1m.
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Water_Temp_1m_Avg'] <- 'TW_-1m'
#Water Temp. -3m.
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Water_Temp_3m_Avg'] <- 'TW_-3m'
#Water Temp. -15m.
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Water_Temp_15m_Avg'] <- 'TW_-15m'
#Water Level
names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'Water_Level_Avg'] <- 'LL'

#AirPressure_hPa_Avg to PA (SITES records the pressure in Pa while Erken records in hPa. All values will be converted)

names(QC_data_final_SITES)[names(QC_data_final_SITES) == 'AirPressure_hPa_Avg'] <- 'PA'
QC_data_final_SITES$PA <- QC_data_final_SITES$PA*100



#What does the SITES data contain in their uploaded data?

#Meteorological DAILY
col_daily_met <- c("TIMESTAMP","TA_1_SHIELD","TA_2_VENT","RH_SHIELD","VP_SHIELD","SW_IN","PPFD","WS","WV","WD","WD_STD","WS_MAX","TIME_WS_MAX","WS_CUBED","P","PA") 

#Water temperature profile DAILY
col_daily_profile <- c("TIMESTAMP","TW_-1m","TW_-3m","TW_-15m")

#Water level DAILY
col_daily_lvl<- c("TIMESTAMP",	"LL")


