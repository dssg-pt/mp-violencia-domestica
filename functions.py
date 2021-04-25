import pandas as pd
import geopandas
from simpledbf import Dbf5
import numpy as np
from shapely.geometry import mapping
from geojson import FeatureCollection
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc

from dashboard_components import metric_dropdown
# function doc
def get_data():

    df_registos = pd.read_csv("data/data_old.csv", sep=";")
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

# function doc
def build_fig(metric, df_data, geojson):

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

# function doc
def update_content(fig):
    return html.Div([html.Div([html.Div(metric_dropdown, id="div1"), html.Div({}, id="div2")],
                                  style={'width': '20%', "display": "inline-block", 'vertical-align': 'top'},
                                  id="parent_div"), html.Div(dcc.Graph(id='portugal_continental', figure=fig),
                         style={'width': '80%', "display": "inline-block", 'vertical-align': 'top'}, id="left_div")])


