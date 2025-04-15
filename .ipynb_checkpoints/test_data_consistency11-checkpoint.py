import sqlite3
import pandas as pd
import re
import numpy as np

# Ścieżka do pliku bazy danych
DB_FILE = 'DbOksary.db'
csv_file = 'CleanData.csv'

# Funkcja pomocnicza do pobierania danych z bazy danych
def get_data_from_db(db_file, query):
    """Pobiera dane z bazy danych SQLite i zwraca je jako DataFrame."""
    try:
        conn = sqlite3.connect(db_file)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.Error as e:
        print(f"Błąd podczas pobierania danych z bazy danych: {e}")
        return None


# Funkcja pomocnicza do wczytywania danych z CSV
def read_csv_data(csv_file):
    """Wczytuje dane z pliku CSV do DataFrame."""
    try:
        df = pd.read_csv(csv_file)
        return df
    except FileNotFoundError:
        print(f"Nie znaleziono pliku CSV: {csv_file}")
        return None
    except Exception as e:
        print(f"Błąd podczas odczytu pliku CSV: {e}")
        return None


# Wczytaj dane
csv_data = read_csv_data(csv_file)
if csv_data is None:
    print("Nie można kontynuować bez danych z pliku CSV.")
    exit()
csv_data.dropna(subset=["aktor"], inplace=True)  # Usuń wiersze, gdzie aktor ma wartość NaN.

# Pobierz dane z bazy danych
query = "SELECT DISTINCT film FROM nagrody"
db_filmy_df = get_data_from_db(DB_FILE, query)

# Przetwórz dane z CSV
csv_filmy = csv_data["film"].unique()
csv_filmy = [str(film).strip().lower() for film in csv_filmy if pd.notna(film)]

# Przetwórz dane z bazy danych
db_filmy = [str(film).strip().lower() for film in db_filmy_df['film'].values if pd.notna(film)]

# Wypisz dane do porównania
print("Filmy z CSV:")
print(csv_filmy)
print(f"Liczba filmów w CSV: {len(csv_filmy)}")

print("\nFilmy z DB:")
print(db_filmy)
print(f"Liczba filmów w DB: {len(db_filmy)}")

# Znajdź różnice
diff_filmy_csv_db = set(csv_filmy) - set(db_filmy)
diff_filmy_db_csv = set(db_filmy) - set(csv_filmy)

# Wypisz różnice
print("\nFilmy w CSV, których nie ma w DB:")
if diff_filmy_csv_db:
    print(diff_filmy_csv_db)
else:
    print("Brak różnic")

print("\nFilmy w DB, których nie ma w CSV:")
if diff_filmy_db_csv:
    print(diff_filmy_db_csv)
else:
    print("Brak różnic")
