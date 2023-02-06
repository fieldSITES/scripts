# Quality control (QC) for hourly  data. R script adapted and further developed based on Don Pierson's IDL script.

###################################################################################################################################################
###################################################################################################################################################
####################################                                                      #########################################################
####################################    TO EXECUTE THE SCRIPT USE CTRL+SHIFT+S            #########################################################
####################################                                                      #########################################################   
### To enhance readability, R Studio is recommended. Increase the size of the script-window that the this box is aligned to ensure ################
###                                               better formatting of the code                                                    ################ 
###################################################################################################################################################
###################################################################################################################################################
###################################################################################################################################################



######
##### R packages used ####
packages <- c("readr", "lubridate", "insol", "dplyr", "data.table", "R.utils", "naniar")

install.packages(setdiff(packages, rownames(installed.packages())))  

library(readr) #Package to read the csv file
library(lubridate) #Used in Gapfill. Package that contains the "hour"-function used in the loop to check the time
library(insol) #Used in Max/Min. For data conversion in julian date
library(dplyr) #Used in Max/Min. Used to merge all deleted data into one data frame for a parameter
library(data.table)
library(R.utils)
library(naniar)


######
#### Raw Data upload ####

#### Enter by user to clean the info within the raw data ####

data_file <- readline(prompt="Enter name of datafile including extension (.csv,.dat,.txt etc.): ")

header_line <- as.numeric(readline(prompt="In which row of the logger output are the parameters stated? (TIMESTAMP, RECORD etc.)(Number):"))

data_row <- as.numeric(readline(prompt="In which row of the logger does the raw data start?(Number):"))

col_prm <- as.numeric(readline(prompt = "In which column is the first measured parameter stated? (NOT TIMESTAMP or RECNBR)(Number):"))


#Only reads the parameter names
header <- read.csv(data_file, skip = header_line-1, nrows=1)

#Only reads the raw data
data_raw <- read_csv(data_file, skip = data_row-1, col_names = FALSE)

#Uses the parameter names to match to the raw data
colnames(data_raw) <- colnames(header)

#Move raw data to new object
QC_raw <- data_raw 

#Delete all previous inputs
rm(data_file)
rm(header_line)
rm(data_raw)
rm(header)


#### Get user input about the data interval ####
time_intervall <- as.numeric(readline(prompt="At what intervall is the data taken? (In minutes) (1-day = 1440):"))


#### Get user input about the parameter file name ###
parameter_file <- readline(prompt="Enter name of parameter file including extension (.R): ")
source(paste(parameter_file))
rm(parameter_file)


#### Load Threshold File ####
threshold_file <- readline(prompt="Enter name of threshold file including extension (.R): ")
source(paste(threshold_file))

# Save thresholds for Output file 
thresholds_used <- read_lines(threshold_file)


#### Load SITES parameters ####
SITES_Parameters <- readline(prompt="Enter name of SITES parameter file including extension (.R):")
source(paste(SITES_Parameters))

#### Get user input where the output should be saved ####
output_save_location <- readline(prompt="Enter the path where the Output (Folder for SITES and QC) should be saved. (Leaving it empty will save all the files in the folder where the script was opened): ")

#### Should an output csv file be created after each step ####
output_each_step <- readline(prompt="Should a .csv file be created for each step of the QC (in addition to the final Output)? (y/n):")

#####
#### Setting  Directories for the final Output #####

# checks if the input was empty. If so the directory of the script is chosen
if (length(output_save_location)==1) {
  
  output_save_location <- getwd()
}

#For manual inputs the "\" need to be replaced with "/" as Windows is still using "\"
output_save_location <- gsub("\\\\", "/", output_save_location)

#Creating directory for the Quality controlled output
output_save_location_QC <- paste (output_save_location,"/QC", sep = "")
dir.create(output_save_location_QC, showWarnings = FALSE)

#Creating directory for the Quality controlled plot output
output_save_location_QCplot <- paste (output_save_location,"/QC/Plot", sep = "")
dir.create(output_save_location_QCplot, showWarnings = FALSE)

#Creating directory for the SITES data output
output_save_location_SITES <- paste (output_save_location,"/SITES", sep = "")
dir.create(output_save_location_SITES, showWarnings = FALSE)

####

### Starting QC#
progress_output_text <- 1

if (progress_output_text ==1) {
  
  print("QC started")
}

#### GapFill ####
QC_data_GF <- QC_raw

# Create a variable with the date of the first row against which all of the following rows will be checked in case a row needs to be added
date_test <- get(var_time,QC_data_GF)[1]

# Creates two different tables to get an output in the end where and when rows where added (added_empty_rows) or removed (rm_gapfill_rows)
rm_gapfill_rows <- QC_data_GF[FALSE,]
added_empty_rows <- QC_data_GF[FALSE,]

i <- 1


while (i< nrow(QC_data_GF)) {
  
  if (get(var_time,QC_data_GF)[i] == get(var_time,QC_data_GF)[i+1]-minutes(time_intervall)) {
    
    i <- i+1
    
  }
  
  else {
    if (difftime(get(var_time,QC_data_GF)[i],get(var_time,QC_data_GF)[i+1],units = "mins") < (-(time_intervall))) {
      
      QC_data_GF[nrow(QC_data_GF)+1,] <- NA
      QC_data_GF[nrow(QC_data_GF), 1] <- date_test+minutes(i*time_intervall)
      added_empty_rows <- rbind(added_empty_rows,QC_data_GF[nrow(QC_data_GF),])
      QC_data_GF<- QC_data_GF %>% arrange(across())
      
    }
      
      
      else {
        
      rm_gapfill_rows <- rbind(rm_gapfill_rows,(QC_data_GF[i+1,]))
      QC_data_GF<-QC_data_GF[-c(i+1),]
      i<- i-1
      }
        
  }
  
}

print("GapFill completed")

if (output_each_step == "y") {
### Export Datasheet with filled gaps ###
write.csv(QC_data_GF,file.path(output_save_location_QC,"QC_Output_GF.csv"), row.names = FALSE)
}


### Export overview of added rows ###
write.csv(rm_gapfill_rows,file.path(output_save_location_QC,"Gapfill_removed_rows.csv"), row.names = FALSE)

### Export overview of added rows ###
write.csv(added_empty_rows,file.path(output_save_location_QC,"Gapfill_added_rows.csv"), row.names = FALSE)


#####
#### DoubleTime ####

