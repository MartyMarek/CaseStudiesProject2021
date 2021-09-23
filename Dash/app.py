import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from dash_html_components.Div import Div
import pandas as pd
import pathlib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask
import statsmodels.api as sm


#region Load & Process Data

# reading in data and converting date to time
data = pd.read_csv(".\\data\\merged_aug_updated.csv")
data.date = pd.to_datetime(data.date, infer_datetime_format=True, dayfirst=True )

# filtering data for chosen states and time frame (removing negative daily doses also)
data.query("state == 'NSW' or state == 'VIC' or state == 'QLD' or state == 'TAS'", inplace=True)
data.query("date <= '2021-08-31'", inplace =True)
data.query("daily_doses > 0", inplace =True)

#back filling missing values
data.bfill(axis = 0, inplace = True)

# Add net transcript and net twitter sentiment columns, along with colours
data = data.assign(
    net_transcript_sentiment = data[
        ['transcript_sentiment_positive','transcript_sentiment_neutral','transcript_sentiment_negative']
    ].idxmax(
        axis='columns'
    ).map(
        {
            'transcript_sentiment_positive': 'Positive',
            'transcript_sentiment_neutral': 'Neutral',
            'transcript_sentiment_negative': 'Negative'
        }
    ),
    net_transcript_sentiment_colour = data[
        ['transcript_sentiment_positive','transcript_sentiment_neutral','transcript_sentiment_negative']
    ].idxmax(
        axis='columns'
    ).map(
        {
            'transcript_sentiment_positive': 'blue',
            'transcript_sentiment_neutral': 'yellow',
            'transcript_sentiment_negative': 'red'
        }
    ),
    net_twitter_sentiment = data[
        ['avr_positive_tweet_sentiment','avr_neutral_tweet_sentiment','avr_negative_tweet_sentiment']
    ].idxmax(
        axis='columns'
    ).map(
        {
            'avr_positive_tweet_sentiment': 'Positive',
            'avr_neutral_tweet_sentiment': 'Neutral',
            'avr_negative_tweet_sentiment': 'Negative'
        }
    ),
    net_twitter_sentiment_colour = data[
        ['avr_positive_tweet_sentiment','avr_neutral_tweet_sentiment','avr_negative_tweet_sentiment']
    ].idxmax(
        axis='columns'
    ).map(
        {
            'avr_positive_tweet_sentiment': 'blue',
            'avr_neutral_tweet_sentiment': 'yellow',
            'avr_negative_tweet_sentiment': 'red'
        }
    )
)

# Correlations
data_corr = data.corr(method='pearson')

#endregion

#region Start Dash

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets=[dbc.themes.DARKLY]
app = dash.Dash(__name__)
#server = Flask(__name__)
#app = dash.Dash(server=server, external_stylesheets=[dbc.themes.DARKLY])
app.title = 'Dashboard'

#endregion

#region Navbar

navbar = html.Nav(
    className='navbar',
    children=[
        html.P(className='team-logo', children='TeamSierra'),
        dcc.Link(
            className='navbar-button',
            children='Home',
            href='/'
        ),
        dcc.Link(
            className='navbar-button',
            children='Press Conferences',
            href='/press-conferences'
        ),
        dcc.Link(
            className='navbar-button',
            children='Twitter',
            href='/twitter'
        )
    ]
)

#endregion

#region Sidebar

