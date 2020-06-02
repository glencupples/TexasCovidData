#TXCovidData
import pandas as pd
import requests
from datetime import date
import yagmail
from EmailPassword import password
from tabulate import tabulate

date_today = date.today()
date_today = date_today.strftime("%Y-%m-%d")
print(date_today)

#get texas census data
census_get = requests.get(url = "https://api.census.gov/data/2019/pep/population?get=COUNTY,NAME,POP&for=county:*&in=state:48" ).json() #get all counties in TX
census_df = pd.DataFrame(data=census_get) #to df
census_df.columns = census_df.iloc[0] #make first row to header
census_df = census_df[1:] #make first row to header pt 2
census_df["fips"] = census_df["state"] + census_df["county"] #combine state and county IDs to make fips column
census_df['fips'] = census_df['fips'].astype(int) #convert to int
census_df['POP'] = census_df['POP'].astype(int) #convert to int
census_df.rename({'POP': 'pop'}, axis=1, inplace=True)
census_df = census_df[['fips','pop']] #reduce df

#get all county covid data
all_county_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv') #make df with all counties
texas_county_data = all_county_data[all_county_data['state']=='Texas'].copy() #reduce df to just TX
texas_county_data['fips'] = texas_county_data['fips'].astype(int)
texas_county_data['cases'] = texas_county_data['cases'].astype(int)
texas_county_data['deaths'] = texas_county_data['deaths'].astype(int)
texas_county_data = pd.merge(texas_county_data, census_df, on='fips', how='inner') #join dfs to add population based on fips (state + county ID)
counties = texas_county_data['county'].unique().tolist() #use this list to iterate through county for today's data?


#cases per capita today



#deaths per capita today


###TODO: make daily case/death increase df
###TODO: make per capita calcs
###TODO: find daily county with biggest one day increase