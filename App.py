import streamlit as st
import pandas as pd
import joblib

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Typer.AI", page_icon="⚽", layout="centered")

# --- FRONTEND ---
st.markdown("""
    <style>
    /* Główne tło (Czerń/Ciemny Grafit) i tekst (Jasny Szary) */
    .stApp {
        background-color: #121212;
        color: #d4d4d4;
    }
    
    /* Nagłówki (Fiolet) */
    h1, h2, h3 {
        color: #9d4edd !important;
        font-family: 'Trebuchet MS', sans-serif;
    }
    
    /* Panel boczny (Sidebar - Ciemny Szary) */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        border-right: 1px solid #3a3a3a;
    }
    
    /* Przycisk predykcji (Szary z fioletowym akcentem, po najechaniu Fioletowy) */
    .stButton>button {
        background-color: #2b2b2b;
        color: white;
        border-radius: 8px;
        border: 1px solid #7b2cbf;
        transition: 0.3s;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #7b2cbf;
        border: 1px solid #9d4edd;
        color: white;
    }
    
    /* Panele informacyjne (Szare tło, fioletowy pasek z lewej) */
    div[data-testid="stAlert"] {
        background-color: #262626;
        border-left-color: #9d4edd;
        color: #e0e0e0;
    }
    
    /* Wskaźniki procentowe (Metrics - Jasny Fiolet i Szary) */
    [data-testid="stMetricValue"] {
        color: #c77dff;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0a0;
    }
    
    /* Pasek postępu (Fiolet) */
    .stProgress > div > div > div > div {
        background-color: #9d4edd;
    }
    
    /* Pola wyboru (Selectbox) - dopasowanie do ciemnego motywu */
    div[data-baseweb="select"] > div {
        background-color: #2b2b2b;
        color: white;
        border-color: #3a3a3a;
    }
    </style>
""", unsafe_allow_html=True)

# --- WCZYTYWANIE MODELI I DANYCH ---
@st.cache_resource
def load_models():
    model = joblib.load('Models/best_model.pkl')
    team_encoder = joblib.load('Models/team_encoder.pkl')
    result_encoder = joblib.load('Models/result_encoder.pkl')
    return model, team_encoder, result_encoder

@st.cache_data
def load_data():
    df = pd.read_csv('DataBase/5lastSezons_ready.csv')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    return df

model, team_encoder, result_encoder = load_models()
df = load_data()

# --- FUNKCJE ANALIZUJĄCE ---
def get_team_stats(team, df):
    past_matches = df[(df['HomeTeam'] == team) | (df['AwayTeam'] == team)].sort_values(by='Date', ascending=False).head(5)
    pts, scored, conceded = 0, 0, 0
    for _, row in past_matches.iterrows():
        if row['HomeTeam'] == team:
            if row['FTR'] == 'H': pts += 3
            elif row['FTR'] == 'D': pts += 1
            scored += row['HomeAttack_5']
            conceded += row['HomeDefense_5']
        else:
            if row['FTR'] == 'A': pts += 3
            elif row['FTR'] == 'D': pts += 1
            scored += row['AwayAttack_5']
            conceded += row['AwayDefense_5']
    if not past_matches.empty:
        last_match = past_matches.iloc[0]
        if last_match['HomeTeam'] == team: return pts, last_match['HomeAttack_5'], last_match['HomeDefense_5']
        else: return pts, last_match['AwayAttack_5'], last_match['AwayDefense_5']
    return 0, 0, 0

def get_h2h_stats(home, away, df):
    h2h_matches = df[((df['HomeTeam'] == home) & (df['AwayTeam'] == away)) | ((df['HomeTeam'] == away) & (df['AwayTeam'] == home))].sort_values(by='Date', ascending=False).head(5)
    pts = 0
    for _, row in h2h_matches.iterrows():
        winner = row['HomeTeam'] if row['FTR'] == 'H' else (row['AwayTeam'] if row['FTR'] == 'A' else 'Draw')
        if winner == home: pts += 3
        elif winner == 'Draw': pts += 1
    return pts

# --- FRONTEND: PANEL BOCZNY (SIDEBAR) ---
st.sidebar.title("⚙️ Parametry wejściowe")
st.sidebar.markdown("Skonfiguruj filtry danych przed uruchomieniem predykcji.")

