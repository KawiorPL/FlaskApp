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




# Aplikacja Flask
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





# Poniższe dekoratory Socket.IO definiują funkcje obsługujące określone zdarzenia połączenia od klientów.

@socketio.on('connect')
def handle_connect():
     print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_Check_Data'.
    #Jej zadaniem jest uruchomienie skryptu 'Check-Data.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.


@socketio.on('uruchom_Check_Data')
def handle_uruchom_Check_Data():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('Check-Data.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread




# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_Chart'.
    #Jej zadaniem jest uruchomienie skryptu 'chart.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.

@socketio.on('uruchom_Chart')
def handle_uruchom_Chart():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('chart.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread


# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'zbieraj_Dane'.
    #Jej zadaniem jest uruchomienie skryptu 'ZbieranieDanych.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.

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


# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_czyszczenie_Data'.
    #Jej zadaniem jest uruchomienie skryptu 'CzyszczenieDanych.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.


@socketio.on('uruchom_czyszczenie_Data')
def handle_uruchom_Clear_Data():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('CzyszczenieDanych.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread


# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_Tworzenie_DB'.
    #Jej zadaniem jest uruchomienie skryptu 'TworzenieDB.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.

@socketio.on('uruchom_Tworzenie_DB')
def handle_uruchom_Tworzenie_DB():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('TworzenieDB.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_Stats'.
    #Jej zadaniem jest uruchomienie skryptu 'stats.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.

@socketio.on('uruchom_Stats')
def handle_uruchom_Stats():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('stats.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread


# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'uruchom_Chart'.
    #Jej zadaniem jest uruchomienie skryptu 'chart.py' w oddzielnym wątku,
    #ale tylko raz dla danej sesji klienta.

@socketio.on('uruchom_Chart')
def handle_uruchom_Chart():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('chart.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread



# Ta funkcja jest wywoływana, gdy klient emituje zdarzenie 'db_created'.



@socketio.on('db_created')
def handle_db_created():
    print("Otrzymano sygnał o utworzeniu bazy danych.")
    emit('dash_needs_refresh_baza', {}, broadcast=True)





# DASH APP EMBEDDING FOR /baza_danych
DATABASE_PATH = r"DbOksary.db"
dash_app = None


# Dekorator @app.route('/') definiuje trasę (URL) dla głównej strony aplikacji.
# Po wejściu na główny adres URL (np. http://localhost:5000/),
# funkcja 'index' zostanie wywołana.
@app.route('/')
def index():
    return render_template('index.html')



# Dekorator @app.route('/baza_danych') definiuje trasę dla strony "baza danych".
# Po wejściu na adres URL /baza_danych, funkcja 'baza_danych_page' zostanie wywołana
@app.route('/baza_danych')
def baza_danych_page():
    db_exist = os.path.exists(DATABASE_PATH)
    dash_url = '/baza_danych/'
    return render_template('bazadanych.html', dash_url=dash_url, db_exist=db_exist)


# Dekorator @app.route('/wizualizacja') definiuje trasę dla strony "wizualizacja".
# Po wejściu na adres URL /wizualizacja, funkcja 'wizualizacja_page' zostanie wywołana.
@app.route('/wizualizacja')
def wizualizacja_page():
    dash_url = '/wizualizacja/'
    dash_urls = '/wizualizacja2/'
    image_path = os.path.join(app.static_folder, 'charts', 'analizaAktorow.png')
    image_exists = os.path.exists(image_path)

    image_path2 = os.path.join('static', 'charts', 'country.html')
    image_exists2 = os.path.exists(image_path2)

    return render_template('wizualizacja.html', dash_url=dash_url,image_exists=image_exists,image_exists2=image_exists2, htmlPath=image_path2, dash_urls=dash_urls)


# Dekorator @app.route('/info') definiuje trasę dla strony "info".
# Po wejściu na adres URL /info, funkcja 'info_page' zostanie wywołana.
@app.route('/info')
def info_page():
    return render_template('info.html')


# Dekorator @app.route('/dok') definiuje trasę dla strony "dokumentacja".
# Po wejściu na adres URL /dok, funkcja 'dokumentacja_page' zostanie wywołana.
@app.route('/dok')
def dokumentacja_page():
    return render_template('dokumentacja.html')




# Nazwa pliku testowego Pytest do sprawdzania spójności danych.
TEST_FILE = 'test_data_consistency.py'


# Dekorator @app.route('/stats') definiuje trasę dla strony ze statystykami.
# Po wejściu na adres URL /stats, funkcja 'stats_page' zostanie wywołana.
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



# Funkcja do pobierania danych z bazy danych SQLite
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


# Funkcja do tworzenia układu aplikacji Dash do przeglądania danych z bazy.
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



# Inicjalizacja zmiennej do przechowywania początkowych danych.
initial_data = None
# Sprawdza, czy baza danych istniała w momencie uruchomienia aplikacji.
db_exists_on_start = os.path.exists(DATABASE_PATH)
if db_exists_on_start:
    initial_data = fetch_data()
    dash_app = Dash(__name__, server=app, url_base_pathname='/baza_danych/')
    dash_app.layout = create_dash_layout(initial_data)

    # Callback do aktualizacji tabeli na podstawie wprowadzonych filtrów.
    @dash_app.callback(
        Output('data-table-baza', 'data'),
        [Input('actor-input', 'value'), Input('year-input', 'value'), Input('film-input', 'value'), Input('type-input', 'value'), Input('category-input', 'value')]
    )

    def update_table_baza_danych(actor_value, year_value, film_value, type_value, category_value):
        global initial_data # Dostęp do zmiennej na poziomie modułu
        if initial_data is None:
            return [] # Lub obsłuż przypadek, gdy dane jeszcze się nie załadowały
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

# Nazwa pliku CSV z wyczyszczonymi danymi.
CleanData ='CleanData.csv'
# Sprawdza, czy plik CSV z danymi istniał w momencie uruchomienia aplikacji.
df_exists_on_start = os.path.exists(CleanData)

# Jeśli plik CSV z danymi istniał, przetwarza dane do wizualizacji.
if df_exists_on_start:
    df = pd.read_csv('CleanData.csv')

    # Filtruje dane, aby uwzględnić tylko określone kategorie aktorów.
    filtered_df = df.loc[df['category'].isin(['ACTOR IN A LEADING ROLE', 'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS'])]
     # Filtruje dane, aby wykluczyć filmy zagraniczne/międzynarodowe.
    dash3_data = df.loc[~df['category'].isin(['FOREIGN LANGUAGE FILM','INTERNATIONAL FEATURE FILM'])]

     # Grupuje dane według aktora i typu nagrody, zliczając wystąpienia.
    grouped_df = filtered_df.groupby(['aktor', 'type']).size().reset_index(name='count')

    # Sortuje zgrupowane dane.
    sorted_df = grouped_df.sort_values(by=['aktor', 'type', 'count'], ascending=[True, False, False])

    # Filtruje dane tylko dla zwycięzców i sortuje według liczby nagród.
    winners_df = sorted_df[sorted_df['type'] == 'Winner'].sort_values(by='count', ascending=False)
    # Zmienia nazwę kolumny 'count' na 'Ilość'.
    winners_df = winners_df.rename(columns={'count': 'Ilość'})




    # Definiuje zewnętrzne arkusze stylów dla aplikacji Dash
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    #Tworzy pierwszą aplikację Dash do wizualizacji danych o aktorach.
    dash_app2 = Dash(
        __name__,
        server=app,
        url_base_pathname='/wizualizacja/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )



     # Układ  aplikacji Dash (liczba Oscarów za role pierwszoplanowe).


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

    # Callback do aktualizacji wykresu słupkowego i tabeli w pierwszej aplikacji Dash.
    @dash_app2.callback(
        [Output(component_id='histo-chart-final', component_property='figure'),
        Output(component_id='data-table', component_property='data')],
        [Input(component_id='my-radio-buttons-final', component_property='value'),
        Input(component_id='count-slider', component_property='value')]
    )
    def update_graph_and_table(col_chosen, min_count):
        # Filtruje dane na podstawie wartości suwaka.
        filtered_df = winners_df[winners_df['Ilość'] >= min_count]

        # Tworzy bar chart
        fig = px.bar(filtered_df, x='aktor', y=col_chosen, color='aktor', title=f'Aktorzy i {col_chosen} otrzymanaych Oksarów za role pierwszoplanowe')

        # Tworzy wykres słupkowy z przefiltrowanych danych.
        return fig, filtered_df.to_dict('records')



    # Tworzy trzecią aplikację Dash do wizualizacji aktorów i nagród filmowych z możliwością filtrowania po kategoriach.
    dash_app3 = Dash(
        __name__,
        server=app,
        url_base_pathname='/wizualizacja2/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

# Pobiera unikalne kategorie filmowe z przefiltrowanych danych (bez filmów zagranicznych).
    unique_categories = dash3_data['category'].unique().tolist()


# Układ  aplikacji Dash. Używa komponentów z biblioteki Dash Bootstrap Components (dbc).
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


     # Callback do aktualizacji wykresu, tabeli i tytułu na podstawie wybranych kategorii w checklist.
    @dash_app3.callback(
        [Output('histo-chart-final', 'figure'),
        Output('data-table', 'data'),
        Output('title-container', 'children')],
        Input('category-checklist', 'value')
    )


    def update_graph_and_table(selected_categories):
        # Jeśli żadna kategoria nie jest wybrana, wyświetla 20 aktorów z największą liczbą nagród (wszystkie kategorie).
        if not selected_categories:
            filtered_df = dash3_data[dash3_data['type'] == 'Winner'].groupby('aktor')[['film']].count().sort_values('film',ascending=False).reset_index().head(20)
            title_main = "Zwycięzcy Oscarów (liczba filmów)"
            title_sub = "(Wszystkie Kategorie)"
        else:
          # Jeśli wybrano kategorie, filtruje dane dla zwycięzców w tych kategoriach i wyświetla 20 aktorów z największą liczbą nagród.
            filtered_df = dash3_data[
                (dash3_data['type'] == 'Winner') & (dash3_data['category'].isin(selected_categories))
            ].groupby('aktor')[['film']].count().sort_values('film', ascending=False).reset_index().head(20)
            categories_str = ", ".join(selected_categories)
            title_main = "Zwycięzcy Oscarów (liczba filmów)"
            title_sub = f"(Kategorie: {categories_str})"


        def split_into_lines(text, line_length=105):
         # Funkcja do dzielenia długiego tekstu na wiele linii.
            wrapped_lines = textwrap.wrap(text, width=line_length)
            return "\n".join(wrapped_lines)

          # Zastosowanie funkcji do podtytułu.
        split_title_sub = split_into_lines(title_sub, line_length=105)



        # Tworzy poziomy wykres słupkowy.
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(y=filtered_df['aktor'],
                            x=filtered_df['film'],
                            marker_color=px.colors.qualitative.Set1,
                            name="Liczba Filmów",
                            orientation='h'),
                    row=1, col=1)

        # Aktualizuje układ wykresu.
        fig.update_layout(
            xaxis_title="Liczba Oskarów",
            yaxis_title="Aktor",
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=50),  # Adjust margins
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=600  # Adjusted figure height
        )
       # Tworzy komponent HTML zawierający sformatowany tytuł.
        title_component = html.Div(
            [
                html.Span(title_main, style={'font-size': '24px', 'color': 'red'}),
                html.Br(),
                html.Span(split_title_sub, style={'font-size': '10px', 'color': 'blue'})
            ],
            style={'textAlign': 'center', 'margin-top': '20px'}
        )


         # Zwraca wykres, dane do tabeli i komponent tytułu.
        return fig, filtered_df.to_dict('records'), title_component


  # Wczytuje dane z pliku CSV.
    df = pd.read_csv('CleanData.csv')

    # Filtruje dane dla zwycięzców w określonych kategoriach aktorskich.

    last=df.loc[(df['type']=='Winner')& ( df['category'].isin(['ACTOR IN A LEADING ROLE',\
                                                            'ACTOR IN A SUPPORTING ROLE','ACTRESS',
                                                                'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS','ACTRESS IN A SUPPORTING ROLE']))]
    # Grupuje według aktora i typu nagrody, zliczając wystąpienia.
    lastn=last.groupby(['aktor', 'type']).size().reset_index(name='count')
    # Sortuje według liczby nagród malejąco.
    lastn=lastn.sort_values(by='count', ascending=False)

      # Tworzy listę aktorów, którzy zdobyli więcej niż jedną nagrodę.
    al=lastn[lastn['count']>1]['aktor']

    # Filtruje oryginalny DataFrame, aby zawierał tylko tych aktorów.
    aktorzy=df[df['aktor'].isin(al)]

     # Inicjalizuje pusty DataFrame do przechowywania statystyk lat nagród dla aktorów
    myData = pd.DataFrame()

    # Iteruje po liście aktorów i oblicza statystyki lat ich nagród.
    for i in al:
        akt=pd.DataFrame({i:aktorzy.loc[aktorzy['aktor']==i]['YEAR'].describe()})
        myData=pd.concat([myData, akt], axis=1)

    # Oblicza rozstęp lat (max - min).
    myData.loc['Rozstep']=myData.loc['max']-myData.loc['min']

    # Oblicza średnią lat nagród dla każdego aktora.
    myData['mean']=myData.mean(axis=1)

    # Transponuje DataFrame statystyk.
    finalmyData=myData.T

    # Zmienia nazwę indeksu na 'Aktor'.
    finalmyData = finalmyData.rename(index={'index': 'Aktor'})
    # Zlicza Oskary dla każdego aktora (tylko 'Winner').
    oskar=aktorzy.loc[aktorzy['type']=='Winner'].groupby('aktor')[['film']].count().sort_values('film').reset_index()

    # Łączy DataFrame statystyk z liczbą Oskarów po lewej stronie (zachowując wszystkich aktorów ze statystyk).
    polaczony_df = pd.merge(finalmyData, oskar, left_index=True, right_on='aktor', how='left').rename(columns={'film': 'Ilosc Oskarow'})

     # Wybiera i porządkuje kolumny w ostatecznym DataFrame.
    polaczony_df[['aktor', 'Ilosc Oskarow','count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'Rozstep']]

    # Ustawia kolumnę 'aktor' jako indeks.
    polaczony_df = polaczony_df.set_index('aktor')


   # Tworzy  aplikację Dash do wyświetlania statystyk aktorów.
    dash_app4 = Dash(
        __name__,
        server=app,
        url_base_pathname='/stats/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )



       # Układ czwartej aplikacji Dash (statystyki aktorów).


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


     # Callback do aktualizacji wykresu i tabeli w czwartej aplikacji Dash na podstawie wybranej kolumny.
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




    # Mapa URL-i do serwerów aplikacji Dash.
    url_map = {
        '/wizualizacja': dash_app2.server,
        '/wizualizacja2': dash_app3.server,
        '/stats': dash_app4.server,
    }

    # Jeśli baza danych istniała na starcie, dodaje do mapy URL-i aplikację do przeglądania bazy danych.
    if db_exists_on_start:
        url_map['/baza_danych'] = dash_app.server
    else:
        print("Warning: dash_app not initialized, '/baza_danych' route not mounted.")


     # Tworzy aplikację nadrzędną, która będzie rozsyłać żądania do odpowiednich aplikacji (Flask i Dash).
    mounted_app = DispatcherMiddleware(app.wsgi_app, url_map)


# Funkcja do uruchamiania serwera Flask z integracją Socket.IO.
def uruchom_serwer(app, debug_mode=True):
    socketio.run(app, debug=debug_mode)


# Główny blok uruchamiający serwer, jeśli skrypt jest uruchamiany bezpośrednio.
if __name__ == '__main__':
    uruchom_serwer(app, debug_mode=True)
