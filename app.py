import pandas as pd 
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

## 1. Cargar el DataFrame
proyecto =pd.read_csv("United_States.csv")

## 2. Transformación de datos (Si es necesario)
proyecto = proyecto.rename(columns={"Name":"Nombre","Industry":"Industria","Revenue (USD millions)":"Ganacia(USD)","Revenue growth":"Crecimiento","Employees":"#Empleados","Headquarters":"Sede"})
proyecto["Ganacia(USD)"] = proyecto["Ganacia(USD)"].str.replace(',', '.').astype(float)
def ganancia(row):
 return row ["Ganacia(USD)"] *1000
proyecto['GananciaTotal']=proyecto.apply(lambda x: ganancia(x),axis=1)
proyecto["Crecimiento"] = proyecto["Crecimiento"].str.replace('%', '').astype(float)

from ast import Return
def Resultado(row):
  if row["Crecimiento"] >0 :
    return "Crece"
  else:
    return "No crece"
proyecto["Resultados"]= proyecto.apply(lambda x: Resultado (x),axis= 1)

Empresas = proyecto['Nombre'].unique()
Industrias = proyecto['Industria'].unique()
Sedes = proyecto['Sede'].unique()
proyecto['GananciaTotal'] = pd.to_numeric(proyecto['GananciaTotal'], errors='coerce') 
Ganancia_min = proyecto['GananciaTotal'].min()
Ganancia_max = proyecto['GananciaTotal'].max()

external_stylesheets = [dbc.themes.PULSE]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Detalle de resultados empresas americanas"

app.layout = dbc.Container([
    dbc.Row([html.H1("Reporte de ganancias industrias Americanas", className="text-center my-4")]),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona la industria:"),
            dcc.Dropdown(
                id='selector_industria',
                options=[{'label': i, 'value': i} for i in Industrias],
                value=Industrias[0] if len(Industrias) > 0 else None
            )
        ], width=4),
        dbc.Col([
            html.Label("Selecciona la empresa:"),
            dcc.Dropdown(
                id='selector_empresa',
                options=[{'label': e, 'value': e} for e in Empresas],
                value=Empresas[0] if len(Empresas) > 0 else None
            )
        ], width=4),
        dbc.Col([
            html.Label("Selecciona la sede:"),
            dcc.Dropdown(
               id='selector_sede',
               options=[{'label': s, 'value': s} for s in Sedes],
               value=Sedes[0] if len(Sedes) > 0 else None,
               clearable=False
            )
        ], width=4)
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona el rango de ganancia:"),
            dcc.RangeSlider(
                id='selector_ganancia',
                min=Ganancia_min,
                max=Ganancia_max,
                value=[Ganancia_min, Ganancia_max],
                step=(Ganancia_max - Ganancia_min) / 100
            )
        ], width=8),
        dbc.Col([
            html.Label("Selecciona los resultados:"),
            dbc.Checklist(
                id='selector_resultados',
                options=[{'label': r, 'value': r} for r in proyecto['Resultados'].unique()],
                value=[proyecto['Resultados'].unique()[0]],
                inline=True
            )
        ], width=4)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([dcc.Graph(id='grafica_barras')], width=6),
        dbc.Col([dcc.Graph(id='grafica_torta')], width=6),
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='grafica_area')], width=12)
    ])
])

@app.callback(
    [Output('grafica_barras', 'figure'),
     Output('grafica_torta', 'figure'),
     Output('grafica_area', 'figure')],
    [Input('selector_industria', 'value'),
     Input('selector_empresa', 'value'),
     Input('selector_sede', 'value'),
     Input('selector_ganancia', 'value'),
     Input('selector_resultados', 'value')]   
)
def crear_graficas(valor_industria, valor_empresa, valor_sede, valor_rango_ganancia, lista_resultados):
    
  
    df_filtrado = proyecto[
        (proyecto['GananciaTotal'] >= valor_rango_ganancia[0]) & 
        (proyecto['GananciaTotal'] <= valor_rango_ganancia[1]) &
        (proyecto['Resultados'].isin(lista_resultados))
    ]

   
    if valor_industria:
        df_filtrado = df_filtrado[df_filtrado['Industria'] == valor_industria]
    
   
    if valor_sede:
        df_filtrado = df_filtrado[df_filtrado['Sede'] == valor_sede]

   
    if df_filtrado.empty:
      
        layout_vacio = {"layout": {"title": "No hay datos con estos filtros"}}
        return layout_vacio, layout_vacio, layout_vacio

   
    grafica_barras = px.bar(
        df_filtrado, 
        x='Nombre',        
        y='GananciaTotal', 
        color='Resultados',
        title='Ganancias por Empresa',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    
    conteo_resultados = df_filtrado['Resultados'].value_counts().reset_index()
    conteo_resultados.columns = ['Resultados', 'Cuenta']
    
    grafica_torta = px.pie(
        conteo_resultados, 
        names='Resultados', 
        values='Cuenta', 
        title='Distribución de Resultados',
        hole=0.4 
    )

   
    grafica_area = px.area(
        df_filtrado, 
        x="Nombre", 
        y="GananciaTotal", 
        color="Sede", 
        title='Acumulado de Ganancias por Sede'
    )

    
    for fig in [grafica_barras, grafica_torta, grafica_area]:
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })

    return grafica_barras, grafica_torta, grafica_area
