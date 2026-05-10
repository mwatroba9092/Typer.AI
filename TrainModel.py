import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

print("Wczytywanie zaawansowanej bazy danych...")
df = pd.read_csv('DataBase/5lastSezons_ready.csv')

team_encoder = LabelEncoder()
result_encoder = LabelEncoder()
all_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
team_encoder.fit(all_teams)

df['HomeTeam_Encoded'] = team_encoder.transform(df['HomeTeam'])
df['AwayTeam_Encoded'] = team_encoder.transform(df['AwayTeam'])
df['FTR_Encoded'] = result_encoder.fit_transform(df['FTR'])

# --- TUTAJ JEST ZMIANA: Model otrzymuje aż 9 zmiennych zamiast 4! ---
features = [
    'HomeTeam_Encoded', 'AwayTeam_Encoded', 
    'HomeForm_5', 'AwayForm_5', 
    'HomeAttack_5', 'HomeDefense_5', 
    'AwayAttack_5', 'AwayDefense_5', 
    'H2H_Home_Pts'
]
X = df[features]
y = df['FTR_Encoded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\nRozpoczynamy trening na rozszerzonych danych...\n")

tree_model = DecisionTreeClassifier(max_depth=5, random_state=42)
tree_model.fit(X_train, y_train)
print(f"🌲 Drzewo Decyzyjne: {accuracy_score(y_test, tree_model.predict(X_test)) * 100:.2f}%")

rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
rf_model.fit(X_train, y_train)
print(f"🌳 Las Losowy: {accuracy_score(y_test, rf_model.predict(X_test)) * 100:.2f}%")

nn_model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)
nn_model.fit(X_train, y_train)
print(f"🧠 Sieć Neuronowa: {accuracy_score(y_test, nn_model.predict(X_test)) * 100:.2f}%")

if not os.path.exists('Models'): os.makedirs('Models')
joblib.dump(rf_model, 'Models/best_model.pkl')
joblib.dump(team_encoder, 'Models/team_encoder.pkl')
joblib.dump(result_encoder, 'Models/result_encoder.pkl')

print("\nGotowe! Nowy, mądrzejszy model zapisany.")