QC_data_GF_DT <- QC_data_GF


### variables for while loop ###

previous_time <- 1 # used as a variable to check the previous row/date
checked_time<-2 # used as a variable to move down the data frame and to check the date of this specific row
i <- 1 # used as a counter within the "while" loop


### New dataframe that will be used as an overview of the rows with the same date detected within the while loop ###
overview_of_double_rows <- QC_data_GF_DT[FALSE,]


### While loop that goes through the uploaded date ###

while (i < nrow(QC_data_GF_DT)){
  
  #If condition checks whether the checked time is the same as the previous date/row. If not -> goes to Else
  if (get(var_time,QC_data_GF_DT)[checked_time] == (get(var_time,QC_data_GF_DT)[previous_time])){
    get(var_time,QC_data_GF_DT)
    
    #In case "if" is TRUE (Both timestamps are the same), the loop while break. The double occuring data should be manually checked and edited.  
    break
  }  
  
  #In case "if" is FALSE (Both timestamps are not the same), counter goes one up to match the time in the next row
  
  else {
    i=i+1
    previous_time <- previous_time+1; 
    checked_time<-checked_time+1; }
  
}

# In case the loop was broken previously, this loop will print out an error message stating where the error occurred. It is triggered by a too low "i" value that will not occur in case the previous "while-loop" ran successfully

if (i<nrow(QC_data_GF_DT)){
  
  stop(  paste("ERROR: Same time occurs in line:",i, "(Date:", (get(var_time,QC_data_GF_DT))[i],") and",i+1,"(Date:", get(var_time,QC_data_GF_DT)[i+1],")")
  )
  
  
}

if (output_each_step == "y") {
  
# The following loop will print out the data, which was checked for "Doubletime" as a .csv file
if (i==nrow(QC_data_GF_DT)) {
  ### Export Datasheet with checked double occurring times ###
  write.csv(QC_data_GF_DT,file.path(output_save_location_QC,"QC_Output_GF_DT.csv"), row.names = FALSE)
  
}
}
print("Doubletime completed")


#####
## Threshold check ##

#QC_data_GF_DT_Threshold <- QC_data_GF_DT

### Counts how many values have been replace with NA ###
#deleted_threshold <- length(which(QC_data_GF_DT_Threshold==-7999))

## Threshold check ##

QC_data_GF_DT_Threshold <- QC_data_GF_DT

### Deletes all values at -7999 and replaces them with NA within the whole dataset ###
QC_data_GF_DT_Threshold_clean<-QC_data_GF_DT_Threshold %>% replace_with_na_all(condition = ~.x == -7999)

### Counts how many values have been replace with NA ###
deleted_threshold <- sum(is.na(QC_data_GF_DT_Threshold_clean))- sum(is.na(QC_data_GF_DT_Threshold))  




#### Max/Min ####  
#######  
QC_data_GF_DT_T_MM_raw <- QC_data_GF_DT_Threshold_clean



###
### Add columns for Year, Month, Day, Hour, Minute and Julian-day-format ###
QC_data_GF_DT_T_MM_raw$Year  <- as.numeric(format(get(var_time,QC_data_GF_DT_T_MM_raw), format="%Y"))
QC_data_GF_DT_T_MM_raw$Month <- as.numeric(format(get(var_time,QC_data_GF_DT_T_MM_raw), format="%m"))
QC_data_GF_DT_T_MM_raw$Day   <- as.numeric(format(get(var_time,QC_data_GF_DT_T_MM_raw), format="%d"))
QC_data_GF_DT_T_MM_raw$Hour  <- as.numeric(format(get(var_time,QC_data_GF_DT_T_MM_raw), format="%H"))
QC_data_GF_DT_T_MM_raw$Minute  <- as.numeric(format(get(var_time,QC_data_GF_DT_T_MM_raw), format="%M"))
QC_data_GF_DT_T_MM_raw$Julian_day  <-JD(get(var_time,QC_data_GF_DT_T_MM_raw), inverse=FALSE)



###
############## EXPLANATION OF LOOP ONLY IN FIRST QC OF TOTAL RAD ###
### QC Max/Min Total Rad ###

#advise the data that went through the "Gapfill" process to a new data frame
QC_data_GF_DT_T_MM_Rad <- QC_data_GF_DT_T_MM_raw 



#Checks if the variable was selected in the parameters file. If it was not selected it will create an empty table that will be used in the Output_info.txt
if (nchar(var_rad) == 0) {
  
  deleted_values_TotalRad <- select(QC_data_GF_DT_T_MM_Rad[i,], all_of(var_time))
  deleted_values_TotalRad<- deleted_values_TotalRad[FALSE,] 
  
} else {
  
  # counter for the upcoming while loop
  i <- 1  
  
  #New data frame that only contains the time and the parameter within this loop. This data frame is needed later to save the removed values during the QC
  deleted_values_TotalRad <- select(QC_data_GF_DT_T_MM_Rad[i,], all_of(var_time), all_of(var_rad))
  
  #Empty the just created data frame, so that it only contains two empty columns
  deleted_values_TotalRad<- deleted_values_TotalRad[FALSE,] 
  
   
#While loop, that will go through the whole column of the parameter#
while (i<= nrow(QC_data_GF_DT_T_MM_Rad)) {
  
  #This if loop checks whether the current value in the specific column is "NA". If so, it will skip this value and go to the next row to avoid the loop to end with an error
  if (is.na(get(var_rad,QC_data_GF_DT_T_MM_Rad)[i])) { 
    i<-i+1
   
  }
  else {
    
    #The value will be checked against the Min/Max values that were predefined further up
    if (get(var_rad,QC_data_GF_DT_T_MM_Rad)[i] > MinTotalRad & get(var_rad,QC_data_GF_DT_T_MM_Rad)[i] < MaxTotalRad[QC_data_GF_DT_T_MM_Rad$Month[i]]){
      
      
      #For some parameters, negative values are impossible but sometimes the measurement is not precise enough and therefore values that are above the Min-threshold but below "0" will be set to "0"
      if (get(var_rad,QC_data_GF_DT_T_MM_Rad)[i]<0) {
        get(var_rad,QC_data_GF_DT_T_MM_Rad)[i]<-0
      }
      i <- i+1
    } 
    
    else {
      
      #Values that are outside the Min/Max threshold will be collected in a new data frame and deleted from the one that is going through the QC. Deleted values will be replaced by "NA" in the QC.
      value_outside_threshold_SWRAD <- select(QC_data_GF_DT_T_MM_Rad[i,], all_of(var_time), all_of(var_rad))
      deleted_values_TotalRad <- bind_rows(deleted_values_TotalRad,value_outside_threshold_SWRAD)
      QC_data_GF_DT_T_MM_Rad[i,var_rad] <- NA
    
      i <- i+1
    }
  }
  
  #This if loop has an output once half of the QC for this parameter is done. This ist just to make sure that the R loop is actually running and not stuck somewhere. 
  if (i>nrow(QC_data_GF_DT_T_MM_Rad)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_Rad)*0.5+0.5){
    print("50% done Max/Min Total Rad")
  }
  
  
  
}
}

