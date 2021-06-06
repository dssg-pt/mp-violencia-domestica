import pandas as pd
import geopandas
from simpledbf import Dbf5
import numpy as np
from shapely.geometry import mapping
from geojson import FeatureCollection
import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
import json
from dashboard_components import *

metric_dropdown = dcc.Dropdown(
    id="drop_down1",
    options=[
        {'label': 'Crimes Registados', 'value': 'nr_crimes'},
        {'label': 'Incidência', 'value': 'incidencia'},
        {'label': 'Tendência', 'value': 'tendencia'}
    ],
    placeholder="Selecione uma métrica"
)

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
    return html.Div([html.Div(className="Row", children=[html.Div(metric_dropdown, id="div1"), html.Div({}, id="div2")],
                              style={'width': '30%', "display": "inline-block", 'vertical-align': 'top'},
                              id="parent_div"), html.Div(dcc.Graph(id='portugal_continental', figure=fig),
                                                         style={'width': '70%', "display": "inline-block",
                                                                'vertical-align': 'top'}, id="left_div")])


def get_data_overview():
    data_overview = pd.read_csv("data/data_overview.csv", sep=";")
    return data_overview



def build_gen_view_figs(year, all_country, county1, county2,counties_options):
    dummy_data = pd.read_csv("data/data.csv", sep=",")

    dummy_data = dummy_data[(dummy_data["ano"]>=year[0]) & (dummy_data["ano"]<=year[1])]

    if (not all_country) & (county1 is not None) & (county2 is not None):
        dummy_data_1 = dummy_data[dummy_data["codigo_municipio"] ==int(county1)]
        dummy_data_2 = dummy_data[dummy_data["codigo_municipio"] ==int(county2)]
        county1_label = [x['label'] for x in counties_options if x['value'] == county1][0]
        county2_label = [x['label'] for x in counties_options if x['value'] == county2][0]

        victim_sex_fig= px.bar(x=["Feminino","Masculino"], y=[dummy_data["num_vitima_feminina"].sum(),dummy_data["num_vitima_masculina"].sum()],barmode="group", title="Sexo", color=[county1_label,county2_label])
        victim_age_fig= px.bar(x=["0-3","35","5-10","10-17","17-24","24-34","34-44","44-54","54-64",">65"], y=dummy_data[["num_vitima_idade_3","num_vitima_idade_5","num_vitima_idade_10","num_vitima_idade_17","num_vitima_idade_24","num_vitima_idade_34","num_vitima_idade_44","num_vitima_idade_54","num_vitima_idade_64","num_vitima_idade_mais_65"]].sum())
        victim_mariptual_state_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        victim_relation_woffender_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_sex_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_age_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_mariptual_state_fig=px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_relation_wvictim_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_type_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_duration_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_local_fig = px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
    else:
        victim_sex_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum(), title="Sexo")
        victim_age_fig= px.bar(x=["0-3","35","5-10","10-17","17-24","24-34","34-44","44-54","54-64",">65"], y=dummy_data[["num_vitima_idade_3","num_vitima_idade_5","num_vitima_idade_10","num_vitima_idade_17","num_vitima_idade_24","num_vitima_idade_34","num_vitima_idade_44","num_vitima_idade_54","num_vitima_idade_64","num_vitima_idade_mais_65"]].sum())
        victim_mariptual_state_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        victim_relation_woffender_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_sex_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_age_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_mariptual_state_fig=px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        offender_relation_wvictim_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_type_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_duration_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())
        criminal_fact_local_fig = px.bar(x=["Feminino","Masculino"], y=dummy_data[["num_vitima_feminina","num_vitima_masculina"]].sum())

    return victim_sex_fig,victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig,offender_sex_fig,offender_age_fig,offender_mariptual_state_fig,offender_relation_wvictim_fig,criminal_fact_type_fig,criminal_fact_duration_fig,criminal_fact_local_fig

