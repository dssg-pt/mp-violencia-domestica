# dependencies
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import geopandas
import numpy as np
import dash_daq as daq

from geojson import FeatureCollection
from shapely.geometry import mapping
from dash.dependencies import Input, Output, State
from simpledbf import Dbf5

from dash.exceptions import PreventUpdate
from dashboard_components import *
from functions import get_choropleth_globalview, get_data, build_fig, update_content, get_data_overview, build_gen_view_figs
from support import CONCELHOS 
##

sortedCONCELHOS = dict(sorted(CONCELHOS.items(), key=lambda x: x[1].lower()))

counties_options = [
    {"label": str(sortedCONCELHOS[county]), "value": str(county)} for county in sortedCONCELHOS
]

dummy_data = pd.read_csv("data/data.csv", sep=",")

df = px.data.tips()
fig = px.pie(df, values='tip', names='day', color_discrete_sequence=px.colors.sequential.RdBu)

##
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

sidebar = html.Div([
    
    dbc.Collapse( # Components inside collapse will be hidden
    [
        html.H6("Observatório Violência Doméstica", className="display-4", style={"fontSize": 20, "fontWeight": "bold"}),
        html.Div(html.Img(src=app.get_asset_url('dssg_logo_lettering.png'), style={'height': '20%', 'width': '50%'}), style={"textAlign":"center"}),
        html.Hr(),
        html.P(
            "O que nos dizem os dados?", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Sobre", href="/", active="exact"),
                dbc.NavLink("Destaques", href="/page-1", active="exact"),
                dbc.NavLink("Visão Global", href="/globalview", active="exact"),
                dbc.NavLink("Dados Demográficos", href="/cartographic_view", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        
    ],
    className="sidebar"
    , id="collapse"),
    
    dbc.Button([html.Img(
        id="sidebar_icon",
        src=app.get_asset_url('sidebar_icon.png'),

    ), html.Div(className="display-4")], outline=False, 
    id="btn_sidebar",  
    )])

df_data, geojson = get_data()

content = html.Div(id="page-content", className="content")
tabs = dbc.Tabs([ dbc.Tab(label="Scatter", tab_id="scatter"), dbc.Tab(label="Histograms", tab_id="histogram"),], id="tabs", active_tab="scatter"), html.Div(id="tab-content", className="p-4")

app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output", data={"value": "nr_crimes"}), sidebar,
                       content, ])

