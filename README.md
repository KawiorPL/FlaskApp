# FlaskApp

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Maintenance](https://img.shields.io/badge/Maintained-yes-green.svg)

Prosta aplikacja Flask. 
Niniejszy projekt koncentruje się na demonstracji praktycznego zastosowania technik web scrapingu, przetwarzania danych, analizy statystycznej w kontekście danych dotyczących ceremonii wręczenia Oscarów. Źródłem danych jest publicznie dostępny zbiór "The Oscar Award", uzyskany ze strony internetowej https://oscar.warpechow.ski/. Celem projektu jest ekstrakcja, transformacja i wizualizacja danych w celu identyfikacji trendów i wzorców w historii nagród filmowych. 

## Instalacja

Poniższe kroki opisują, jak zainstalować i uruchomić aplikację na Twoim lokalnym komputerze.

### Wymagania wstępne

* **Python 3.9+** (zalecana wersja) - Możesz pobrać go ze strony [python.org](https://www.python.org/downloads/).
* **Git** - Do sklonowania repozytorium. Możesz pobrać go ze strony [git-scm.com](https://git-scm.com/downloads).
* **Anaconda** (opcjonalnie, dla środowisk Conda) - Możesz pobrać ją ze strony [anaconda.com](https://www.anaconda.com/download/). Lżejszą alternatywą jest [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
* **Virtualenv** (opcjonalnie, dla zwykłych środowisk wirtualnych) - Zazwyczaj jest wbudowany w nowsze wersje Pythona (`python -m venv`).

### Kroki instalacji

1.  **Sklonuj repozytorium z GitHub:**

    Otwórz terminal lub wiersz poleceń i przejdź do folderu, w którym chcesz zainstalować aplikację. Następnie wykonaj polecenie:

    ```bash
    git clone [https://github.com/KawiorPL/FlaskApp.git](https://github.com/KawiorPL/FlaskApp.git)
    cd FlaskApp
    ```

2.  **Utwórz i aktywuj środowisko wirtualne:**

    Wybierz jedną z poniższych opcji w zależności od preferowanego narzędzia:

    #### Opcja A: Użycie Conda (zalecane)

    Jeśli używasz Anacondy lub Minicondy:

    ```bash
    conda create --name flask_env python=3.10.17
    conda activate flask_env
    ```

    #### Opcja B: Użycie venv

    Jeśli nie używasz Condy:

    ```bash
    python -m venv venv
    # Aktywacja środowiska:
    # Windows (CMD):
    .\venv\Scripts\activate
    # Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # macOS/Linux:
    source venv/bin/activate
    ```

    Po aktywacji środowiska nazwa środowiska (`(flask_env)` lub `(venv)`) powinna pojawić się na początku linii poleceń.

3.  **Zainstaluj zależności:**

    Po aktywowaniu środowiska przejdź do folderu `FlaskApp` (jeśli jeszcze tam nie jesteś) i zainstaluj wymagane biblioteki z pliku `requirements.txt`:

    ```bash
    cd FlaskApp
    pip install -r requirements.txt
    ```

    To polecenie zainstaluje wszystkie pakiety wymienione w pliku `requirements.txt`.

### Uruchomienie aplikacji

Po pomyślnej instalacji zależności możesz uruchomić aplikację Flask. Zakładając, że główny plik aplikacji to `app.py`, wykonaj polecenie:

```bash
python app.py
