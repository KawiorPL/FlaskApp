import funkcje as fu
import pandas as pd
import sys

data = pd.read_csv('CleanData.csv')

print("Tworznie wykresu")
sys.stdout.flush()
fu.analizaaktorow(data)
print("Tworznie wykresu2")
fu.winnersfilm(data)

print("Tworznie wykresu3")
fu.mapaswaita(data)