import sqlite3
import pandas as pd
import pytest
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


class TestDataConsistency:
    """Klasa zawierająca testy sprawdzające spójność danych."""

    @classmethod
    def setup_class(cls):
        """Uruchamiana raz przed wszystkimi testami w klasie. Wczytuje dane z CSV."""
        cls.csv_data = read_csv_data("CleanData.csv")  # Ścieżka do pliku CSV
        if cls.csv_data is None:
            pytest.skip("Nie można kontynuować testów bez danych z pliku CSV.")
        # Usuń wiersze, gdzie aktor ma wartość NaN.
        cls.csv_data.dropna(subset=["aktor"], inplace=True)

    @classmethod
    def teardown_class(cls):
        pass  # Nie robimy nic, nie usuwamy bazy danych

    def test_kategorie(self):
        """Test porównujący kategorie z CSV i bazy danych."""
        query = "SELECT DISTINCT nazwa_kategorii FROM kategorie"  # Dodano DISTINCT
        db_kategorie_df = get_data_from_db(DB_FILE, query)
        csv_kategorie = self.csv_data["category"].unique()
        # Filtrowanie NaNów i pustych stringów.
        csv_kategorie = [
            kategoria for kategoria in csv_kategorie if not (pd.isna(kategoria) or kategoria == "")
        ]
        db_kategorie_df['nazwa_kategorii'] = db_kategorie_df['nazwa_kategorii'].astype(str)
        db_kategorie = [
            kategoria for kategoria in db_kategorie_df['nazwa_kategorii'].values if not (pd.isna(kategoria) or kategoria == "")
        ]

        assert db_kategorie_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_kategorie) == len(
            db_kategorie
        ), "Liczba kategorii w CSV i DB jest różna"
        assert all(
            kategoria in db_kategorie for kategoria in csv_kategorie
        ), "Kategorie w CSV i DB się nie zgadzają"

    def test_aktorzy(self):
        """Test porównujący aktorów z CSV i bazy danych."""
        query = "SELECT DISTINCT imie_nazwisko FROM aktorzy WHERE imie_nazwisko != 'nan'"  # Dodano DISTINCT i warunek
        db_aktorzy_df = get_data_from_db(DB_FILE, query)
        csv_aktorzy = self.csv_data["aktor"].unique()

        # Filtrowanie NaNów i pustych stringów.
        csv_aktorzy = [
            aktor for aktor in csv_aktorzy if not (pd.isna(aktor) or aktor == "")
        ]

        db_aktorzy_df['imie_nazwisko'] = db_aktorzy_df['imie_nazwisko'].astype(str)
        db_aktorzy = [
            aktor for aktor in db_aktorzy_df['imie_nazwisko'].values if not (pd.isna(aktor) or aktor == "")
        ]
        csv_aktorzy_set = set(csv_aktorzy)
        db_aktorzy_set = set(db_aktorzy)

        print(f"Liczba aktorów w CSV: {len(csv_aktorzy_set)}")
        print(f"Liczba aktorów w DB: {len(db_aktorzy_set)}")

        assert db_aktorzy_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_aktorzy_set) == len(
            db_aktorzy_set
        ), "Liczba aktorów w CSV i DB jest różna"

        roznicujacy_aktorzy = csv_aktorzy_set - db_aktorzy_set
        if roznicujacy_aktorzy:
            print("Aktorzy z CSV, których nie ma w DB:")
            print(roznicujacy_aktorzy)
            assert False, "Aktorzy w CSV i DB się nie zgadzają"
        else:
            print("Wszyscy aktorzy z CSV są w DB")

    def test_filmy(self):
        """Test porównujący filmy z CSV i bazy danych."""
        query = "SELECT DISTINCT film FROM nagrody"  # Dodano DISTINCT
        db_filmy_df = get_data_from_db(DB_FILE, query)
        csv_filmy = self.csv_data["film"].unique()

        # Filtrowanie NaNów i pustych stringów.
        csv_filmy = [film for film in csv_filmy if not (pd.isna(film) or film == "")]
        db_filmy_df['film'] = db_filmy_df['film'].astype(str)
        db_filmy = [film for film in db_filmy_df['film'].values if not (pd.isna(film) or film == "")]

        assert db_filmy_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_filmy) == len(db_filmy), "Liczba filmów w CSV i DB jest różna"
        assert all(film in db_filmy for film in csv_filmy), "Filmy w CSV i DB się nie zgadzają"

    def test_typy_nagrod(self):
        """Test porównujący typy nagród z CSV i bazy danych."""
        query = "SELECT DISTINCT nazwa_typu FROM typy_nagrod"  # Dodano DISTINCT
        db_typy_nagrod_df = get_data_from_db(DB_FILE, query)
        csv_typy_nagrod = self.csv_data["type"].unique()

        # Filtrowanie NaNów i pustych stringów.
        csv_typy_nagrod = [
            typ for typ in csv_typy_nagrod if not (pd.isna(typ) or typ == "")
        ]
        db_typy_nagrod_df['nazwa_typu'] = db_typy_nagrod_df['nazwa_typu'].astype(str)
        db_typy_nagrod = [
            typ for typ in db_typy_nagrod_df['nazwa_typu'].values if not (pd.isna(typ) or typ == "")
        ]

        assert db_typy_nagrod_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_typy_nagrod) == len(
            db_typy_nagrod
        ), "Liczba typów nagród w CSV i DB jest różna"
        assert all(
            typ in db_typy_nagrod for typ in csv_typy_nagrod
        ), "Typy nagród w CSV i DB się nie zgadzają"

    def test_nagrody_rok(self):
        """Test porównujący lata nagród z CSV i bazy danych."""
        query = "SELECT DISTINCT rok FROM nagrody ORDER BY rok"  # Dodano DISTINCT
        db_lata_df = get_data_from_db(DB_FILE, query)
        csv_lata = self.csv_data["YEAR"].sort_values().unique()

        # Filtrowanie NaNów i pustych stringów.
        csv_lata = [rok for rok in csv_lata if not (pd.isna(rok) or rok == "") ]

        db_lata_df['rok'] = db_lata_df['rok'].astype(str)
        db_lata = [rok for rok in db_lata_df['rok'].values if not (pd.isna(rok) or rok == "")]

        assert db_lata_df is not None, "Nie udało się pobrać danych z bazy danych"
        assert len(csv_lata) == len(db_lata), "Liczba lat w CSV i DB jest różna"
        assert all(rok in db_lata for rok in csv_lata), "Lata w CSV i DB się nie zgadzają"