####
### QC Max/Min PAR ### 
QC_data_GF_DT_T_MM_PAR<- QC_data_GF_DT_T_MM_Rad


if (nchar(var_par) == 0) {
  
  deleted_values_PAR <-select(QC_data_GF_DT_T_MM_PAR[i,], all_of(var_time))
  deleted_values_PAR<- deleted_values_PAR[FALSE,]
  
  
}else {

i <- 1
deleted_values_PAR <-select(QC_data_GF_DT_T_MM_PAR[i,], all_of(var_time), all_of(var_par))
deleted_values_PAR<- deleted_values_PAR[FALSE,]





while (i<= nrow(QC_data_GF_DT_T_MM_PAR)) {
  
  if (is.na(get(var_par, QC_data_GF_DT_T_MM_PAR)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_par, QC_data_GF_DT_T_MM_PAR)[i] >MinPAR[QC_data_GF_DT_T_MM_PAR$Month[i]] & get(var_par, QC_data_GF_DT_T_MM_PAR)[i]< MaxPAR[QC_data_GF_DT_T_MM_PAR$Month[i]]){
      if (get(var_par, QC_data_GF_DT_T_MM_PAR)[i]<0) {
        get(var_par, QC_data_GF_DT_T_MM_PAR)[i]<-0
      }
      i <- i+1
    }
    else {
      
      value_outside_threshold_PAR <- select(QC_data_GF_DT_T_MM_PAR[i,], all_of(var_time), all_of(var_par))
      deleted_values_PAR <- bind_rows(deleted_values_PAR,value_outside_threshold_PAR)
      QC_data_GF_DT_T_MM_PAR[i,var_par] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_PAR)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_PAR)*0.5+0.5){
    print("50% done Max/Min PAR")
  }
  
  
  
}

}

####
### QC Max/Min Water Temp 1m ###

QC_data_GF_DT_T_MM_WTmp1 <- QC_data_GF_DT_T_MM_PAR



if (nchar(var_Wtmp1) == 0) {
  deleted_values_WTmp1 <-select(QC_data_GF_DT_T_MM_WTmp1[i,], all_of(var_time))
  deleted_values_WTmp1<- deleted_values_WTmp1[FALSE,]  

} else {

i <- 1
deleted_values_WTmp1 <-select(QC_data_GF_DT_T_MM_WTmp1[i,], all_of(var_time), all_of(var_Wtmp1))
deleted_values_WTmp1<- deleted_values_WTmp1[FALSE,]



while (i<= nrow(QC_data_GF_DT_T_MM_WTmp1)) {
  
  if (is.na(get(var_Wtmp1, QC_data_GF_DT_T_MM_WTmp1)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_Wtmp1, QC_data_GF_DT_T_MM_WTmp1)[i] >MinWtemp[QC_data_GF_DT_T_MM_WTmp1$Month[i]] & get(var_Wtmp1, QC_data_GF_DT_T_MM_WTmp1)[i]< MaxWtemp[QC_data_GF_DT_T_MM_WTmp1$Month[i]]){
     
       if (get(var_Wtmp1, QC_data_GF_DT_T_MM_WTmp1)[i]<0) {
        get(var_Wtmp1, QC_data_GF_DT_T_MM_WTmp1)[i]<-0
      }
      i <- i+1
    }
    else {
      
      value_outside_threshold_WTmp1 <- select(QC_data_GF_DT_T_MM_WTmp1[i,],all_of(var_time), all_of(var_Wtmp1))
      deleted_values_WTmp1 <- bind_rows(deleted_values_WTmp1,value_outside_threshold_WTmp1)
      QC_data_GF_DT_T_MM_WTmp1[i,var_Wtmp1] <- NA
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_WTmp1)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_WTmp1)*0.5+0.5){
    print("50% done Max/Min Water Temp 1m")
  }
  
  
  
}
}

### QC Max/Min Water Temp 3m ###

QC_data_GF_DT_T_MM_WTmp3 <- QC_data_GF_DT_T_MM_WTmp1



if (nchar(var_Wtmp3) == 0) {
  deleted_values_WTmp3 <-select(QC_data_GF_DT_T_MM_WTmp3[i,], all_of(var_time))
  deleted_values_WTmp3<- deleted_values_WTmp3[FALSE,]  
  
} else {
  
  i <- 1
  deleted_values_WTmp3 <-select(QC_data_GF_DT_T_MM_WTmp3[i,], all_of(var_time), all_of(var_Wtmp3))
  deleted_values_WTmp3<- deleted_values_WTmp3[FALSE,]
  
  
  
  while (i<= nrow(QC_data_GF_DT_T_MM_WTmp3)) {
    
    if (is.na(get(var_Wtmp3, QC_data_GF_DT_T_MM_WTmp3)[i])) {
      i<-i+1
    }
    else {
      
      
      if (get(var_Wtmp3, QC_data_GF_DT_T_MM_WTmp3)[i] >MinWtemp[QC_data_GF_DT_T_MM_WTmp3$Month[i]] & get(var_Wtmp3, QC_data_GF_DT_T_MM_WTmp3)[i]< MaxWtemp[QC_data_GF_DT_T_MM_WTmp3$Month[i]]){
        
        if (get(var_Wtmp3, QC_data_GF_DT_T_MM_WTmp3)[i]<0) {
          get(var_Wtmp3, QC_data_GF_DT_T_MM_WTmp3)[i]<-0
        }
        i <- i+1
      }
      else {
        
        value_outside_threshold_WTmp3 <- select(QC_data_GF_DT_T_MM_WTmp3[i,],all_of(var_time), all_of(var_Wtmp3))
        deleted_values_WTmp3 <- bind_rows(deleted_values_WTmp3,value_outside_threshold_WTmp3)
        QC_data_GF_DT_T_MM_WTmp3[i,var_Wtmp3] <- NA
        
        i <- i+1
      }
    }
    
    if (i>nrow(QC_data_GF_DT_T_MM_WTmp3)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_WTmp3)*0.5+0.5){
      print("50% done Max/Min Water Temp 1m")
    }
    
    
    
  }
}




