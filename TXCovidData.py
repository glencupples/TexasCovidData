#TXCovidData
import pandas as pd
import requests
from datetime import date
import yagmail
from EmailPassword import password
from tabulate import tabulate

#get all county data
all_county_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv') #make df with all counties
texas_county_data = all_county_data[all_county_data['state']=='Texas'] #reduce df to just TX


#get texas county data
census_get = requests.get(url = "https://api.census.gov/data/2019/pep/population?get=COUNTY,NAME,POP&for=county:*&in=state:48" ).json() #get all counties in TX
census_df = pd.DataFrame(data=census_get) #to df
census_df.columns = census_df.iloc[0] #make first row to header
census_df = census_df[1:] #make first row to header pt 2


#group by county, sum and sort by total cases
county_cases_sum = texas_county_data.groupby(['county'],as_index=False).agg({'cases':'sum','fips':'mean'}).sort_values(by='cases',ascending=False)
county_cases_sum = county_cases_sum[:10]
print(county_cases_sum)

###TODO: split out and make new repository
###TODO: make slice county out of fips column on county data
###TODO: make daily case/death increase df
###TODO: make per capita calcs
###TODO: find daily county with biggest one day increase