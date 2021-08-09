'''

Naming Convention:
page_GraphType_plotname_sequence.csv??

'''

import pandas as pd
import pathlib

#region Load Base Data

covid_cur_clean = pd.read_csv('.\\data\\covid_data.csv')
covid_countries = pd.read_pickle('.\\data\\covid_countries.pkl')
covid_regions = pd.read_pickle('.\\data\\covid_regions.pkl')

#endregion

#region Split regions and countries

'''

# Define regions list (identified by irregular iso_code values)
regions_list = [
    'Africa',
    'Asia',
    'European Union',
    'Europe',
    'International',
    'North America',
    'Oceania',
    'South America',
    'World'
]

# Split countries
covid_countries = covid_cur_clean.loc[~covid_cur_clean['location'].isin(regions_list)]
# Split regions
covid_regions = covid_cur_clean.loc[covid_cur_clean['location'].isin(regions_list)]

# Write pickles
covid_countries.to_pickle(".\\data\\covid_countries.pkl")
covid_regions.to_pickle(".\\data\\covid_regions.pkl")

'''

#endregion

#region Home_Scatter_Testing_01

mean_stringency = covid_countries.groupby('location')['stringency_index'].mean()
total_deaths = covid_countries.groupby('location')['total_deaths'].max()
max_population = covid_countries.groupby('location')['population'].max()
plot_data = pd.concat([mean_stringency,total_deaths,max_population],axis=1)
plot_data = plot_data.merge(covid_countries[['continent','location']],how='left',on='location')
plot_data['total_deaths_per_population'] = plot_data['total_deaths']/plot_data['population']

plot_data.to_pickle(".\\data\\plots\\home_scatter_test_01.pkl")

#endregion

#region continent_scatter_marty_01

plot_data = covid_countries.groupby(['continent','date']).agg({'new_cases' : 'sum', 'stringency_index' : 'sum', 'total_cases' : 'sum'})
plot_data.to_pickle(".\\data\\plots\\continent_scatter_marty_01.pkl")

#endregion