import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as sp

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
    html.Div(dcc.Input(id='input-box', type='number', value=0)),
    # html.Button('Submit', id='button'),
    dcc.Graph(id='output-graph'),
])

def get_fig(df, salary, dma, age_range=None, gender=None):
    query = "metarea.str.contains(@dma) "
    subset = df.query(query)
    subset['weight'] = subset.ASECWT / subset.ASECWT.sum()
    dist = subset.sort_values('inctot').loc[:, ['inctot', 'weight']]
    dist['cdf'] = dist.weight.cumsum()
    fig = px.line(
        dist,
        x='inctot',
        y='cdf',
        range_x=(0, 250000),
        range_y=(0,1)
        )
    percentile = sp.percentileofscore(dist.inctot, int(salary))
    fig.add_scatter(
        x=[salary, salary],
        y=[0, 1],
        mode='lines',
        line=dict(color='black', width=2, dash='dot'),
        showlegend=False
    )
    fig.add_annotation(
        text=f'${salary:,} = {percentile:.0f}th Percentile',
        x=salary,
        y=percentile/100,
        showarrow=True,
        align='left'
        )
    layout = go.Layout(
        title=f"Total Income Distribution in {dma}",
        yaxis={
            "title": "% of Full-Time Workers Earning Up To $X Per Year",
            "range": [0, 1],
            },
        xaxis={"title": "Total Annual Income"},
        )
    fig.update_layout(layout)

    return fig


@app.callback(
    Output(component_id='output-graph', component_property='figure'),
    [
        Input(component_id='dma', component_property='value'),
        Input('input-box', 'value')
    ],
        # Input(component_id='salary', component_property='date')
)
def update_figure(dma, salary):
    fig = get_fig(df=working_pop, dma=dma, salary=salary)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
