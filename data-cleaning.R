# call libraries
library(dplyr)
library(readxl)
library(tidyr)

# Load dataset
daily_temp <- read_excel("/Users/arijacob/Documents/Oeconomica - IO Cohort - ICSIOCS Data/Daily-temperature-data.xlsx")

# Take out 'F' from the temperature entries
daily_temp <- daily_temp %>%
  mutate(across(c(DE, CT, MA, MD, ME, NH, NJ, NY, PA, VA, VT), ~ str_remove(., "F")))

# Take out C from temperature entries
daily_temp <- daily_temp %>%
  mutate(RI = str_remove(RI, "C"))

# Convert temperature into numeric
daily_temp <- daily_temp %>%
  mutate(across(c(DE, CT, MA, MD, ME, NH, NJ, NY, PA, VA, VT, RI), as.numeric))

# Function to convert Celsius into Fahrenheit 
ctof <- function(tempC){
  return(tempC*(9/5)+32)
} 

# Change RI column to Fahrenheit
daily_temp <- daily_temp %>%
  mutate(RI = (ctof(RI)))

# Date in proper format
daily_temp <- daily_temp %>%
  mutate(date = as.Date(date))
