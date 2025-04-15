import sqlite3
import pandas as pd
import pytest

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


class TestDataConsistency:
    """Klasa zawierająca testy sprawdzające spójność danych."""

    @classmethod
    def setup_class(cls):
        """Uruchamiana raz przed wszystkimi testami w klasie. Wczytuje dane z CSV."""
        cls.csv_data = read_csv_data(
            "CleanData.csv"
        )  # Ścieżka do pliku CSV
        if cls.csv_data is None:
            pytest.skip("Nie można kontynuować testów bez danych z pliku CSV.")
        # Usuń wiersze, gdzie aktor ma wartość NaN.
        cls.csv_data.dropna(subset=["aktor"], inplace=True)

    @classmethod
    def teardown_class(cls):
        pass  # Nie robimy nic, nie usuwamy bazy danych

    def test_kategorie(self):
        """Test porównujący kategorie z CSV i bazy danych."""
        query = "SELECT nazwa_kategorii FROM kategorie"
        db_kategorie_df = get_data_from_db(DB_FILE, query)
        csv_kategorie = self.csv_data['category'].unique()
    
        assert db_kategorie_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_kategorie) == len(db_kategorie_df), "Liczba kategorii w CSV i DB jest różna"
        assert all(kategoria in db_kategorie_df['nazwa_kategorii'].values for kategoria in csv_kategorie), "Kategorie w CSV i DB się nie zgadzają"


    def test_aktorzy(self):
        """Test porównujący aktorów z CSV i bazy danych."""
        query = "SELECT imie_nazwisko FROM aktorzy WHERE imie_nazwisko != 'nan'"
        db_aktorzy_df = get_data_from_db(DB_FILE, query)
        csv_aktorzy = self.csv_data["aktor"].unique()
        db_aktorzy = set(db_aktorzy_df['imie_nazwisko'].values)
        csv_aktorzy_set = set(csv_aktorzy)
    
        print(f"Liczba aktorów w CSV: {len(csv_aktorzy_set)}")
        print(f"Liczba aktorów w DB: {len(db_aktorzy)}")
    
        assert db_aktorzy_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_aktorzy_set) == len(db_aktorzy), "Liczba aktorów w CSV i DB jest różna"
    
        roznicujacy_aktorzy = csv_aktorzy_set - db_aktorzy
        if roznicujacy_aktorzy:
            print("Aktorzy z CSV, których nie ma w DB:")
            print(roznicujacy_aktorzy)
            assert False, "Aktorzy w CSV i DB się nie zgadzają"
        else:
            print("Wszyscy aktorzy z CSV są w DB")

    def test_filmy(self):
        """Test porównujący filmy z CSV i bazy danych."""
        query = "SELECT film FROM nagrody"
        db_filmy_df = get_data_from_db(DB_FILE, query)
        csv_filmy = cls.csv_data["film"].unique()

        assert db_filmy_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_filmy) == len(
            db_filmy_df
        ), "Liczba filmów w CSV i DB jest różna"
        assert all(
            film in db_filmy_df["film"].values for film in csv_filmy
        ), "Filmy w CSV i DB się nie zgadzają"

    def test_typy_nagrod(self):
        """Test porównujący typy nagród z CSV i bazy danych."""
        query = "SELECT nazwa_typu FROM typy_nagrod"
        db_typy_nagrod_df = get_data_from_db(DB_FILE, query)
        csv_typy_nagrod = cls.csv_data["type"].unique()

        assert db_typy_nagrod_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_typy_nagrod) == len(
            db_typy_nagrod_df
        ), "Liczba typów nagród w CSV i DB jest różna"
        assert all(
            typ in db_typy_nagrod_df["nazwa_typu"].values for typ in csv_typy_nagrod
        ), "Typy nagród w CSV i DB się nie zgadzają"

    def test_nagrody_rok(self):
        """Test porównujący lata nagród z CSV i bazy danych."""
        query = "SELECT rok FROM nagrody ORDER BY rok"
        db_lata_df = get_data_from_db(DB_FILE, query)
        csv_lata = cls.csv_data["YEAR"].sort_values().unique()

        assert db_lata_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_lata) == len(
            db_lata_df
        ), "Liczba lat w CSV i DB jest różna"
        assert all(
            rok in db_lata_df["rok"].values for rok in csv_lata
        ), "Lata w CSV i DB się nie zgadzają"
