'''

Naming Convention:
page_GraphType_plotname_sequence.csv??

'''

import pandas as pd
import pathlib

#region Load Base Data

#covid_cur_clean = pd.read_csv('.\\data\\covid_data.csv')
covid_cur_clean = pd.read_csv('./data/covid_data.csv')
#covid_countries = pd.read_pickle('.\\data\\covid_countries.pkl')
#covid_regions = pd.read_pickle('.\\data\\covid_regions.pkl')

#covid_cur_clean = pd.read_hdf('.\\data\\covid_data.h5', key='covid_all')
#covid_countries = pd.read_hdf('.\\data\\covid_data.h5', key='covid_countries')
#covid_regions = pd.read_hdf('.\\data\\covid_data.h5', key='covid_regions')

#endregion

#region Split regions and countries



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
#covid_countries.to_pickle(".\\data\\covid_countries.pkl")
#covid_regions.to_pickle(".\\data\\covid_regions.pkl")
#covid_countries.to_hdf('.\\data\\covid_data.h5', key='covid_countries', mode='a')
#covid_regions.to_hdf('.\\data\\covid_data.h5', key='covid_regions', mode='a')
#covid_cur_clean.to_hdf('.\\data\\covid_data.h5', key='covid_all', mode='a')
covid_countries.to_hdf('./data/covid_data.h5', key='covid_countries', mode='a')
covid_regions.to_hdf('./data/covid_data.h5', key='covid_regions', mode='a')
covid_cur_clean.to_hdf('./data/covid_data.h5', key='covid_all', mode='a')



#endregion

#region Home_Scatter_Testing_01

plot_data = covid_countries.groupby(
    [
        'location'
    ]
).agg(
    {
        'stringency_index': 'mean',
        'total_deaths': 'max',
        'population': 'max'
    }
).merge(
    covid_countries[['continent','location']],
    how='left',
    on='location'
).assign(
    total_deaths_per_population = lambda row: row['total_deaths']/row['population']
)

#plot_data.to_pickle(".\\data\\plots\\home_scatter_test_01.pkl")
#plot_data.to_csv(".\\data\\plots\\home_scatter_test_01.csv")
plot_data.to_hdf('./data/plots/plot_data.h5', key='home_scatter_test_01', mode='a')
#a = pd.read_hdf('.\\data\\plots\\plot_data.h5', key='home_scatter_test_01')
#endregion

#region continent_scatter_marty_01

plot_data = covid_countries.groupby(
    [
        'continent',
        'date'
    ]
).agg(
    {
        'new_cases' : 'sum',
        'stringency_index' : 'sum',
        'total_cases' : 'sum'
    }
)

#plot_data.to_pickle(".\\data\\plots\\continent_scatter_marty_01.pkl")
#plot_data.to_csv(".\\data\\plots\\marty_scatter_01.csv")
plot_data.to_hdf('./data/plots/plot_data.h5', key='continent_scatter_marty_01', mode='a')

#endregion