sidebar = html.Div(
    className='sidebar-a',
    children=[
        dcc.Markdown(
            className="item-sidebar",
            children='''
            ## Filters
            Use these filters to interact with the plots and discover more insights.
            
            '''
        ),
        html.Label(
            className='item-sidebar',
            children='State:'
        ),
        dcc.Dropdown(
            id = "states-dropdown",
            className='item-dropdown',
            options = [
                {'label' : "Victoria", "value" : 'VIC'},
                {'label' : "Queensland", "value" : 'QLD'},
                {'label' : "New South Wales", "value" : 'NSW'}#,
                #{'label' : "Tasmania", "value" : 'TAS'}
            ],
            value = "VIC"
        ),
        html.Label(
            className='item-sidebar',
            children='Transcript Sentiment:'
        ),
        dcc.Dropdown(
            id = "transcript-sentiment-dropdown",
            className='item-dropdown',
            options = [
                {'label' : "Negative", "value" : 'transcript_sentiment_negative'},
                {'label' : "Neutral", "value" : 'transcript_sentiment_neutral'},
                {'label' : "Positive", "value" : 'transcript_sentiment_positive'}
            ],
            value = "transcript_sentiment_negative"
        ),
        html.Label(
            className='item-sidebar',
            children='Twitter Sentiment:'
        ),
        dcc.Dropdown(
            id = "twitter-sentiment-dropdown",
            className='item-dropdown',
            options = [
                {'label' : "Negative", "value" : 'avr_negative_tweet_sentiment'},
                {'label' : "Neutral", "value" : 'avr_neutral_tweet_sentiment'},
                {'label' : "Positive", "value" : 'avr_positive_tweet_sentiment'}],
            value = "avr_negative_tweet_sentiment"
        ),
        html.Label(
            className='item-sidebar',
            children='Metric:'
        ),
        dcc.Dropdown(
            id = "metric-dropdown",
            className='item-dropdown',
            options = [
                {'label' : "Daily Cases", "value" : 'daily_newcase'},
                {'label' : "Daily Doses", "value" : 'daily_doses'},
                {'label' : "Total Doses", "value" : 'total_doses'},
                {'label' : "Daily Tweets", "value" : 'tweet_total'}
            ],
            value = "daily_doses"
        ),
    ]
)

#endregion

#region Content (Static)

content = html.Div(
    id='page-content',
    className='content-container-a'
)

#endregion

#region App layout (Static)

app.layout = html.Div(
    className='application',
    children=[
        dcc.Location(id='url'),
        navbar,
        sidebar,
        content,
    ]
)

#endregion

#region Pages

page_home = html.Div(
    className='page-container',
    children=[
        # First Row
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                            # This is the home page!
                            Consider a brief introduction to the project.

                            - Who is the audience?
                            - What are the benefits?
                            - How is it NOVEL?

                            '''
                        )
                    ]
                )
            ]
        ),
        # Correlation Heatmap
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Graph(
                            className='item-plot',
                            figure= px.imshow(
                                data_corr,
                                color_continuous_scale='RdBu_r'
                            )
                        ),
                    ]
                ),
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                            # Correlation Map
                            This plot shows the correlation between different metrics overall
                            '''
                        )
                    ]
                )
            ]
        ),
    ]
)

