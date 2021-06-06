import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import copy

from functions import get_data_overview

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=5, r=5, b=20, t=30),
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
        values=[61.6, 19.5, 17.7],
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

crime_loc_values = [65, 12.9, 8.3, 4.6, 2.4, 5]  # to be update with values from APAV database

crime_location = [
    dict(
        type="pie",
        labels=["Residência Comum", "Residência Vítima", "Via Pública",
                "Residência Autor", "Local de Trabalho", "Outro"],
        values=crime_loc_values,
        name="LOCAL DO CRIME",
        text=[
            "Residência Comum",
            "Residência Vítima",
            "Via Pública",
            "Residência Autor",
            "Local de Trabalho",
            "Outro"
        ],
        hoverinfo="text+percent",
        textinfo="label+percent+name",
        hole=0.5,
        marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8", "#e5f799", "#d599f7", "#ffc369"
                            ])
    )
]

layout_pie2 = copy.deepcopy(layout)

layout_pie2["title"] = "LOCAL DO CRIME"
layout_pie2["margin"] = dict(l=90, r=5, b=20, t=30)

layout_pie2["font"] = dict(color="#777777")
layout_pie2["legend"] = dict(
    font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
)

crime_location_graph = dict(data=crime_location, layout=layout_pie2)

relationship_values = [34.2, 19.7, 15.6, 12.5, 9.2, 8.1]  # to be update with values from APAV database

relationship_data = [
    dict(
        type="pie",
        labels=["Cônjuge", "Outro", "Companheiro(a)",
                "Filho(a)", "Ex-Companheiro(a)", "Pai/Mãe"],
        values=relationship_values,
        name="Relação da Vítima com Autor do Crime",
        text=["Cônjuge", "Outro", "Companheiro(a)",
                "Filho(a)", "Ex-Companheiro(a)", "Pai/Mãe"],
        hoverinfo="text+percent",
        textinfo="label+percent+name",
        hole=0.5,
        marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8", "#e5f799", "#d599f7", "#ffc369"
                            ])
    )
]

layout_pie3 = copy.deepcopy(layout)

layout_pie3["title"] = "LOCAL DO CRIME"

layout_pie3["font"] = dict(color="#777777")
layout_pie3["legend"] = dict(
    font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
)

layout_pie3["title"] = "RELAÇÃO DA VÍTIMA COM AUTOR DO CRIME"

relationship_chart = dict(data=relationship_data, layout=layout_pie3)

victim_sex_data = [
    dict(
        type="pie",
        labels=["Feminino",
                "Masculino"],
        values=[5976, 911],
        name="Sexo da Vítima",
        text=["Feminino", "Masculino"],
        hoverinfo="text+percent",
        textinfo="label+percent+name",
        marker=dict(colors=["#fac1b7",  "#92d8d8"])
    )
]

layout_pie4 = copy.deepcopy(layout)
layout_pie4["title"] = "SEXO DA VÍTIMA"

layout_pie4["font"] = dict(color="#777777")
layout_pie4["legend"] = dict(
    font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
)

victim_sex_chart = dict(data=victim_sex_data, layout=layout_pie4)

offender_sex_data = [
    dict(
        type="pie",
        labels=["Feminino",
                "Masculino"],
        values=[897, 6100],
        name="Sexo do Agressor",
        text=["Feminino", "Masculino"],
        hoverinfo="text+percent",
        textinfo="label+percent+name",
        marker=dict(colors=["#fac1b7",  "#92d8d8"])
    )
]

layout_pie5 = copy.deepcopy(layout)
layout_pie5["title"] = "SEXO DO AGRESSOR"

layout_pie5["font"] = dict(color="#777777")
layout_pie5["legend"] = dict(
    font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
)

offender_sex_chart = dict(data=offender_sex_data, layout=layout_pie5)

drop_down = dcc.Dropdown(
    id="lineplot_dropdown",
    options=[
        {'label': 'Vítima: Feminino', 'value': 'vitimas_feminino'},
        {'label': 'Vítima: Maculino', 'value': 'vitimas_masculino'},
        {'label': 'Autor do Crime: Feminino', 'value': 'autor_crime_feminino'},
        {'label': "Autor do Crime: Masculino", 'value': "autor_crime_masculino"}
    ],
    placeholder="Selecione um indicador",
    multi=True,
    persistence=True,
    persistence_type="memory"
    )

data = get_data_overview()

victims_age = ["vitimas_0_10", "vitimas_11_17", "vitimas_18_25", "vitimas_26_35", "vitimas_36_45",
               "vitimas_46_55", "vitimas_56_64", "vitimas_65+"
               ]

aggressors_age = ["autor_crime_0_17", "autor_crime_18_25", "autor_crime_26_35", "autor_crime_36_45",
                  "autor_crime_46_55", "autor_crime_56_64", "autor_crime_65+"
                  ]

victim_bins = data[data["ano"] == 2017][victims_age].values[0]
aggressor_bins = data[data["ano"] == 2017][aggressors_age].values[0]

aggressor_bins = np.insert(aggressor_bins, 0, 169)  # to update once we have data for 0-10 years old

y = list(range(8))

layout_2 = go.Layout(yaxis=go.layout.YAxis(title='Idade', range=[0, 7],
                                           tickvals=[0, 1, 2, 3, 4, 5, 6, 7],
                                           ticktext=["0-10", "10-17", "18-35", "26-35", "36-45",
                                                     "46-55", "56-64", "65+"
                                                     ]
                                           ),
                     margin=dict(l=40, r=40, b=20, t=40),
                     xaxis=go.layout.XAxis(
                       range=[-1500, 1500],
                       tickvals=[-1400, -700, -350, 0, 350, 700, 1400],
                       ticktext=[1400, 700, 350, 0, 350, 700, 1400],
                       title='Nº de Casos'),
                     barmode='overlay')

data_2 = [go.Bar(y=y,
               x=aggressor_bins,
               orientation='h',
               name='Agressores',
               hoverinfo='x',
               marker=dict(color='blue')
               ),
        go.Bar(y=y,
               x=-1*victim_bins,
               orientation='h',
               name='Vítimas',
               text=-1 * victim_bins.astype('int'),
               hoverinfo='text',
               marker=dict(color='red')
               )]
layout_2["title"] = "CASOS POR PERFIL/IDADE"

layout_2["font"] = dict(color="#777777")
age_by_sex_graph = (dict(data=data_2, layout=layout_2))




