from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
from flask import Flask, jsonify
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import sqlite3
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import textwrap
import funkcje as fu




# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'twoja_tajna_klucz'
socketio = SocketIO(app)

# Słownik dla wątków: pozwala przechowywać dane procesów dla każdej sesji
active_threads = {}

def run_script_once(script_path, args, session_id):
    script_name = os.path.splitext(os.path.basename(script_path))[0]
    process = subprocess.Popen(['python', script_path] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        socketio.emit('script_output', {'output': line.strip(), 'script': script_name}, room=session_id)
    stderr_output = process.stderr.read()
    if stderr_output:
        socketio.emit('script_error', {'error': stderr_output.strip(), 'script': script_name}, room=session_id)






@socketio.on('connect')
def handle_connect():
     print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('uruchom_Check_Data')
def handle_uruchom_Check_Data():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('Check-Data.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

@socketio.on('uruchom_Chart')
def handle_uruchom_Chart():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('chart.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread




@socketio.on('zbieraj_Dane')
def handle_zbieraj_Dane(data):
    url = data.get('url')
    session_id = request.sid
    if url:
        if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
            thread = threading.Thread(target=run_script_once, args=('ZbieranieDanych.py', [url], session_id))
            thread.start()
            active_threads[session_id] = thread
    else:
        emit('script_error', {'error': "Nie podano URL-a."}, room=session_id)


@socketio.on('uruchom_czyszczenie_Data')
def handle_uruchom_Clear_Data():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('CzyszczenieDanych.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread



@socketio.on('uruchom_Tworzenie_DB')
def handle_uruchom_Tworzenie_DB():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('TworzenieDB.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread


@socketio.on('uruchom_Stats')
def handle_uruchom_Stats():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('stats.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread


@socketio.on('uruchom_Chart')
def handle_uruchom_Chart():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('chart.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

@socketio.on('db_created')
def handle_db_created():
    print("Otrzymano sygnał o utworzeniu bazy danych.")
    emit('dash_needs_refresh_baza', {}, broadcast=True)

# DASH APP EMBEDDING FOR /baza_danych
DATABASE_PATH = r"DbOksary.db"
dash_app = None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/baza_danych')
def baza_danych_page():
    db_exist = os.path.exists(DATABASE_PATH)
    dash_url = '/baza_danych/'
    return render_template('bazadanych.html', dash_url=dash_url, db_exist=db_exist)





@app.route('/wizualizacja')
def wizualizacja_page():
    dash_url = '/wizualizacja/'
    dash_urls = '/wizualizacja2/'
    image_path = os.path.join(app.static_folder, 'charts', 'analizaAktorow.png')
    image_exists = os.path.exists(image_path)

    image_path2 = os.path.join('static', 'charts', 'country.html')
    image_exists2 = os.path.exists(image_path2)

    return render_template('wizualizacja.html', dash_url=dash_url,image_exists=image_exists,image_exists2=image_exists2, htmlPath=image_path2, dash_urls=dash_urls)




@app.route('/info')
def info_page():
    return render_template('info.html')



@app.route('/dok')
def dokumentacja_page():
    return render_template('dokumentacja.html')


TEST_FILE = 'test_data_consistency.py'



@app.route('/stats')
def stats_page():
    stats = None
    try:
        # Sprawdź, czy plik CleanData.csv istnieje przed próbą analizy
        if os.path.exists('CleanData.csv'):
            stats = fu.analizuj_dane()
        else:
            stats = "Brak Pliku"
    except FileNotFoundError as e:
        stats = f"Błąd odczytu pliku: {e}"
    except Exception as e:
        stats = f"Wystąpił błąd podczas analizy danych: {e}"

    try:
        # Uruchom Pytest
        result = subprocess.run(['pytest', '-q', TEST_FILE], capture_output=True, text=True)

        # Przetwórz wynik
        if result.returncode == 0:
            test_status = 'Passed'
        else:
            test_status = 'Failed'
        test_output = result.stdout


    except Exception as e:
        test_status = 'Error'
        test_output = str(e)


    dash_url = '/stats/'
    return render_template('stats.html', dash_url=dash_url, stats=stats, test_status=test_status, test_output=test_output)

def fetch_data():
    conn = sqlite3.connect(DATABASE_PATH)
    query = """SELECT a.imie_nazwisko AS Actor, n.rok AS Year, n.film AS Film, tn.nazwa_typu AS Type, k.nazwa_kategorii AS Category
               FROM nagrody n
               JOIN kategorie k ON k.id_kategorii = n.id_kategorii
               JOIN typy_nagrod tn ON tn.id_typu = n.id_typu
               JOIN aktorzy a ON a.id_aktora = n.id_aktora"""
    try:
        df = pd.read_sql_query(query, conn)
    except pd.errors.DatabaseError as e:
        print(f"Error fetching data: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    return df



def create_dash_layout(initial_df):
    return html.Div([
        html.Div(children='Przegląd Danych', style={'textAlign': 'center', 'color': 'blue', 'fontSize': 20, 'margin-bottom': '20px'}),
        html.Div(className='row', children=[
            html.Div(className='input-group', children=[
                html.Label("Filter by Actor:", className='input-label'),
                dcc.Input(id='actor-input', type='text', placeholder='Enter Actor', value='', className='input-field'),
            ], style={'margin': '10px'}),  # Dodano margin
            html.Div(className='input-group', children=[
                html.Label("Filter by Year:", className='input-label'),
                dcc.Input(id='year-input', type='number', placeholder='Enter Year', value=None, className='input-field'),
            ], style={'margin': '10px'}),  # Dodano margin
            html.Div(className='input-group', children=[
                html.Label("Filter by Film:", className='input-label'),
                dcc.Input(id='film-input', type='text', placeholder='Enter Film', value='', className='input-field'),
            ], style={'margin': '10px'}),  # Dodano margin
            html.Div(className='input-group', children=[
                html.Label("Filter by Type:", className='input-label'),
                dcc.Input(id='type-input', type='text', placeholder='Enter Type', value='', className='input-field'),
            ], style={'margin': '10px'}),  # Dodano margin
            html.Div(className='input-group', children=[
                html.Label("Filter by Category:", className='input-label'),
                dcc.Input(id='category-input', type='text', placeholder='Enter Category', value='', className='input-field'),
            ], style={'margin': '10px'}),  # Dodano margin
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'align-items': 'center', 'padding': '10px'}),  # Dodano padding
        dash_table.DataTable(
            id='data-table-baza',
            columns=[{"name": i, "id": i} for i in initial_df.columns],
            data=initial_df.to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto'},
            filter_action='none',
            sort_action='native',
            style_cell={'padding': '5px', 'textAlign': 'left'},
            style_header={
                'backgroundColor': 'lightgray',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ]
        )
    ], style={'padding': '20px'})

initial_data = None
db_exists_on_start = os.path.exists(DATABASE_PATH)
if db_exists_on_start:
    initial_data = fetch_data()
    dash_app = Dash(__name__, server=app, url_base_pathname='/baza_danych/')
    dash_app.layout = create_dash_layout(initial_data)

    @dash_app.callback(
        Output('data-table-baza', 'data'),
        [Input('actor-input', 'value'), Input('year-input', 'value'), Input('film-input', 'value'), Input('type-input', 'value'), Input('category-input', 'value')]
    )
    def update_table_baza_danych(actor_value, year_value, film_value, type_value, category_value):
        global initial_data # Access the module-level variable
        if initial_data is None:
            return [] # Or handle the case where data hasn't loaded yet
        filtered_data = initial_data.copy()
        if actor_value:
            filtered_data = filtered_data[filtered_data['Actor'].str.contains(actor_value, case=False, na=False)]
        if year_value:
            try:
                year_value = int(year_value)
                filtered_data = filtered_data[filtered_data['Year'] == year_value]
            except ValueError:
                pass
        if film_value:
            filtered_data = filtered_data[filtered_data['Film'].str.contains(film_value, case=False, na=False)]
        if type_value:
            filtered_data = filtered_data[filtered_data['Type'].str.contains(type_value, case=False, na=False)]
        if category_value:
            filtered_data = filtered_data[filtered_data['Category'].str.contains(category_value, case=False, na=False)]
        return filtered_data.to_dict('records')
else:
    dash_app = Dash(__name__, server=app, url_base_pathname='/baza_danych/')
    dash_app.layout = html.Div("Wystąpił błąd. Proszę zrestartować aplikację.")


CleanData ='CleanData.csv'
df_exists_on_start = os.path.exists(CleanData)

if df_exists_on_start:
    df = pd.read_csv('CleanData.csv')

    # Filter data to include only specific categories
    filtered_df = df.loc[df['category'].isin(['ACTOR IN A LEADING ROLE', 'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS'])]

    dash3_data = df.loc[~df['category'].isin(['FOREIGN LANGUAGE FILM','INTERNATIONAL FEATURE FILM'])]

    # Group and count occurrences for each actor and type
    grouped_df = filtered_df.groupby(['aktor', 'type']).size().reset_index(name='count')

    # Sort the grouped data
    sorted_df = grouped_df.sort_values(by=['aktor', 'type', 'count'], ascending=[True, False, False])

    # Filter data for winners only
    winners_df = sorted_df[sorted_df['type'] == 'Winner'].sort_values(by='count', ascending=False)
    winners_df = winners_df.rename(columns={'count': 'Ilość'})





    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    dash_app2 = Dash(
        __name__,
        server=app,
        url_base_pathname='/wizualizacja/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )



    # App layout


    dash_app2.layout = html.Div([
        html.Div(className='row', children='Zestawienie liczby Oscarów zdobytych za role pierwszoplanowe',
                style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30, 'justifyContent': 'center', 'display': 'flex'}),

        html.Div(className='row', children=[
            dcc.RadioItems(options=['Ilość'],
                        value='Ilość',
                        inline=True,
                        id='my-radio-buttons-final')
        ]),

        html.Div(className='row', children=[
            dcc.Slider(
                id='count-slider',
                min=0,
                max=winners_df['Ilość'].max(),
                step=1,
                value=0,
                marks={i: str(i) for i in range(0, winners_df['Ilość'].max() + 1, 5)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'margin': '20px'}),

        html.Div(className='row', children=[
            html.Div(className='six columns', children=[
                dash_table.DataTable(id='data-table', data=winners_df.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'})
            ]),
            html.Div(className='six columns', children=[
                dcc.Graph(figure={}, id='histo-chart-final')
            ])
        ])
    ])

    # Add controls to build the interaction
    @dash_app2.callback(
        [Output(component_id='histo-chart-final', component_property='figure'),
        Output(component_id='data-table', component_property='data')],
        [Input(component_id='my-radio-buttons-final', component_property='value'),
        Input(component_id='count-slider', component_property='value')]
    )
    def update_graph_and_table(col_chosen, min_count):
        # Filter the data based on the slider's value
        filtered_df = winners_df[winners_df['Ilość'] >= min_count]

        # Create the bar chart with filtered data
        fig = px.bar(filtered_df, x='aktor', y=col_chosen, color='aktor', title=f'Aktorzy i {col_chosen} otrzymanaych Oksarów za role pierwszoplanowe')

        # Return both the figure and the filtered DataFrame's data for the DataTable
        return fig, filtered_df.to_dict('records')




    dash_app3 = Dash(
        __name__,
        server=app,
        url_base_pathname='/wizualizacja2/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    unique_categories = dash3_data['category'].unique().tolist()



    dash_app3.layout = dbc.Container([
        html.Div(className='row', children='Aktorzy i Nagrody Filmowe',
                style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30, 'justifyContent': 'center', 'display': 'flex'}),
        dbc.Row([
            dbc.Col(md=4, children=[
                html.Div("Wybierz kategorie:", style={'margin-bottom': '10px'}),
                dcc.Checklist(
                    id='category-checklist',
                    options=[{'label': cat, 'value': cat} for cat in sorted(unique_categories)],
                    value=[],
                    labelStyle={'display': 'block', 'margin-right': '10px', 'width': '150px'},  # Reduced width
                    style={'margin-bottom': '20px'}
                ),
            ]),
            dbc.Col(md=8, children=[
                dcc.Graph(id='histo-chart-final', figure={}),
                dash_table.DataTable(
                    id='data-table',
                    data=[],
                    page_size=20,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'},
                    sort_action='native',
                    filter_action='native',
                    #export_format='csv',
                ),

                html.Div(id='title-container', style={'textAlign': 'center', 'margin-top': '20px'})  # Title container
            ]),
        ])
    ], fluid=True)


    # Add controls to build the interaction
    @dash_app3.callback(
        [Output('histo-chart-final', 'figure'),
        Output('data-table', 'data'),
        Output('title-container', 'children')],
        Input('category-checklist', 'value')
    )


    def update_graph_and_table(selected_categories):
        if not selected_categories:
            filtered_df = dash3_data[dash3_data['type'] == 'Winner'].groupby('aktor')[['film']].count().sort_values('film',ascending=False).reset_index().head(20)
            title_main = "Zwycięzcy Oscarów (liczba filmów)"
            title_sub = "(Wszystkie Kategorie)"
        else:
            filtered_df = dash3_data[
                (dash3_data['type'] == 'Winner') & (dash3_data['category'].isin(selected_categories))
            ].groupby('aktor')[['film']].count().sort_values('film', ascending=False).reset_index().head(20)
            categories_str = ", ".join(selected_categories)
            title_main = "Zwycięzcy Oscarów (liczba filmów)"
            title_sub = f"(Kategorie: {categories_str})"


        def split_into_lines(text, line_length=105):
        # S Split the text into lines at word boundaries, respecting the line length
            wrapped_lines = textwrap.wrap(text, width=line_length)
            return "\n".join(wrapped_lines)

        # Apply the function to `title_sub`
        split_title_sub = split_into_lines(title_sub, line_length=105)



        # Create the horizontal bar chart
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(y=filtered_df['aktor'],
                            x=filtered_df['film'],
                            marker_color=px.colors.qualitative.Set1,
                            name="Liczba Filmów",
                            orientation='h'),
                    row=1, col=1)


        fig.update_layout(
            xaxis_title="Liczba Oskarów",
            yaxis_title="Aktor",
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=50),  # Adjust margins
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=600  # Adjusted figure height
        )

        title_component = html.Div(
            [
                html.Span(title_main, style={'font-size': '24px', 'color': 'red'}),
                html.Br(),
                html.Span(split_title_sub, style={'font-size': '10px', 'color': 'blue'})
            ],
            style={'textAlign': 'center', 'margin-top': '20px'}
        )


        # Return the figure and the DataFrame's data for the DataTable
        return fig, filtered_df.to_dict('records'), title_component



    df = pd.read_csv('CleanData.csv')

    last=df.loc[(df['type']=='Winner')& ( df['category'].isin(['ACTOR IN A LEADING ROLE',\
                                                            'ACTOR IN A SUPPORTING ROLE','ACTRESS',
                                                                'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS','ACTRESS IN A SUPPORTING ROLE']))]
    lastn=last.groupby(['aktor', 'type']).size().reset_index(name='count')
    lastn=lastn.sort_values(by='count', ascending=False)

    #lista aktorow
    al=lastn[lastn['count']>1]['aktor']
    aktorzy=df[df['aktor'].isin(al)]
    myData = pd.DataFrame()

    for i in al:
        akt=pd.DataFrame({i:aktorzy.loc[aktorzy['aktor']==i]['YEAR'].describe()})
        myData=pd.concat([myData, akt], axis=1)

    myData.loc['Rozstep']=myData.loc['max']-myData.loc['min']

    myData['mean']=myData.mean(axis=1)

    finalmyData=myData.T
    finalmyData = finalmyData.rename(index={'index': 'Aktor'})

    oskar=aktorzy.loc[aktorzy['type']=='Winner'].groupby('aktor')[['film']].count().sort_values('film').reset_index()
    polaczony_df = pd.merge(finalmyData, oskar, left_index=True, right_on='aktor', how='left').rename(columns={'film': 'Ilosc Oskarow'})
    polaczony_df[['aktor', 'Ilosc Oskarow','count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'Rozstep']]
    polaczony_df = polaczony_df.set_index('aktor')



    dash_app4 = Dash(
        __name__,
        server=app,
        url_base_pathname='/stats/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )



    # App layout


    dash_app4.layout = html.Div([
        html.H1("Aktorzy i statystyki"),
        dcc.Dropdown(
            id='data-column-dropdown',
            options=[
                {'label': 'Ilosc Oskarow', 'value': 'Ilosc Oskarow'},
                {'label': 'Ilość', 'value': 'count'},
                {'label': 'Mean', 'value': 'mean'},
                {'label': 'Standard Deviation', 'value': 'std'},  # Poprawiony label
                {'label': 'Minimum Year', 'value': 'min'},      # Poprawiony label
                {'label': '25th Percentile', 'value': '25%'},
                {'label': 'Median', 'value': '50%'},
                {'label': '75th Percentile', 'value': '75%'},
                {'label': 'Maximum Year', 'value': 'max'},      # Poprawiony label
                {'label': 'Range', 'value': 'Rozstep'}       # Poprawiony label
            ],
            value='count',
        ),
        dcc.Graph(id='actor-stats-chart'),
        dash_table.DataTable(
            id='actor-stats-table',
            columns=[{"name": i, "id": i} for i in polaczony_df.reset_index().columns],
            data=polaczony_df.reset_index().to_dict('records'),
            page_size=50
        )
    ])


    # Callback
    @dash_app4.callback(
        [Output('actor-stats-chart', 'figure'),
        Output('actor-stats-table', 'data')],
        [Input('data-column-dropdown', 'value')]
    )
    def update_chart_and_table(selected_column):
        tytul = f"Aktorzy i {selected_column.title()}"
        if selected_column == 'count':
            tytul = "Aktorzy i Ilość"
        fig = px.bar(polaczony_df.reset_index(), x=polaczony_df.index, y=selected_column,
                    title=tytul)
        # Dodaj opcjonalne skalowanie osi Y tutaj, jeśli jest to potrzebne dla konkretnych kolumn
        if selected_column in ['mean', 'min', '25%','50%', '75%', 'max']:
            fig.update_layout(yaxis=dict(range=[1920, polaczony_df[selected_column].max()]))
        return fig, polaczony_df.reset_index().to_dict('records')





    url_map = {
        '/wizualizacja': dash_app2.server,
        '/wizualizacja2': dash_app3.server,
        '/stats': dash_app4.server,
    }


    if db_exists_on_start:
        url_map['/baza_danych'] = dash_app.server
    else:
        print("Warning: dash_app not initialized, '/baza_danych' route not mounted.")



    mounted_app = DispatcherMiddleware(app.wsgi_app, url_map)



def uruchom_serwer(app, debug_mode=True):
    socketio.run(app, debug=debug_mode)



if __name__ == '__main__':
    uruchom_serwer(app, debug_mode=True)
