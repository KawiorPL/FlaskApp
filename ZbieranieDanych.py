from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random
import funkcje as fu
import os



import sys
import datetime

print("Rozpoczęto uruchuamianie danych ...\n")
sys.stdout.flush()

if len(sys.argv) > 1:
    url = sys.argv[1]

    print(f"Otrzymano URL: {url}")
    sys.stdout.flush()

    print(f"Dane zebrane ze strony: {url}")
    sys.stdout.flush()

    main = url
    folder = 'pliki'


    sonda = fu.Sonda(main, folder)

    if sonda:
        print('sonda skonczona')
        sys.stdout.flush()

    test_file_path = os.path.join(folder, "linki.txt")
    if os.path.exists(test_file_path):
        x = fu.DatFrameYearLink(test_file_path)


        sys.stdout.flush()

        if isinstance(x, pd.DataFrame):
            csv_file_path = "years_and_links.csv"
            x.to_csv(csv_file_path, index=False, encoding='utf-8')
            print(f"Dane zostały zapisane do pliku {csv_file_path}")
            sys.stdout.flush()
            dataframe = pd.read_csv(csv_file_path)
            print("Rzut z DataFrame")
            print(dataframe)
            sys.stdout.flush()


            year_list = dataframe['year'].unique().tolist()
            lata = []
            for nazwa_pliku in os.listdir(folder):
                if nazwa_pliku.startswith("dane") and nazwa_pliku.endswith(".txt") and len(nazwa_pliku) >= 8:
                    rok_z_pliku = nazwa_pliku[-8:-4]  # Wyciągnij 4 znaki przed ".txt"
                    if rok_z_pliku.isdigit():
                        lata.append(int(rok_z_pliku))

            # Usuń z year_list elementy, które znajdują się w lata
            year_list_to_process = [rok for rok in year_list if rok not in lata]

            pobrane = [rok for rok in year_list if rok in lata]


            print(f"Lista lat do przetworzenia: {year_list_to_process}")
            sys.stdout.flush()

            print(f"Lista lat pobrana: {pobrane}")
            sys.stdout.flush()

            while len(year_list_to_process) > 0:
                remaining_pages = len(year_list_to_process)
                start_time = time.time()  # Zapisz czas rozpoczęcia iteracji

                print(f"Pozostało {remaining_pages} stron do skopiowania.\n")
                sys.stdout.flush()
                try:
                    wylosowany_element = random.choice(year_list_to_process)
                    print(f"Pobierany rok {wylosowany_element}")
                    sys.stdout.flush()
                    second = dataframe.loc[dataframe['year'] == wylosowany_element]['link'].values[0]
                    go = main + second

                    response = requests.get(go)
                    dane = response.text

                    #sprawdzanie czy to ten sam rok
                    soup = BeautifulSoup(dane, 'html.parser')
                    h1_tag = soup.find('h1')

                    if h1_tag:
                        h1_text = h1_tag.text.strip()
                        rok = h1_text.split()

                        ostatnie_cztery_cyfry = rok[-1]



                    if len(dane) > 10000 and int(ostatnie_cztery_cyfry) == int(wylosowany_element):
                        output_file_path = os.path.join(folder, f"dane{wylosowany_element}.txt")
                        with open(output_file_path, "w", encoding='utf-8') as f:

                            f.write(dane)
                        print(f"Pobrano dane dla roku {wylosowany_element} i zapisano do {output_file_path}")
                        sys.stdout.flush()
                        year_list_to_process.remove(wylosowany_element)
                        pobrane.append(wylosowany_element)
                    else:
                        print('Nie udalo sie pobrac pelnych danych. Plik nie zostanie zapisany.')
                        with open(f"bledy/bledne{wylosowany_element}.txt", "w", encoding='utf-8') as f:
                            f.write(go)
                            f.write("\n")
                            f.write(dane)
                        print(f"Zapisanow bledne dane dla roku {wylosowany_element} i zapisano do: bledne{wylosowany_element}.txt")
                        sys.stdout.flush()
                        time.sleep(125)
                    sleep_time = random.randint(50, 150)
                    time.sleep(sleep_time)
                except UnicodeEncodeError:
                    print(f"Błąd kodowania Unicode podczas przetwarzania roku {wylosowany_element}. Pomijam.")
                    sys.stdout.flush()
                    time.sleep(100)
                except requests.exceptions.RequestException as e:
                    print(f"Błąd podczas pobierania danych dla roku {wylosowany_element}: {e}")
                    sys.stdout.flush()
                    time.sleep(100)
                except IndexError:
                    print(f"Błąd: Nie znaleziono linku dla roku {wylosowany_element}.")
                    sys.stdout.flush()
                    if wylosowany_element in year_list_to_process:
                        year_list_to_process.remove(wylosowany_element)
                    time.sleep(50)
                finally:
                    end_time = time.time()  # Zapisz czas zakończenia iteracji
                    iteration_time = end_time - start_time
                    expected_seconds = remaining_pages * iteration_time
                    expected_time = datetime.timedelta(seconds=expected_seconds)
                    hours = expected_time.seconds // 3600
                    minutes = (expected_time.seconds % 3600) // 60
                    print(f"Oczekiwany czas ukończenia (przybliżony): {hours} godzin i {minutes} minut.\n")
                    sys.stdout.flush()
        else:
            print(f"Plik {test_file_path} nie istnieje. Nie można przetworzyć linków.")
            sys.stdout.flush()
    else:
        print("Błąd: Nie podano wymaganych argumentów (folder i URL).")
        sys.stdout.flush()

    print("Zbieranie danych zakończone. Dane z wszystkich lat pobrane")
    sys.stdout.flush()
    try:
        if pobrane:

            final = pobrane.sort()
            print(f"Pelna Lista:{pobrane}")
    except NameError:
        pass
    sys.stdout.flush()



