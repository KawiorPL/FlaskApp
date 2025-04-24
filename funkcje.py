import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from difflib import SequenceMatcher
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests, json, re, folium, sys, os
from folium.features import DivIcon
import sqlite3
import pandas as pd
import pytest
import re


# Główny adres URL, z którego będą pobierane dane.
main = "https://oscar.warpechow.ski/"
# Nazwę folderu, w którym zostaną zapisane dane
folder='pliki'


# Pobiera dane ze wskazanego adresu URL, zapisuje je do pliku tekstowego.
def Sonda(main,folder):

    respone = requests.get(main)
    dane = respone.text
    f = open(f"{folder}/linki.txt", "w")
    f.write(dane)
    f.close()

    return 1


#Tworzenie dataframe z Linkami i latami
def DatFrameYearLink(html_file_path):
    #otwieraniue pliku z danymi.
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        #tresc strony
        soup = BeautifulSoup(html_content, 'html.parser')

        #zbieranie danych year i linki
        data = []
        for year_card in soup.find_all('div', class_='year-card'):
            year = year_card.get('data-year')
            link = year_card.find('a').get('href') if year_card.find('a') else None  # Handle missing <a>
            data.append({'year': year, 'link': link})

        #tworzenie DataFrame z danymi.
        df = pd.DataFrame(data)
        return df

    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {html_file_path}")
        return None
    except Exception as e:
        print(f"Wystąpil bład: {e}")
        return None






def znajdz_roznice(lista1, lista2):
    """
    Znajduje elementy z listy1, które nie występują w liście2.

    Args:
        lista1 (list): Pierwsza lista.
        lista2 (list): Druga lista.

    Returns:
        list: Lista elementów z listy1, które nie występują w liście2.
    """
    lista3 = []
    for element in lista1:
        if element not in lista2:
            lista3.append(element)
    return lista3




def extract_winner(html_file_path, year):
    """
    Ekstrahuje informacje o zwycięzcach z pliku HTML zawierającego dane z ceremonii Oscarów.

    Args:
        html_file_path (str): Ścieżka do pliku HTML do przetworzenia.
        year (int): Rok ceremonii Oscarów, który zostanie dodany do danych.

    Returns:
        pd.DataFrame: DataFrame zawierający informacje o zwycięzcach (rok, kategoria, aktor, film, typ).
                       Zwraca pusty DataFrame w przypadku braku zwycięzców.
    """

    with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()


    soup = BeautifulSoup(html_content, 'html.parser')

    other=[] # Lista do przechowywania zwycięzców w kategoriach specjalnych.
    cat=[]  # Lista do przechowywania nazw kategorii specjalnych.

     # Lista kategorii nagród specjalnych, które wymagają innego sposobu parsowania.
    listaHo=['HONORARY AWARD', 'SPECIAL AWARD', 'SPECIAL FOREIGN LANGUAGE FILM AWARD', 'AWARD OF COMMENDATION', 'IRVING G. THALBERG MEMORIAL AWARD']
    winners = []  # Główna lista do przechowywania informacji o wszystkich zwycięzcach.

     # Znajdź wszystkie sekcje kategorii na stronie.
    for category_section in soup.find_all('div', class_='category-section'):
        category = category_section.find('h2').text.strip()

            # Jeśli kategoria znajduje się na liście nagród specjalnych.
        if category in listaHo:
            for nominee_element in category_section.find_all('div', class_='winner'):
                nominee_paragraph = nominee_element.find('p')

                # Jeśli paragraf został znaleziony.
                if nominee_paragraph:
                    nominee = nominee_paragraph.text.strip()
                    other.append(nominee)
                    cat.append(category)

              # Przetwarzaj listy 'other' i 'cat', aby wyodrębnić aktora i film (jeśli istnieją).
            for y,category in zip(other,cat):

                try:
                    parts = y.split(' - ')
                    if len(parts) >= 2:
                        aktor = parts[0].strip()
                        film = ' - '.join(parts[1:]).strip()

                    elif len(parts) == 2:
                        aktor = parts[0].strip()
                        film = parts[1].strip()

                    else:
                        aktor = parts[0].strip()
                        film = np.nan

                except ValueError:
                            aktor = y
                            film = np.nan

                winners.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film': film, 'type': 'Winner'})




        else:

            # Przetwarzanie zwycięzcy (zakładam, że jest tylko jeden element z klasą 'winner' w sekcji)
            winner_element = category_section.find('div', class_='winner')

            if winner_element:
                winner_paragraph = winner_element.find('p')

                if winner_paragraph:
                    winner = winner_paragraph.text.strip()


                    try:
                        aktor, film = winner.split(' - ')
                    except ValueError:
                        aktor = winner
                        film = np.nan
                    winners.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film': film, 'type': 'Winner'})
    # Utwórz DataFrame z zebranych informacji o zwycięzcach
    df = pd.DataFrame(winners)
    return df



def extract_nominee(html_file_path, year):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()


    soup = BeautifulSoup(html_content, 'html.parser')

    listnominee = []  # Główna lista do przechowywania informacji o wszystkich nominowanych.
    ACTOR = []       # Lista do przechowywania nominowanych w kategorii 'ACTOR'.
    other = []       # Lista do przechowywania nominowanych w innych kategoriach.
    cat = []         # Lista do przechowywania nazw kategorii dla nominowanych w 'other'

    # Znajdź wszystkie sekcje kategorii na stronie.
    for category_section in soup.find_all('div', class_='category-section'):
        category = category_section.find('h2').text.strip()


        # Znajdź wszystkie elementy div z klasą 'nominee' w tej sekcji.

        for nominee_element in category_section.find_all('div', class_='nominee'):
            nominee_paragraph = nominee_element.find('p')


            if nominee_paragraph:
                nominee = nominee_paragraph.text.strip()
                # Jeśli kategoria to 'ACTOR', dodaj nominowanego do listy 'ACTOR'.
                if category =='ACTOR':
                    ACTOR.append(nominee)
                else:
                    # W przeciwnym razie, dodaj nominowanego do listy 'other' i nazwę kategorii do listy 'cat'.
                    other.append(nominee)
                    cat.append(category)

    # Zwraca elementy, które są w 'ACTOR', a nie w 'other'
    lista3 = znajdz_roznice(ACTOR, other)

    # Dodaj elementy znalezione w 'lista3' do listy 'other'.
    for i in lista3:
        other.append(i)

    # Dla każdego elementu dodanego z 'lista3', dodaj kategorię 'ACTOR' do listy 'cat'.
    for i in range(len(lista3)):
        cat.append('ACTOR')

