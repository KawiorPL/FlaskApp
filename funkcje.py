import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
from difflib import SequenceMatcher
import pandas as pd
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import os


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

    with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()


    soup = BeautifulSoup(html_content, 'html.parser')


    winners = []
    for category_section in soup.find_all('div', class_='category-section'):
        category = category_section.find('h2').text.strip()


        # Przetwarzanie zwycięzcy (zakładam, że jest tylko jeden element z klasą 'winner' w sekcji)
        winner_element = category_section.find('div', class_='winner')

        if winner_element:
            winner_paragraph = winner_element.find('p')
            #print(winner_paragraph)
            if winner_paragraph:
                winner = winner_paragraph.text.strip()


                try:
                    aktor, film = winner.split(' - ')
                except ValueError:
                    aktor = winner
                    film = np.nan
                winners.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film': film, 'type': 'Winner'})

    df = pd.DataFrame(winners)
    return df


def extract_nominee(html_file_path, year):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()


    soup = BeautifulSoup(html_content, 'html.parser')

    listnominee=[]
    ACTOR=[]
    other=[]
    cat=[]
    for category_section in soup.find_all('div', class_='category-section'):
        category = category_section.find('h2').text.strip()

        for nominee_element in category_section.find_all('div', class_='nominee'):
            nominee_paragraph = nominee_element.find('p')


            if nominee_paragraph:
                nominee = nominee_paragraph.text.strip()
                if category =='ACTOR':
                    ACTOR.append(nominee)
                else:
                    other.append(nominee)
                    cat.append(category)


    lista3 = znajdz_roznice(ACTOR, other)


    for i in lista3:
        other.append(i)

    for i in range(len(lista3)):
        cat.append('ACTOR')


    for y,category in zip(other,cat):

        try:
            aktor, film = y.split(' - ')

        except ValueError:
                    aktor = y
                    film = np.nan

        listnominee.append({'YEAR': year, 'category': category, 'aktor': aktor, 'film': film, 'type': 'nominee'})

    df = pd.DataFrame(listnominee)
    return df






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

    remove = ['Metro-Goldwyn-Mayer', 'Warner Bros.','Producer', 'Producers', 'Sound Director', 'Music', 'Jr.']


    maska = new['aktor'].isin(remove)
    df_oczyszczony = new[~maska]

    return df_oczyszczony


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
             ' for superlative artistry', 'Adapted for the screen by ', '  for the creation of'
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
                    sys.stdout.flush()
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

        #tworzenie DataFrame plik csv.
        Datazamiana=pd.DataFrame(columns=['old','new'])
        temp=pd.DataFrame(columns=['old','new'])

        for i in final:
            temp=pd.DataFrame({'old':[i[0][0]],'new':[i[1][0]]})
            Datazamiana = pd.concat([Datazamiana,temp], ignore_index=True)

    dozamiany_lista = Datazamiana.to_dict(orient='records')
    return Datazamiana, dozamiany_lista



def zamiana(data,lista):
    for index, y in lista.iterrows():
        print(f"zamiana {y['old']} na {y['new']}")

        data['aktor']=data['aktor'].replace(y['old'], y['new'])


    return data




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