### QC Max/Min Water Temp 15m ###
QC_data_GF_DT_T_MM_WTmp15 <- QC_data_GF_DT_T_MM_WTmp3



if (nchar(var_Wtmp15) == 0) {
  deleted_values_WTmp15 <-select(QC_data_GF_DT_T_MM_WTmp15[i,], all_of(var_time))
  deleted_values_WTmp15<- deleted_values_WTmp15[FALSE,]  
  
} else {
  
  i <- 1
  deleted_values_WTmp15 <-select(QC_data_GF_DT_T_MM_WTmp15[i,], all_of(var_time), all_of(var_Wtmp15))
  deleted_values_WTmp15<- deleted_values_WTmp15[FALSE,]
  
  
  
  while (i<= nrow(QC_data_GF_DT_T_MM_WTmp15)) {
    
    if (is.na(get(var_Wtmp15, QC_data_GF_DT_T_MM_WTmp15)[i])) {
      i<-i+1
    }
    else {
      
      
      if (get(var_Wtmp15, QC_data_GF_DT_T_MM_WTmp15)[i] >MinWtemp[QC_data_GF_DT_T_MM_WTmp15$Month[i]] & get(var_Wtmp15, QC_data_GF_DT_T_MM_WTmp15)[i]< MaxWtemp[QC_data_GF_DT_T_MM_WTmp15$Month[i]]){
        
        if (get(var_Wtmp15, QC_data_GF_DT_T_MM_WTmp15)[i]<0) {
          get(var_Wtmp15, QC_data_GF_DT_T_MM_WTmp15)[i]<-0
        }
        i <- i+1
      }
      else {
        
        value_outside_threshold_WTmp15 <- select(QC_data_GF_DT_T_MM_WTmp15[i,],all_of(var_time), all_of(var_Wtmp15))
        deleted_values_WTmp15 <- bind_rows(deleted_values_WTmp15,value_outside_threshold_WTmp15)
        QC_data_GF_DT_T_MM_WTmp15[i,var_Wtmp15] <- NA
        
        i <- i+1
      }
    }
    
    if (i>nrow(QC_data_GF_DT_T_MM_WTmp15)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_WTmp15)*0.5+0.5){
      print("50% done Max/Min Water Temp 1m")
    }
    
    
    
  }
}



####
### QC Max/Min Humidity Sensor (HS) Air Temp ###
QC_data_GF_DT_T_MM_Htmp<- QC_data_GF_DT_T_MM_WTmp15


if (nchar(var_Htmp) == 0) {
  deleted_values_AirTmpHS <-select(QC_data_GF_DT_T_MM_Htmp[i,], all_of(var_time))
  deleted_values_AirTmpHS<- deleted_values_AirTmpHS[FALSE,]
  
} else {

i <- 1
deleted_values_AirTmpHS <-select(QC_data_GF_DT_T_MM_Htmp[i,], all_of(var_time), all_of(var_Htmp))
deleted_values_AirTmpHS<- deleted_values_AirTmpHS[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_Htmp)) {
  
  if (is.na(get(var_Htmp,QC_data_GF_DT_T_MM_Htmp)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_Htmp,QC_data_GF_DT_T_MM_Htmp)[i] >MinAirTemp[QC_data_GF_DT_T_MM_Htmp$Month[i]] & get(var_Htmp,QC_data_GF_DT_T_MM_Htmp)[i]< MaxAirTemp[QC_data_GF_DT_T_MM_Htmp$Month[i]]){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_AirTmpHS <- select(QC_data_GF_DT_T_MM_Htmp[i,], all_of(var_time), all_of(var_Htmp))
      deleted_values_AirTmpHS <- bind_rows(deleted_values_AirTmpHS,value_outside_threshold_AirTmpHS)
      QC_data_GF_DT_T_MM_Htmp[i,var_Htmp] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_Htmp)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_Htmp)*0.5+0.5){
    print("50% done Max/Min Air Temp Avg HS ")
  }
  
  
  
}
}


####
### QC MX/Min AS Air Temp ###
QC_data_GF_DT_T_MM_Tmp<- QC_data_GF_DT_T_MM_Htmp


if (nchar(var_tmp) == 0) {
  deleted_values_AirTmpAS <-select(QC_data_GF_DT_T_MM_Tmp[i,], all_of(var_time))
  deleted_values_AirTmpAS<- deleted_values_AirTmpAS[FALSE,]
  
} else {
  
i <- 1
deleted_values_AirTmpAS <-select(QC_data_GF_DT_T_MM_Tmp[i,], all_of(var_time), all_of(var_tmp))
deleted_values_AirTmpAS<- deleted_values_AirTmpAS[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_Tmp)) {
  
  if (is.na(get(var_tmp, QC_data_GF_DT_T_MM_Tmp)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_tmp, QC_data_GF_DT_T_MM_Tmp)[i] >MinAirTemp[QC_data_GF_DT_T_MM_Tmp$Month[i]] & get(var_tmp, QC_data_GF_DT_T_MM_Tmp)[i]< MaxAirTemp[QC_data_GF_DT_T_MM_Tmp$Month[i]]){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_AirTmpAS <- select(QC_data_GF_DT_T_MM_Tmp[i,], all_of(var_time), all_of(var_tmp))
      deleted_values_AirTmpAS <- bind_rows(deleted_values_AirTmpAS,value_outside_threshold_AirTmpAS)
      QC_data_GF_DT_T_MM_Tmp[i,var_tmp] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_Tmp)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_Tmp)*0.5+0.5){
    print("50% done Max/Min Air Temp Avg AS ")
  }
  
  
  
}

}

####
### QC Max/Min Wind Speed ###
QC_data_GF_DT_T_MM_Wspd<- QC_data_GF_DT_T_MM_Tmp