# Przetwarzaj listy 'other' i 'cat', aby wyodrębnić aktora i film (jeśli istnieją).
    for y,category in zip(other,cat):

        try:
            parts = y.split(' - ')
            if len(parts) >= 2:
                aktor = parts[0].strip()
                film = ' - '.join(parts[1:]).strip()

            elif len(parts) == 2:
                aktor = parts[0].strip()
                film = parts[1].strip()

            else:
                aktor = parts[0].strip()
                film = np.nan

        except ValueError:
                    aktor = y
                    film = np.nan

        # Dodaj informacje o nominowanym do głównej listy 'listnominee'.
        listnominee.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film': film, 'type': 'nominee'})

    df = pd.DataFrame(listnominee)
    return df






def weryfikuj_i_rozdziel_osoby(data):
    """
    Weryfikuje kolumnę 'aktor' w DataFrame, rozdziela osoby wymienione po przecinku lub 'and',
    tworząc nowe wiersze dla każdej osoby. Usuwa również wiersze zawierające określone nieosobowe wartości.

    Args:
        data (pd.DataFrame): DataFrame zawierający kolumny 'YEAR', 'category', 'aktor', 'film', 'type'.

    Returns:
        pd.DataFrame: Nowy DataFrame, w którym każda osoba jest w osobnym wierszu,
                       a wiersze z nieosobowymi wartościami zostały usunięte.
    """

    new=pd.DataFrame()

    for index, i in data.iterrows():
        YEAR=i['YEAR']
        category=i['category']
        film=i['film']
        ztype=i['type']
        try:
             # Sprawdzenie, czy w kolumnie 'aktor' występuje przecinek (sugerujący wiele osób).
            if ',' in i['aktor']:
                aktor = i['aktor'].split(',')
                for a in aktor:
                    tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [a.strip()],'film': [film],'type': [ztype]})
                    new= pd.concat([new,tempo], ignore_index=True)
            # Sprawdzenie, czy w kolumnie 'aktor' występuje ' and ' (sugerujące wiele osób).
            elif ' and ' in i['aktor']:
                aktor = i['aktor'].split(' and ')
                for a in aktor:
                    tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [a.strip()],'film': [film],'type': [ztype]})
                    new= pd.concat([new,tempo], ignore_index=True)
            else:
                tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [i['aktor'].strip()],'film': [film],'type': [ztype]})
                new= pd.concat([new,tempo], ignore_index=True)

        except TypeError:
            print(f'Error {i["aktor"]}')
    # Lista wartości, które mają zostać usunięte z kolumny 'aktor' (np. nazwy firm, tytuły).
    remove = ['Metro-Goldwyn-Mayer', 'Warner Bros.','Producer', 'Producers', 'Sound Director', 'Music', 'Jr.']

 # Stworzenie maski logicznej wskazującej wiersze, w których wartość kolumny 'aktor' znajduje się na liście 'remove'.
    maska = new['aktor'].isin(remove)
     # Filtrowanie DataFrame 'new' i zachowanie tylko tych wierszy, które nie spełniają maski (czyli nie zawierają wartości z 'remove').
    df_oczyszczony = new[~maska]

    return df_oczyszczony


# Funkcja pozostawiona do mozliwego przyszłego wykorzystania obecnie weryfikuj_i_rozdziel_osoby spelnia te funkcje.
def czyszczenie_przecinek(data):

    new=pd.DataFrame()

    for index, i in data.iterrows():
        YEAR=i['YEAR']
        category=i['category']
        film=i['film']
        ztype=i['type']
        try:
            if ',' in i['aktor']:
                aktor = i['aktor'].split(',')
                for a in aktor:
                    tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [a.strip()],'film': [film],'type': [ztype]})
                    new= pd.concat([new,tempo], ignore_index=True)
            else:
                tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [i['aktor'].strip()],'film': [film],'type': [ztype]})
                new= pd.concat([new,tempo], ignore_index=True)

        except TypeError:
            print(f'Error {i["aktor"]}')

    return new



#Funckja relizuje zadania jakie weryfikuj_i_rozdziel_osoby jednak byla potrzebna do ponownego podzialu.
def czyszczenie_and(data):
    """
    Weryfikuje kolumnę 'aktor' w DataFrame, rozdziela osoby wymienione  'and',
    tworząc nowe wiersze dla każdej osoby.

    Args:
        data (pd.DataFrame): DataFrame zawierający kolumny 'YEAR', 'category', 'aktor', 'film', 'type'.

    Returns:
        pd.DataFrame: Nowy DataFrame, w którym każda osoba jest w osobnym wierszu,
                       a wiersze z nieosobowymi wartościami zostały usunięte.
    """

    new=pd.DataFrame()

    for index, i in data.iterrows():
        YEAR=i['YEAR']
        category=i['category']
        film=i['film']
        ztype=i['type']
        try:
            if ' and ' in i['aktor']:
                aktor = i['aktor'].split(' and ')
                for a in aktor:
                    tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [a.strip()],'film': [film],'type': [ztype]})
                    new= pd.concat([new,tempo], ignore_index=True)
            else:
                tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [i['aktor'].strip()],'film': [film],'type': [ztype]})
                new= pd.concat([new,tempo], ignore_index=True)

        except TypeError:
            print(f'Error {i["aktor"]}')

    return new