@app.callback(
    Output("collapse", "is_open"),
    Output('sidebar_icon', 'style'),
    Output('btn_sidebar', 'style'),
    Output('page-content', 'style'),
    [Input("btn_sidebar", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    
    if n:

        if not is_open:

            width="22rem"
            sidebar_style = {'height': '85%', 'width': '8.25%'}
            content_style = {"margin-left":"17rem"}

        else:

            width="3.5rem"
            sidebar_style = {'height': '85%', 'width': '85%'}
            content_style = {"margin-left":"0rem"}

        style={"position": "fixed", "top": 0, "left":0, "text-align": "left", 
        "width": width, "height": "2.5rem", "box-shadow":"none", "background-color": "#807d75", "border": "none"}
        
        return not is_open, sidebar_style, style, content_style

    sidebar_style = {'height': '85%', 'width': '85%'}

    style={"position": "fixed", "top": 0, "left":0, "text-align": "left", 
    "width": "3.5rem", "height": "2.5rem", "box-shadow":"none", "background-color": "#807d75", "border": "none"}
    content_style = {"margin-left":"0rem"}
    return is_open, sidebar_style, style, content_style


@app.callback(Output("page-content", "children"), Input("url", "pathname"), Input("memory_output", "data"))
def render_page_content(pathname, data):
    if pathname == "/":
        return ""
    elif pathname == "/page-1":
        gen_view = get_general_view()
        return gen_view
    elif pathname == "/globalview":
        gen_view = get_global_view()
        return gen_view
    
def get_general_view():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                "APAV: Relatório Anual", style={"font-weight": "bold"}
                            ),
                            html.H2(
                                "2017", style={"margin-top": "0px", "font-weight": "bold"}
                            ),
                        ]
                    )
                ],
                className="one-half column",
                id="title",
            ),
            html.Div(
                [
                      html.H3(children=[
                              html.Img(src=app.get_asset_url('profile.png'),
                                       style={
                                           'height': '5%', 'width': '5%', 'display': 'inline-block'
                                              }), "    PERFIS TÍPICOS"],
                              style={
                                  "margin-top": "0px", "font-weight": "bold"
                              })
                ]),
            html.Div(
                [
                    html.Div([
                        html.P(html.H5("VÍTIMA", style={"font-weight": "bold"}), className="mini_container_label"),
                        html.P(html.Ul([
                            html.Li("Mulher"),
                            html.Li("36 a 45 anos"),
                            html.Li("Casada"),
                            html.Li("Família Nuclear com Filhos")]
                        ))
                    ], id='victim_profile', className="profile_container"

                    ),

                    html.Div([
                        html.P(html.H5("AUTOR DO CRIME", style={"font-weight": "bold"}), className="mini_container_label"),
                        html.P(html.Ul([
                            html.Li("Homem"),
                            html.Li("36 a 45 anos"),
                            html.Li("Casado"),
                            html.Li("Família Nuclear com Filhos")]
                        ))
                    ], id='aggressor_profile', className="profile_container"

                    ),

                    html.Div([
                        html.P(html.H5("CRIME", style={"font-weight": "bold"}), className="mini_container_label"),
                        html.P(html.Ul([
                            html.Li("Vitimação Continuada"),
                            html.Li("2 a 6 anos Duração"),
                            html.Li("Residência Comum")]
                        ))
                    ], id='crime_profile', className="profile_container"

                    )



                ],
                id="info-container",
                className="row container-display",
            ),

            html.Div(
                [

                    ]),
            html.H3(children=[
                html.Img(src=app.get_asset_url('alert.png'),
                         style={
                             'height': '5%', 'width': '5%', 'display': 'inline-block'
                         }), "    DESTAQUES"], style={"margin-top": "10px", "font-weight": "bold",
                                                                    'position': 'relative'}),
            html.Div(
                [

                    html.Div(
                        [html.H4("6.528*", className="mini_container_text"),
                         html.P("PROCESSOS DE APOIO", className="mini_container_label")],
                        id="support",
                        className="mini_container",
                        style={"background-color": "#ccffcc"}

                    ),
                    html.Div(
                        [html.H4(6887, className="mini_container_text"),
                         html.P("VÍTIMAS", className="mini_container_label")],
                        id="victims",
                        className="mini_container",
                        style={"background-color": "#ccffcc"}
                    ),
                    html.Div(
                        [html.H4(69, className="mini_container_text"),
                         html.P("SERVIÇOS DE PROXIMIDADE", className="mini_container_label")],
                        id="victims",
                        className="mini_container",
                        style={"background-color": "#ccffcc"}
                    )
                ],
                id="info-container",
                className="row container-display",
            ),
            html.H3(children=[
                html.Img(src=app.get_asset_url('cardinal.png'),
                         style={
                             'height': '5%', 'width': '5%', 'display': 'inline-block'
                         }), "    NÚMERO MÉDIO DE VÍTIMAS"], style={ "margin-top": "10px", "font-weight": "bold",
                                                                     'position': 'relative'}),

            html.Div(
                [

                    html.Div(
                        [html.H4("MULHERES", className="mini_container_label"),
                         html.P([html.B(8720), " ANO"]), html.P([html.B(167), " Semana"]),
                         html.P([html.B(24), " Dia"])],
                        id="woman_number",
                        className="mini_container",
                        style={"background-color": "#ff000033",
                               "background-image": "url(assets/women.png)",
                               "background-repeat": "no-repeat",
                               "background-size": "30%",
                               "background-position-y": "bottom",
                               "background-position-x": "right",
                               }
                    ),
                    html.Div(
                        [html.H4("CRIANÇAS", className="mini_container_label"),
                         html.P([html.B(1841), " ANO"]), html.P([html.B(35), " Semana"]),
                         html.P([html.B(5), " Dia"])],
                        id="children_number",
                        className="mini_container",
                        style={"background-color": "#ff000033",
                               "background-image": "url(assets/children_1.png)",
                               "background-repeat": "no-repeat",
                               "background-size": "30%",
                               "background-position-y": "bottom",
                               "background-position-x": "right",
                               }
                    ),
                    html.Div(
                        [html.H4("HOMENS", className="mini_container_label"),
                         html.P([html.B(1627), " ANO"]), html.P([html.B(31), " Semana"]),
                         html.P([html.B(4), " Dia"])],
                        id="men_numbers",
                        className="mini_container",
                        style={"background-color": "#ff000033",
                               "background-image": "url(assets/men.png)",
                               "background-repeat": "no-repeat",
                               "background-size": "30%",
                               "background-position-y": "bottom",
                               "background-position-x": "right",
                               }
                    ),
                    html.Div(
                        [html.H4("IDOSOS", className="mini_container_label"),
                         html.P([html.B(1626), " ANO"]), html.P([html.B(31), " Semana"]),
                         html.P([html.B(4), " Dia"])],
                        id="formativeactivies",
                        className="mini_container",
                        style={"background-color": "#ff000033",
                               "background-image": "url(assets/senior.png)",
                               "background-repeat": "no-repeat",
                               "background-size": "30%",
                               "background-position-y": "bottom",
                               "background-position-x": "right",
                               }
                    ),
                ],
                id="info-container_2",
                className="row container-display",
            ),
            html.H3(children=[
                html.Img(src=app.get_asset_url('simple-search.png'),
                         style={
                             'height': '5%', 'width': '5%', 'display': 'inline-block'
                         }), "    EM DETALHE"], style={"margin-top": "10px", "font-weight": "bold",
                                                                    'position': 'relative'}),
            html.Div(
                [
                    html.Div([

                        html.Div(
                            [dcc.Graph(id="relationship_chart", figure=relationship_chart)],
                            style={"width": "50%", "position": "relative", "float": "left",
                                   }

                        ),

                        html.Div(
                            [dcc.Graph(id="crime_loc_chart", figure=crime_location_graph)],
                            style={"width": "50%", "float": "left", "position": "relative"}
                        )

                    ],
                        className="pretty_container pie_chart",
                        id="donut_chart_container"),

                    html.Div([

                        html.Div(
                            [dcc.Graph(id="victim_sex_chart", figure=victim_sex_chart)],
                            style={"width": "50%", "position": "relative", "float": "left",
                    }

                        ),

                        html.Div(
                            [dcc.Graph(id="offender_sex_chart", figure=offender_sex_chart)],
                            style={"width": "50%", "float": "left", "position": "relative"}
                        )

                    ],
                        className="pretty_container", style={"left": "7.5%", "width": "74.5%"},
                        id="parent_sex_container"),

                    html.Div(
                        [dcc.Graph(id="age_by_sex_graph", figure=age_by_sex_graph)],
                        className="pretty_container three columns", style={"left": "9.75%"}
                    ),

                    html.Div(
                        [dcc.Graph(id="conctact_type_graph", figure=contact_type_graph)],
                        className="pretty_container three columns", style={"left": "9.75%"}
                    )
                ], className="row")
        ],
        id="right-column",
        className="eight columns",
        style={'position': "relative", "left": "50px", "horizontal-alignment": "center"}
    )


