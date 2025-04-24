import os
from bs4 import BeautifulSoup




# Ścieżka do folderu zawierającego pliki do sprawdzenia.
folder_sciezka='pliki'

# Sprawdzenie, czy folder istnieje. Jeśli nie, wypisanie błędu i zakończenie.
if not os.path.isdir(folder_sciezka):
    print(f"Błąd: Folder '{folder_sciezka}' nie istnieje.")


# Inicjalizacja pustych list do przechowywania nazw plików do usunięcia i poprawnych danych.
to_remove=[]
poprawne=[]


# Iteracja po wszystkich elementach wewnątrz podanego folderu.
for nazwa_pliku in os.listdir(folder_sciezka):
    # Sprawdzenie, czy dany element jest plikiem z rozszerzeniem ".txt".
    if nazwa_pliku.endswith(".txt"):
        # Utworzenie pełnej ścieżki do pliku.
        sciezka_do_pliku = os.path.join(folder_sciezka, nazwa_pliku)
        try:
            # Otwarcie pliku w trybie do odczytu z kodowaniem UTF-8.
            with open(sciezka_do_pliku, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            h1_tag = soup.find('h1')

             # Sprawdzenie, czy znacznik <h1> został znaleziony
            if h1_tag:
                h1_text = h1_tag.text.strip()
                data = h1_text.split()

                ostatnie_cztery_cyfry = data[-1]
                 # Pobranie ostatnich czterech znaków z nazwy pliku (bez rozszerzenia)
                nazwa_bez_rozszerzenia = nazwa_pliku[-8:-4]

                 # Porównanie ostatnich czterech znaków nazwy pliku z ostatnim słowem z <h1>.
                if nazwa_bez_rozszerzenia == ostatnie_cztery_cyfry:
                    poprawne.append(nazwa_bez_rozszerzenia)

                else:
                    # Jeśli nie są zgodne, sprawdzenie warunków wykluczających
                    if nazwa_bez_rozszerzenia =='inki' or ostatnie_cztery_cyfry =='Years':
                        continue
                    else:
                        # W przeciwnym razie, wypisanie informacji o błędzie i dodanie nazwy bez rozszerzenia do listy plików do usunięcia.
                        print(f"Blad w {nazwa_bez_rozszerzenia} and {ostatnie_cztery_cyfry}\n")
                        to_remove.append(nazwa_bez_rozszerzenia)


           # Obsługa błędów, które mogły wystąpić podczas przetwarzania pliku (np. problem z otwarciem, odczytem, parsowaniem).
        except Exception as e:
            print(f"Błąd podczas przetwarzania pliku: {e}")

print(f'Poprawne dane w {" ".join(poprawne)}\n')


# Sprawdzenie, czy lista plików do usunięcia nie jest pusta.
if to_remove:
    listaDoUsuniecia = "remove.txt"

    try:
        with open(listaDoUsuniecia, 'w') as plik:
            for i in to_remove:
                linia = f"{i}\n"
                plik.write(linia)
        print(f"Błędne dane zostały zapisane do pliku: {listaDoUsuniecia}")
    except Exception as e:
        print(f"Wystąpił błąd podczas zapisywania do pliku: {e}")

# Jeśli nie ma błędnych danych, wypisanie odpowiedniej informacji.
else:
    print('Brak błędnych danych')