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

def get_choropleth_globalview(df, geojson, highlights=[]):

    if not highlights:
        opacity=1
    else:
        opacity=0.3
    
    choropleth_globalview = px.choropleth_mapbox(
        data_frame=df, 
        geojson=geojson,
        locations="municipio",
        color="incidencia",
        center={"lat": 39.6753, "lon": -8.14679}, 
        range_color=(0, df["incidencia"].max()),
        opacity=opacity,
        mapbox_style="carto-positron",
        zoom=5.5,
        )
    if highlights:
        choropleth_globalview.add_trace(

            px.choropleth_mapbox(

                data_frame=df[df["codigo_municipio"].isin(highlights)], 
                geojson=geojson,
                locations="municipio",
                color="incidencia",
                center={"lat": 39.6753, "lon": -8.14679}, 
                range_color=(0, df["incidencia"].max()),
                opacity=1,
                mapbox_style="carto-positron",
                zoom=5.5,
        ).data[0]

        )

    choropleth_globalview.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    #choropleth_globalview.update_traces(colorbar_xpad=2, colorbar_x=-1.5, selector=dict(type='choropleth'))
    

    return choropleth_globalview

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
    dummy_data = pd.read_csv("data/data_drilldown_cd.csv", sep=",")

    dummy_data = dummy_data[(dummy_data["ano"]>=year[0]) & (dummy_data["ano"]<=year[1])]

    if (not all_country) & (county1 is not None) & (county2 is not None):
        dummy_data_1 = dummy_data[dummy_data["codigo_municipio"] ==int(county1)]
        dummy_data_2 = dummy_data[dummy_data["codigo_municipio"] ==int(county2)]
        county1_label = [x['label'] for x in counties_options if x['value'] == county1][0]
        county2_label = [x['label'] for x in counties_options if x['value'] == county2][0]

        victim_sex_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=["Feminino","Masculino"], y=[dummy_data_1["vitimas_feminino"].sum(),dummy_data_1["vitimas_masculino"].sum()]),
                    go.Bar(name=county2_label, x=["Feminino","Masculino"], y=[dummy_data_2["vitimas_feminino"].sum(),dummy_data_2["vitimas_masculino"].sum()]),
                ])

        victim_age_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=["0-10","11-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data_1[['vitima_0_10','vitima_11_17','vitima_18_25','vitima_26_35','vitima_36_45','vitima_46_55','vitima_56_64','vitima_65+']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=["0-10","11-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data_2[['vitima_0_10','vitima_11_17','vitima_18_25','vitima_26_35','vitima_36_45','vitima_46_55','vitima_56_64','vitima_65+']].sum(), labels=dict(x="", y="")),
                   ])     

        victim_mariptual_state_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data_1[['vitima_casado','vitima_divorciado','vitima_separado','vitima_solteiro','vitima_uniao_de_facto','vitima_viuvo']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data_2[['vitima_casado','vitima_divorciado','vitima_separado','vitima_solteiro','vitima_uniao_de_facto','vitima_viuvo']].sum(), labels=dict(x="", y="")),
                   ])    
        victim_relation_woffender_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data_1[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data_2[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y="")),
                   ])  
        offender_sex_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=["Feminino","Masculino"], y=[dummy_data_1["autor_crime_feminino"].sum(),dummy_data_1["autor_crime_masculino"].sum()]),
                    go.Bar(name=county2_label, x=["Feminino","Masculino"], y=[dummy_data_2["autor_crime_feminino"].sum(),dummy_data_2["autor_crime_masculino"].sum()]),
                ])

        offender_age_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=["0-10","11-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data_1[['autor_crime_0_17','autor_crime_18_25','autor_crime_26_35','autor_crime_36_45','autor_crime_46_55','autor_crime_56_64','autor_crime_65+']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=["0-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data_2[['autor_crime_0_17','autor_crime_18_25','autor_crime_26_35','autor_crime_36_45','autor_crime_46_55','autor_crime_56_64','autor_crime_65+']].sum(), labels=dict(x="", y="")),
                   ])     

        offender_mariptual_state_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data_1[['autor_crime_casado','autor_crime_divorciado','autor_crime_separado','autor_crime_solteiro','autor_crime_uniao_de_facto','autor_crime_viuvo']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data_2[['autor_crime_casado','autor_crime_divorciado','autor_crime_separado','autor_crime_solteiro','autor_crime_uniao_de_facto','autor_crime_viuvo']].sum(), labels=dict(x="", y="")),
                   ])    
        offender_relation_wvictim_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data_1[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data_2[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y="")),
                   ])                                                                       
        criminal_fact_duration_fig = go.Figure(data=[
                    go.Bar(name=county1_label, x=["1-6 Meses","7-12 Meses","2-6 Anos", "7-11 Anos", "12-25 Anos", "26-40 Anos", "40+ Anos"], y=dummy_data_1[['duracao_vitimacao_1_6_m','duracao_vitimacao_7_12_m','duracao_vitimacao_2_6_a','duracao_vitimacao_7_11_a','duracao_vitimacao_12_25_a','26_40_anos','40_mais_anos']].sum(), labels=dict(x="", y="")),
                    go.Bar(name=county2_label, x=["1-6 Meses","7-12 Meses","2-6 Anos", "7-11 Anos", "12-25 Anos", "26-40 Anos", "40+ Anos"], y=dummy_data_2[['duracao_vitimacao_1_6_m','duracao_vitimacao_7_12_m','duracao_vitimacao_2_6_a','duracao_vitimacao_7_11_a','duracao_vitimacao_12_25_a','26_40_anos','40_mais_anos']].sum(), labels=dict(x="", y="")),
                   ])            
        
        df, geojson = get_data()
        choropleth_globalview=get_choropleth_globalview(df, geojson, highlights=[int(county1), int(county2)])
    else:

        victim_sex_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["vitimas_feminino","vitimas_masculino"]].sum(), title="Sexo", labels=dict(x="", y=""))
        victim_age_fig= px.bar(x=["0-10","11-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data[['vitima_0_10','vitima_11_17','vitima_18_25','vitima_26_35','vitima_36_45','vitima_46_55','vitima_56_64','vitima_65+']].sum(), labels=dict(x="", y=""))
        victim_mariptual_state_fig= px.bar(x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data[['vitima_casado','vitima_divorciado','vitima_separado','vitima_solteiro','vitima_uniao_de_facto','vitima_viuvo']].sum(), labels=dict(x="", y=""))
        victim_relation_woffender_fig= px.bar(x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y=""))
        offender_sex_fig= px.bar(x=["Feminino","Masculino"], y=dummy_data[["autor_crime_feminino","autor_crime_masculino"]].sum(), labels=dict(x="", y=""))
        offender_age_fig= px.bar(x=["0-17","18-25","25-35","36-45","46-55","55-65","65+"], y=dummy_data[['autor_crime_0_17','autor_crime_18_25','autor_crime_26_35','autor_crime_36_45','autor_crime_46_55','autor_crime_56_64','autor_crime_65+']].sum(), labels=dict(x="", y=""))
        offender_mariptual_state_fig=px.bar(x=['Casado','Divorciado','Separado','Solteiro','União de Facto','Viúvo'], y=dummy_data[['autor_crime_casado','autor_crime_divorciado','autor_crime_separado','autor_crime_solteiro','autor_crime_uniao_de_facto','autor_crime_viuvo']].sum(), labels=dict(x="", y=""))
        offender_relation_wvictim_fig= px.bar(x=['Conjuge','Companheiro','Filho','Ex Companheiro','Progenitor','Outro'], y=dummy_data[['rel_agr_conjuge','rel_agr_companheiro','rel_agr_filho','rel_agr_ex_companheiro','rel_agr_progenitor','rel_agr_outro']].sum(), labels=dict(x="", y=""))
        criminal_fact_duration_fig= px.bar(x=["1-6 Meses","7-12 Meses","2-6 Anos", "7-11 Anos", "12-25 Anos", "26-40 Anos", "40+ Anos"], y=dummy_data[['duracao_vitimacao_1_6_m','duracao_vitimacao_7_12_m','duracao_vitimacao_2_6_a','duracao_vitimacao_7_11_a','duracao_vitimacao_12_25_a','26_40_anos','40_mais_anos']].sum(), labels=dict(x="", y=""))


        df, geojson = get_data()
        choropleth_globalview=get_choropleth_globalview(df, geojson)


    victim_sex_fig.update_layout(
            title={
            'text': "Sexo",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    victim_age_fig.update_layout(
            title={
            'text': "Idade",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    victim_mariptual_state_fig.update_layout(
            title={
            'text': "Estado Civil",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    victim_relation_woffender_fig.update_layout(
            title={
            'text': "Relação com Agressor(a)",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    offender_sex_fig.update_layout(
            title={
            'text': "Sexo",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    offender_age_fig.update_layout(
            title={
            'text': "Idade",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    offender_mariptual_state_fig.update_layout(
            title={
            'text': "Estado Civil",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    offender_relation_wvictim_fig.update_layout(
            title={
            'text': "Relaçao com a Vítima",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    criminal_fact_duration_fig.update_layout(
            title={
            'text': "Duração",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return victim_sex_fig,victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig,offender_sex_fig,offender_age_fig,offender_mariptual_state_fig,offender_relation_wvictim_fig,criminal_fact_duration_fig, choropleth_globalview