if (nchar(var_wspd) == 0) {
  deleted_values_WindS <-select(QC_data_GF_DT_T_MM_Wspd[i,], all_of(var_time), all_of(var_wspd))
  deleted_values_WindS<- deleted_values_WindS[FALSE,]
  
} else {

i <- 1
deleted_values_WindS <-select(QC_data_GF_DT_T_MM_Wspd[i,], all_of(var_time))
deleted_values_WindS<- deleted_values_WindS[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_Wspd)) {
  
  if (is.na(get(var_wspd,QC_data_GF_DT_T_MM_Wspd)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_wspd,QC_data_GF_DT_T_MM_Wspd)[i] >MinWind & get(var_wspd,QC_data_GF_DT_T_MM_Wspd)[i]< MaxWind){
      
      
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_WindS <- select(QC_data_GF_DT_T_MM_Wspd[i,], all_of(var_time), all_of(var_wspd))
      deleted_values_WindS <- bind_rows(deleted_values_WindS,value_outside_threshold_WindS)
      QC_data_GF_DT_T_MM_Wspd[i,var_wspd] <- NA
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_Wspd)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_Wspd)*0.5+0.5){
    print("50% done Max/Min Wind speed")
  }
  
  
  
}
}


####
### QC Max/Min Wind Direction ###
QC_data_GF_DT_T_MM_Wdir<- QC_data_GF_DT_T_MM_Wspd

if (nchar(var_wdir) == 0) {
  deleted_values_WindDir <-select(QC_data_GF_DT_T_MM_Wdir[i,], all_of(var_time), )
  deleted_values_WindDir<- deleted_values_WindDir[FALSE,]
  
} else {

i <- 1
deleted_values_WindDir <-select(QC_data_GF_DT_T_MM_Wdir[i,], all_of(var_time), all_of(var_wdir))
deleted_values_WindDir<- deleted_values_WindDir[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_Wdir)) {
  
  if (is.na(get(var_wdir,QC_data_GF_DT_T_MM_Wdir)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_wdir,QC_data_GF_DT_T_MM_Wdir)[i] >MinWindDir & get(var_wdir,QC_data_GF_DT_T_MM_Wdir)[i]< MaxWindDir){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_WindDir <- select(QC_data_GF_DT_T_MM_Wdir[i,], all_of(var_time), all_of(var_wdir))
      deleted_values_WindDir <- bind_rows(deleted_values_WindDir,value_outside_threshold_WindDir)
      QC_data_GF_DT_T_MM_Wdir[i,var_wdir] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_Wdir)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_Wdir)*0.5+0.5){
    print("50% done Max/Min Wind direction ")
  }
  
}
}


####
### QC Max/Min Water level ###
QC_data_GF_DT_T_MM_lvl <- QC_data_GF_DT_T_MM_Wdir

if (nchar(var_lvl) == 0) {
  deleted_values_WatLev <-select(QC_data_GF_DT_T_MM_lvl[i,], all_of(var_time))
  deleted_values_WatLev<- deleted_values_WatLev[FALSE,]
  
} else {

i <- 1
deleted_values_WatLev <-select(QC_data_GF_DT_T_MM_lvl[i,], all_of(var_time),all_of(var_lvl))
deleted_values_WatLev<- deleted_values_WatLev[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_lvl)) {
  
  if (is.na(get(var_lvl, QC_data_GF_DT_T_MM_lvl)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_lvl, QC_data_GF_DT_T_MM_lvl)[i] >MinLev & get(var_lvl, QC_data_GF_DT_T_MM_lvl)[i]< MaxLev){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_WatLev <- select(QC_data_GF_DT_T_MM_lvl[i,], all_of(var_time), all_of(var_lvl))
      deleted_values_WatLev <- bind_rows(deleted_values_WatLev,value_outside_threshold_WatLev)
      QC_data_GF_DT_T_MM_lvl[i,var_lvl] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_lvl)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_lvl)*0.5+0.5){
    print("50% done Max/Min Water Level ")
  }
  
}

}


####
### QC Max/Min Humidity ###
QC_data_GF_DT_T_MM_hum <- QC_data_GF_DT_T_MM_lvl

if (nchar(var_hum) == 0) {
  
} else {
  deleted_values_Hum <-select(QC_data_GF_DT_T_MM_hum[i,], all_of(var_time))
  deleted_values_Hum<- deleted_values_Hum[FALSE,]
  
i <- 1
deleted_values_Hum <-select(QC_data_GF_DT_T_MM_hum[i,], all_of(var_time), all_of(var_hum))
deleted_values_Hum<- deleted_values_Hum[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_hum)) {
  
  if (is.na(get(var_hum, QC_data_GF_DT_T_MM_hum)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_hum, QC_data_GF_DT_T_MM_hum)[i] >MinHum & get(var_hum, QC_data_GF_DT_T_MM_hum)[i]< MaxHum){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_Hum <- select(QC_data_GF_DT_T_MM_hum[i,], all_of(var_time), all_of(var_hum))
      deleted_values_Hum <- bind_rows(deleted_values_Hum,value_outside_threshold_Hum)
      QC_data_GF_DT_T_MM_hum[i,var_hum] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_hum)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_hum)*0.5+0.5){
    print("50% done Max/Min Humidity ")
  }
  
}
}


####
### QC Max/Min Air Pressure ###
QC_data_GF_DT_T_MM_pre<- QC_data_GF_DT_T_MM_hum

if (nchar(var_pre) == 0) {
  deleted_values_Pre <-select(QC_data_GF_DT_T_MM_pre[i,], all_of(var_time))
  deleted_values_Pre<- deleted_values_Pre[FALSE,]
  
} else {

i <- 1
deleted_values_Pre <-select(QC_data_GF_DT_T_MM_pre[i,], all_of(var_time), all_of(var_pre))
deleted_values_Pre<- deleted_values_Pre[FALSE,]


while (i<= nrow(QC_data_GF_DT_T_MM_pre)) {
  
  if (is.na(get(var_pre,QC_data_GF_DT_T_MM_pre)[i])) {
    i<-i+1
  }
  else {
    
    
    if (get(var_pre,QC_data_GF_DT_T_MM_pre)[i] > MinAirPress & get(var_pre,QC_data_GF_DT_T_MM_pre)[i] < MaxAirPress){
      
      i <- i+1
    }
    else {
      
      value_outside_threshold_Pre <- select(QC_data_GF_DT_T_MM_pre[i,], all_of(time_var), all_of(var_pre))
      deleted_values_Pre <- bind_rows(deleted_values_Pre,value_outside_threshold_Pre)
      QC_data_GF_DT_T_MM_pre[i,var_pre] <- NA
      
      
      i <- i+1
    }
  }
  
  if (i>nrow(QC_data_GF_DT_T_MM_pre)*0.5-0.5 & i<= nrow(QC_data_GF_DT_T_MM_pre)*0.5+0.5){
    print("50% done Max/Min Air Pressure ")
  }
  
}

}
### Final Output of Max/Min QC ###
QC_data_GF_DT_T_MM <- QC_data_GF_DT_T_MM_pre





