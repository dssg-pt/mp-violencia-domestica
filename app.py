import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import geopandas
import numpy as np


from geojson import FeatureCollection
from shapely.geometry import mapping
from dash.dependencies import Input, Output, State
from simpledbf import Dbf5


external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "22rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "23rem",
    "margin-right": "2rem",
    "padding": "5rem 1rem",
}

sidebar = html.Div(
    [
        html.H6("Observatório Violência Doméstica", className="display-4", style={"fontSize": 20, "fontWeight": "bold"}),
        html.Div(html.Img(src=app.get_asset_url('dssg_logo_lettering.png'), style={'height': '20%', 'width': '50%'}), style={"textAlign":"center"}),
        html.Hr(),
        html.P(
            "O que nos dizem os dados?", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Vista Geral", href="/page-1", active="exact"),
                dbc.NavLink("Dados Demográficos", href="/cartographic_view", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


def get_data():

    df_registos = pd.read_csv("data/data.csv", sep=";")
    df = geopandas.read_file("data/concelhos.shp")

    df_registos = df_registos[df_registos["ano"] == 2017]
    df_registos["incidencia"] = (df_registos["nr_crimes"] / df_registos["populacao_residente"]) * 100000

    dbf = Dbf5("data/concelhos.dbf")
    df_meta = dbf.to_dataframe()
    df_meta["CCA_2"] = df_meta["CCA_2"].astype(np.float64)

    municipalities = len(df)

    features = [{"type": "Feature", "geometry": (mapping(df.iloc[i]["geometry"].simplify(tolerance=0.01))),
                 "id": df_registos[df_registos["codigo_municipio"] == df_meta.iloc[i]["CCA_2"]]["municipio"]}
                for i in range(municipalities)]

    df_data = df_registos.drop(["ano"], axis=1)
    geojson = FeatureCollection(features)

    return df_data, geojson


df_data, geojson = get_data()

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output", data={"value": "nr_crimes"}), sidebar, content])

dropdown = dcc.Dropdown(
    id="drop_down1",
    options=[
        {'label': 'Crimes Registados', 'value': 'nr_crimes'},
        {'label': 'Incidência', 'value': 'incidencia'},
        {'label': 'Tendência', 'value': 'tendencia'}
    ],
    placeholder="Selecione uma métrica",
)


def build_fig(metric):

    fig = px.choropleth(
        df_data,
        geojson=geojson,
        locations='municipio',
        color=df_data[metric],
        range_color=(0, df_data[metric].max()),
    )

    fig.update_geos(lonaxis_range=[349, 355], lataxis_range=[36, 44])
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_traces(colorbar_xpad=2, colorbar_x=-1.5, selector=dict(type='choropleth'))
    return fig


def update_content(fig):
    return html.Div([html.Div([html.Div(dropdown, id="div1"), html.Div({}, id="div2")],
                                  style={'width': '20%', "display": "inline-block", 'vertical-align': 'top'},
                                  id="parent_div"), html.Div(dcc.Graph(id='portugal_continental', figure=fig),
                         style={'width': '80%', "display": "inline-block", 'vertical-align': 'top'}, id="left_div")])


@app.callback(Output("page-content", "children"), Input("url", "pathname"), Input("memory_output", "data"))
def render_page_content(pathname, data):
    if pathname == "/":
        return ""
    elif pathname == "/page-1":
        return html.P("")
    elif pathname == "/cartographic_view":
        fig = build_fig(metric="incidencia")
        return update_content(fig)


@app.callback(Output("memory_output", "data"), [Input("dropdown1", "value")])
def on_dropdown_select(value):
    return {"value": value}


if __name__ == '__main__':
    app.run_server(debug=True)

