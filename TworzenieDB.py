import sqlite3
import csv

# Nazwy plików i tabel
csv_file = 'dane_startowe.csv'
db_file = 'dwie_tabele.db'
produkty_table = 'produkty'
kategorie_table = 'kategorie'

# Połączenie z bazą danych
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    # Utworzenie tabeli 'kategorie'
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {kategorie_table} (
            id_kategorii INTEGER PRIMARY KEY AUTOINCREMENT,
            nazwa_kategorii TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()

    # Utworzenie tabeli 'produkty' z kluczem obcym do 'kategorie'
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {produkty_table} (
            id_produktu INTEGER PRIMARY KEY,
            nazwa_produktu TEXT NOT NULL,
            id_kategorii INTEGER,
            wartosc REAL NOT NULL,
            FOREIGN KEY (id_kategorii) REFERENCES {kategorie_table}(id_kategorii)
        )
    ''')
    conn.commit()

    # Wczytanie kategorii z CSV i wstawienie do tabeli 'kategorie'
    kategorie = set()
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        nazwa_kategorii_index = header.index('nazwa_kategorii')
        for row in csv_reader:
            kategorie.add(row[nazwa_kategorii_index])

    kategorie_map = {}
    for kategoria in kategorie:
        cursor.execute(f'''
            INSERT OR IGNORE INTO {kategorie_table} (nazwa_kategorii)
            VALUES (?)
        ''', (kategoria,))
    conn.commit()

    # Pobranie mapowania nazw kategorii na ich ID
    cursor.execute(f'''
        SELECT nazwa_kategorii, id_kategorii FROM {kategorie_table}
    ''')
    kategorie_map = {row[0]: row[1] for row in cursor.fetchall()}

    # Wstawienie produktów do tabeli 'produkty' z odpowiednimi ID kategorii
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        id_produktu_index = header.index('id_produktu')
        nazwa_produktu_index = header.index('nazwa_produktu')
        nazwa_kategorii_index = header.index('nazwa_kategorii')
        wartosc_index = header.index('wartosc')

        for row in csv_reader:
            id_produktu = row[id_produktu_index]
            nazwa_produktu = row[nazwa_produktu_index]
            nazwa_kategorii = row[nazwa_kategorii_index]
            wartosc = row[wartosc_index]
            id_kategorii = kategorie_map.get(nazwa_kategorii)
            if id_kategorii is not None:
                cursor.execute(f'''
                    INSERT INTO {produkty_table} (id_produktu, nazwa_produktu, id_kategorii, wartosc)
                    VALUES (?, ?, ?, ?)
                ''', (id_produktu, nazwa_produktu, id_kategorii, wartosc))
        conn.commit()

    print(f"Baza danych '{db_file}' została utworzona z tabelami '{produkty_table}' i '{kategorie_table}' połączonymi kluczem obcym.")

except sqlite3.Error as e:
    print(f"Błąd SQLite: {e}")
except FileNotFoundError:
    print(f"Nie znaleziono pliku CSV: '{csv_file}'")
except ValueError as e:
    print(f"Błąd wartości CSV: {e}")
finally:
    if conn:
        conn.close()