import streamlit as st
import google.generativeai as genai
from PIL import Image
import csv
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="MarketScanner Niger",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS OPTIMISÉ ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stProgress > div > div > div > div { background-color: #d97706; }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        border-left: 5px solid #d97706;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .style-tag { 
        background-color: #e5e7eb; 
        padding: 5px 10px; 
        border-radius: 15px; 
        font-size: 0.8em; 
        color: #374151; 
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION CLÉ API ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    with st.expander("🔐 Configuration (Admin)"):
        api_key = st.text_input("Clé API Google Gemini", type="password")

# --- FONCTION DE SAUVEGARDE ---
def save_data(furniture_type, style, material, price, score, risk_level):
    try:
        file_exists = os.path.exists("data_meubles.csv")
        with open("data_meubles.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Date", "Type_Meuble", "Style", "Matiere_Reelle", "Prix_FCFA", "Score_Global", "Niveau_Risque"])
            writer.writerow([datetime.now(), furniture_type, style, material, price, score, risk_level])
    except Exception as e:
        print(f"Erreur sauvegarde CSV: {e}")

# --- FONCTION INTELLIGENTE : CHOIX DU MODÈLE ---
def get_best_available_model():
    """Scanne les modèles disponibles et privilégie le plus puissant (PRO)"""
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # ORDRE DE PRÉFÉRENCE (Du plus puissant au plus rapide)
        preferences = [
            'models/gemini-1.5-pro',         # Le plus intelligent (Top qualité)
            'models/gemini-1.5-pro-001',     # Version stable précédente
            'models/gemini-1.5-flash',       # Le plus rapide (Roue de secours)
            'models/gemini-1.5-flash-001',
            'models/gemini-pro'              # Ancienne génération
        ]

        # On prend le premier de la liste de préférence qui existe dans les modèles disponibles
        for pref in preferences:
            if pref in available_models:
                return pref
        
        # Si on ne trouve rien de précis, on cherche n'importe quoi avec 'gemini'
        for m in available_models:
            if 'gemini' in m:
                return m
                    
        return 'gemini-1.5-flash' # Fallback ultime
    except Exception as e:
        return None

# --- FONCTION D'ANALYSE ---
def analyze_image(image, price, api_key):
    genai.configure(api_key=api_key)
    
    # 1. Définition du Prompt
    prompt = f"""
    Tu es un expert en ameublement basé à Niamey, Niger.
    CONTEXTE : Analyse d'un meuble d'occasion pour un acheteur potentiel sur mobile.
    PRIX PROPOSÉ : {price} FCFA.
    CLIMAT : Sahélien.

    --- ÉTAPE 1 : SÉCURITÉ ---
    Est-ce un meuble ? Si NON, réponds : "ERREUR_NON_MEUBLE".
    Si OUI, passe à l'étape 2.

    --- ÉTAPE 2 : ANALYSE ---
    Réponds avec ce format exact (une info par ligne) :
    TYPE_PRECIS: [Type]
    STYLE_DESIGN: [Style]
    MATIERE_REELLE: [Matière]
    ETAT_STRUCTURE: [Bon/Moyen/Mauvais]
    SCORE_CLIMAT_SAHEL: [Note/10]
    SCORE_GLOBAL: [Note/10]
    VERDICT_PRIX: [Cher/Correct/Affaire]
    ANALYSE_VISUELLE: [3 phrases]
    CONSEIL_NEGOCIATION: [1 phrase]
    """

    # 2. Recherche automatique du bon modèle
    model_name = get_best_available_model()
    
    if not model_name:
        return "ERREUR_DETAIL: Impossible de lister les modèles. Vérifiez que 'Generative Language API' est activé dans votre console Google Cloud."

    try:
        # 3. Tentative avec le modèle trouvé
        # print(f"Tentative avec le modèle : {model_name}") # Debug
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return response.text

    except Exception as e:
        return f"ERREUR_DETAIL: Échec avec le modèle {model_name}. Erreur : {str(e)}"

# --- INTERFACE ---
st.title("🇳🇪 MarketScanner")
st.caption("L'Expert Meuble dans votre poche")

# Indicateur du modèle utilisé (pour vérifier qu'on est bien en PRO)
# On le cache pour l'utilisateur final, utile pour le debug
# st.caption(f"🤖 IA : {get_best_available_model()}")

uploaded_file = st.file_uploader("Photo du meuble", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")

if not uploaded_file:
    st.info("👆 Appuyez ci-dessus pour prendre une photo.")

price_input = st.number_input("Prix annoncé (FCFA)", min_value=1000, step=500, format="%d")

if uploaded_file and price_input > 0:
    if st.button("🔍 SCANNER MAINTENANT"):
        if not api_key:
            st.error("⚠️ Clé API manquante.")
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Analyse...", use_container_width=True)
            
            with st.spinner("🕵️‍♂️ Analyse approfondie (Mode Pro)..."):
                result_text = analyze_image(image, price_input, api_key)

            if "ERREUR_NON_MEUBLE" in result_text:
                st.error("🛑 Ce n'est pas un meuble.")
            
            elif "ERREUR_DETAIL:" in result_text:
                st.error("❌ Erreur technique.")
                st.warning(result_text.replace("ERREUR_DETAIL:", ""))
                if "API key not valid" in result_text:
                    st.caption("👉 Votre clé API semble incorrecte.")
                elif "Generative Language API" in result_text:
                    st.caption("👉 Activez l'API sur console.cloud.google.com")
                elif "429" in result_text:
                    st.caption("👉 Trop de requêtes (Mode Pro limité). Réessayez dans 1 minute.")
                
            elif "ERREUR_API" in result_text:
                st.error("Erreur de connexion générique.")
                
            else:
                # SUCCÈS
                lines = result_text.split('\n')
                data = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()

                st.success("Analyse terminée !")
                
                st.markdown(f"### {data.get('TYPE_PRECIS', 'Meuble')}")
                
                verdict = data.get("VERDICT_PRIX", "N/A")
                color = "green" if "Affaire" in verdict else "orange" if "Correct" in verdict else "red"
                
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class='style-tag'>{data.get('STYLE_DESIGN', 'Standard')}</span>
                    <b style="color:{color}; font-size:1.1em;">{verdict.upper()}</b>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")

                sahel_val = int(data.get("SCORE_CLIMAT_SAHEL", "0").split('/')[0]) if data.get("SCORE_CLIMAT_SAHEL") else 0
                global_val = int(data.get("SCORE_GLOBAL", "0").split('/')[0]) if data.get("SCORE_GLOBAL") else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.caption("🌵 Sahel")
                    st.progress(sahel_val / 10)
                with col2:
                    st.caption("⭐ Global")
                    st.progress(global_val / 10)
                
                st.markdown("---")

                st.markdown("**📝 L'avis de l'expert**")
                st.markdown(f"""
                <div class="metric-card">
                {data.get('ANALYSE_VISUELLE', '...')}
                <hr style="margin:10px 0; opacity:0.3;">
                💡 <i>{data.get('CONSEIL_NEGOCIATION', '')}</i>
                </div>
                """, unsafe_allow_html=True)

                save_data(data.get("TYPE_PRECIS"), data.get("STYLE_DESIGN"), data.get("MATIERE_REELLE"), price_input, global_val, verdict)

# Admin footer
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛡️ Zone Admin"):
    if st.checkbox("Données"):
        if os.path.exists("data_meubles.csv"):
            with open("data_meubles.csv", "r", encoding="utf-8") as f:
                st.download_button("📥 CSV", f, "data_meubles.csv")