lista_lig = ["Wszystkie Ligi"] + sorted(df['League'].dropna().unique().tolist())
wybrana_liga = st.sidebar.selectbox("Filtrowanie Ligi:", lista_lig)

if wybrana_liga != "Wszystkie Ligi":
    df_filtered = df[df['League'] == wybrana_liga]
else:
    df_filtered = df

all_teams_sorted = sorted(pd.concat([df_filtered['HomeTeam'], df_filtered['AwayTeam']]).dropna().unique())

st.sidebar.divider()
st.sidebar.info("Model klasyfikacyjny: Random Forest (Las Losowy)\n\nZbiór uczący: 5 ostatnich sezonów.")

# --- FRONTEND: GŁÓWNY EKRAN ---
st.title("⚽ Typer.AI")
st.markdown("### Zaawansowana analityka sportowa i predykcja wyników")
st.write("System wykorzystuje algorytmy uczenia maszynowego do estymacji prawdopodobieństwa wyników na podstawie historycznych danych wejściowych, takich jak bieżąca forma, skuteczność bramkowa oraz bezpośrednie starcia (H2H).")
st.divider()

col1, col2 = st.columns(2)
with col1: 
    default_home = all_teams_sorted.index("Real Madrid") if "Real Madrid" in all_teams_sorted else 0
    home_team = st.selectbox("Wybierz Gospodarza (Home):", all_teams_sorted, index=default_home)
    
with col2: 
    default_away = all_teams_sorted.index("Barcelona") if "Barcelona" in all_teams_sorted else (1 if len(all_teams_sorted) > 1 else 0)
    away_team = st.selectbox("Wybierz Gościa (Away):", all_teams_sorted, index=default_away)

st.write("")

# --- LOGIKA AI ---
if st.button("Uruchom Analizę Predykcyjną", use_container_width=True):
    if home_team == away_team:
        st.error("Błąd: Wybrano tę samą drużynę dla obu stron. Proszę wskazać różnych przeciwników.")
    else:
        with st.spinner("Inicjalizacja modeli i pobieranie wektorów cech..."):
            h_form, h_att, h_def = get_team_stats(home_team, df)
            a_form, a_att, a_def = get_team_stats(away_team, df)
            h2h_pts = get_h2h_stats(home_team, away_team, df)
            
            st.info(f"📊 **Bieżąca forma ({home_team}):** {h_form} pkt. | Bilans bramek: {h_att}:{h_def} (ostatnie 5 meczów)")
            st.info(f"📊 **Bieżąca forma ({away_team}):** {a_form} pkt. | Bilans bramek: {a_att}:{a_def} (ostatnie 5 meczów)")
            st.info(f"⚔️ **Statystyki H2H:** W ostatnich 5 bezpośrednich spotkaniach gospodarz zdobył {h2h_pts} pkt.")
            
            home_encoded = team_encoder.transform([home_team])[0]
            away_encoded = team_encoder.transform([away_team])[0]
            
            input_data = pd.DataFrame([[home_encoded, away_encoded, h_form, a_form, h_att, h_def, a_att, a_def, h2h_pts]], 
                                      columns=['HomeTeam_Encoded', 'AwayTeam_Encoded', 'HomeForm_5', 'AwayForm_5', 'HomeAttack_5', 'HomeDefense_5', 'AwayAttack_5', 'AwayDefense_5', 'H2H_Home_Pts'])
            
            probabilities = model.predict_proba(input_data)[0]
            classes = result_encoder.inverse_transform(model.classes_)
            prob_dict = {res: prob for res, prob in zip(classes, probabilities)}
            
            st.divider()
            st.subheader("Estymowane Prawdopodobieństwo Wyniku:")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric(label=f"Zwycięstwo: {home_team}", value=f"{prob_dict.get('H', 0)*100:.1f}%")
            res_col2.metric(label="Remis", value=f"{prob_dict.get('D', 0)*100:.1f}%")
            res_col3.metric(label=f"Zwycięstwo: {away_team}", value=f"{prob_dict.get('A', 0)*100:.1f}%")
            
            st.progress(int(prob_dict.get('H', 0)*100))