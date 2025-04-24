import os
import sys

"""Skrypt nalezy uruchomic recznie"""




folder_pliki='pliki' # Określenie folderu, w którym znajdują się pliki do usunięcia.

file='remove.txt'
remove = os.path.exists(file)

if remove:
    with open("remove.txt", "r") as plik:
        # Czytanie zawartości pliku
        dane = plik.readlines()


    sys.stdout.flush()
    for i in dane:  # Iteracja po liniach odczytanych z pliku.
        rok_do_usuniecia = i.strip()  # Usunięcie białych znaków (np. spacji, znaków nowej linii) z początku i końca linii, która reprezentuje rok.
        nazwa_pliku_do_usuniecia = os.path.join(folder_pliki, f"dane{rok_do_usuniecia}.txt")  # Utworzenie pełnej ścieżki do pliku, który ma zostać usunięty.
        # Użycie f-string do wstawienia wartości zmiennej 'rok_do_usuniecia' do nazwy pliku.
        if os.path.exists(nazwa_pliku_do_usuniecia):  # Sprawdzenie, czy plik o podanej ścieżce istnieje.
            os.remove(nazwa_pliku_do_usuniecia)  # Jeśli plik istnieje, usunięcie go.
            print(f"Usunięto plik: dane{rok_do_usuniecia}.txt")  # Wypisanie komunikatu o usunięciu pliku.
            sys.stdout.flush()
        # Jeśli plik nie istnieje, pętla przechodzi do kolejnej iteracji (kolejnego roku z pliku "remove.txt").

else:
    print('Brak plików do usuniecia')