def usuwanie_dodatkowych_slow(data, kolumna='aktor'):
    """
    Usuwa określone dodatkowe słowa z wybranej kolumny DataFrame.

    Args:
        data (pd.DataFrame): DataFrame do przetworzenia.
        kolumna (str, optional): Nazwa kolumny zawierającej tekst do oczyszczenia.
                                  Domyślnie 'aktor'.

    Returns:
        pd.DataFrame: Nowy DataFrame z usuniętymi dodatkowymi słowami i potencjalnie
                      rozdzielonymi aktorami (jeśli występuje ';').
    """
    new = pd.DataFrame()
    words = ['Set Decoration: ', 'Screenplay - ', 'Written by ', 'Music by ', 'Lyric by ',
             'Production Design: ', 'Written for the screen by ', 'Set Decoration: ', 'To ',
             'Screenplay by ', 'Art Direction: ', 'Lyrics by ', 'Screen story by ',
             'Story by ', 'Art Direction: ', 'Orchestral Score by ', 'Sound Effects by ',
             'Adaptation Score by', 'Song Score by ', 'lyrics by ', 'adaptation score by ',
             ' for superlative artistry', 'Adapted for the screen by ', '  for the creation of'
             ' for superlative artistry', 'for the design', 'Adaptation Score by ',
             'Lyrics by ', ' for the wise', 'Adaptation by ', 'Song Score by ',
             'Adaptation score by ','Photographic Effects by ','head of department Score by ',
             'musical director Score by ','musical director Score by ','Written for the Screen by ']

    for index, i in data.iterrows():
        YEAR = i['YEAR']
        category = i['category']
        film = i['film']
        ztype = i['type']
        aktor = i[kolumna]

        # Usuń dodatkowe słowa
        for w in words:
            if isinstance(aktor, str) and w in aktor:
                aktor = aktor.replace(w, "").strip() # Dodano .strip()

        # Rozdziel aktorów po średniku i dodaj do nowego DataFrame
        if isinstance(aktor, str) and ';' in aktor:
            aktorzy = [a.strip() for a in aktor.split(';')]
            for a in aktorzy:
                tempo = pd.DataFrame({'YEAR': [YEAR], 'category': [category], 'aktor': [a.strip()], 'film': [film], 'type': [ztype]})
                new = pd.concat([new, tempo], ignore_index=True)
        elif isinstance(aktor, str):
            tempo = pd.DataFrame({'YEAR': [YEAR], 'category': [category], 'aktor': [aktor.strip()], 'film': [film], 'type': [ztype]})
            new = pd.concat([new, tempo], ignore_index=True)
        else:
            print(f'Error w kolumnie "{kolumna}" dla wiersza z indeksem {index}: {aktor}')

    return new


def czyszczenie_at(data):
    """
    Weryfikuje kolumnę 'aktor' w DataFrame, rozdziela osoby wymienione  '&',
    tworząc nowe wiersze dla każdej osoby.

    Args:
        data (pd.DataFrame): DataFrame zawierający kolumny 'YEAR', 'category', 'aktor', 'film', 'type'.

    Returns:
        pd.DataFrame: Nowy DataFrame, w którym każda osoba jest w osobnym wierszu,
                       a wiersze z nieosobowymi wartościami zostały usunięte.
    """

    new=pd.DataFrame()

    for index, i in data.iterrows():
        YEAR=i['YEAR']
        category=i['category']
        film=i['film']
        ztype=i['type']
        try:
            if ' & ' in i['aktor']:
                aktor = i['aktor'].split(' & ')
                for a in aktor:
                    tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [a.strip()],'film': [film],'type': [ztype]})
                    new= pd.concat([new,tempo], ignore_index=True)
            else:
                tempo=pd.DataFrame({'YEAR': [YEAR],'category': [category],'aktor': [i['aktor'].strip()],'film': [film],'type': [ztype]})
                new= pd.concat([new,tempo], ignore_index=True)

        except TypeError:
            print(f'Error {i["aktor"]}')

    return new


def usun_nawiasy_w_miejscu(data, kolumna='aktor'):
    """
    Usuwa nawiasy okrągłe z określonej kolumny DataFrame, modyfikując go w miejscu.

    Args:
        data (pd.DataFrame): DataFrame do zmodyfikowania.
        kolumna (str, optional): Nazwa kolumny do przetworzenia. Domyślnie 'aktor'.
    """
    data[kolumna] = data[kolumna].str.replace(r'[()]', '', regex=True).str.strip()


def usun_wszystkie_biale_znaki(data, kolumna='aktor'):
    """
    Usuwa wszystkie białe znaki (spacje, tabulatory, nowe linie itp.)
    z wartości w określonej kolumnie DataFrame, modyfikując go w miejscu.

    Args:
        data (pd.DataFrame): DataFrame do zmodyfikowania.
        kolumna (str, optional): Nazwa kolumny do przetworzenia. Domyślnie 'aktor'.
    """
    data[kolumna] = data[kolumna].str.strip()


def znajdz_prawie_podobne(lista, prog_podobienstwa=0.9):
    """
    Znajduje i wypisuje prawie duplikaty w liście stringów.

    Args:
        lista: Lista stringów do przeszukania.
        prog_podobienstwa: Minimalny współczynnik podobieństwa (od 0 do 1)
                           uznawany za "prawie duplikat". Domyślnie 0.9.
    """
    n = len(lista)
    znalezione_pary = set()  # Aby uniknąć duplikatów par

    for i in range(n):
        for j in range(i + 1, n):
            slowo1 = lista[i]
            slowo2 = lista[j]

            # Oblicz współczynnik podobieństwa między dwoma słowami
            matcher = SequenceMatcher(None, slowo1, slowo2)
            podobienstwo = matcher.ratio()

            if podobienstwo >= prog_podobienstwa:
                # Sortuj słowa w parze, aby uniknąć duplikatów w zbiorze znalezionych par
                para = tuple(sorted((slowo1, slowo2)))
                if para not in znalezione_pary:
                    print(f"Znaleziono podobne : '{slowo1}', '{slowo2}', podobieństwo: {podobienstwo:.2f}")
                    sys.stdout.flush()
                    znalezione_pary.add(para)

    return znalezione_pary



