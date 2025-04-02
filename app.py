from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
from dash import Dash, html, dash_table, dcc
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/baza_danych')
def baza_danych_page():
    return render_template('bazadanych.html')

@app.route('/wizualizacja')
def wizualizacja_page():
    dash_url = '/wizualizacja/'  # Ensure this matches the `url_base_pathname` of your Dash app
    return render_template('wizualizacja.html', dash_url=dash_url)

# DASH APP EMBEDDING
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

dash_app = Dash(__name__, server=app, url_base_pathname='/wizualizacja/')

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
        id='data-table',
        columns=[{"name": i, "id": i} for i in initial_data.columns],
        data=initial_data.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])

@dash_app.callback(
    Output('data-table', 'data'),
    [Input('type-input', 'value'),
     Input('actor-input', 'value'),
     Input('year-input', 'value'),
     Input('film-input', 'value')]
)
def update_table(type_value, actor_value, year_value, film_value):
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


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('uruchom_Check_Data')
def handle_uruchom_Check_Data():
    session_id = request.sid
    if session_id not in active_threads:
        thread = threading.Thread(target=run_script_once, args=('Check-Data.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

@socketio.on('zbieraj_Dane')
def handle_zbieraj_Dane(data):
    url = data.get('url')
    session_id = request.sid
    if url:
        if session_id not in active_threads:
            thread = threading.Thread(target=run_script_once, args=('ZbieranieDanych.py', [url], session_id))
            thread.start()
            active_threads[session_id] = thread
    else:
        emit('script_error', {'error': "Nie podano URL-a."}, room=session_id)

@socketio.on('uruchom_czyszczenie_Data')
def handle_uruchom_Check_Data():
    session_id = request.sid
    if session_id not in active_threads:
        thread = threading.Thread(target=run_script_once, args=('CzyszczenieDanych.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

@socketio.on('uruchom_Tworzenie_DB')
def handle_uruchom_Tworzenie_DB():
    session_id = request.sid
    if session_id not in active_threads:
        thread = threading.Thread(target=run_script_once, args=('TworzenieDB.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread

if __name__ == '__main__':
    socketio.run(app, debug=True)