####
### Output all deleted values ###


# Bei allen den ersten Timestmap der ersten Zeiel einfuegen

deleted_values_list <- list(deleted_values_TotalRad, 
                            deleted_values_PAR,
                            deleted_values_WTmp1,
                            deleted_values_WTmp3,
                            deleted_values_WTmp15,
                            deleted_values_AirTmpHS,
                            deleted_values_AirTmpAS,
                            deleted_values_WindS,
                            deleted_values_WindDir,
                            deleted_values_WatLev,
                            deleted_values_Hum,
                            deleted_values_Pre ) #All deleted values of each column are merged into one list

all_deleted_values <- Reduce(function(x,y) merge(x=x ,y=y,by= (var_time), all=T), deleted_values_list)# Output that shows all deleted values during the QC for Min/Max thresholds


print("Min/Max completed")

if (output_each_step == "y") {
  
#Export the QC data as .csv file. 
write.csv(QC_data_GF_DT_T_MM,file.path(output_save_location_QC,"QC_Output_GF_DT_MM.csv"), row.names = FALSE)
}

#Export the deleted data from Max/Min .csv file. 
write.csv(all_deleted_values,file.path(output_save_location_QC,"Min_Max_deleted_values.csv"), row.names = FALSE)


######
#### Repeated values ####
QC_data_GF_DT_T_MM_RV <- QC_data_GF_DT_T_MM

i <- 3 # Counter for all the loops that tracks the position. TWo same values are allowed to occur consecutively and therefore the first two rows of the datasheet will not be touched. Therefore it starts at 3 as the script
column <- data_row # Indicates the column in which the progress should start. Leaving out the first column, as it contains the date (Timestamp)
max_number_columns <- 1 #Counter that counts how many columns have been progressed already. As soon as this counter reaches the total number of columns available in the script it will terminate the whole loop and end the QC




#An empty data frame is created to be used later to store all deleted values
# deleted_repeated_values <- select(QC_data_GF_DT_T_MM_RV[i,], all_of(var_time), colnames(QC_data_GF_DT_T_MM_RV[,column]))
# deleted_repeated_values <- deleted_repeated_values[FALSE,]
# 

### TEST area
#"deleted_values_Pre <-select(QC_data_GF_DT_T_MM_pre[i,], all_of(var_time))"

deleted_repeated_values <- select(QC_data_GF_DT_T_MM_RV[i,], all_of(var_time))
deleted_repeated_values <- deleted_repeated_values[FALSE,]





#This while loop process the whole datasheet. It will check column by column whether sequences of repeated same values occur.
while (i<= nrow(QC_data_GF_DT_T_MM_RV)) {
  
  ######

  
  if( (colnames(QC_data_GF_DT_T_MM_RV[1,column])) %in% (column_names)) {
    
    
    
    #It checks whether the selected cell (i) in the column is already NA. It checks the same for the cell one and two positions before and the cell ahead. If any of those cells is already NA it will go on to the next cell. This is to avoid unncessary computing as NA values are not seen as a continuation of a sequence (e.g. 1,1,Na,1,1 ; would not be deleted in the script as two same values are allowed to follow each other. When there is no information about the value inbetween it cannot be deleted or assumed that it is the same)
    if (is.na(QC_data_GF_DT_T_MM_RV[i,column]) |is.na(QC_data_GF_DT_T_MM_RV[i-1,column]) | is.na(QC_data_GF_DT_T_MM_RV[i-2,column])| is.na(QC_data_GF_DT_T_MM_RV[i+1,column])){
      i<-i+1
      
    }
    
    else {
      
      
      #If there is no NA found it is checked whether the two previous cells contain the same value as the currently selected. If so the "count" and "sequence counter" will be set.
      if (QC_data_GF_DT_T_MM_RV[i,column] == QC_data_GF_DT_T_MM_RV[i-1,column] & QC_data_GF_DT_T_MM_RV[i,column] == QC_data_GF_DT_T_MM_RV[i-2,column]){
        
        
        #COunt and sequence will be used as variables to store information of how long the sequence of same values is in the data. It is used to determine how many cells will be replaced with NA
        count <- 1
        seq_counter <- 0
        
        #This loop is the main QC that will check all cells following the selected one (i). 
        while (count <=(nrow(QC_data_GF_DT_T_MM_RV)-i)){
          
          if (QC_data_GF_DT_T_MM_RV[i, column] == QC_data_GF_DT_T_MM_RV[i+count,column]){
            
            seq_counter <- seq_counter+1
            
            count <- count+1
            
            
            #This is a kill switch in case the sequence that occurs is at the end of the data sheet or an NA is up next. It checks whether the next value is even existing. If an NA occurs it of course ends the sequence of repeated values. 
            
            if(is.na(QC_data_GF_DT_T_MM_RV[i+count,column])){
              
              count<-nrow(QC_data_GF_DT_T_MM_RV) #this is used to set the count of the while loop to the end point so it terminates
              
              
              #The "Sequence counter" is now used to determine the length of the sequence that is copied to the deleted value file and how many values are replaced by NA.
              repeated_values <- select(QC_data_GF_DT_T_MM_RV[(i-1):((i-1)+seq_counter+1),], all_of(var_time), colnames(QC_data_GF_DT_T_MM_RV[,column]))
              
              deleted_repeated_values <- bind_rows(deleted_repeated_values,repeated_values)
              
              QC_data_GF_DT_T_MM_RV[(i-1):((i-1)+seq_counter+1),column] <- NA
              
              seq_counter <-0
            }
            
          }
          #This else clause will take action in case the next value is not matching the one looked for in the sequence. (e.g. 1,1,1,2 ; will be terminated at "2"). 
          else {
            count <- nrow(QC_data_GF_DT_T_MM_RV)
            
            repeated_values <- select(QC_data_GF_DT_T_MM_RV[(i-1):((i-1)+seq_counter+1),], all_of(var_time), colnames(QC_data_GF_DT_T_MM_RV[,column]))
            
            deleted_repeated_values <- bind_rows(deleted_repeated_values,repeated_values)
            
            QC_data_GF_DT_T_MM_RV[(i-1):((i-1)+seq_counter+1),column] <- NA
          }
          
          
        }
        #Variable "i" is increased and used in the following to search the next cell in the column
        i <- i+1
        
        
      }
      
      else {
        
        i<-i+1
      }
      
      
    }
    
  }
  
  else {
    
   if (column==length(QC_data_GF_DT_T_MM_RV)){
     i<- nrow(QC_data_GF_DT_T_MM_RV)+1
   }
    else {
      i<- nrow(QC_data_GF_DT_T_MM_RV)
    }
  }
  
  #If all conditions meet, the next column will be chosen to be checked. If it not all conditions are met the script will remain i the same column and go to the next cell in the column. If all conditions are met, it will mean that it reached the last cell of the last column. Therefore it will terminate the whole data cleaning.  (It will terminate in the end, as it will not reset "i", "column" and "max_number_columns" and jump back to the while loop. Then it won't meet the requirements of the while loop as "i" will be bigger than the number of rows. This will terminate it)
  
  if (i==nrow(QC_data_GF_DT_T_MM_RV)& max_number_columns <length(QC_data_GF_DT_T_MM_RV) & column<=length(QC_data_GF_DT_T_MM_RV)){
    i<-3
    column <- column+1
    max_number_columns<- max_number_columns+1
  }
  
}




