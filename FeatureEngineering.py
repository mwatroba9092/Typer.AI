import pandas as pd

print("Rozpoczynam Zaawansowaną Inżynierię Cech (Forma, Gole, H2H)...")

df = pd.read_csv('DataBase/5lastSezons.csv')
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df = df.sort_values('Date').reset_index(drop=True)

# Słowniki pamięci
team_history = {} # klucz: drużyna, wartość: lista [(punkty, strzelone, stracone)]
h2h_history = {}  # klucz: para drużyn, wartość: lista [zwycięzca_meczu]

def get_points(result, role):
    if result == 'D': return 1
    if (result == 'H' and role == 'Home') or (result == 'A' and role == 'Away'): return 3
    return 0

# Nowe puste kolumny
home_forms, away_forms = [], []
home_attack, away_attack = [], []
home_defense, away_defense = [], []
h2h_home_pts_list = []

for index, row in df.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    res = row['FTR']
    hg = row['FTHG'] # Gole gospodarza
    ag = row['FTAG'] # Gole gościa
    
    if home not in team_history: team_history[home] = []
    if away not in team_history: team_history[away] = []
    
    # 1. ZBIERANIE FORMY I GOLI (ostatnie 5 meczów)
    home_past = team_history[home][-5:]
    away_past = team_history[away][-5:]
    
    home_forms.append(sum([x[0] for x in home_past]))
    home_attack.append(sum([x[1] for x in home_past]))
    home_defense.append(sum([x[2] for x in home_past]))
    
    away_forms.append(sum([x[0] for x in away_past]))
    away_attack.append(sum([x[1] for x in away_past]))
    away_defense.append(sum([x[2] for x in away_past]))
    
    # 2. ZBIERANIE H2H (Head-to-Head - bezpośrednie starcia)
    teams_tuple = tuple(sorted([home, away]))
    if teams_tuple not in h2h_history: h2h_history[teams_tuple] = []
    
    # Punkty gospodarza w ostatnich 5 wspólnych meczach
    h2h_past = h2h_history[teams_tuple][-5:]
    home_h2h_pts = sum([3 if winner == home else (1 if winner == 'Draw' else 0) for winner in h2h_past])
    h2h_home_pts_list.append(home_h2h_pts)
    
    # --- AKTUALIZACJA HISTORII NA PRZYSZŁOŚĆ ---
    team_history[home].append((get_points(res, 'Home'), hg, ag))
    team_history[away].append((get_points(res, 'Away'), ag, hg))
    
    winner = home if res == 'H' else (away if res == 'A' else 'Draw')
    h2h_history[teams_tuple].append(winner)

# Przypisanie nowych kolumn do tabeli
df['HomeForm_5'] = home_forms
df['HomeAttack_5'] = home_attack
df['HomeDefense_5'] = home_defense

df['AwayForm_5'] = away_forms
df['AwayAttack_5'] = away_attack
df['AwayDefense_5'] = away_defense

df['H2H_Home_Pts'] = h2h_home_pts_list

# Usuwamy początkowe mecze, w których drużyny nie miały jeszcze historii
df = df.dropna()

df.to_csv('DataBase/5lastSezons_ready.csv', index=False)
print("Gotowe! Wygenerowano nowe cechy: Gole Strzelone, Stracone oraz Historię H2H.")