def suguesia_zamiany(dane,data):
    """
    Analizuje listę par ciągów znaków i na podstawie różnych kryteriów
    sugeruje zamiany, zwracając DataFrame z proponowanymi zamianami
    oraz listę słowników reprezentujących te zamiany.

    Args:
        dane (list): Lista par ciągów znaków (list zawierająca dwie str).
        data (DataFrame): DataFrame zawierający dane, używany do weryfikacji
                          i wyciągania informacji o aktorach. Oczekuje się,
                          że DataFrame zawiera kolumny 'aktor' i 'YEAR' oraz 'category'.

    Returns:
        tuple: Krotka zawierająca:
            - Datazamiana (DataFrame): DataFrame z kolumnami 'old' i 'new',
                                       zawierający oryginalne i sugerowane ciągi znaków.
            - dozamiany_lista (list): Lista słowników, gdzie każdy słownik
                                       ma klucze 'old' i 'new' reprezentujące
                                       sugerowaną zamianę.
    """
    final=[]
    for i in dane:
        one = i[0].split(" ")
        two = i[1].split(" ")

        # Sprawdzenie warunków długości ciągów znaków
        if len(one) <4 and len(two)<4 or len(one)==1 and len(two)==1:
            try:
                # Przypadek, gdy liczba słów w ciągach jest różna
                if len(one) != len(two):
                    # Sprawdzenie, czy pierwsze i ostatnie słowa są takie same
                    if one[0] == two[0] and one[-1] == two[-1]:

                        # Pobranie statystyk dotyczących liczby i zakresu lat dla aktorów
                        num1=data.loc[data['aktor']==i[0]]['YEAR'].count()
                        num2 = data.loc[data['aktor']==i[1]]['YEAR'].count()
                        num1max = data.loc[data['aktor']==i[0]]['YEAR'].max()
                        num1min=data.loc[data['aktor']==i[0]]['YEAR'].min()
                        num2mean = data.loc[data['aktor']==i[1]]['YEAR'].mean()

                        num2max = data.loc[data['aktor']==i[1]]['YEAR'].max()
                        num2min=data.loc[data['aktor']==i[1]]['YEAR'].min()
                        num1mean = data.loc[data['aktor']==i[0]]['YEAR'].mean()

                         # Sugerowanie zamiany na podstawie liczby i zakresu lat
                        if num1 > num2:
                            if num1max > num2mean and num2mean > num1min:
                                final.append([i,[f"{one[0]} {one[-1]}"]])

                        elif num1 < num2:
                            if num2max > num1mean and num1mean > num2min:
                                final.append([i,[f"{one[0]} {one[-1]}"]])

                else:
                     # Przypadek, gdy liczba słów w ciągach jest taka sama
                    if one[1] == two[1]:
                         # Sprawdzenie długości pierwszego słowa i ostatniej litery drugiego słowa
                        if len(one[0]) < len(two[0]) and two[0][-1] =='y':

                            # Pobranie najczęstszej kategorii dla obu aktorów
                            num1=data.loc[data['aktor']==i[0]]['category'].value_counts().reset_index()['category'].iloc[0]
                            num2=data.loc[data['aktor']==i[1]]['category'].value_counts().reset_index()['category'].iloc[0]

                            num1New=num1.split()[0]
                            num2New=num2.split()[0]
                             # Sugerowanie zamiany, jeśli pierwsze słowa najczęstszych kategorii są podobne
                            if num1New.lower() == num2New.lower():
                                final.append([i,[f"{two[0]} {one[1]}"]])

                        # Sprawdzenie, czy pierwsze słowo drugiego ciągu zaczyna się tak samo jak pierwsze słowo pierwszego ciągu
                        elif len(one[0]) < len(two[0]):
                            num=len(one[0])
                            for l in range(len(one[0])):
                                if one[0][l] ==two[0][l]:
                                    num-=1

                            if num == 0:
                                final.append([i,[f"{two[0]} {one[1]}"]])


                        else:
                            continue
            except IndexError:
                print(f'error {i[0]} ')
        else:
            print(f"Trudne do indetyfikacji, zostanie pominęte: {i}")

        try:
             # Sprawdzenie, czy długości całych ciągów są identyczne
            if len(i[0]) == len(i[1]):

                num=len(i[0])
                 # Sprawdzenie, czy wszystkie znaki (ignorując wielkość liter) są takie same
                for l in range(len(i[0])):
                    if i[0][l].lower() == i[1][l].lower():
                        num-=1
                    if num == 0:
                        final.append([i,[i[0].title()]])

              # Ponowne sprawdzenie, czy długości całych ciągów są identyczne
            if len(i[0]) == len(i[1]):

                num=len(i[0])
                 # Iteracja po znakach w ciągach
                for l in range(len(i[0])):
                    if i[0][l].lower() == i[1][l].lower():
                        num-=1


                    else:
                        # Sprawdzenie, czy na danej pozycji występuje '-'
                        if '-' == i[0][l]:
                            final.append([i,[i[0]]])
                        elif '-' == i[1][l]:
                            final.append([i,[i[1]]])




        except IndexError:
            print(f'error {i[0]}')

        #tworzenie DataFrame plik csv.
        Datazamiana=pd.DataFrame(columns=['old','new'])
        temp=pd.DataFrame(columns=['old','new'])

        for i in final:
            temp=pd.DataFrame({'old':[i[0][0]],'new':[i[1][0]]})
            Datazamiana = pd.concat([Datazamiana,temp], ignore_index=True)

    dozamiany_lista = Datazamiana.to_dict(orient='records')
    return Datazamiana, dozamiany_lista