recznie=False

if recznie:
    url = 'https://oscar.warpechow.ski/'

    print(f"Otrzymano URL: {url}")
    sys.stdout.flush()

    print(f"Dane zebrane ze strony: {url}")
    sys.stdout.flush()

    main = url
    folder = 'pliki'


    sonda = fu.Sonda(main, folder)

    if sonda:
        print('sonda skonczona')
        sys.stdout.flush()

    test_file_path = os.path.join(folder, "linki.txt")
    if os.path.exists(test_file_path):
        x = fu.DatFrameYearLink(test_file_path)


        sys.stdout.flush()

        if isinstance(x, pd.DataFrame):
            csv_file_path = "years_and_links.csv"
            x.to_csv(csv_file_path, index=False, encoding='utf-8')
            print(f"Dane zostały zapisane do pliku {csv_file_path}")
            sys.stdout.flush()
            dataframe = pd.read_csv(csv_file_path)
            print("Rzut z DataFrame")
            print(dataframe)
            sys.stdout.flush()


            year_list = dataframe['year'].unique().tolist()
            lata = []
            for nazwa_pliku in os.listdir(folder):
                if nazwa_pliku.startswith("dane") and nazwa_pliku.endswith(".txt") and len(nazwa_pliku) >= 8:
                    rok_z_pliku = nazwa_pliku[-8:-4]  # Wyciągnij 4 znaki przed ".txt"
                    if rok_z_pliku.isdigit():
                        lata.append(int(rok_z_pliku))

            # Usuń z year_list elementy, które znajdują się w lata
            year_list_to_process = [rok for rok in year_list if rok not in lata]

            pobrane = [rok for rok in year_list if rok in lata]


            print(f"Lista lat do przetworzenia: {year_list_to_process}")
            sys.stdout.flush()

            print(f"Lista lat pobrana: {pobrane}")
            sys.stdout.flush()

            while len(year_list_to_process) > 0:
                remaining_pages = len(year_list_to_process)
                start_time = time.time()  # Zapisz czas rozpoczęcia iteracji

                print(f"Pozostało {remaining_pages} stron do skopiowania.\n")
                sys.stdout.flush()
                try:
                    wylosowany_element = random.choice(year_list_to_process)
                    print(f"Pobierany rok {wylosowany_element}")
                    sys.stdout.flush()
                    second = dataframe.loc[dataframe['year'] == wylosowany_element]['link'].values[0]
                    go = main + second

                    response = requests.get(go)
                    dane = response.text

                    #sprawdzanie czy to ten sam rok
                    soup = BeautifulSoup(dane, 'html.parser')
                    h1_tag = soup.find('h1')

                    if h1_tag:
                        h1_text = h1_tag.text.strip()
                        rok = h1_text.split()

                        ostatnie_cztery_cyfry = rok[-1]



                    if len(dane) > 10000 and int(ostatnie_cztery_cyfry) == int(wylosowany_element):
                        output_file_path = os.path.join(folder, f"dane{wylosowany_element}.txt")
                        with open(output_file_path, "w", encoding='utf-8') as f:

                            f.write(dane)
                        print(f"Pobrano dane dla roku {wylosowany_element} i zapisano do {output_file_path}")
                        sys.stdout.flush()
                        year_list_to_process.remove(wylosowany_element)
                        pobrane.append(wylosowany_element)
                    else:
                        print('Nie udalo sie pobrac pelnych danych. Plik nie zostanie zapisany.')
                        with open(f"bledy/bledne{wylosowany_element}.txt", "w", encoding='utf-8') as f:
                            f.write(go)
                            f.write("\n")
                            f.write(dane)
                        print(f"Zapisanow bledne dane dla roku {wylosowany_element} i zapisano do: bledne{wylosowany_element}.txt")
                        sys.stdout.flush()
                        time.sleep(125)
                    sleep_time = random.randint(50, 150)
                    time.sleep(sleep_time)
                except UnicodeEncodeError:
                    print(f"Błąd kodowania Unicode podczas przetwarzania roku {wylosowany_element}. Pomijam.")
                    sys.stdout.flush()
                    time.sleep(100)
                except requests.exceptions.RequestException as e:
                    print(f"Błąd podczas pobierania danych dla roku {wylosowany_element}: {e}")
                    sys.stdout.flush()
                    time.sleep(100)
                except IndexError:
                    print(f"Błąd: Nie znaleziono linku dla roku {wylosowany_element}.")
                    sys.stdout.flush()
                    if wylosowany_element in year_list_to_process:
                        year_list_to_process.remove(wylosowany_element)
                    time.sleep(50)
                finally:
                    end_time = time.time()  # Zapisz czas zakończenia iteracji
                    iteration_time = end_time - start_time
                    expected_seconds = remaining_pages * iteration_time
                    expected_time = datetime.timedelta(seconds=expected_seconds)
                    hours = expected_time.seconds // 3600
                    minutes = (expected_time.seconds % 3600) // 60
                    print(f"Oczekiwany czas ukończenia (przybliżony): {hours} godzin i {minutes} minut.\n")
                    sys.stdout.flush()
        else:
            print(f"Plik {test_file_path} nie istnieje. Nie można przetworzyć linków.")
            sys.stdout.flush()
    else:
        print("Błąd: Nie podano wymaganych argumentów (folder i URL).")
        sys.stdout.flush()

    print("Zbieranie danych zakończone. Dane z wszystkich lat pobrane")
    sys.stdout.flush()
    try:
        if pobrane:

            final = pobrane.sort()
            print(f"Pelna Lista:{pobrane}")
    except NameError:
        pass
    sys.stdout.flush()