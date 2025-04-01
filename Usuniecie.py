import os
import sys
folder_pliki='pliki2'

with open("remove.txt", "r") as plik:
    # Czytanie zawartości pliku
    dane = plik.readlines()


sys.stdout.flush()
for i in dane:
    rok_do_usuniecia = i.strip()
    nazwa_pliku_do_usuniecia = os.path.join(folder_pliki, f"dane{rok_do_usuniecia}.txt")
    if os.path.exists(nazwa_pliku_do_usuniecia):
        os.remove(nazwa_pliku_do_usuniecia)
        print(f"Usunięto plik: dane{rok_do_usuniecia}.txt")
        sys.stdout.flush()