def zamiana(data,lista):
    """
    Iteruje po wierszach DataFrame zawierającego sugerowane zamiany
    i wykonuje te zamiany w kolumnie 'aktor' innego DataFrame.

    Args:
        data (DataFrame): DataFrame, w którym ma zostać przeprowadzona zamiana
                          w kolumnie 'aktor'.
        lista (DataFrame): DataFrame z kolumnami 'old' i 'new', zawierający
                           informacje o zamianach do wykonania.

    Returns:
        DataFrame: DataFrame z zaktualizowaną kolumną 'aktor' po przeprowadzeniu zamian.
    """
    for index, y in lista.iterrows():
        print(f"zamiana {y['old']} na {y['new']}")

        data['aktor']=data['aktor'].replace(y['old'], y['new'])


    return data




def usuwanie_dodatkowych_slow2(data, kolumna='aktor'):
    """
    Przetwarza DataFrame, usuwając określone dodatkowe słowa z podanej kolumny
    tekstowej ('aktor' domyślnie) i tworząc nowy DataFrame z wyczyszczonymi danymi.

    Args:
        data (DataFrame): DataFrame do przetworzenia.
        kolumna (str, optional): Nazwa kolumny tekstowej do oczyszczenia.
                                  Domyślnie 'aktor'.

    Returns:
        DataFrame: Nowy DataFrame zawierający dane z usuniętymi dodatkowymi słowami
                   w określonej kolumnie.
    """

    new = pd.DataFrame()
    words = ['Special Audible Effects by ','Special Visual Effects by ', 'head of department ',' for the animation direction of Who Framed Roger Rabbit.']

    for index, i in data.iterrows():
        YEAR = i['YEAR']
        category = i['category']
        film = i['film']
        ztype = i['type']
        aktor = i[kolumna]

        # Usuń dodatkowe słowa
        for w in words:
            if isinstance(aktor, str) and w in aktor:
                aktor = aktor.replace(w, "").strip() # Dodano .strip()
                tempo = pd.DataFrame({'YEAR': [YEAR], 'category': [category], 'aktor': [aktor.strip()], 'film': [film], 'type': [ztype]})
                new = pd.concat([new, tempo], ignore_index=True)

        # Rozdziel aktorów po średniku i dodaj do nowego DataFrame

        if isinstance(aktor, str):
            tempo = pd.DataFrame({'YEAR': [YEAR], 'category': [category], 'aktor': [aktor.strip()], 'film': [film], 'type': [ztype]})
            new = pd.concat([new, tempo], ignore_index=True)
        else:
            print(f'Error w kolumnie "{kolumna}" dla wiersza z indeksem {index}: {aktor}')

    return new




def special_award(df):
    """
    Przetwarza DataFrame w celu wyodrębnienia informacji o osobach nagrodzonych
    specjalnymi nagrodami, normalizując ich imiona i nazwiska.

    Args:
        df (DataFrame): DataFrame zawierający dane o nagrodach, z kolumnami
                        takimi jak 'category', 'aktor', 'film'.

    Returns:
        DataFrame: Nowy DataFrame zawierający unikalne wiersze po przetworzeniu
                   kolumny 'aktor' dla specjalnych nagród.
    """


    lista2 = []
    listaHo=['HONORARY AWARD', 'SPECIAL AWARD', 'SPECIAL FOREIGN LANGUAGE FILM AWARD', 'AWARD OF COMMENDATION', 'IRVING G. THALBERG MEMORIAL AWARD']

    # Wybierz unikalnych aktorów z kategorii innych niż specjalne
    listakto=df.loc[~df['category'].isin(listaHo)]['aktor'].unique()

     # Jeśli brakuje tytułu filmu, przypisz nazwę aktora
    warunek= df['film'].isna()


    df.loc[warunek, 'film'] = df.loc[warunek, 'aktor']

    # Utwórz listę aktorów składających się z dwóch słów (zakładając, że to imię i nazwisko)
    for i in listakto:
        d=str(i).split()
        if len(d) !=2:
            continue
        else:
            lista2.append(i)

    def sprawdz_imie_naziwsko(aktor, lista2):
        """Sprawdza, czy aktor zawiera którekolwiek imię i nazwisko z listy2."""
        for imie_nazwisko in lista2:
            if imie_nazwisko in aktor:
                return imie_nazwisko  # Zwraca znalezione imię i nazwisko
        return aktor  # Zwraca oryginalną wartość, jeśli nic nie znaleziono


    def extract_between_to_comma(text):
        """Wyciąga tekst pomiędzy 'To ' a pierwszą napotkaną ','."""
        if "To " in text and "," in text:
            part1 = text.split("To ", 1)[1]  # Dzielimy po pierwszym "To " i bierzemy drugą część
            part2 = part1.split(",", 1)[0]   # Dzielimy po pierwszym "," i bierzemy pierwszą część
            return part2.strip()              # Usuwamy ewentualne białe znaki na początku i końcu
        else:
            return text

    def remove_producer(text):
        """Usuwa frazę ', Producer' z tekstu."""
        if ', Producer' in text:
            text=text.replace(', Producer',"")
        return text


    # Załóżmy, że 'lista2' jest już zdefiniowana i zawiera imiona i nazwiska
    maska = df['aktor'].apply(lambda aktor: any(imie_nazwisko in aktor for imie_nazwisko in lista2))

    # Jeśli chcesz zastąpić całą wartość w 'aktor' znalezionym imieniem i nazwiskiem:
    df['aktor'] = df['aktor'].apply(lambda aktor: next((imie_nazwisko for imie_nazwisko in lista2 if imie_nazwisko in aktor), aktor))

    znaki =[' - ',' for ', ' in recognition',' in appreciation']
    for znak in znaki:
        df['aktor'] = df['aktor'].str.split(znak, n=1, expand=True)[0]

    # Zastosuj funkcje do dalszego oczyszczenia kolumny 'aktor'
    df['aktor'] = df['aktor'].apply(extract_between_to_comma)
    df['aktor'] = df['aktor'].apply(remove_producer)

    final = df.drop_duplicates()

    return final






