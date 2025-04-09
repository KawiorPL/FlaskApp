import os
from bs4 import BeautifulSoup





folder_sciezka='pliki'

if not os.path.isdir(folder_sciezka):
    print(f"Błąd: Folder '{folder_sciezka}' nie istnieje.")

to_remove=[]
poprawne=[]
for nazwa_pliku in os.listdir(folder_sciezka):
    if nazwa_pliku.endswith(".txt"):
        sciezka_do_pliku = os.path.join(folder_sciezka, nazwa_pliku)
        try:
            with open(sciezka_do_pliku, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            h1_tag = soup.find('h1')

            if h1_tag:
                h1_text = h1_tag.text.strip()
                data = h1_text.split()

                ostatnie_cztery_cyfry = data[-1]
                nazwa_bez_rozszerzenia = nazwa_pliku[-8:-4]

                if nazwa_bez_rozszerzenia == ostatnie_cztery_cyfry:
                    poprawne.append(nazwa_bez_rozszerzenia)

                else:

                    if nazwa_bez_rozszerzenia =='inki' or ostatnie_cztery_cyfry =='Years':
                        continue
                    else:
                        print(f"Blad w {nazwa_bez_rozszerzenia} and {ostatnie_cztery_cyfry}\n")
                        to_remove.append(nazwa_bez_rozszerzenia)



        except Exception as e:
            print(f"Błąd podczas przetwarzania pliku: {e}")

print(f'Poprawne dane w {" ".join(poprawne)}\n')

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

else:
    print('Brak błędnych danych')