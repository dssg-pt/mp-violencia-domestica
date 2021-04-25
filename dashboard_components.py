import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import copy

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h")
)

layout_pie = copy.deepcopy(layout)

data = [
    dict(
        type="pie",
        labels=["Telefónico", "Presencial", "Apoio Online/Email"],
        values=[61.6,19.5, 17.7],
        name="TIPO DE CONTACTO",
        text=[
            "TELEFÓNICO",
            "PRESENCIAL",
            "APOIO ONLINE/EMAIL",
        ],
        hoverinfo="text+percent",
        textinfo="label+percent+name",
        hole=0.5,
        marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"])
    )
]
layout_pie["title"] = "TIPO DE CONTACTO"

layout_pie["font"] = dict(color="#777777")
layout_pie["legend"] = dict(
    font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
)

contact_type_graph = dict(data=data, layout=layout_pie)




women_bins = np.array([-600, -623, -653, -650, -670, -578, -541, -411, -322, -230])
men_bins = np.array([600, 623, 653, 650, 670, 578, 541, 360, 312, 170])

y = list(range(0, 100, 10))

layout_2 = go.Layout(yaxis=go.layout.YAxis(title='Idade'),
                     margin=dict(l=30, r=30, b=20, t=40),
                   xaxis=go.layout.XAxis(
                       range=[-1200, 1200],
                       tickvals=[-1000, -700, -300, 0, 300, 700, 1000],
                       ticktext=[1000, 700, 300, 0, 300, 700, 1000],
                       title='Nº de Casos'),
                   barmode='overlay')

data_2 = [go.Bar(y=y,
               x=men_bins,
               orientation='h',
               name='Homens',
               hoverinfo='x',
               marker=dict(color='blue')
               ),
        go.Bar(y=y,
               x=women_bins,
               orientation='h',
               name='Mulheres',
               text=-1 * women_bins.astype('int'),
               hoverinfo='text',
               marker=dict(color='red')
               )]
layout_2["title"] = "CASOS POR SEXO/IDADE"

layout_2["font"] = dict(color="#777777")
age_by_sex_graph = (dict(data=data_2, layout=layout_2))



metric_dropdown = dcc.Dropdown(
    id="drop_down1",
    options=[
        {'label': 'Crimes Registados', 'value': 'nr_crimes'},
        {'label': 'Incidência', 'value': 'incidencia'},
        {'label': 'Tendência', 'value': 'tendencia'}
    ],
    placeholder="Selecione uma métrica",
)