def analizaaktorow(df):
    """
    Analizuje nominacje i zwycięstwa aktorów, tworzy wykresy i zapisuje dane do plików CSV.

    Args:
        df (pd.DataFrame): DataFrame zawierający dane o Oscarach.
    """

    # 1. Filtrowanie danych: Wybierz tylko wiersze z kategoriami aktorskimi.

    # 1. Filtrowanie danych: Wybierz tylko wiersze z kategoriami aktorskimi.
    filtered_df = df.loc[df['category'].isin(['ACTOR IN A LEADING ROLE', 'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS'])]

    # 2. Grupowanie i zliczanie: Zlicz liczbę wystąpień dla każdego aktora i typu nominacji.
    grouped_df = filtered_df.groupby(['aktor', 'type']).size().reset_index(name='count')

    # 3. Sortowanie danych: Posortuj dane według aktora, typu nominacji i liczby wystąpień.
    sorted_df = grouped_df.sort_values(by=['aktor', 'type', 'count'], ascending=[True, False, False])

    # 4. Tworzenie DataFrame z samymi zwycięzcami: Wybierz tylko wiersze ze zwycięzcami i posortuj według liczby zwycięstw.
    winners_df = sorted_df[sorted_df['type'] == 'Winner'].sort_values(by='count', ascending=False)

    # 5. Tworzenie pustego DataFrame na wynik: Inicjalizuj pusty DataFrame, który będzie przechowywać wyniki.
    result_df = pd.DataFrame()

    # 6. Iterowanie po zwycięzcach i dodawanie ich nominacji (poprawione): Dla każdego zwycięzcy dodaj jego zwycięstwa i nominacje do DataFrame.
    for actor in winners_df['aktor']:
        actor_winners = sorted_df[(sorted_df['aktor'] == actor) & (sorted_df['type'] == 'Winner')]
        actor_nominees = sorted_df[(sorted_df['aktor'] == actor) & (sorted_df['type'] == 'nominee')]

        # Dodaj najpierw zwycięstwa, a potem nominacje
        result_df = pd.concat([result_df, actor_winners, actor_nominees], ignore_index=True)

    # 7. Tworzenie tabeli przestawnej: Utwórz tabelę przestawną z danymi o aktorach, nominacjach i zwycięstwach.





    # 9. Przygotowanie danych dla wykresu słupkowego i punktowego: Wybierz 50 najlepszych aktorów i utwórz tabelę przestawną.

    pivot_df = result_df.pivot_table(index='aktor', columns='type', values='count', fill_value=0).reset_index()
    pivot_df['total'] = pivot_df['Winner'] + pivot_df['nominee']
    pivot_df['%win'] = round((pivot_df['Winner'] / pivot_df['total']) * 100, 2)
    pairplot = pivot_df.loc[pivot_df['Winner'] > 1].sort_values(['Winner', '%win'], ascending=[False, False])
    pairplot['nominee'] = pairplot['nominee'].astype(int)
    pairplot['winner'] = pairplot['Winner'].astype(int)
    pairplot['total'] = pairplot['total'].astype(int)


    # 10. Tworzenie wykresu słupkowego i punktowego: Wykres słupkowy przedstawiający nominacje i zwycięstwa, wykres punktowy przedstawiający lata.
    fig, ax1 = plt.subplots(figsize=(12, 8))
    df_award = df.loc[df['category'].isin(['ACTOR IN A LEADING ROLE', 'ACTOR', 'ACTRESS IN A LEADING ROLE', 'ACTRESS'])]
    chart = pairplot.set_index('aktor')
    chart[['Winner', 'nominee']].plot(kind='bar', stacked=True, ax=ax1) #Zmieniono kolejność kolumn na wykresie słupkowym
    ax1.set_title('Nominacje i Wygrane Oscarów')
    ax1.set_xlabel('Aktorzy')
    ax1.set_ylabel('Liczba')
    ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
    ax2 = ax1.twinx()
    winners = []
    nominees = []
    for actor, row in chart.iterrows():
        actor_data = df_award[df_award['aktor'] == actor] #Zmieniłem nazwę zmiennej aby nie nadpisywała df z argumentu funkcji
        years = actor_data['YEAR'].tolist()
        types = actor_data['type'].tolist()
        for year, t in zip(years, types):
            if t == 'Winner':
                winners.append((actor, year))
            else:
                nominees.append((actor, year))


    ax2.scatter([actor for actor, year in winners], [year for actor, year in winners], color='lime', marker='o', s=50, label='Zwycięstwo')
    ax2.scatter([actor for actor, year in nominees], [year for actor, year in nominees], color='black', marker='o', s=50, label='Nominacja')
    ax2.scatter([actor for actor, year in winners], [year for actor, year in winners], color='lime', marker='o', s=50, label='Zwycięstwo')

    ax2.set_ylabel('Lata', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    handles, labels = ax2.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax2.legend(*zip(*unique), loc='upper center', bbox_to_anchor=(0.5, 1.25), ncol=2)
    CHART_PATH = os.path.join('static', 'charts', 'analizaAktorow.png')

    plt.tight_layout()
    plt.savefig(CHART_PATH)






def winnersfilm(df):
    """
    Generuje wykres punktowy przedstawiający filmy z największą liczbą Oscarów w różnych latach.

    Args:
        df (pd.DataFrame): DataFrame zawierający dane o Oscarach.
    """

    # 1. Wybór filmów, które zdobyły Oscara, grupowanie według lat i filmów, sortowanie malejąco według liczby Oscarów.
    three = df.loc[df['type'] == 'Winner'][['YEAR','category','film']].drop_duplicates().groupby(['YEAR', 'film']).size().reset_index(name='category').sort_values('category', ascending=False)
    two=three[three['category']>7]

    # 2. Wybór 10 filmów z największą liczbą Oscarów.
    films = two['film'].to_list()

    # 3. Filtrowanie danych, aby uwzględnić tylko 10 wybranych filmów.
    final = three.loc[three['film'].isin(films)]

    # 4. Tworzenie wykresu punktowego.
    plt.figure(figsize=(10, 6))

    # 5. Rysowanie punktów dla każdego filmu i roku.
    for i, row in final.iterrows():
        # Rysowanie punktu, rozmiar punktu zależy od liczby Oscarów (category).
        plt.scatter(row['film'], row['YEAR'], s=row['category'] * 60, alpha=0.6)
        # Dodawanie liczby Oscarów obok punktu.
        plt.text(row['film'], row['YEAR'], str(row['category']), ha='center', va='center', fontsize=18)

    # 6. Dodawanie tytułu i etykiet osi.
    plt.title('Rok i ilość otrzymanych Oskarow dla Filmów')
    plt.xlabel('Filmy')
    plt.ylabel('Lata')

    # 7. Obracanie etykiet osi X o 30 stopni.
    plt.xticks(rotation=30, ha='right')

    # 8. Wyświetlanie siatki i wykresu.
    plt.grid(True)
    plt.tight_layout()
    CHART_PATH = os.path.join('static', 'charts', 'filmy_zwyciescy.png')


    plt.tight_layout()
    plt.savefig(CHART_PATH)




def mapaswaita(data):
    """
    Generuje mapę świata z zaznaczonymi krajami, które zdobyły nagrody
    w kategoriach 'FOREIGN LANGUAGE FILM' i 'INTERNATIONAL FEATURE FILM',
    wraz z liczbą zdobytych nagród dla każdego kraju.

    Args:
        data (DataFrame): DataFrame zawierający dane o nagrodach, z kolumnami
                        'category', 'aktor', 'film', 'type'.

    Returns:
        folium.Map: Obiekt mapy Folium z zaznaczonymi krajami i liczbą nagród.
    """
    # 1. Filtrowanie i grupowanie danych:
    #    - Wybiera wiersze z kategoriami 'FOREIGN LANGUAGE FILM' i 'INTERNATIONAL FEATURE FILM'
    #      i typem 'Winner'.
    #    - Grupuje po 'aktor' (zakładamy, że 'aktor' reprezentuje kraj) i liczy wystąpienia 'film' (liczbę nagród).

    thelist = data.loc[(data['category'].isin(['FOREIGN LANGUAGE FILM','INTERNATIONAL FEATURE FILM']) & (data['type']=='Winner'))].groupby('aktor')['film'].count().sort_values()

    # 2. Mapowanie nazw krajów:
    #    - Definiuje słownik do mapowania starych/nieaktualnych nazw krajów na aktualne.
    country_list={'Bosnia':'Bosnia and Herzegovina',
                'Federal Republic of Germany':'Germany',
                'Czechoslovakia':'Czech Republic',
                'Union of Soviet Socialist Republics':'Russia',
                'The Netherlands':'Netherlands'}

    #    - Aktualizuje nazwy krajów w indeksie serii 'thelist'.
    updated_thelist = thelist.rename(country_list)

    # 3. Tworzenie słownika z liczbą nagród dla każdego kraju:
    #    - Tworzy słownik 'con', gdzie kluczem jest nazwa kraju, a wartością
    #      liczba zdobytych nagród (suma nagród dla danego kraju).
    con={}
    for i in updated_thelist.index:
        con[i]=int(updated_thelist[i].sum())

    countries = list(con.keys())
    numbers = list(con.values())


    # 4. Pobieranie danych GeoJSON o granicach krajów:
    #    - Pobiera dane GeoJSON z granicami krajów z publicznie dostępnego źródła.

    res = requests.get("https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json")
    res.raise_for_status()
    df = pd.DataFrame(json.loads(res.content.decode()))
    #    - Wyodrębnia identyfikatory i nazwy krajów z danych GeoJSON.
    df = df.assign(
        id=df["features"].apply(pd.Series)["id"],
        name=df["features"].apply(pd.Series)["properties"].apply(pd.Series)["name"]
    )

    # 5. Pobieranie informacji o kolorach krajów z Wikipedii:
    #    - Pobiera kod HTML strony Wikipedii zawierającej informacje o kolorach narodowych.
    resp = requests.get("https://en.wikipedia.org/wiki/National_colours")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content.decode(), "html.parser")
    colours = []
    #    - Iteruje po tabelach HTML na stronie i wyodrębnia nazwy krajów i kolory.

    for t in soup.find_all("table", class_="wikitable"):
        cols = t.find_all("th")
        # Sprawdza, czy to właściwa tabela (zawiera kolumny "Country" i "Primary").
        ok = (len(cols) > 5 and cols[0].string.strip() == "Country" and cols[4].string.strip() == "Primary")
        if ok:
            for tr in t.find_all("tr"): # Iteruje po wierszach tabeli.
                td = tr.find_all("td") # Iteruje po komórkach wiersza.
                if len(td) > 5:
                    try:
                        # Pobiera nazwę kraju, uwzględniając różne struktury HTML.
                        country_name_element = td[0].find("a")
                        if country_name_element and country_name_element.string:
                            country_name = country_name_element.string.strip()
                        else:
                            country_name_element = td[0]
                            if country_name_element and country_name_element.string:
                                country_name = country_name_element.string.strip()
                            else:
                                continue # Pomiń wiersz, jeśli nie można znaleźć nazwy kraju
                         # Pobiera kolory kraju.
                        sp = td[4].find_all("span")
                        if sp:
                            c1 = re.sub(r"background-color:([\w,#,0-9]*).*", r"\1", sp[0]["style"])
                            c2 = c1 if len(sp) == 1 else re.sub(r"background-color:([\w,#,0-9]*).*", r"\1", sp[1]["style"])
                            colours.append({
                                "country": country_name,
                                "colour1": c1,
                                "colour2": c2,
                            })
                    except AttributeError:
                        continue
    dfc = pd.DataFrame(colours).set_index("country")

    # 6. Definiowanie funkcji stylizującej dla GeoJSON:
    #    - Definiuje funkcję 'style_fn', która na podstawie nazwy kraju
    #      pobiera kolory z DataFrame 'dfc' i zwraca słownik stylów dla GeoJSON
    def style_fn(feature):
        try:
            cc = dfc.loc[feature["properties"]["name"]]
            ss = {'fillColor': f'{cc[0]}', 'color': f'{cc[1]}'}
            return ss
        except KeyError:
            return {'fillColor': 'gray', 'color': 'black'}

    # 7. Definiowanie funkcji do obliczania centroidu
    def get_country_centroid(feature):
        """Calculates a simple centroid for a GeoJSON feature."""
        geometry_type = feature['geometry']['type']
        coordinates = feature['geometry']['coordinates']
        if geometry_type == 'Polygon':
            coords = np.array(coordinates[0])
            centroid_lon = np.mean(coords[:, 0])
            centroid_lat = np.mean(coords[:, 1])
            return [centroid_lat, centroid_lon]
        elif geometry_type == 'MultiPolygon':
            all_coords = np.concatenate([np.array(polygon[0]) for polygon in coordinates])
            centroid_lon = np.mean(all_coords[:, 0])
            centroid_lat = np.mean(all_coords[:, 1])
            return [centroid_lat, centroid_lon]
        return None

    # 8. Tworzenie mapy Folium:
    #    - Tworzy obiekt mapy Folium, ustawiając początkowy punkt i poziom zoom.
    m = folium.Map(location=[50, 0], zoom_start=1, control_scale=True)

    # 9. Dodawanie warstw GeoJSON i etykiet do mapy:
    #    - Iteruje po liście krajów i ich liczbie nagród.
    #    - Dla każdego kraju pobiera dane GeoJSON i dodaje je jako warstwę do mapy.
    #    - Dodaje etykiety z liczbą nagród dla każdego kraju
    for i, country_name_from_list in enumerate(countries):
        try:
            country_data = df[df["name"] == country_name_from_list].iloc[0]
            geo_json_data = country_data["features"]
            tooltip_text = f"{country_name_from_list}: {numbers[i]}"
            folium.GeoJson(geo_json_data, name=country_name_from_list, tooltip=tooltip_text, style_function=style_fn).add_to(m)

            centroid = get_country_centroid(geo_json_data)
            if centroid:
                icon = DivIcon(
                    icon_size=(40, 20),
                    icon_anchor=(20, 10),
                    html=f'<div style="font-size: 12pt; color: black; text-align: center;">{numbers[i]}</div>',
                )
                folium.Marker(centroid, icon=icon).add_to(m)
        except IndexError:
            print(f"Nie znaleziono danych GeoJSON dla: {country_name_from_list}")
        except KeyError as e:
            print(f"Błąd klucza podczas stylizowania: {e} dla kraju: {country_name_from_list}")

    # 10. Zapisywanie mapy do pliku HTML:
    #     - Zapisuje mapę do pliku HTML.
    CHART_PATH = os.path.join('static', 'charts', 'country.html')
    m.save(CHART_PATH)
    return m


