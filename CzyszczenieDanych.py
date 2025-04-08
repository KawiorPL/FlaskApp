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

    #okreslenie sciezki dla danego roku.
    file_name=dataframe.loc[dataframe['year'] == i]['link'].values[0]

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





newdata = fu.weryfikuj_i_rozdziel_osoby(df_bez_listaHo)

newdata1 = fu.czyszczenie_and(newdata)

newdata2 = fu.usuwanie_dodatkowych_slow(newdata1)

newdata3 = fu.czyszczenie_at(newdata2)

fu.usun_nawiasy_w_miejscu(newdata3, kolumna='aktor')

fu.usun_wszystkie_biale_znaki(newdata3, kolumna='aktor')

mylist=list(set(newdata3['aktor'].to_list()))


print("Szukanie Podobnych ")
sys.stdout.flush()
dane=fu.znajdz_prawie_podobne(mylist)
sys.stdout.flush()


print("Sugestie do zmiany ")
sys.stdout.flush()
Datazamiana, dozamiany_lista = fu.suguesia_zamiany(dane,newdata3)
sys.stdout.flush()




print("Potwierdz czy akcetpujesz zmiany.")
print(Datazamiana)
sys.stdout.flush()


pozamianie=fu.zamiana(newdata3,Datazamiana)



Honor= fu.special_award(df_z_listaHo)



prawiefinal = pd.concat([Honor,pozamianie], ignore_index=True)

final = fu.usuwanie_dodatkowych_slow2(prawiefinal)




final.to_csv("CleanData.csv", index=False)

print('Czyste dane zapisane do CleanData.csv')
sys.stdout.flush()


print('Dane gotowe do Analizy')
sys.stdout.flush()

# Zapis do pliku JSON w formacie tabeli
newdata3.to_json('data_table.json', orient='table')

print('Zapisanie danych do json plik: data_table.json')
sys.stdout.flush()