### Deleted repeated values as data frame ###

#The datasheet of deleted values is just stacked with a lot of same dates. In order to increase visibility and to reduce the size of the file, all values with the same Timestamp will be put in the same row. To not mess with the original outcome of the QC it, the data will be stored in a separate file that then will be transformed.It will always have at least one row less than the file, that went through the QC as values in the first row of the datafile will never be deleted (remember that always the first value of a sequence will be kept.)
deleted_values_not_merged <- deleted_repeated_values

if (nrow(deleted_values_not_merged)>1){
deleted_values_merged <- aggregate(x = deleted_values_not_merged, by = list (get(var_time,deleted_values_not_merged)), FUN = function(x) na.omit(x)[1])[,-1]
}
#####

#### Export QC Data ####
QC_data_final <- QC_data_GF_DT_T_MM_RV



if (exists("deleted_values_merged")){
  write.csv(deleted_values_merged,file.path(output_save_location_QC,"Repeated_values_deleted.csv"), row.names = FALSE)}

print("Repeated values completed")




#### Export QC DATA ####
######
write.csv(QC_data_final,file.path(output_save_location_QC,"QC_data_final.csv"),row.names = FALSE)

print("QC Output created")

#### Export SITES DATA ####
QC_data_final_SITES <- QC_data_final


######





#### OUTPUT FOR SITES ####
  
# Count how many different SITES outputs were predefined in the SITES_parameters file
count_SITES_total<- length((ls(pattern = "col_daily_")))

#Start with number 1
count_SITES <- 1


while(count_SITES <= count_SITES_total){
  #Create the new variable to create the SITES output. Changes with each circle of the loop
  SITES_output_variable <- paste("col_daily_",count_SITES, sep="")
  
  #R takes the info from the SITES_parameters file
  QC_SITES_PLOT <- QC_data_final_SITES[, (get(SITES_output_variable))]
  
  write.csv(QC_SITES_PLOT, file.path(output_save_location_SITES,paste0("QC_data_hourly_",count_SITES,"_SITES.csv")), row.names = FALSE)
  
  count_SITES <- count_SITES+1
  
}


print("SITES Output created")





##### INFO OUTPUT AS TXT ####

#Make output info name depended on input of time interval
if (time_intervall==60){
fileConn<-file(file.path(output_save_location_QC,"Output_Info_hourly.txt"))
Output_text_info <- (paste("Quality control info hourly. Date:", Sys.time()))
} else {
   if (time_intervall== 1440){
     fileConn<-file(file.path(output_save_location_QC,"Output_Info_daily.txt"))
     Output_text_info <- (paste("Quality control info daily Date:", Sys.time()))
   }
   else {
     fileConn<-file(file.path(output_save_location_QC,"Output_Info.txt"))
     Output_text_info <- (paste("Quality control info. Date:", Sys.time()))
   }
}
Output_text_Gapfill<- (paste("Gapfill:",nrow(added_empty_rows),"rows were added and", nrow(rm_gapfill_rows),"rows were deleted."))
Output_text_Doubletime<- (paste ("Doubletime: There were", nrow(rm_gapfill_rows), "repeated timestamps found."))
Output_text_Threshold <- (paste("Threshold:",deleted_threshold ,"values were recorded at the sensor threshold (-7999) and replaced with NA during Max/Min"))
Output_text_MaxMin1<- (paste ("Min/Max:", nrow(deleted_values_TotalRad),"values were deleted for TotalRad.", (if (nchar(var_rad)==0){paste("(not used)")}))) 
Output_text_MaxMin2<- (paste ("Min/Max:",nrow(deleted_values_PAR),"values were deleted for PAR.", (if (nchar(var_par )==0){paste("(not used)")}))) 
Output_text_MaxMin3<- (paste ("Min/Max:",nrow(deleted_values_WTmp1),"values were deleted for WTmp at 1m.", (if (nchar(var_Wtmp1)==0){paste("(not used)")}))) 
Output_text_MaxMin4<- (paste ("Min/Max:",nrow(deleted_values_WTmp3),"values were deleted for WTmp at 3m.", (if (nchar(var_Wtmp3)==0){paste("(not used)")}))) 
Output_text_MaxMin5<- (paste ("Min/Max:",nrow(deleted_values_WTmp15),"values were deleted for WTmp at 15m.", (if (nchar(var_Wtmp15)==0){paste("(not used)")}))) 
Output_text_MaxMin6<- (paste ("Min/Max:",nrow(deleted_values_AirTmpHS), "values were deleted for AirTmpHS.", (if (nchar(var_Htmp)==0){paste("(not used)")}))) 
Output_text_MaxMin7<- (paste ("Min/Max:",nrow(deleted_values_AirTmpAS),"values were deleted for AirTmpAS.", (if (nchar(var_tmp)==0){paste("(not used)")}))) 
Output_text_MaxMin8<- (paste ("Min/Max:",nrow(deleted_values_WindS), "values were deleted for WindS.", (if (nchar(var_wspd)==0){paste("(not used)")}))) 
Output_text_MaxMin9<- (paste ("Min/Max:",nrow(deleted_values_WindDir),"values were deleted for WindDir.", (if (nchar(var_wdir)==0){paste("(not used)")})))  
Output_text_MaxMin10<- (paste ("Min/Max:",nrow(deleted_values_WatLev), "values were deleted for WatLev.", (if (nchar(var_lvl)==0){paste("(not used)")}))) 
Output_text_MaxMin11<- (paste ("Min/Max:",nrow(deleted_values_Hum),"values were deleted for Hum.", (if (nchar(var_hum)==0){paste("(not used)")}))) 
Output_text_MaxMin12<- (paste ("Min/Max:",nrow(deleted_values_Pre),"values were deleted for Pre.", (if (nchar(var_pre )==0){paste("(not used)")}))) 
Output_text_Repeatedvalues<- (paste ("Repeated values:",nrow(deleted_repeated_values),"repeated values were deleted."))
Output_text_threshold <- paste("#### THRESHOLDS USED FOR MAX/MIN")
Output_text_threshold_use <- thresholds_used
Output_text_gap <- paste("")