def analizuj_dane():
    """
    Analizuje DataFrame z danymi o nagrodach filmowych.

    Args:
        df (pd.DataFrame): DataFrame z kolumnami ['YEAR', 'category', 'aktor', 'film', 'type'].
    """
    df = pd.read_csv('CleanData.csv')
    output = "Analiza Pozyskanych Danych:\n\n"

    # Statystyki
    output += "Statystyki:\n"
    output += f"- Liczba ceremonii (lat): {df['YEAR'].nunique()}\n"
    output += f"- Liczba kategorii: {df['category'].nunique()}\n"
    output += f"- Liczba aktorów/aktorek: {df['aktor'].nunique()}\n"
    output += f"- Liczba filmów: {df['film'].nunique()}\n"
    output += f"- Liczba typów nagród: {df['type'].nunique()}\n\n"

    # Kompletność danych
    output += "Kompletność Danych:\n"
    output += "Brakujące dane:\n"
    output += f"{df.isnull().sum().to_string()}\n\n"
    # Poprawione obliczanie procentu brakujących danych
    total_cells = df.size
    missing_values = df.isnull().sum().sum()
    percent_missing = (missing_values / total_cells) * 100
    output += f"Procent brakujących danych: {percent_missing:.2f}%\n\n"
    output += f"- Liczba duplikatów: {df.duplicated().sum()}\n\n"

    # Analiza unikalnych wartości
    output += "Analiza unikalnych wartości:\n"
    output += "Rozkład lat:\n"
    output += f"{df['YEAR'].value_counts().sort_index().to_string()}\n\n"
    output += "Rozkład kategorii TOP 20:\n"
    output += f"{df['category'].value_counts()[:20].to_string()}\n\n"
    output += "Rozkład aktorów TOP 20:\n"
    output += f"{df['aktor'].value_counts()[:20].to_string()}\n\n"
    output += "Rozkład filmów TOP 20:\n"
    output += f"{df['film'].value_counts()[:20].to_string()}\n\n"
    output += "Rozkład typów nagród:\n"
    output += f"{df['type'].value_counts().to_string()}\n\n"

    # Analiza opisowa kolumny YEAR
    output += "Analiza opisowa kolumny YEAR:\n"
    output += "Statystyki opisowe dla YEAR:\n"
    output += f"{df['YEAR'].describe().to_string()}\n\n"


    return output.split('\n')

# Przykład użycia (załóżmy, że masz DataFrame o nazwie 'dane')

