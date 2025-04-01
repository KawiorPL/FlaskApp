import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
from difflib import SequenceMatcher
import pandas as pd


main = "https://oscar.warpechow.ski/"
folder='pliki2'

def Sonda(main,folder):

    respone = requests.get(main)
    dane = respone.text
    f = open(f"{folder}/linki.txt", "w")
    f.write(dane)
    f.close()

    return 1



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




def extract_award_data(html_file_path, year):
    """
    Ekstrahuje dane dotyczące nagród z pliku HTML, identyfikując sekcje kategorii,
    zwycięzców i nominowanych, a następnie organizuje te informacje w postaci
    ramki danych (DataFrame) biblioteki Pandas.

    Funkcja ta została zaprojektowana do przetwarzania plików HTML o specyficznej
    strukturze, gdzie główne kategorie nagród są oznaczone klasą CSS 'category-section',
    a w ich obrębie znajdują się podkategorie dla zwycięzców (klasa 'winner')
    i nominowanych (klasa 'nominee'). Wewnątrz tych podkategorii oczekuje się
    znacznika `<p>` zawierającego nazwę zwycięzcy lub nominowanego.

    Args:
        html_file_path (str): Ścieżka do pliku HTML zawierającego dane nagród.
        year (int): Rok, którego dotyczą nagrody (ta informacja zostanie dodana
                      do tworzonej ramki danych).

    Returns:
        pandas.DataFrame: Ramka danych zawierająca informacje o nagrodach.
                          Każdy wiersz reprezentuje jedną kategorię nagród i zawiera
                          kolumny 'YEAR' (rok), 'category' (nazwa kategorii),
                          'winner' (lista zwycięzców w danej kategorii) oraz
                          'nominees' (lista nominowanych w danej kategorii).
                          Zwraca None w przypadku wystąpienia błędów (np. brak pliku).

    Możliwość adaptacji do innych stron:
    Funkcja ta może być dostosowana do pracy z innymi stronami internetowymi
    zawierającymi podobną strukturę danych. Kluczowym elementem jest istnienie
    nadrzędnej sekcji (odpowiednik 'category-section') grupującej podkategorie
    zawierające poszczególne elementy (odpowiedniki 'winner' i 'nominee').
    Aby zaadaptować funkcję do innej strony, konieczne będzie zidentyfikowanie
    odpowiednich klas CSS lub innych selektorów HTML używanych do oznaczania
    tych sekcji i zmodyfikowanie argumentów przekazywanych do metod `find_all`
    biblioteki BeautifulSoup.

    Użytkownik ma możliwość dostosowania formatu wyjściowej ramki danych
    poprzez modyfikację sposobu tworzenia listy `data` oraz struktury
    słownika dodawanego do tej listy wewnątrz pętli. Można na przykład
    rozdzielić zwycięzców i nominowanych do osobnych wierszy, dodać dodatkowe
    informacje wyekstrahowane z HTML lub zmienić nazwy kolumn w ramce danych.
    """
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        data = []
        for category_section in soup.find_all('div', class_='category-section'):
            category = category_section.find('h2').text.strip()

            winners = []
            for winner_element in category_section.find_all('div', class_='winner'):
                winner_paragraph = winner_element.find('p')
                if winner_paragraph:
                    winner = winner_paragraph.text.strip()
                    winners.append(winner)


                    try:
                        aktor, film =winner.split(' - ')

                    except ValueError:

                        aktor = winner
                        film = np.nan


                data.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film':film, 'type': 'Winner'})


            nominees = []
            for nominee_element in category_section.find_all('div', class_='nominee'):
                nominee_paragraph = nominee_element.find('p')
                if nominee_paragraph:
                    nominee = nominee_paragraph.text.strip()
                    nominees.append(nominee)

                    try:
                        aktor, film =nominee.split(' - ')

                    except ValueError:

                        aktor = nominee
                        film = np.nan


                data.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film':film, 'type': 'nominees'})


        df = pd.DataFrame(data)
        return df

    except FileNotFoundError:
        print(f"Nie znaleziono pliku: {html_file_path}")
        return None
    except Exception as e:
        print(f"Wystąpil bład: {e}")
        return None





def weryfikuj_i_rozdziel_osoby(data):

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

    return new


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




def czyszczenie_and(data):

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
             ' for superlative artistry', 'Adapted for the screen by ',
             ' for superlative artistry', 'for the design', 'Adaptation Score by ',
             'Lyrics by ', ' for the wise', 'Adaptation by ', 'Song Score by ',
             'Adaptation score by ']

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
                    znalezione_pary.add(para)

    return znalezione_pary



def suguesia_zamiany(dane,data):
    final=[]
    for i in dane:
        one = i[0].split(" ")
        two = i[1].split(" ")

        if len(one) <4 and len(two)<4 or len(one)==1 and len(two)==1:
            try:

                if len(one) != len(two):
                    if one[0] == two[0] and one[-1] == two[-1]:


                        num1=data.loc[data['aktor']==i[0]]['YEAR'].count()
                        num2 = data.loc[data['aktor']==i[1]]['YEAR'].count()
                        num1max = data.loc[data['aktor']==i[0]]['YEAR'].max()
                        num1min=data.loc[data['aktor']==i[0]]['YEAR'].min()
                        num2mean = data.loc[data['aktor']==i[1]]['YEAR'].mean()

                        num2max = data.loc[data['aktor']==i[1]]['YEAR'].max()
                        num2min=data.loc[data['aktor']==i[1]]['YEAR'].min()
                        num1mean = data.loc[data['aktor']==i[0]]['YEAR'].mean()


                        if num1 > num2:
                            if num1max > num2mean and num2mean > num1min:
                                final.append([i,[f"{one[0]} {one[-1]}"]])

                        elif num1 < num2:
                            if num2max > num1mean and num1mean > num2min:
                                final.append([i,[f"{one[0]} {one[-1]}"]])

                else:
                    if one[1] == two[1]:
                        if len(one[0]) < len(two[0]) and two[0][-1] =='y':


                            num1=data.loc[data['aktor']==i[0]]['category'].value_counts().reset_index()['category'].iloc[0]
                            num2=data.loc[data['aktor']==i[1]]['category'].value_counts().reset_index()['category'].iloc[0]

                            num1New=num1.split()[0]
                            num2New=num2.split()[0]

                            if num1New.lower() == num2New.lower():
                                final.append([i,[f"{two[0]} {one[1]}"]])


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
            if len(i[0]) == len(i[1]):

                num=len(i[0])
                for l in range(len(i[0])):
                    if i[0][l].lower() == i[1][l].lower():
                        num-=1
                    if num == 0:
                        final.append([i,[i[0].title()]])


            if len(i[0]) == len(i[1]):

                num=len(i[0])
                for l in range(len(i[0])):
                    if i[0][l].lower() == i[1][l].lower():
                        num-=1


                    else:

                        if '-' == i[0][l]:
                            final.append([i,[i[0]]])
                        elif '-' == i[1][l]:
                            final.append([i,[i[1]]])




        except IndexError:
            print(f'error {i[0]}')


    return final












