import os

import pandas_datareader.data as web
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.Div(children='''
        Symbol to graph:
    '''),
    dcc.Input(id='ticker', value='FB', type='text'),
    dcc.DatePickerSingle(
        id='dropdown_dt',
        date=datetime.datetime(2016, 1, 1)
        ),

    html.Div(id='output-graph'),
])

@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [
        Input(component_id='ticker', component_property='value'),
        Input(component_id='dropdown_dt', component_property='date')
    ]
)
def update_value(ticker, dropdown_dt):
    start = datetime.datetime(2015, 1, 1)
    end = datetime.datetime(2018, 2, 8)
    df = web.DataReader(ticker, "av-daily", start, end, api_key='V2764H5UZUO1SZ2Y')
    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': df.index, 'y': df.close, 'type': 'line', 'name': ticker},
                {
                    'x': [dropdown_dt, dropdown_dt],
                    'y': [80, 180], 'type': 'line', 'name': u'dropdown'
                    },
            ],
            'layout': {
                'title': ticker
            }
        }
    )





if __name__ == '__main__':
    app.run_server(debug=True)