writeLines(c(Output_text_info,Output_text_gap,Output_text_Gapfill,Output_text_Doubletime,Output_text_Threshold,Output_text_MaxMin1,Output_text_MaxMin2,Output_text_MaxMin3,Output_text_MaxMin4,Output_text_MaxMin5,Output_text_MaxMin6,Output_text_MaxMin7,Output_text_MaxMin8,Output_text_MaxMin9,Output_text_MaxMin10,Output_text_MaxMin11,Output_text_MaxMin12,Output_text_Repeatedvalues,Output_text_gap,Output_text_threshold,Output_text_gap, Output_text_threshold_use),fileConn)
close(fileConn)

print("QC INFO created")

##### PLOTTING THE OUTPUT #####

### Fusing the repeated sequence deleted values with the deleted Max/Min values to show both in the plots ###

## To be able to included the deleted values from Max/Min as well as Repeated values in the plots both tables with deleted values each need to be fused. This is happening in the loop.

#This loop is only executed if there were repeated values that have been deleted
if (nrow(deleted_repeated_values)>1){


c_rep <- 2 #Counter to navigate through the columns of the Max/Min sheet and compare the column names with the ones from the repeated values
fused_columns <- 0 #Counts how many columns have been fused. Used to end this loop wenn the correct number of columns that the repeated values sheet contains is reached

while(fused_columns < length(deleted_repeated_values)-1) {
  
  
  #This loop looks for matching column names going through both data sheets one by one
  if (colnames(all_deleted_values)[c_rep] %in% colnames(deleted_repeated_values)){
    
    
    #If a matching column name was found it fuses both together
    correct_column <- grep(colnames(all_deleted_values)[c_rep], colnames(deleted_repeated_values))

    fused_thresholds_repeated_values <- rbind(all_deleted_values[c(1,c_rep)], deleted_repeated_values[c(1,correct_column)] )
    
    all_deleted_values <- all_deleted_values[,-c_rep]
    
    
    fused_thresholds_repeated_values <- tibble(fused_thresholds_repeated_values)
    
    fused_thresholds_repeated_values <- na.omit(fused_thresholds_repeated_values)
    
    fused_thresholds_repeated_values_correct_order <- arrange(fused_thresholds_repeated_values, TMSTAMP)
    
     
    fused_aslist <- list(all_deleted_values,fused_thresholds_repeated_values_correct_order )
    
    fuse_test_alltogether_again <- Reduce(function(x,y) merge(x=x ,y=y,by= (var_time), all=T), fused_aslist)
    
    
    #The fused column of min/max and repeated values is merged again to allow for the next cycle in the loop to do the same as above
    all_deleted_values <- fuse_test_alltogether_again
     
    c_rep <- c_rep+1 
    fused_columns <- fused_columns+1
    
    } else {
      
      c_rep <- c_rep+1 
    }
    

  }
}








###

# Delete all -7999 thresholds to avoid wrong scaling of the y-axis

  deleted_values_plot <-all_deleted_values %>% replace_with_na_all(condition = ~.x == -7999)
  



col_prm <- 3

ldif <- length(QC_data_final)- length(QC_raw)

# Loop to create the plot output and to merge the deleted data with the quality controlled data in the same plot to allow visual check-ups
# The length of the file is reduced by "ldif" columns where added including year, day, hour etc. (See first step Max/Min).

while (col_prm <= length(QC_data_final)-ldif) {
  
  var_plot <- (colnames(QC_data_final[,col_prm]))
  
  plot_QC <- select(QC_data_final, all_of(var_time), all_of(var_plot))
  names(plot_QC)[1] <- "Time"
  names(plot_QC)[2] <- "QC_Data"
  
  
  if  ((colnames(QC_data_final[,col_prm]))%in% colnames(deleted_values_plot)){
    
    plot_del <- select(deleted_values_plot,all_of(var_time),all_of(var_plot))
    names(plot_del)[1] <- "Time"
    names(plot_del)[2] <- "Del_data"
    
    
    pdf(file.path(output_save_location_QCplot, file=paste0(var_plot,".pdf")))
    plot(plot_QC$Time,plot_QC$QC_Data, type = "l", xlab = "TIME", ylab = var_plot,ylim = c(min(c(plot_QC$QC_Data, plot_del$Del_data), na.rm = TRUE),(max(c(plot_QC$QC_Data, plot_del$Del_data), na.rm = TRUE))))
    lines(plot_del$Time,plot_del$Del_data,type="p", col="red", lwd=0.5)
    legend("topright", legend = c(paste("Deleted values:",sum(!is.na(plot_del$Del_data))),paste("NAs:",sum(is.na(plot_QC$QC_Data))-sum(!is.na(plot_del$Del_data)))), cex = 0.7)
    
    dev.off()
    
    col_prm <- col_prm+1
    
    
    
  }
  else {   pdf(file.path(output_save_location_QCplot, file=paste0(var_plot,".pdf")))
    plot(plot_QC$Time,plot_QC$QC_Data, type = "l", xlab = "TIME", ylab = var_plot,ylim = c(min(c(plot_QC$QC_Data), na.rm = TRUE),(max(c(plot_QC$QC_Data), na.rm = TRUE))))
    legend("topright", legend = c(paste("NAs:",sum(is.na(plot_QC$QC_Data)))), cex = 0.7)
    
    dev.off()
    
    col_prm <- col_prm+1

  }

}

print("Plots created")

print("QC DONE")
