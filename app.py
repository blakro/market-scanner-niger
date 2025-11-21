import streamlit as st
import google.generativeai as genai
from PIL import Image
import csv
import os
from datetime import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(
    page_title="MarketScanner Niger",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS ---
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

# --- API KEY ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    with st.expander("🔐 Configuration"):
        api_key = st.text_input("Clé API", type="password")

# --- SAUVEGARDE ---
def save_data(furniture_type, style, material, price, score, risk_level):
    try:
        file_exists = os.path.exists("data_meubles.csv")
        with open("data_meubles.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Date", "Type", "Style", "Matiere", "Prix", "Score", "Risque"])
            writer.writerow([datetime.now(), furniture_type, style, material, price, score, risk_level])
    except Exception:
        pass

# --- ANALYSE ROBUSTE (BOUCLE DE SECOURS) ---
def analyze_image(image, price, api_key):
    genai.configure(api_key=api_key)
    
    # LISTE D'ORDRE DE BATAILLE
    # On essaie ces modèles l'un après l'autre.
    # Si l'un échoue (404 ou 429), on passe au suivant.
    models_priority = [
        "gemini-1.5-flash",          # Le standard rapide
        "gemini-1.5-flash-001",      # La version spécifique (souvent la solution au 404)
        "gemini-1.5-flash-002",      # Nouvelle version
        "gemini-1.5-pro",            # Plus lent mais puissant
        "gemini-1.5-pro-001",
        "gemini-pro"                 # L'ancêtre (très stable)
    ]
    
    prompt = f"""
    Rôle : Expert ameublement à Niamey.
    Prix : {price} FCFA.
    
    Tâche 1 : Si ce n'est pas un meuble, réponds juste "ERREUR_NON_MEUBLE".
    
    Tâche 2 : Analyse (Format strict) :
    TYPE_PRECIS: [Type]
    STYLE_DESIGN: [Style]
    MATIERE_REELLE: [Matière]
    ETAT_STRUCTURE: [Bon/Moyen/Mauvais]
    SCORE_CLIMAT_SAHEL: [Note/10]
    SCORE_GLOBAL: [Note/10]
    VERDICT_PRIX: [Cher/Correct/Affaire]
    ANALYSE_VISUELLE: [3 phrases courtes]
    CONSEIL_NEGOCIATION: [1 phrase]
    """

    last_error = ""
    
    # LA BOUCLE "TANT QU'IL Y A DE L'ESPOIR"
    for model_name in models_priority:
        try:
            # On tente...
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, image])
            
            # Si on arrive ici, c'est que ça a marché ! On renvoie le résultat.
            return response.text, model_name

        except Exception as e:
            # Si ça plante, on note l'erreur et on continue la boucle
            last_error = str(e)
            # Petite pause si c'est une erreur de quota
            if "429" in last_error:
                time.sleep(1)
            continue
            
    # Si on sort de la boucle, c'est que TOUT a échoué
    return f"ERREUR_DETAIL: Tous les modèles ont échoué. Dernière erreur : {last_error}", "Aucun"

# --- INTERFACE ---
st.title("🇳🇪 MarketScanner")
st.caption("L'Expert Meuble")

uploaded_file = st.file_uploader("Photo", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")

if not uploaded_file:
    st.info("👆 Ajoutez une photo pour commencer")

price_input = st.number_input("Prix (FCFA)", min_value=1000, step=500, format="%d")

if uploaded_file and price_input > 0:
    if st.button("🔍 SCANNER"):
        if not api_key:
            st.error("⚠️ Clé manquante")
        else:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            with st.spinner("🕵️‍♂️ Analyse en cours..."):
                result_text, used_model = analyze_image(image, price_input, api_key)

            if "ERREUR_NON_MEUBLE" in result_text:
                st.error("🛑 Pas un meuble.")
            
            elif "ERREUR_DETAIL" in result_text:
                st.error("Oups ! Souci technique.")
                st.warning(result_text.replace("ERREUR_DETAIL:", ""))
                st.caption("Conseil : Vérifiez votre clé API Google.")
                
            else:
                # Parsing
                data = {}
                for line in result_text.split('\n'):
                    if ":" in line:
                        k, v = line.split(':', 1)
                        data[k.strip()] = v.strip()

                st.success("Terminé !")
                # st.caption(f"Modèle : {used_model}") # Debug optionnel
                
                # Affichage Résultat
                col_res, col_verdict = st.columns([2,1])
                with col_res:
                    st.markdown(f"### {data.get('TYPE_PRECIS', 'Meuble')}")
                    st.caption(f"Style : {data.get('STYLE_DESIGN', 'Standard')}")
                with col_verdict:
                    verdict = data.get('VERDICT_PRIX', 'N/A')
                    color = "green" if "Affaire" in verdict else "red"
                    st.markdown(f":{color}[**{verdict}**]")

                try:
                    score_val = int(data.get('SCORE_GLOBAL', '0').split('/')[0]) / 10
                except:
                    score_val = 0
                st.progress(score_val, text="Note Globale")
                
                st.markdown(f"""
                <div class="metric-card">
                <b>L'avis de l'expert :</b><br>
                {data.get('ANALYSE_VISUELLE', 'Pas d\'info')}
                <hr>
                💡 {data.get('CONSEIL_NEGOCIATION', '')}
                </div>
                """, unsafe_allow_html=True)

                save_data(data.get("TYPE_PRECIS"), data.get("STYLE_DESIGN"), data.get("MATIERE_REELLE"), price_input, 0, verdict)

# Admin zone
with st.expander("Admin"):
    if st.checkbox("CSV"):
        if os.path.exists("data_meubles.csv"):
            with open("data_meubles.csv", "r") as f:
                st.download_button("Télécharger", f, "data.csv")
