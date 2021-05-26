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

from dashboard_components import contact_type_graph, age_by_sex_graph
from functions import get_data,build_fig, update_content,build_gen_view_figs
from support import CONCELHOS 
##
counties_options = [
    {"label": str(CONCELHOS[county]), "value": str(county)} for county in CONCELHOS
]

dummy_data = pd.read_csv("data/data.csv", sep=",")

df = px.data.tips()
fig = px.pie(df, values='tip', names='day', color_discrete_sequence=px.colors.sequential.RdBu)

##
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server
vbar = dbc.NavbarSimple(
    children=[
        dbc.Button("Sidebar", outline=True, color="secondary", className="mr-1", id="btn_sidebar"),
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Brand",
    brand_href="#",
    color="dark",
    dark=True,
    fluid=True,
)



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
                dbc.NavLink("Vista Geral (nova)", href="/globalview", active="exact"),
                dbc.NavLink("Dados Demográficos", href="/cartographic_view", active="exact"),
                dbc.Button("Sidebar", outline=True, color="secondary", className="mr-1", id="btn_sidebar"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar"
)

df_data, geojson = get_data()

content = html.Div(id="page-content", className="content")
tabs = dbc.Tabs([ dbc.Tab(label="Scatter", tab_id="scatter"), dbc.Tab(label="Histograms", tab_id="histogram"),], id="tabs", active_tab="scatter"), html.Div(id="tab-content", className="p-4")

app.layout = html.Div([dcc.Location(id="url"), dcc.Store(id="memory_output", data={"value": "nr_crimes"}), sidebar,
                       content, ])



@app.callback(Output("page-content", "children"), Input("url", "pathname"), Input("memory_output", "data"))
def render_page_content(pathname, data):
    if pathname == "/":
        return ""
    elif pathname == "/page-1":
        gen_view = get_general_view1()
        return gen_view
    elif pathname == "/globalview":
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
            html.Div([
                html.H3("Quando?", style = {"width":"100%"}, className="when_header"),
                html.Div([dcc.RangeSlider(
                    id="year_slider",
                    min=2000,
                    max=2020,
                    value=[2000, 2020],
                    marks={
                        2000: '2000',
                        2001: '2001',
                        2002: '20002',
                        2003: '2003',
                        2004: '2004',
                        2005: '2005',
                        2006: '2006',
                        2007: '2007',
                        2008: '2008',
                        2009: '2009',
                        2010: '2010',
                        2011: '2011',
                        2012: '2012',
                        2013: '2013',
                        2014: '2014',
                        2015: '2015',
                        2016: '2016',
                        2017: '2017',
                        2018: '2018',
                        2019: '2019',
                        2020: '2020',
                    }
                )], style ={"width":"100%"}),
                html.Br(),
                html.Div([
                        html.H3("Quem?", style = {"width":"96%"}, className="who_header"),
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
                 ], style={'width': '40%'}),

                html.Div(
                    [
                        html.H3(
                            "Facto Criminoso", style={"margin-top": "0px", "font-weight": "bold", "width":"100%"}
                        ),
                        html.Div([
                            html.H5('Tipo'),
                            dcc.Graph(id='criminal_fact_type', )
                        ], className="col-md-4"),
                        html.Div([
                            html.H5('Duração'),
                            dcc.Graph(id='criminal_fact_duration', )
                        ], className="col-md-4"),
                        html.Div([
                            html.H5('Local'),
                            dcc.Graph(id='criminal_fact_local', )
                        ], className="col-md-4"),
                    ], className="row",  style={'width': '100%'}),
            ], className="pretty_container row"),

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
    Output('offender_mariptual_state', 'figure'),Output('offender_relation_wvictim', 'figure'),Output('criminal_fact_type', 'figure'),Output('criminal_fact_duration', 'figure'),Output('criminal_fact_local', 'figure')],
    [dash.dependencies.Input('my-toggle-switch', 'on'), dash.dependencies.Input('year_slider', 'value'), dash.dependencies.Input('county1_dpdn', 'value'),dash.dependencies.Input('county2_dpdn', 'value')]
)
def update_da(all_country,year, county1, county2):
  ###  this method return all figs to present on the view 
    transformed_value = [v for v in year]
    victim_sex_fig, victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig, offender_sex_fig, offender_age_fig, offender_mariptual_state_fig, offender_relation_wvictim_fig, criminal_fact_type_fig, criminal_fact_duration_fig, criminal_fact_local_fig = build_gen_view_figs(transformed_value, all_country, county1, county2, counties_options)
    return victim_sex_fig, victim_age_fig, victim_mariptual_state_fig, victim_relation_woffender_fig, offender_sex_fig, offender_age_fig, offender_mariptual_state_fig, offender_relation_wvictim_fig, criminal_fact_type_fig, criminal_fact_duration_fig, criminal_fact_local_fig


    
if __name__ == '__main__':
    app.run_server(debug=True)