page_press_conferences = html.Div(
    className='page-container',
    children=[
        # First Row
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                            # This page is for exploring the messaging from the state governments
                            Here we want to introduce the different kinds of graphs and analysis on this page.
                            '''
                        )
                    ]
                )
            ]
        ),
        # Transcript Sentiment Over Time
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container-66',
                    children=[
                        dcc.Graph(
                            id='transcript-sentiment-over-time-line-plot',
                            className='item-plot'
                        )
                    ]
                ),
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            id='transcript-sentiment-over-time-markdown',
                            className="item-markdown",
                        )
                    ]
                )
            ]
        ),
        # Metric & Transcript Sentiment Over Time
        html.Div(
            className='row-container',
            children=[
                html.Div(
                    className='column-card',
                    children=[
                        dcc.Markdown(
                            id='metric-and-transcript-sentiment-over-time-markdown',
                            className="item-markdown"
                        )
                    ]
                ),
                html.Div(
                    className='column-card-66',
                    children=[
                        dcc.Graph(
                            id='metric-and-transcript-sentiment-over-time-line-plot',
                            className='item-plot'
                        ),
                        dcc.Graph(
                            id='metric-and-transcript-sentiment-over-time-bar-plot',
                            className='item-plot'
                        )
                    ]
                )
            ]
        ),
        # Transcript Sentiment vs Twitter Sentiment
        html.Div(
            className='row-container',
            children=[
                html.Div(
                    className='column-card-66',
                    children=[
                        dcc.Graph(
                            id='transcript-sentiment-vs-twitter-sentiment-plot',
                            className='item-plot'
                        )
                    ]
                ),
                html.Div(
                    className='column-card',
                    children=[
                        dcc.Markdown(
                            id='transcript-sentiment-vs-twitter-sentiment-markdown',
                            className="item-markdown"
                        )
                    ]
                )
            ]
        ),
        # Transcript Sentiment Analysis
        html.Div(
            className='column-container',
            children=[
                html.Div(
                    className='row-card',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                                # Transcript Sentiment Analysis
                                These bubble charts shows the negative vs positive sentiment of press conferences per state.
                                The size of the bubble indicates number of daily covid cases.
                                This analysis tried to determine the ‘clarity’ of press conference messaging to the public.
                                Either high negative or high positive scores are ‘good’ as they indicate clarity in sentiment and overall message delivery.
                                The area is the middle indicates neutral sentiment and could be perceived as unclear messaging. 
                            '''
                        )
                    ]
                ),
                html.Div(
                    className='row-container',
                    children=[
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "transcript_sentiment_positive",
                                        y = 'transcript_sentiment_negative', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.1, 1.0],
                                        range_y=[0.1, 1.0],
                                        title = "Transcript Sentiment by state",
                                        orientation='h'
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        ),
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "transcript_sentiment_neutral",
                                        y = 'transcript_sentiment_negative', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.0, 0.3],
                                        range_y=[0.0, 1.0],
                                        title = "Transcript Sentiment by state (neutral vs negative)"
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        ),
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "transcript_sentiment_neutral",
                                        y = 'transcript_sentiment_positive', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.0, 0.3],
                                        range_y=[0.0, 1.0],
                                        title = "Transcript Sentiment by state (neutral vs positive)"
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        # Metric vs Transcript Sentiment
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='row-container',
                    children=[
                        html.Div(
                            className='column-container',
                            children=[
                                dcc.Markdown(
                                    id='metric-vs-transcript-sentiment-markdown',
                                    className="item-markdown"
                                ),
                                dcc.Graph(
                                    id='metric-vs-transcript-sentiment-scatter-plot',
                                    className='item-plot'
                                )
                            ]
                        ),
                        html.Div(
                            className='column-container',
                            children=[
                                dcc.Graph(
                                    id='metric-vs-transcript-sentiment-contour-plot',
                                    className='item-plot'
                                )
                            ]
                        )
                    ]
                ),
            ]
        )
    ]
)

