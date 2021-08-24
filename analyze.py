'''
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("house.csv", index_col=0)
df['date'] =  pd.to_datetime(df['date'], format='%Y-%m-%d')
print(df)

#fig = px.scatter(df, x="area")
#fig = go.Figure()

fig = px.scatter(df, x="date", y="avg_price",
                 size="total_price", color="area",
                 color_continuous_scale=px.colors.sequential.Turbo,
                 size_max=50, hover_name="house")

#fig.show()
fig.write_html("house.html", include_plotlyjs="True")
'''



import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("house.csv", index_col=0)
df['date'] =  pd.to_datetime(df['date'], format='%Y-%m-%d')
print(df)

regions = df['house'].unique().tolist()
regions.append("All")

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        [
            html.Div(
                [
                    html.H2("Select your region", style={'margin-right': '1em', 'display': 'inline'})
                ],
            ),

            html.Div([
            dcc.Dropdown(
                id='region_dropdown',
                options=[{"value":x, "label":x} for x in regions],
                placeholder="Select Region Area",
            )],
                style=dict(
                    width='20%',
                    display='inline',
                    verticalAlign="middle"
                )
            ),
        ],
        style=dict(display='flex')
    ),
    #style={"width": "50%"},
    html.Div([
        dcc.Graph(id="graph",
                  figure={
                    "layout": {
                        "title": "My Dash Graph",
                        "height": 760,  # px
                    },
                  },)
    ])
])

@app.callback(
    Output("graph", "figure"),
    [Input("region_dropdown", "value")])
def change_colorscale(region):
    if region != "All":
        new = df[df['house'] == region]
    else:
        new = df

    fig = px.scatter(
        new, x="date", y="avg_price", size="total_price",
        color="area", color_continuous_scale=px.colors.sequential.Turbo,
        size_max=50, hover_name="house")
    return fig

app.run_server(debug=False)
