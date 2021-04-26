# dependencies
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

from dashboard_components import contact_type_graph, age_by_sex_graph
from functions import get_data,build_fig, update_content
##

df = px.data.tips()
fig = px.pie(df, values='tip', names='day', color_discrete_sequence=px.colors.sequential.RdBu)

##
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

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
    className="sidebar"
)

df_data, geojson = get_data()

content = html.Div(id="page-content", className="content")
app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output", data={"value": "nr_crimes"}), sidebar,
                       content])



@app.callback(Output("page-content", "children"), Input("url", "pathname"), Input("memory_output", "data"))
def render_page_content(pathname, data):
    if pathname == "/":
        return ""
    elif pathname == "/page-1":
        gen_view = get_general_view()
        return gen_view
    elif pathname == "/cartographic_view":
        fig = build_fig(metric="incidencia", df_data=df_data, geojson=geojson)
        return update_content(fig)








@app.callback(Output("memory_output", "data"), [Input("dropdown1", "value")])
def on_dropdown_select(value):
    return {"value": value}

def get_general_view():
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(
                                "APAV", style={"font-weight": "bold"}
                            ),
                            html.H2(
                                "Relatório Anual 2020", style={"margin-top": "0px", "font-weight": "bold"}
                            ),
                        ]
                    )
                ],
                className="one-half column",
                id="title",
            ),
            html.H3(
                "DESTAQUES", style={"margin-top": "0px", "font-weight": "bold"}
            ),
            html.Div(
                [

                    html.Div(
                        [html.H4(66.408, className="mini_container_text"),
                         html.P("ATENDIMENTOS", className="mini_container_label")],
                        id="attendance",
                        className="mini_container"

                    ),
                    html.Div(
                        [html.H4(19.697, className="mini_container_text"),
                         html.P("CRIMES & OUTRAS FORMAS DE VIOLÊNCIA", className="mini_container_label")],
                        id="crime",
                        className="mini_container"
                    ),
                    html.Div(
                        [html.H4(13.093, className="mini_container_text"),
                         html.P("VÍTIMAS", className="mini_container_label")],
                        id="victims",
                        className="mini_container"
                    ),
                    html.Div(
                        [html.H4(1.227, className="mini_container_text"),
                         html.P("ATIVIDADES FORMATIVAS", className="mini_container_label")],
                        id="formativeactivies",
                        className="mini_container"
                    ),
                ],
                id="info-container",
                className="row container-display",
            ),
            html.H3(
                "NÚMERO MÉDIO DE VÍTIMAS", style={"margin-top": "0px", "font-weight": "bold"}
            ),
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
            html.H3(
                "NÚMERO MÉDIO DE VÍTIMAS", style={"margin-top": "0px", "font-weight": "bold"}
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="conctact_type_graph", figure=contact_type_graph)],
                        className="pretty_container three columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="age_by_sex_graph", figure=age_by_sex_graph)],
                        className="pretty_container three columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="conctact_type_graph", figure=contact_type_graph)],
                        className="pretty_container three columns",
                    ),
                    html.Div(
                        [dcc.Graph(id="conctact_type_graph", figure=contact_type_graph)],
                        className="pretty_container three columns",
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
    )

if __name__ == '__main__':
    server = app.server
    app.run_server(debug=True)


