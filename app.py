import os

import pandas_datareader.data as web
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import sys
print(f"sys.path: {sys.path}")

import os
try:
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
except:
    print('no PYTHONPATH found')

from os import listdir
print(f"listdir('.'): {listdir('.')}")
print()
print(f"listdir('/app': {listdir('/app'}")


from gameplan.growth.income_percentile_estimate import get_working_population_data

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

working_pop = get_working_population_data()
DMAS = [
    'New York-Northern New Jersey-Long Island, NY-NJ-PA',
    'Los Angeles-Long Beach-Anaheim, CA',
    'Washington, DC/MD/VA',
    'Chicago-Naperville-Joliet, IL-IN-WI',
    'Boston-Cambridge-Newton, MA-NH',
    'Dallas-Fort Worth-Arlington, TX',
    'Philadelphia-Camden-Wilmington, PA/NJ/DE',
]

app.layout = html.Div(children=[
    html.Div(children='''
        Metro Area (DMA):
    '''),
    dcc.Dropdown(
        id='dma',
        options=[{'label': dma, 'value': dma} for dma in DMAS],
        value='New York-Northern New Jersey-Long Island, NY-NJ-PA'
    ),
    html.Div(dcc.Input(id='input-box', type='number')),
    # html.Button('Submit', id='button'),
    dcc.Graph(id='output-graph'),
])

def get_fig():
    METRO_AREA = 'New York'
    YEARLY_SALARY = 180000
    SEX = 'Male'


    subset = cohort_data.query("AGE.between(27, 31) & metarea.str.contains(@METRO_AREA)")
    subset['weight'] = subset.ASECWT / subset.ASECWT.sum()
    dist = subset.sort_values('inctot').loc[:, ['inctot', 'weight']]
    dist['cdf'] = dist.weight.cumsum()

    fig = px.line(dist, x='inctot', y='cdf', range_x=(0, 250000), range_y=(0,1))
    percentile = sp.percentileofscore(dist.inctot, YEARLY_SALARY)

    fig.add_scatter(
        x=[YEARLY_SALARY, YEARLY_SALARY],
        y=[0, 1],

        mode='lines',
        line=dict(color='black', width=2, dash='dot'),
        showlegend=False
    )
    fig.add_annotation(text=f'${YEARLY_SALARY:,} = {percentile:.0f}th Percentile', x=YEARLY_SALARY, y=percentile/100, showarrow=True, align='left')


@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [
        Input(component_id='dma', component_property='value'),
        Input('input-box', 'value')
    ],
        # Input(component_id='salary', component_property='date')
)
def update_figure(dma, salary):
    df = working_pop.query("metarea == @dma")
    return {
            'data': [
                {
                    'x': [salary, salary],
                    'y': [0, 1],
                    'type': 'line',
                    'name': dma
                },
                {
                    'x': df.inctot,
                    # 'y': [80, 180],
                    'type': 'histogram',
                    # 'histnorm': 'probability'
                    # 'name': u'dropdown'
                    },
            ],
            'layout': {
                'title': dma,

            }
        }

if __name__ == '__main__':
    app.run_server(debug=True)