def get_global_view():

    return html.Div(
        [
            html.Div([
                html.H3("Quando?", style = {"width":"100%"}, className="when_header"),
                html.Div([dcc.RangeSlider(
                    id="year_slider",
                    min=2013,
                    max=2018,
                    value=[2013, 2018],
                    marks={
                        2013: '2013',
                        2014: '2014',
                        2015: '2015',
                        2016: '2016',
                        2017: '2017',
                        2018: '2018'
                    }
                )], style ={"width": "100%"}),
                html.Br(),
                html.Div([
                        html.H3("Quem?", style = {"width": "96%"}, className="who_header"),
                        html.H4('A Vítima', style={'width': '100%', "margin-top": "0px", "font-weight": "bold","text-align": "center"}),
                        html.Div([
                            html.Div([
                                html.H5('Sexo'),
                                dcc.Graph(id='victim_sex',)
                            ], className="col-md-6"),
                            html.Div([
                                html.H5('Faixa Etária'),
                                dcc.Graph(id='victim_age',)
                            ], className="col-md-6"),
                            html.Div([
                                html.H5('Estado Civil'),
                                dcc.Graph(id='victim_mariptual_state', )
                            ], className="col-md-6"),
                            html.Div([
                                html.H5('Relação com o Autor'),
                                dcc.Graph(id='victim_relation_woffender', )
                            ], className="col-md-6")
                        ], className="row", style={'width': '100%'}),

                        html.H4('O Autor', style={'width': '100%', "margin-top": "0px", "font-weight": "bold","text-align": "center"}),
                        html.Div([
                            html.Div([
                                html.H5('Sexo'),
                                dcc.Graph(id='offender_sex', )
                            ], className="col-md-6"),
                            html.Div([
                                html.H3('Faixa Etária'),
                                dcc.Graph(id='offender_age', )
                            ], className="col-md-6"),
                            html.Div([
                                html.H3('Estado Civil'),
                                dcc.Graph(id='offender_mariptual_state', )
                            ], className="col-md-6"),
                            html.Div([
                                html.H3('Relação com a Vítima'),
                                dcc.Graph(id='offender_relation_wvictim', )
                            ], className="col-md-6")
                        ], className="row", style={'width': '100%'}),
                    ], className="row",  style={'width': '60%'}),
                html.Div([
                    html.H3("Onde?", style = {"width":"100%"}, className="where_header"),
                    html.Label([ 
                        "País todo?",
                        daq.BooleanSwitch(
                            id='my-toggle-switch',
                            on=True,
                            color= '#ccffcc',
                            style = {"margin-left":"5px"}
                        )], style={"width":"100%", "display":"flex"}),
                     html.Label([
                        "Concelho 1",
                        dcc.Dropdown(
                            options= counties_options,
                            multi=False,
                            placeholder="Escolha o concelho",
                            id = 'county1_dpdn'
                        )
                    ], style={"width":"45%", "margin-right":"5px"}),
                    html.Label([
                        "Concelho 2",
                        dcc.Dropdown(
                            options= counties_options,
                            multi=False,
                            placeholder="Escolha o concelho",
                            id = 'county2_dpdn'
                        )
                    ], style={"width":"50%", }),

                    dcc.Graph(id="choro_global", )

                 ], style={'width': '40%'}),

                html.Div(
                    [
                        html.H3(
                            "Facto Criminoso", style={"margin-top": "0px", "font-weight": "bold", "width":"100%"}
                        ),
                        html.Div([
                            html.H5('Duração'),
                            dcc.Graph(id='criminal_fact_duration', )
                        ], className="col-md-4")
                    ], className="row",  style={'width': '100%'}),
            ], className="pretty_container row"),
        ],
        id="right_column",
        className="eight columns",
    )



