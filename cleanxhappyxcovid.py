import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.metrics import r2_score

read_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

population_url = 'https://www.worldometers.info/world-population/population-by-country/'

recovery_url = 'https://raw.githubusercontent.com/crondonm/TrackingR/main/Estimates-Database/database.csv'

happiness_url = 'https://raw.githubusercontent.com/abel-salau/happy-x-covid/main/A-Z%20world%20happiness.csv'

#request begin to webscrape
r = requests.get(population_url)
soup = BeautifulSoup(r.content, "lxml")
countries = soup.find_all("table")[0]

#needed databases
happy_df = pd.read_csv(happiness_url)
countries_df = pd.read_html(str(countries))[0]
recovery_df = pd.read_csv(recovery_url)
covid_rate_df = pd.read_csv(read_url)

#countries that work / filtering
matching_countries = covid_rate_df['Country/Region'].to_numpy()
happy_df = happy_df[happy_df['Country name'].isin(matching_countries)]

top_ten = happy_df['Country name'].to_numpy()

covid_rate_df = covid_rate_df[covid_rate_df['Province/State'].isnull()]
covid_rate_df = covid_rate_df[covid_rate_df['Country/Region'].isin(top_ten)]
covid_rate_df.drop(columns=covid_rate_df.columns[0], axis=1, inplace=True)
covid_rate_df = covid_rate_df.rename(columns={covid_rate_df.columns[len(covid_rate_df.columns)-1]: 'Cumulative Confirmed Cases'})
covid_rate_df.drop(columns=covid_rate_df.columns[1: len(covid_rate_df.columns)-1], axis=1, inplace=True)

#repeat filtering
matching_countries_2 = covid_rate_df['Country/Region'].to_numpy()
happy_df = happy_df[happy_df['Country name'].isin(matching_countries_2)]
top_ten_2 = happy_df['Country name'].to_numpy()
covid_rate_df = covid_rate_df[covid_rate_df['Country/Region'].isin(top_ten_2)]

#things to add to the covid rate data base

#population info
countries_df = countries_df[countries_df['Country (or dependency)'].isin(top_ten_2)]
countries_df.drop(columns=countries_df.columns[0], axis=1, inplace=True)
countries_df = countries_df.sort_values(by ='Country (or dependency)', ascending = 1)
countries_df.drop(columns=countries_df.columns[2], axis=1, inplace=True)
countries_df = countries_df.rename(columns={countries_df.columns[1]: 'Population'})

pop_array = countries_df['Population'].to_numpy() #population amount
name_array = countries_df['Country (or dependency)'].to_numpy() #country name
density_array = countries_df['Density (P/Km²)'].to_numpy() #population density

#repeat filtering
happy_df = happy_df[happy_df['Country name'].isin(name_array)]
covid_rate_df = covid_rate_df[covid_rate_df['Country/Region'].isin(name_array)]

#reproduction rate
recovery_df = recovery_df[recovery_df['Country/Region'].isin(name_array)]
recovery_df = recovery_df.drop_duplicates(subset='Country/Region' , keep= "last", inplace=False)
R = recovery_df['R'].to_numpy()



#Calculation - Case Per Capita
cum_case = covid_rate_df['Cumulative Confirmed Cases'].to_numpy()
cpc = []
for i in range(len(cum_case)):
    cpc = np.append(cpc,cum_case[i]/pop_array[i])


#insert info
happiness_index = happy_df['Ladder score'].to_numpy() # Happiness Score First
covid_rate_df.insert(loc=0, column='Happiness Index', value=happiness_index)

covid_rate_df.insert(loc=len(covid_rate_df.columns), column='Population', value=pop_array)
covid_rate_df.insert(loc=len(covid_rate_df.columns), column='Case per Capita', value=cpc)
covid_rate_df.insert(loc=len(covid_rate_df.columns), column='Density (P/Km²)', value=density_array)
covid_rate_df.insert(loc=len(covid_rate_df.columns), column='R Value', value=R)

#final form
covid_rate_df = covid_rate_df.sort_values(by ='Happiness Index', ascending = 0)


print(covid_rate_df)

var1 = covid_rate_df['R Value'].to_numpy()
var2 = covid_rate_df['Case per Capita'].to_numpy()

R_t = r2_score(var2,var1)
kek = np.corrcoef(var1,var2)[0,1]


print("Corellation Coefficient = "+ str(kek))
covid_rate_df.to_csv("/Users/abelsalau/Documents/PROJ/happinessXcovid.csv")
