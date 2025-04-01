from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os

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
    return render_template('wizualizacja.html')


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
def handle_uruchom_Check_Data():
    session_id = request.sid
    if session_id not in active_threads:  # Uruchom skrypt tylko raz dla sesji
        thread = threading.Thread(target=run_script_once, args=('CzyszczenieDanych.py', [], session_id))
        thread.start()
        active_threads[session_id] = thread



if __name__ == '__main__':
    socketio.run(app, debug=True)
