import funkcje as fu
import pandas as pd
import sys

# Wczytanie danych z pliku CSV
data = pd.read_csv('CleanData.csv')

# Informacja o rozpoczęciu tworzenia pierwszego wykresu.
print("Tworznie wykresu")

# Wymuszenie natychmiastowego wypisania bufora standardowego wyjścia.
sys.stdout.flush()

#Wywołanie funkcji z modułu 'fu' w celu wygenerowania analizy aktorów na podstawie wczytanych danych.

fu.analizaaktorow(data)

#Wywołanie funkcji z modułu 'fu' w celu wygenerowania wykresu
# Informacja o rozpoczęciu tworzenia 2 wykresu.
print("Tworznie wykresu2")
fu.winnersfilm(data)

#Wywołanie funkcji z modułu 'fu' w celu wygenerowania mapy swiata.
# Informacja o rozpoczęciu tworzenia 3 wykresu.
print("Tworznie wykresu3")
fu.mapaswaita(data)