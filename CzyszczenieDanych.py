import pandas as pd

import sys
import datetime
import json
from datetime import date
import datetime
import numpy as np
import os




import funkcje as fu

print('Pobieranie danych z years_and_links.csv')
sys.stdout.flush()
dataframe = pd.read_csv('years_and_links.csv')


#stworznie dataframe finalnego, do ktorego beda dodawane dane z kazdego roku.
Finaldf= pd.DataFrame()

#okreslenie unikalnych lat.
year=dataframe['year'].unique()

base_dir='pliki'


print('Przetwarzanie danych')
sys.stdout.flush()
#dla kazdego roku pobieranie danych
for i in year:


    file_path = os.path.join(base_dir, f"dane{i}.txt")

    #tworzenie dataframe z danymi z danego roku. Rok okreslia i
    df = fu.extract_winner(file_path,i)

    #dodawanie danych do glownego dataframe z danego roku.
    Finaldf = pd.concat([Finaldf,df])

    df2 = fu.extract_nominee(file_path,i)

    #dodawanie danych do glownego dataframe z danego roku.
    Finaldf = pd.concat([Finaldf,df2])





#zapis danych do pliku csv.
Finaldf.to_csv("Finaldf.csv", index=False)

print('Zapis surowych danych do Finaldf.csv')
sys.stdout.flush()

print('Czyszczenie danych')
sys.stdout.flush()


#oddzielenie ['HONORARY AWARD', 'SPECIAL AWARD', 'SPECIAL FOREIGN LANGUAGE FILM AWARD', 'AWARD OF COMMENDATION', 'IRVING G. THALBERG MEMORIAL AWARD']
listaHo=['HONORARY AWARD', 'SPECIAL AWARD', 'SPECIAL FOREIGN LANGUAGE FILM AWARD', 'AWARD OF COMMENDATION', 'IRVING G. THALBERG MEMORIAL AWARD']
maska_z_listaHo = Finaldf['category'].isin(listaHo)

maska_bez_listaHo = ~Finaldf['category'].isin(listaHo)

df_z_listaHo = Finaldf[maska_z_listaHo].copy()

df_bez_listaHo = Finaldf[maska_bez_listaHo].copy()




#Uruchamianie funkcji z pliku fu to czyszczenia danych
newdata = fu.weryfikuj_i_rozdziel_osoby(df_bez_listaHo)

newdata1 = fu.czyszczenie_and(newdata)

newdata2 = fu.usuwanie_dodatkowych_slow(newdata1)

newdata3 = fu.czyszczenie_at(newdata2)

fu.usun_nawiasy_w_miejscu(newdata3, kolumna='aktor')

fu.usun_wszystkie_biale_znaki(newdata3, kolumna='aktor')


#Tworzenie unikalnej listy aktorow
mylist=list(set(newdata3['aktor'].to_list()))


# Informacja o rozpoczęciu procesu Szukanie Podobnych.
print("Szukanie Podobnych ")

# Wymuszenie natychmiastowego wypisania bufora standardowego wyjścia.
sys.stdout.flush()


dane=fu.znajdz_prawie_podobne(mylist)
sys.stdout.flush()

# Informacja o wygenerowaniu sugestii do zmiany.
print("Sugestie do zmiany ")
sys.stdout.flush()

# Wywołanie funkcji 'suguesia_zamiany' z modułu 'fu'
Datazamiana, dozamiany_lista = fu.suguesia_zamiany(dane,newdata3)
sys.stdout.flush()




print("Potwierdz czy akcetpujesz zmiany.")

# Wyświetlenie proponowanych zmian w DataFrame 'Datazamiana'.
print(Datazamiana)
sys.stdout.flush()

# Wywołanie funkcji 'zamiana'
pozamianie=fu.zamiana(newdata3,Datazamiana)


# Wywołanie funkcji 'special_award'
honorary= fu.special_award(df_z_listaHo)


# Połączenie (konkatenacja) DataFrame 'honorary' (nagrody specjalne) i 'pozamianie' (dane po zamianach)
prawiefinal = pd.concat([honorary,pozamianie], ignore_index=True)

# Wywołanie funkcji 'usuwanie_dodatkowych_slow2'
final = fu.usuwanie_dodatkowych_slow2(prawiefinal)



data_filtered = final[~final['aktor'].isnull()]

# Usunięcie wierszy, w których kolumna 'aktor' jest pusta (NaN).

finalClean = data_filtered.dropna(subset=['aktor'])


# Zapisanie wyczyszczonych danych z DataFrame 'finalClean' do pliku CSV
finalClean.to_csv("CleanData.csv", index=False)

# Informacja o pomyślnym zapisaniu czystych danych do pliku CSV.
print('Czyste dane zapisane do CleanData.csv')
sys.stdout.flush()


print('Dane gotowe do Analizy')
sys.stdout.flush()

# Zapis do pliku JSON w formacie tabeli
finalClean.to_json('data_table.json', orient='table')

print('Zapisanie danych do json plik: data_table.json')
sys.stdout.flush()