## app callbacks for genera view 
@app.callback(
    [Output('county1_dpdn', 'disabled'), Output('county2_dpdn', 'disabled'),Output('county1_dpdn', 'value'), Output('county2_dpdn', 'value'), 
        Output('county1_dpdn', 'options'), Output('county2_dpdn', 'options')],
    [dash.dependencies.Input('my-toggle-switch', 'on'),dash.dependencies.Input('county1_dpdn', 'value'),dash.dependencies.Input('county2_dpdn', 'value')])
def update_county_filters(value, county1, county2):
    if county1 == None:
        counties_options_2 = counties_options
    else:
        counties_options_2 = list(filter(lambda d: d['value'] not in [county1], counties_options))        
    if county2 == None:
        counties_options_1 = counties_options
    else:
        counties_options_1 = list(filter(lambda d: d['value'] not in [county2], counties_options))
    if value:
        county1 = None
        county2 = None

    return value, value, county1, county2, counties_options_1, counties_options_2;

@app.callback([Output('victim_sex', 'figure'),Output('victim_age', 'figure'),Output('victim_mariptual_state', 'figure'),Output('victim_relation_woffender', 'figure'),Output('offender_sex', 'figure'),Output('offender_age', 'figure'),
    Output('offender_mariptual_state', 'figure'),Output('offender_relation_wvictim', 'figure'),Output('criminal_fact_duration', 'figure'),Output('choro_global', 'figure')],
    [dash.dependencies.Input('my-toggle-switch', 'on'), dash.dependencies.Input('year_slider', 'value'), dash.dependencies.Input('county1_dpdn', 'value'),dash.dependencies.Input('county2_dpdn', 'value')]
)

def update_da(all_country,year, county1, county2):
  ###  this method return all figs to present on the view 
    transformed_value = [v for v in year]
    victim_sex_fig, victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig, offender_sex_fig, offender_age_fig, offender_mariptual_state_fig, offender_relation_wvictim_fig, criminal_fact_duration_fig, choropleth_global_view = build_gen_view_figs(transformed_value, all_country, county1, county2, counties_options)
    return victim_sex_fig, victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig, offender_sex_fig, offender_age_fig, offender_mariptual_state_fig, offender_relation_wvictim_fig, criminal_fact_duration_fig, choropleth_global_view



if __name__ == '__main__':
    app.run_server(debug=True)


