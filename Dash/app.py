import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import pathlib
import plotly.express as px

#region Load Data

data_path = pathlib.Path('.\\data\\covid_data.csv')
covid_cur_clean = pd.read_csv(data_path)

#endregion

#region Preprocess Data

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

mean_stringency = covid_countries.groupby('location')['stringency_index'].mean()
total_deaths = covid_countries.groupby('location')['total_deaths'].max()
max_population = covid_countries.groupby('location')['population'].max()
plot_data = pd.concat([mean_stringency,total_deaths,max_population],axis=1)
plot_data = plot_data.merge(covid_countries[['continent','location']],how='left',on='location')
plot_data['total_deaths_per_population'] = plot_data['total_deaths']/plot_data['population']

fig = px.scatter(plot_data, x="stringency_index", y="total_deaths_per_population", color="continent", hover_data=['location'])

#endregion

#region Start Dash

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.DARKLY]
app = dash.Dash(__name__)

#endregion

#region Navbar

def build_navbar_button(label: str, href: str):
    button = dcc.Link(
        className='navbar-button',
        children=label,
        href=href
    )
    return button

navbar = html.Nav(
    className='navbar navbar-expand-lg navbar-dark bg-primary',
    children=[
        html.P(className='team-logo', children='TeamSierra'),
        build_navbar_button('Home','/'),
        build_navbar_button('Confirmed Cases','/page1'),
        build_navbar_button('Reproduction Rate','/page2'),
        build_navbar_button('Death Rate','/page2')
    ]
)

#endregion

#region Content

content = html.Div(
    id='page-content',
    className='content',
)

#endregion

#region App layout

app.layout = html.Div(
    className='application',
    children=[
        dcc.Location(id='url'),
        navbar,
        content,
    ]
)

#endregion

#region Pages

page_home = html.Div(
    children=[
        html.H1("This is the home page!"),
        html.Img(src="static\\aepphltiqy911.png"),
        dcc.Graph(
            figure=fig
        )
    ]
)

page_1 = html.Div(
    children=[
        html.Div(
            className='page-title',
            children=html.H1(
                children="This is page 1!"
            ),
        )
    ]
)

page_2 = html.Div(
    children=[
        html.Div(
            className='page-title',
            children=html.H1(
                children="This is page 2!"
            ),
        )
    ]
)

#endregion

#region Callbacks

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return page_home
    elif pathname == "/page1":
        return page_1
    elif pathname == "/page2":
        return page_2
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

#endregion

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)