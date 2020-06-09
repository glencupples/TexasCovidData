#TXCovidData
import pandas as pd
import requests
from datetime import date, timedelta
import datetime
import yagmail
from EmailPassword import password
from tabulate import tabulate

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

#get all county covid data and reduce to TX
all_county_data = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv') #make df with all counties
texas_county_data = all_county_data[all_county_data['state']=='Texas'].copy() #reduce df to just TX
texas_county_data['fips'] = texas_county_data['fips'].astype(int)
texas_county_data['cases'] = texas_county_data['cases'].astype(int)
texas_county_data['deaths'] = texas_county_data['deaths'].astype(int)
texas_county_data = pd.merge(texas_county_data, census_df, on='fips', how='inner') #join dfs to add population based on fips (state + county ID)


#create yesterday and two days ago data
date_yesterday = date.today() - timedelta(days = 1)
date_yesterday = date_yesterday.strftime('%Y-%m-%d')
date_twodaysago = date.today() - timedelta(days = 2)
date_twodaysago = date_twodaysago.strftime('%Y-%m-%d')

yesterday_county_data = texas_county_data.loc[texas_county_data['date'] == date_yesterday]
twodaysago_county_data = texas_county_data.loc[texas_county_data['date'] == date_twodaysago]





#create two dfs and rename columns to yesterdaycases, todaycases, etc.. merge both dfs on fips
compare_yesterday_data =  yesterday_county_data.copy()
compare_yesterday_data.rename(columns = {'cases':'yesterdaycases', 'deaths':'yesterdaydeaths'}, inplace = True)
compare_twodaysago_data = twodaysago_county_data.copy()
compare_twodaysago_data.rename(columns = {'cases':'twodaysagocases','deaths':'twodaysagodeaths'}, inplace = True)
compare_twodaysago_data = compare_twodaysago_data[['twodaysagocases','twodaysagodeaths','fips']] #reduce before joining
compare_data = pd.merge(compare_yesterday_data, compare_twodaysago_data, on='fips', how='inner') #join dfs to be able to subtract two columns for increase

#top 5 county case count
display_case_total = compare_data.sort_values('yesterdaycases', ascending=False) #yesterdaycases is field from merged df with most recent day's total
display_case_total = display_case_total[:5]
display_case_total = display_case_total[['county','yesterdaycases']]
display_case_total = tabulate(display_case_total, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting

#top 5 county death count
display_death_total = compare_data.sort_values('yesterdaydeaths', ascending=False) #yesterdaydeaths is field from merged df with most recent day's total
display_death_total = display_death_total[:5]
display_death_total = display_death_total[['county','yesterdaydeaths']]
display_death_total = tabulate(display_death_total, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting

#biggest case increase
compare_case_data = compare_data.copy()
compare_case_data['caseIncrease'] = compare_case_data['yesterdaycases']-compare_case_data['twodaysagocases']
compare_case_data.sort_values('caseIncrease', ascending=False, inplace=True) 
display_case_data = compare_case_data[:5]
display_case_data = display_case_data[['county','caseIncrease']]
display_case_data = tabulate(display_case_data, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#biggest case increase per capita
compare_case_data['casePerCapitaIncrease'] = compare_case_data['caseIncrease']/compare_case_data['pop']
compare_case_data.sort_values('casePerCapitaIncrease', ascending=False, inplace=True) 
display_casePCIncrease_data = compare_case_data[:5]
display_casePCIncrease_data = display_casePCIncrease_data[['county','caseIncrease']]
display_casePCIncrease_data = tabulate(display_casePCIncrease_data, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#biggest death increase
compare_death_data = compare_data.copy()
compare_death_data['deathIncrease'] = compare_death_data['yesterdaydeaths']-compare_death_data['twodaysagodeaths']
compare_death_data.sort_values('deathIncrease', ascending=False, inplace=True) 
display_death_data = compare_death_data[:5]
display_death_data = display_death_data[['county','deathIncrease']]
display_death_data = tabulate(display_death_data, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#biggest death increase per capita
compare_death_data['deathPerCapitaIncrease'] = compare_death_data['deathIncrease']/compare_death_data['pop']
compare_death_data.sort_values('deathPerCapitaIncrease', ascending=False, inplace=True) 
display_deathPCIncrease_data = compare_death_data[:5]
display_deathPCIncrease_data = display_deathPCIncrease_data[['county','deathIncrease']]
display_deathPCIncrease_data = tabulate(display_deathPCIncrease_data, headers = "keys", tablefmt="html", numalign="right", showindex=False) #tabulate formatting 

#email it out
yag = yagmail.SMTP("glen.cupples.dev@gmail.com",password)
contents = [
	"Top 5 county case total"+
	display_case_total,
	"Top 5 county death total"+
	display_death_total,
	"Biggest case increase:"+
    display_case_data,
    "Biggest case increase per capita:"+
    display_casePCIncrease_data,
    "Biggest death increase:"+
    display_death_data,
    "Biggest death increase per capita:"+
    display_deathPCIncrease_data,
]
yag.send('glen.cupples@gmail.com', 'TX Daily Covid Update', contents)


###TODO: compare distance from highest case counties to Travis, or case count by 10 closest counties
