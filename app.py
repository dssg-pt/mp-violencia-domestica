# dependencies
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import geopandas
import numpy as np
import json

from geojson import FeatureCollection
from shapely.geometry import mapping
from dash.dependencies import Input, Output, State
from simpledbf import Dbf5

from dash.exceptions import PreventUpdate
from dashboard_components import *
from functions import get_data, build_fig, update_content, get_data_overview
##

df = px.data.tips()
fig = px.pie(df, values='tip', names='day', color_discrete_sequence=px.colors.sequential.RdBu)

##
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

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
                dbc.NavLink("Destaques", href="/page-1", active="exact"),
                dbc.NavLink("Visão Global", href="/overview", active="exact"),
                dbc.NavLink("Dados Demográficos", href="/cartographic_view", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar"
)

df_data, geojson = get_data()


content = html.Div(id="page-content", className="content")
app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output"), sidebar, content])


@app.callback(Output("page-content", "children"), Input("url", "pathname"), Input("memory_output", "data"))
def render_page_content(pathname, data):
    if pathname == "/":
        return ""
    elif pathname == "/page-1":
        gen_view = get_general_view()
        return gen_view
    elif pathname == "/overview":
        return get_overview(data)
    elif pathname == "/cartographic_view":
        fig = build_fig(metric="incidencia", df_data=df_data, geojson=geojson)
        return update_content(fig)


@app.callback(Output("memory_output", "data"), [Input("lineplot_dropdown", "value")])
def on_dropdown_select(value):
    print(value)
    if not value or value is None:
        return json.dumps(["vitimas_feminino"])  # default = vitimas_feminino
    return json.dumps(value)


def get_overview(var_toplot):

    if var_toplot is None:
        var_toplot = ["vitimas_feminino"]
    else:
        var_toplot = json.loads(var_toplot)

    df = get_data_overview()
    fig = px.line(df, x="ano", y=var_toplot,
                  title="Vítimas de Violência Doméstica entre 2000 e 2020")
    # ,labels={"value": "Número de Vítimas", "variable": "Sexo"})

    mapping_dict = {"vitimas_feminino": "Vítimas/ Sexo Feminino", "vitimas_masculino": "Vítimas/ Sexo Masculino",
                    "autor_crime_feminino": "Agressor / Sexo Feminino", "autor_crime_masculino": "Agressor /Masculino"}
    # update dictionary with all possible values for legend entries

    legend_entries = [v for k, v in mapping_dict.items() if v in var_toplot]

    for idx, name in enumerate(legend_entries):
        fig.data[idx].name = name
        fig.data[idx].hovertemplate = '<b> Sexo</b>: ' + name + '<br> <b>Ano</b>: %{x} <br>' + \
                                      '<b> Vítimas</b>: %{y}'
        fig.update_layout(autosize=True)

    return html.Div(children=[html.Div(children=drop_down, id="metric",
                    style={"vertical-align": "top", "width": "90%"}),
                     html.Div(children=dcc.Graph(id='evolution_overview', figure=fig),
                              id="fig_div", style={"position": "relative", "top": "30px", "width": "90%"})],
                    id="parent_div", style={'position': "relative", "left": "30px"})


def get_general_view():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                "2017", style={"font-weight": "bold"}
                            ),
                            html.H2(
                                "APAV: Relatório Anual", style={"margin-top": "0px", "font-weight": "bold"}
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
                ], className="row"),
            html.Footer(
                [
                    html.B("Fonte: "),
                    html.A("https://apav.pt/apav_v3/images/pdf/Estatisticas_APAV_Relatorio_Anual_2020.pdf")
                ],
                className="footer"
            )
        ],
        id="right-column",
        className="eight columns",
        style={'position': "relative", "left": "50px", "horizontal-alignment": "center"}
    )


if __name__ == '__main__':
    app.run_server(debug=True)


