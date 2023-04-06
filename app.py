import pandas as pd
import requests
import twitter
import plotly.express as px
import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


external_stylesheets = [dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Store(id='tweet-df'),
    html.Br(),
    dcc.Loading(id="loading", type="default", children=html.Div(id="loading-output")),
    html.Br(),
    html.Center(html.H1('Twitter Data')),
    html.Br(),
    html.Div([
        html.Center([dcc.Input(id='usernames', type='text', placeholder='Twitter usernames: google,amazon', value='',
                               style={'margin-bottom': 10, 'width': '40%'})]),
        html.Center([dcc.Input(id='start-date', type='text', placeholder='Start date (yyyy-mm-dd)', value='',
                               style={'margin-bottom': 10, 'width': '40%'})]),
        html.Center([dcc.Input(id='end-date', type='text', placeholder='End date (yyyy-mm-dd)', value='',
                               style={'margin-bottom': 10, 'width': '40%'})]),
    ], style={'display': 'inline-block', 'width': '100%'}, id='inputs'),
    html.Br(),
    html.Br(),
    html.Div([
        html.Center([html.Button('Get Tweets',
                                 id='get-tweets',
                                 n_clicks=0,
                                 style={'margin-right': 10, 'margin-bottom': 10})]),
    ]),
    html.Br(),
    html.Div([
        html.Div(dcc.Graph(id='tweet-data', style={'display': 'none'}),
                 style={'display': 'inline-block', 'width': '60%'}),
        html.Div(id='tweet-container', style={'display': 'inline-block', 'width': '30%'})
    ], style={'display': 'flex', 'justifyContent': 'center'})
])


@app.callback(Output('tweet-data', 'figure'),
              Output('tweet-data', 'style'),
              Output('tweet-df', 'data'),
              Output('loading-output', 'children'),
              Input('get-tweets', 'n_clicks'),
              State('usernames', 'value'),
              State('start-date', 'value'),
              State('end-date', 'value'))
def get_data(clicks, usernames, start_date, end_date):
    if clicks == 0:
        raise PreventUpdate
    elif clicks > 0:
        if end_date != '':
            tweets = twitter.get_tweets(usernames=usernames, start=start_date, end=end_date)
        else:
            tweets = twitter.get_tweets(usernames=usernames, start=start_date)

        fig = px.scatter(tweets, x='created_at', y='public_metrics.like_count',
                         title=f'{usernames} Tweets', color='account',
                         hover_data=['account', 'created_at',
                                     'public_metrics.like_count', 'public_metrics.impression_count'])
        fig.update_layout(dict(xaxis_title='Date', yaxis_title='Likes'))
        return fig, {}, tweets.to_dict(orient='records'), clicks


@app.callback(Output('tweet-container', 'children'),
              Input('tweet-data', 'hoverData'),
              Input('tweet-df', 'data'))
def hover_event(hover, tweet_dict):
    if hover:
        df = pd.DataFrame(tweet_dict)
        idx = hover['points'][0]['pointIndex']
        name = hover['points'][0]['customdata'][0]
        hover_data = df[df['account'].eq(name)].iloc[idx]
        url = f"https://twitter.com/{hover_data['account']}/status/{hover_data['id']}"
        embed = requests.get(f'https://publish.twitter.com/oembed?url={url}').json()
        iframe = html.Iframe(srcDoc=embed['html'], style={'width': '100%',
                                                          'height': '90%',
                                                          'margin-top': '10px',
                                                          'margin-left': '10px'})
        return iframe

    if tweet_dict:
        df = pd.DataFrame(tweet_dict)
        hover_data = df.iloc[0]
        url = f"https://twitter.com/{hover_data['account']}/status/{hover_data['id']}"
        embed = requests.get(f'https://publish.twitter.com/oembed?url={url}').json()
        iframe = html.Iframe(srcDoc=embed['html'], style={'width': '100%',
                                                          'height': '90%',
                                                          'margin-top': '10px',
                                                          'margin-left': '10px'})
        return iframe


if __name__ == '__main__':
    app.run_server(debug=False)
