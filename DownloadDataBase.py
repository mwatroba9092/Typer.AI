import pandas as pd
import os

# 1. Top 5 lig europejskich
leagues = {
    'E0': 'Premier League',
    'SP1': 'La Liga',
    'D1': 'Bundesliga',
    'I1': 'Serie A',
    'F1': 'Ligue 1'
}

# Sezony (ewetualnie mozna dodac wiecej)
seasons = ['2122', '2223', '2324', '2425', '2526']

all_data = []

print("Rozpoczynam pobieranie danych dla Typer.ai z 5 sezonów...\n")

# 2. Pobieramy dane dla każdego sezonu i każdej ligi
for season in seasons:
    print(f"--- Pobieranie sezonu {season} ---")
    for league_code, league_name in leagues.items():
        url = f"https://www.football-data.co.uk/mmz4281/{season}/{league_code}.csv"
        
        try:
            df = pd.read_csv(url)
            df['League'] = league_name
            df['Season'] = season
            
            # Zostawiamy potrzebne kolumny
            cols_to_keep = ['League', 'Season', 'Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
            
            available_cols = [col for col in cols_to_keep if col in df.columns]
            df = df[available_cols]
            
            all_data.append(df)
            print(f"  Pobrano: {league_name}")
        except Exception as e:
            print(f"  [BŁĄD] Nie udało się pobrać {league_name} dla sezonu {season}. Powód: {e}")

# 3. Łączymy wszystkie dane
final_data = pd.concat(all_data, ignore_index=True)

print("\n--- ZAKOŃCZONO POBIERANIE ---")
print(f"Pobrano łącznie {final_data.shape[0]} meczów!")

# 4. Zapis danych do pliku CSV
if not os.path.exists('DataBase'):
    os.makedirs('DataBase')

sciezka_zapisu = 'DataBase/5lastSezons.csv'
final_data.to_csv(sciezka_zapisu, index=False)

print(f"Dane zapisane bezpiecznie w: {sciezka_zapisu}")