page_twitter = html.Div(
    className='page-container',
    children=[
        # First Row
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                            # This is for twitter focussed analysis
                            What did we learn?
                            '''
                        )
                    ]
                )
            ]         
        ),
        # Twitter Sentiment Over Time
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='column-container-66',
                    children=[
                        dcc.Graph(
                            id='twitter-sentiment-over-time-line-plot',
                            className='item-plot'
                        )
                    ]
                ),
                html.Div(
                    className='column-container',
                    children=[
                        dcc.Markdown(
                            id='twitter-sentiment-over-time-markdown',
                            className="item-markdown",
                        )
                    ]
                )
            ]
        ),
        # Metric & Twitter Sentiment Over Time
        html.Div(
            className='row-container',
            children=[
                html.Div(
                    className='column-card',
                    children=[
                        dcc.Markdown(
                            id='metric-and-twitter-sentiment-over-time-markdown',
                            className="item-markdown"
                        )
                    ]
                ),
                html.Div(
                    className='column-card-66',
                    children=[
                        dcc.Graph(
                            id='metric-and-twitter-sentiment-over-time-line-plot',
                            className='item-plot'
                        ),
                        dcc.Graph(
                            id='metric-and-twitter-sentiment-over-time-bar-plot',
                            className='item-plot'
                        )
                    ]
                )
            ]
        ),
        # Twitter Sentiment vs Transcript Sentiment
        html.Div(
            className='row-container',
            children=[
                html.Div(
                    className='column-card-66',
                    children=[
                        dcc.Graph(
                            id='twitter-sentiment-vs-transcript-sentiment-plot',
                            className='item-plot'
                        )
                    ]
                ),
                html.Div(
                    className='column-card',
                    children=[
                        dcc.Markdown(
                            id='twitter-sentiment-vs-transcript-sentiment-markdown',
                            className="item-markdown"
                        )
                    ]
                )
            ]
        ),
        # Twitter Sentiment Analysis
        html.Div(
            className='column-container',
            children=[
                html.Div(
                    className='row-card',
                    children=[
                        dcc.Markdown(
                            className="item-markdown",
                            children='''
                                # Twitter Sentiment Analysis
                                These bubble charts shows the negative vs positive sentiment of press conferences per state.
                                The size of the bubble indicates number of daily covid cases.
                                This analysis tried to determine the ‘clarity’ of press conference messaging to the public.
                                Either high negative or high positive scores are ‘good’ as they indicate clarity in sentiment and overall message delivery.
                                The area is the middle indicates neutral sentiment and could be perceived as unclear messaging. 
                            '''
                        )
                    ]
                ),
                html.Div(
                    className='row-container',
                    children=[
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "avr_positive_tweet_sentiment",
                                        y = 'avr_negative_tweet_sentiment', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.1, 1.0],
                                        range_y=[0.1, 1.0],
                                        title = "Twitter Sentiment by state",
                                        orientation='h'
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        ),
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "avr_neutral_tweet_sentiment",
                                        y = 'avr_negative_tweet_sentiment', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.0, 0.3],
                                        range_y=[0.0, 1.0],
                                        title = "Twitter Sentiment by state (neutral vs negative)"
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        ),
                        html.Div(
                            className='column-card',
                            children=[
                                dcc.Graph(
                                    className='item-plot',
                                    figure= px.scatter(
                                        data,
                                        x = "avr_neutral_tweet_sentiment",
                                        y = 'avr_positive_tweet_sentiment', 
                                        color = "state",
                                        size = "daily_newcase",
                                        size_max = 50,
                                        range_x=[0.0, 0.3],
                                        range_y=[0.0, 1.0],
                                        title = "Twitter Sentiment by state (neutral vs positive)"
                                    ).update_layout(
                                        template = "simple_white"
                                    )
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        # Metric vs Twitter Sentiment
        html.Div(
            className='row-card',
            children=[
                html.Div(
                    className='row-container',
                    children=[
                        html.Div(
                            className='column-container',
                            children=[
                                dcc.Markdown(
                                    id='metric-vs-twitter-sentiment-markdown',
                                    className="item-markdown"
                                ),
                                dcc.Graph(
                                    id='metric-vs-twitter-sentiment-scatter-plot',
                                    className='item-plot'
                                )
                            ]
                        ),
                        html.Div(
                            className='column-container',
                            children=[
                                dcc.Graph(
                                    id='metric-vs-twitter-sentiment-contour-plot',
                                    className='item-plot'
                                )
                            ]
                        )
                    ]
                ),
            ]
        )
    ]
)

#endregion

#region Functions

def get_transcript_sentiment_text(selected_transcript_sentiment):

    if 'positive' in selected_transcript_sentiment:
        return 'Positive Transcript Sentiment'
    elif 'negative' in selected_transcript_sentiment:
        return 'Negative Transcript Sentiment'
    elif 'neutral' in selected_transcript_sentiment:
        return 'Neutral Transcript Sentiment'
    else:
        return 'No Transcript Sentiment Selected'

def get_twitter_sentiment_text(selected_twitter_sentiment):

    if 'positive' in selected_twitter_sentiment:
        return 'Positive Twitter Sentiment'
    elif 'negative' in selected_twitter_sentiment:
        return 'Negative Twitter Sentiment'
    elif 'neutral' in selected_twitter_sentiment:
        return 'Neutral Twitter Sentiment'
    else:
        return 'No Twitter Sentiment Selected'

def get_state_text(selected_state):

    if 'VIC' in selected_state:
        return 'Victoria'
    elif 'QLD' in selected_state:
        return 'Queensland'
    elif 'NSW' in selected_state:
        return 'New South Wales'
    elif 'TAS' in selected_state:
        return 'Tasmania'
    else:
        return 'No State Selected'

def get_metric_text(selected_metric):

    if 'daily_doses' in selected_metric:
        return 'Daily Doses'
    elif 'daily_newcase' in selected_metric:
        return 'Daily Cases'
    elif 'total_doses' in selected_metric:
        return 'Total Cases'
    elif 'tweet_total' in selected_metric:
        return 'Daily Tweets'
    else:
        return 'No Metric Selected'

#endregion

#region Callbacks

#region Press Conference Page

# Transcript Sentiment Over Time
@app.callback(
    [
        Output('transcript-sentiment-over-time-line-plot', 'figure'),
        Output('transcript-sentiment-over-time-markdown', 'children')
    ],
    [
        Input('transcript-sentiment-dropdown', 'value')
    ]
)
def render(selected_transcript_sentiment):

    transcript_sentiment_text = get_transcript_sentiment_text(selected_transcript_sentiment)
    fig_title = '{0} Over Time'.format(transcript_sentiment_text)

    markdown = '''
        # {0}
        This graph shows the change in sentiment from August 1 to August 31 for Vicotria, Queensland and New South Wales. 
        NSW is consistantly more negative than other states, whilst QLD and VIC are more positive. 
        All states show a relatively low proportion of neutral sentiment.
    '''.format(fig_title)

    fig = px.line(
        data,
        x = "date",
        y =selected_transcript_sentiment ,
        color = "state",
        template = "simple_white"
    ).update_layout(
        title=fig_title,
        xaxis_title='Date',
        yaxis_title=transcript_sentiment_text
    )

    return [fig, markdown]

# Metric & Transcript Sentiment Over Time
@app.callback(
    [
        Output('metric-and-transcript-sentiment-over-time-line-plot', 'figure'),
        Output('metric-and-transcript-sentiment-over-time-bar-plot', 'figure'),
        Output('metric-and-transcript-sentiment-over-time-markdown', 'children')
    ],
    [
        Input('states-dropdown', 'value'),
        Input('transcript-sentiment-dropdown', 'value'),
        Input('metric-dropdown', 'value')
    ]
)
def render(selected_state, selected_transcript_sentiment, selected_metric):

    transcript_sentiment_text = get_transcript_sentiment_text(selected_transcript_sentiment)
    state_text = get_state_text(selected_state)
    metric_text = get_metric_text(selected_metric)
    fig_title = "Number of {0} and {1} Over Time in {2}".format(metric_text,transcript_sentiment_text, state_text)

    filtdf= data[data["state"] == selected_state]

    fig = make_subplots(
        rows = 2,
        shared_xaxes = True,
        vertical_spacing = 0.15
    ).add_trace(
        go.Scatter(
            x=filtdf["date"],
            y=filtdf[selected_metric],
            name=metric_text
        ),
        row = 1, col =1
    ).add_trace(
        go.Bar(
            x=filtdf["date"],
            y=filtdf[selected_transcript_sentiment],
            name="Proportion of {0}".format(transcript_sentiment_text)
        ),
        row = 2, col = 1
    ).update_yaxes(
        title = str.title("Number of {0}".format(metric_text)),
        row =1,
        col = 1,
        title_font = {"size":10},
        title_standoff = 30
    ).update_yaxes(
        title = str.title("Proportion of {0}".format(transcript_sentiment_text)),
        row =2,
        col = 1,
        title_font = {"size":10},
        title_standoff = 30
    ).update_layout(
        title_text= str.title(fig_title), 
        template = "simple_white"
    )

    fig_bar_title = 'Sentiment Proportion Over Time for {0}'.format(state_text)

    fig_bar = px.bar(
        data_frame=filtdf,
        x='date',
        y=['transcript_sentiment_negative','transcript_sentiment_neutral','transcript_sentiment_positive']
    ).update_layout(
        title=fig_bar_title,
        xaxis_title='Date',
        yaxis_title="Sentiment Proportion"
    )

    markdown = '''
        # {0}
        This graph shows the change in goverment press conference sentiment and the daily doses of covid-19 vaccine administered.
        The top portion shows the number of doses in thousands, bottom portion shows the sentiment proportion of transcript for each
        date. 
    '''.format(fig_title)

    return [fig, fig_bar, markdown]

# Transcript Sentiment vs Twitter Sentiment
@app.callback(
    [
        Output('transcript-sentiment-vs-twitter-sentiment-plot', 'figure'),
        Output('transcript-sentiment-vs-twitter-sentiment-markdown', 'children')
    ],
    [
        Input('states-dropdown', 'value'),
        Input('transcript-sentiment-dropdown', 'value'),
        Input('twitter-sentiment-dropdown','value')
    ]
)
def render(selected_state, selected_transcript_sentiment,selected_twitter_sentiment ):

    transcript_sentiment_text = get_transcript_sentiment_text(selected_transcript_sentiment)
    twitter_sentiment_text = get_twitter_sentiment_text(selected_twitter_sentiment)
    state_text = get_state_text(selected_state)
    fig_title = "{0} vs. {1} in {2}".format(twitter_sentiment_text, transcript_sentiment_text, state_text)


    filt = data[data["state"] == selected_state]

    fig = px.scatter(
        filt,
        x = selected_transcript_sentiment,
        y = selected_twitter_sentiment,
        trendline="ols"
    ).update_layout(
        xaxis_title=transcript_sentiment_text,
        yaxis_title=twitter_sentiment_text,
        title= str.title(fig_title), 
        template = "simple_white"
    )

    markdown = '''
        # {0}
        This scatterplot allows users to compare transcript and twitter sentiment for selected state. 
        Input is controlled by the dropdowns at the top. 
        Trendline shows the strength of the relationship. 
        Appears as though there is not a strong relationship between transcript and twitter sentiment.
    '''.format(fig_title)

    return [fig, markdown]

# Metric vs Transcript Sentiment
@app.callback(
    [
        Output(
            component_id='metric-vs-transcript-sentiment-scatter-plot',
            component_property='figure'
        ),
        Output(
            component_id='metric-vs-transcript-sentiment-contour-plot',
            component_property='figure'
        ),
        Output(
            component_id='metric-vs-transcript-sentiment-markdown',
            component_property='children'
        )
    ],
    [
        Input(
            component_id='transcript-sentiment-dropdown',
            component_property='value'
        ),
        Input(
            component_id='metric-dropdown',
            component_property='value'
        )
    ]
)
def render_plot(selected_transcript_sentiment,selected_metric):

    transcript_sentiment_text = get_transcript_sentiment_text(selected_transcript_sentiment)
    metric_text = get_metric_text(selected_metric)
    fig_title = "{0} vs {1}".format(metric_text, transcript_sentiment_text)

    fig = px.scatter(
        data,
        x = selected_metric,
        y = selected_transcript_sentiment, 
        color = "state",
        size='total_doses',
        size_max = 50,
        range_y=[0.0, 1.0],
        title = fig_title
    ).update_layout(
        template = "simple_white",
        xaxis_title=metric_text,
        yaxis_title=transcript_sentiment_text
    )

    fig_contour = px.density_contour(
        data_frame=data,
        x=selected_metric,
        y=selected_transcript_sentiment,
        #facet_col='state',
        marginal_x='histogram',
        marginal_y='histogram',
        color='state',
        title=fig_title,
        height=800
    ).update_layout(
        template = "simple_white",
        xaxis_title=metric_text,
        yaxis_title=transcript_sentiment_text
    )

    markdown = '''
        # {0}
        These bubble charts show total doses by state vs sentiment of press conferences
    '''.format(fig_title)

    return [fig, fig_contour, markdown]

#endregion

#region Twitter Page

# Twitter Sentiment Over Time
@app.callback(
    [
        Output('twitter-sentiment-over-time-line-plot', 'figure'),
        Output('twitter-sentiment-over-time-markdown', 'children')
    ],
    [
        Input('twitter-sentiment-dropdown', 'value')
    ]
)
def render(selected_twitter_sentiment):

    twitter_sentiment_text = get_twitter_sentiment_text(selected_twitter_sentiment)
    fig_title = '{0} Over Time'.format(twitter_sentiment_text)

    markdown = '''
        # {0}
        This graph shows the change in sentiment from August 1 to August 31 for Vicotria, Queensland and New South Wales. 
        NSW is consistantly more negative than other states, whilst QLD and VIC are more positive. 
        All states show a relatively low proportion of neutral sentiment.
    '''.format(fig_title)

    fig = px.line(
        data,
        x = "date",
        y =selected_twitter_sentiment ,
        color = "state",
        template = "simple_white"
    ).update_layout(
        title=fig_title,
        xaxis_title='Date',
        yaxis_title=twitter_sentiment_text
    )

    return [fig, markdown]

# Metric & Twitter Sentiment Over Time
@app.callback(
    [
        Output('metric-and-twitter-sentiment-over-time-line-plot', 'figure'),
        Output('metric-and-twitter-sentiment-over-time-bar-plot', 'figure'),
        Output('metric-and-twitter-sentiment-over-time-markdown', 'children')
    ],
    [
        Input('states-dropdown', 'value'),
        Input('twitter-sentiment-dropdown', 'value'),
        Input('metric-dropdown', 'value')
    ]
)
def render(selected_state, selected_twitter_sentiment, selected_metric):

    twitter_sentiment_text = get_twitter_sentiment_text(selected_twitter_sentiment)
    state_text = get_state_text(selected_state)
    metric_text = get_metric_text(selected_metric)
    fig_title = "Number of {0} and {1} Over Time in {2}".format(metric_text,twitter_sentiment_text, state_text)

    filtdf= data[data["state"] == selected_state]

    fig = make_subplots(
        rows = 2,
        shared_xaxes = True,
        vertical_spacing = 0.15
    ).add_trace(
        go.Scatter(
            x=filtdf["date"],
            y=filtdf[selected_metric],
            name=metric_text
        ),
        row = 1, col =1
    ).add_trace(
        go.Bar(
            x=filtdf["date"],
            y=filtdf[selected_twitter_sentiment],
            name="Proportion of {0}".format(twitter_sentiment_text)
        ),
        row = 2, col = 1
    ).update_yaxes(
        title = str.title("Number of {0}".format(metric_text)),
        row =1,
        col = 1,
        title_font = {"size":10},
        title_standoff = 30
    ).update_yaxes(
        title = str.title("Proportion of {0}".format(twitter_sentiment_text)),
        row =2,
        col = 1,
        title_font = {"size":10},
        title_standoff = 30
    ).update_layout(
        title_text= str.title(fig_title), 
        template = "simple_white"
    )

    fig_bar_title = 'Sentiment Proportion Over Time for {0}'.format(state_text)

    fig_bar = px.bar(
        data_frame=filtdf,
        x='date',
        y=['avr_negative_tweet_sentiment','avr_neutral_tweet_sentiment','avr_positive_tweet_sentiment']
    ).update_layout(
        title=fig_bar_title,
        xaxis_title='Date',
        yaxis_title="Sentiment Proportion"
    )

    markdown = '''
        # {0}
        This graph shows the change in goverment press conference sentiment and the daily doses of covid-19 vaccine administered.
        The top portion shows the number of doses in thousands, bottom portion shows the sentiment proportion of twitter for each
        date. 
    '''.format(fig_title)

    return [fig, fig_bar, markdown]

# Twitter Sentiment vs Transcript Sentiment
@app.callback(
    [
        Output('twitter-sentiment-vs-transcript-sentiment-plot', 'figure'),
        Output('twitter-sentiment-vs-transcript-sentiment-markdown', 'children')
    ],
    [
        Input('states-dropdown', 'value'),
        Input('twitter-sentiment-dropdown', 'value'),
        Input('transcript-sentiment-dropdown','value')
    ]
)
def render(selected_state, selected_twitter_sentiment, selected_transcript_sentiment ):

    twitter_sentiment_text = get_twitter_sentiment_text(selected_twitter_sentiment)
    transcript_sentiment_text = get_transcript_sentiment_text(selected_transcript_sentiment)
    state_text = get_state_text(selected_state)
    fig_title = "{0} vs. {1} in {2}".format(twitter_sentiment_text, transcript_sentiment_text, state_text)


    filt = data[data["state"] == selected_state]

    fig = px.scatter(
        filt,
        x = selected_twitter_sentiment,
        y = selected_transcript_sentiment,
        trendline="ols"
    ).update_layout(
        xaxis_title=twitter_sentiment_text,
        yaxis_title=transcript_sentiment_text,
        title= str.title(fig_title), 
        template = "simple_white"
    )

    markdown = '''
        # {0}
        This scatterplot allows users to compare twitter and transcript sentiment for selected state. 
        Input is controlled by the dropdowns at the top. 
        Trendline shows the strength of the relationship. 
        Appears as though there is not a strong relationship between twitter and transcript sentiment.
    '''.format(fig_title)

    return [fig, markdown]

# Metric vs Twitter Sentiment
@app.callback(
    [
        Output(
            component_id='metric-vs-twitter-sentiment-scatter-plot',
            component_property='figure'
        ),
        Output(
            component_id='metric-vs-twitter-sentiment-contour-plot',
            component_property='figure'
        ),
        Output(
            component_id='metric-vs-twitter-sentiment-markdown',
            component_property='children'
        )
    ],
    [
        Input(
            component_id='twitter-sentiment-dropdown',
            component_property='value'
        ),
        Input(
            component_id='metric-dropdown',
            component_property='value'
        )
    ]
)
def render_plot(selected_twitter_sentiment,selected_metric):

    twitter_sentiment_text = get_twitter_sentiment_text(selected_twitter_sentiment)
    metric_text = get_metric_text(selected_metric)
    fig_title = "{0} vs {1}".format(metric_text, twitter_sentiment_text)

    fig = px.scatter(
        data,
        x = selected_metric,
        y = selected_twitter_sentiment, 
        color = "state",
        size='total_doses',
        size_max = 50,
        range_y=[0.0, 1.0],
        title = fig_title
    ).update_layout(
        template = "simple_white",
        xaxis_title=metric_text,
        yaxis_title=twitter_sentiment_text
    )

    fig_contour = px.density_contour(
        data_frame=data,
        x=selected_metric,
        y=selected_twitter_sentiment,
        #facet_col='state',
        marginal_x='histogram',
        marginal_y='histogram',
        color='state',
        title=fig_title,
        height=800
    ).update_layout(
        template = "simple_white",
        xaxis_title=metric_text,
        yaxis_title=twitter_sentiment_text
    )

    markdown = '''
        # {0}
        These bubble charts show total doses by state vs sentiment of press conferences
    '''.format(fig_title)

    return [fig, fig_contour, markdown]


#endregion

# Render content for selected page
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    if pathname == "/":
        return page_home
    elif pathname == "/press-conferences":
        return page_press_conferences
    elif pathname == "/twitter":
        return page_twitter
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
    app.run_server(debug=True)
    #app.run_server(debug=False, host='0.0.0.0', port='80')