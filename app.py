from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import sqlite3
from werkzeug.middleware.dispatcher import DispatcherMiddleware

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


@socketio.on('uruchom_Chart')
def handle_uruchom_Chart():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('chart.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread







@app.route('/')
def index():
    return render_template('index.html')

@app.route('/baza_danych')
def baza_danych_page():
    dash_url = '/baza_danych/'  # Ensure this matches the `url_base_pathname` of your Dash app
    return render_template('bazadanych.html', dash_url=dash_url)

@app.route('/wizualizacja')
def wizualizacja_page():
    dash_url = '/wizualizacja/'
    image_path = os.path.join(app.static_folder, 'charts', 'analizaAktorow.png')
    image_exists = os.path.exists(image_path)
    return render_template('wizualizacja.html', dash_url=dash_url,image_exists=image_exists)



@app.route('/info')
def info_page():
    return render_template('info.html')



@app.route('/dok')
def dokumentacja_page():
    return render_template('dokumentacja.html')









# DASH APP EMBEDDING FOR /baza_danych
DATABASE_PATH = r"DbOksary.db"

def fetch_data():
    """Fetches data based on the specific SQL query."""
    conn = sqlite3.connect(DATABASE_PATH)
    query = """SELECT tn.nazwa_typu AS Type, a.imie_nazwisko AS Actor, n.rok AS Year, n.film AS Film
               FROM nagrody n
               JOIN kategorie k ON k.id_kategorii = n.id_kategorii
               JOIN typy_nagrod tn ON tn.id_typu = n.id_typu
               JOIN aktorzy a ON a.id_aktora = n.id_aktora"""
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

initial_data = fetch_data()

dash_app = Dash(__name__, server=app, url_base_pathname='/baza_danych/')

dash_app.layout = html.Div([
    html.Div(children='My App with Filters for All Columns', style={'textAlign': 'center', 'color': 'blue', 'fontSize': 20}),

    html.Div(className='row', children=[
        html.Label("Filter by Type:"),
        dcc.Input(id='type-input', type='text', placeholder='Enter Type', value=None, style={'margin': '10px'}),
        html.Label("Filter by Actor:"),
        dcc.Input(id='actor-input', type='text', placeholder='Enter Actor', value=None, style={'margin': '10px'}),
        html.Label("Filter by Year:"),
        dcc.Input(id='year-input', type='number', placeholder='Enter Year', value=None, style={'margin': '10px'}),
        html.Label("Filter by Film:"),
        dcc.Input(id='film-input', type='text', placeholder='Enter Film', value=None, style={'margin': '10px'}),
    ]),

    dash_table.DataTable(
        id='data-table-baza',  # Changed ID to be unique
        columns=[{"name": i, "id": i} for i in initial_data.columns],
        data=initial_data.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])

@dash_app.callback(
    Output('data-table-baza', 'data'),  # Updated Output ID
    [Input('type-input', 'value'),
     Input('actor-input', 'value'),
     Input('year-input', 'value'),
     Input('film-input', 'value')]
)
def update_table_baza_danych(type_value, actor_value, year_value, film_value):
    filtered_data = initial_data
    if type_value:
        filtered_data = filtered_data[filtered_data['Type'].str.contains(type_value, case=False, na=False)]
    if actor_value:
        filtered_data = filtered_data[filtered_data['Actor'].str.contains(actor_value, case=False, na=False)]
    if year_value:
        filtered_data = filtered_data[filtered_data['Year'] == year_value]
    if film_value:
        filtered_data = filtered_data[filtered_data['Film'].str.contains(film_value, case=False, na=False)]

    return filtered_data.to_dict('records')




df = pd.read_csv('CleanData.csv')

# Filter data to include only specific categories
filtered_df = df.loc[df['category'].isin(['ACTOR IN A LEADING ROLE', 'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS'])]

# Group and count occurrences for each actor and type
grouped_df = filtered_df.groupby(['aktor', 'type']).size().reset_index(name='count')

# Sort the grouped data
sorted_df = grouped_df.sort_values(by=['aktor', 'type', 'count'], ascending=[True, False, False])

# Filter data for winners only
winners_df = sorted_df[sorted_df['type'] == 'Winner'].sort_values(by='count', ascending=False)




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app2 = Dash(
    __name__,
    server=app,
    url_base_pathname='/wizualizacja/',
    external_stylesheets=external_stylesheets
)



# App layout
dash_app2.layout = html.Div([
    html.Div(className='row', children='My First App with Data, Graph, and Controls',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),

    html.Div(className='row', children=[
        dcc.RadioItems(options=['count'],
                       value='count',
                       inline=True,
                       id='my-radio-buttons-final')
    ]),

    html.Div(className='row', children=[
        dcc.Slider(
            id='count-slider',
            min=0,
            max=winners_df['count'].max(),
            step=1,
            value=0,
            marks={i: str(i) for i in range(0, winners_df['count'].max() + 1, 5)},
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
    filtered_df = winners_df[winners_df['count'] >= min_count]

    # Create the bar chart with filtered data
    fig = px.bar(filtered_df, x='aktor', y=col_chosen, color='aktor', title=f'Filtered Data by {col_chosen}')

    # Return both the figure and the filtered DataFrame's data for the DataTable
    return fig, filtered_df.to_dict('records')




mounted_app = DispatcherMiddleware(app.wsgi_app, {
    '/wizualizacja': dash_app2.server,
    '/baza_danych': dash_app.server

})






if __name__ == '__main__':
    socketio.run(app, debug=True)