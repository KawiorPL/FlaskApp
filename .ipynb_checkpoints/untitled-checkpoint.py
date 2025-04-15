import sqlite3
import pandas as pd
import os
import pytest

# Załóżmy, że masz funkcję create_database zdefiniowaną w osobnym module, np. 'database.py'
# from database import create_database  # Odkomentuj, jeśli masz taką strukturę

# Ścieżka do pliku bazy danych (możesz chcieć to przenieść do konfiguracji testów)
DB_FILE = 'DbOksary.db'

csv_file = 'CleanData.csv'


# Funkcja pomocnicza do wczytywania danych z CSV (dostosuj ścieżkę)
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


# Przykładowe testy (do dostosowania)
class TestDataConsistency:
    """Klasa zawierająca testy sprawdzające spójność danych."""
    @classmethod
    def setup_class(cls):
        """Uruchamiana raz przed wszystkimi testami w klasie. Tworzy testową bazę danych."""
        create_test_database()  # Użyj funkcji tworzącej baze danych
        # Wczytaj dane z CSV do DataFrame, np.
        cls.csv_data = read_csv_data("nagrody.csv") # Podmień na swoj plik csv
        if cls.csv_data is None:
            pytest.skip("Nie można kontynuować testów bez danych z pliku CSV.")

    @classmethod
    def teardown_class(cls):
        """Uruchamiana raz po wszystkich testach w klasie.  Opcjonalnie usuwa testową bazę."""
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            print(f"Usunięto testową bazę danych: {DB_FILE}")

    def test_kategorie(self):
        """Test porównujący kategorie z CSV i bazy danych."""
        # 1. Załaduj dane do bazy danych
        # Tutaj umieść kod, który ładuje dane z self.csv_data do bazy danych
        #   - Będziesz musiał przetworzyć self.csv_data i użyć instrukcji INSERT
        #   - Pamiętaj o obsłudze zależności (kategorie, aktorzy, typy_nagrod)
        #   - Możesz użyć funkcji pomocniczych do wstawiania danych

        # 2. Pobierz dane z bazy danych
        query = "SELECT nazwa_kategorii FROM kategorie"
        db_kategorie_df = get_data_from_db(DB_FILE, query)

        # 3. Pobierz unikalne kategorie z CSV (zakładam, że masz taką kolumnę)
        csv_kategorie = self.csv_data['category'].unique() # Dostosuj nazwe kolumny

        # 4. Porównaj dane
        assert db_kategorie_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_kategorie) == len(db_kategorie_df), "Liczba kategorii w CSV i DB jest różna"
        assert all(kategoria in db_kategorie_df['nazwa_kategorii'].values for kategoria in csv_kategorie), "Kategorie w CSV i DB się nie zgadzają"
    
    def test_aktorzy(self):
        """Test porownujacy aktorow"""
        query = "SELECT imie_nazwisko FROM aktorzy"
        db_aktorzy_df = get_data_from_db(DB_FILE, query)
        csv_aktorzy = self.csv_data['aktor'].unique()
        
        assert db_aktorzy_df is not None
        assert len(csv_aktorzy) == len(db_aktorzy_df)
        assert all(aktor in db_aktorzy_df['imie_nazwisko'].values for aktor in csv_aktorzy)

    def test_filmy(self):
        """Test porownujacy filmy"""
        query = "SELECT film FROM nagrody"
        db_filmy_df = get_data_from_db(DB_FILE, query)
        csv_filmy = self.csv_data['film'].unique()
        
        assert db_filmy_df is not None
        assert len(csv_filmy) == len(db_filmy_df)
        assert all(film in db_filmy_df['film'].values for film in csv_filmy)

    def test_typy_nagrod(self):
        """Test porownujacy typy nagrod"""
        query = "SELECT nazwa_typu FROM typy_nagrod"
        db_typy_nagrod_df = get_data_from_db(DB_FILE, query)
        csv_typy_nagrod = self.csv_data['type'].unique()
        
        assert db_typy_nagrod_df is not None
        assert len(csv_typy_nagrod) == len(db_typy_nagrod_df)
        assert all(typ in db_typy_nagrod_df['nazwa_typu'].values for typ in csv_typy_nagrod)

    def test_nagrody_rok(self):
        """Test porównujący lata nagród."""
        query = "SELECT rok FROM nagrody ORDER BY rok"
        db_lata_df = get_data_from_db(DB_FILE, query)
        csv_lata = self.csv_data['YEAR'].sort_values().unique() # Dostosuj nazwe kolumny

        assert db_lata_df is not None
        assert len(csv_lata) == len(db_lata_df)
        assert all(rok in db_lata_df['rok'].values for rok in csv_lata)
