import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import pathlib
import plotly.express as px

#region Load Data

#covid_cur_clean = pd.read_csv('.\\data\\covid_data.csv')
#covid_countries = pd.read_pickle('.\\data\\covid_countries.pkl')
#covid_regions = pd.read_pickle('.\\data\\covid_regions.pkl')

# Home page
home_scatter_test_01 = pd.read_pickle(".\\data\\plots\\home_scatter_test_01.pkl")

# Continent page
continent_scatter_marty_01 = pd.read_pickle(".\\data\\plots\\continent_scatter_marty_01.pkl")

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
        build_navbar_button('Continent','/continent'),
        build_navbar_button('Country','/country'),
        build_navbar_button('Death Rate','/country')
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
        #html.Img(src="static\\aepphltiqy911.png"),
        # Test scatter plot on home page
        dcc.Graph(
            figure= px.scatter(
                home_scatter_test_01,
                x="stringency_index",
                y="total_deaths_per_population",
                color="continent",
                hover_data=['location']
            )
        )
    ]
)

# Continent graphs

page_continent = html.Div(
    children=[
        html.Div(
            className='page-title',
            children=html.H1(
                children="This is page 1!"
            ),
        ),
        dcc.Graph(
            figure = px.scatter(
                continent_scatter_marty_01,
                x="new_cases",
                y="stringency_index",
                color=continent_scatter_marty_01.index.get_level_values(0),
                size='total_cases',
                animation_frame=continent_scatter_marty_01.index.get_level_values(1),
                log_x=True
            )
        )
    ]
)

page_country = html.Div(
    children=[
        html.Div(
            className='page-title',
            children=html.H1(
                children="This is page 2!"
            )
        ),
        #dcc.Graph(
        #    figure = px.scatter(
        #        covid_countries,
        #        x="new_cases",
        #        y="stringency_index",
        #        color="location",
        #        size='total_cases',
        #        animation_frame="date",
        #        log_x=True
        #    )
        #)
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
    elif pathname == "/continent":
        return page_continent
    elif pathname == "/country":
        return page_country
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