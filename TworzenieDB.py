import csv
import sqlite3
import os
import time

from socketio import Client

csv_file = 'CleanData.csv'
db_file = 'DbOksary.db'

def create_database(db_file):
    """Tworzy bazę danych SQLite i tabele, usuwając istniejącą bazę."""
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Usunięto istniejącą bazę danych: {db_file}")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()


    # Tabela kategorie
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategorie (
            id_kategorii INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa_kategorii TEXT UNIQUE NOT NULL
        )
    """)

    # Tabela aktorzy
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aktorzy (
            id_aktora INTEGER PRIMARY KEY AUTOINCREMENT,
            imie_nazwisko TEXT UNIQUE NOT NULL
        )
    """)

    # Tabela typy_nagrod
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS typy_nagrod (
            id_typu INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa_typu TEXT UNIQUE NOT NULL
        )
    """)

    # Tabela nagrody
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nagrody (
            id_nagrody INTEGER PRIMARY KEY AUTOINCREMENT,
            rok INTEGER NOT NULL,
            id_kategorii INTEGER NOT NULL,
            id_aktora INTEGER NOT NULL,
            film TEXT NOT NULL,
            id_typu INTEGER NOT NULL,
            FOREIGN KEY (id_kategorii) REFERENCES kategorie(id_kategorii),
            FOREIGN KEY (id_aktora) REFERENCES aktorzy(id_aktora),
            FOREIGN KEY (id_typu) REFERENCES typy_nagrod(id_typu)
        )
    """)

    conn.commit()
    conn.close()

def populate_database(db_file, csv_file):
    """Wczytuje dane z pliku CSV i wypełnia bazę danych."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            rok = int(row['YEAR'])
            kategoria = row['category']
            aktor = row['aktor']
            film = row['film'].strip('"') # Usuwamy cudzysłowy z nazwy filmu
            typ = row['type']

            # Pobierz lub dodaj kategorię
            cursor.execute("SELECT id_kategorii FROM kategorie WHERE nazwa_kategorii=?", (kategoria,))
            kategoria_result = cursor.fetchone()
            if kategoria_result:
                id_kategorii = kategoria_result[0]
            else:
                cursor.execute("INSERT INTO kategorie (nazwa_kategorii) VALUES (?)", (kategoria,))
                id_kategorii = cursor.lastrowid

            # Pobierz lub dodaj aktora
            cursor.execute("SELECT id_aktora FROM aktorzy WHERE imie_nazwisko=?", (aktor,))
            aktor_result = cursor.fetchone()
            if aktor_result:
                id_aktora = aktor_result[0]
            else:
                cursor.execute("INSERT INTO aktorzy (imie_nazwisko) VALUES (?)", (aktor,))
                id_aktora = cursor.lastrowid

            # Pobierz lub dodaj typ nagrody
            cursor.execute("SELECT id_typu FROM typy_nagrod WHERE nazwa_typu=?", (typ,))
            typ_result = cursor.fetchone()
            if typ_result:
                id_typu = typ_result[0]
            else:
                cursor.execute("INSERT INTO typy_nagrod (nazwa_typu) VALUES (?)", (typ,))
                id_typu = cursor.lastrowid

            # Dodaj rekord do tabeli nagrody
            cursor.execute("""
                INSERT INTO nagrody (rok, id_kategorii, id_aktora, film, id_typu)
                VALUES (?, ?, ?, ?, ?)
            """, (rok, id_kategorii, id_aktora, film, id_typu))

        conn.commit()
    conn.close()

def notify_db_created():
    sio = Client()
    try:
        sio.connect('http://localhost:5000')  # Zmień adres, jeśli Twój serwer działa na innym porcie
        sio.emit('db_created')
        sio.disconnect()
        print("Wysłano powiadomienie o utworzeniu bazy danych.")
    except Exception as e:
        print(f"Błąd podczas łączenia z SocketIO: {e}")


if __name__ == "__main__":
    create_database(db_file)
    populate_database(db_file, csv_file)
    print(f"Baza danych '{db_file}' została utworzona i wypełniona danymi z '{csv_file}'.")
