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


df_data, geojson = get_data()

content = html.Div(id="page-content", className="content")
app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output", data={"value": "nr_crimes"}), sidebar,
                       content])

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
        gen_view = get_general_view()
        return gen_view
    elif pathname == "/cartographic_view":
        fig = build_fig(metric="incidencia")
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
    app.run_server(debug=True)

