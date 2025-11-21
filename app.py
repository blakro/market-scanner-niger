import streamlit as st
import google.generativeai as genai
from PIL import Image
import csv
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE (MOBILE FIRST) ---
st.set_page_config(
    page_title="MarketScanner Niger",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed" # Menu caché par défaut sur mobile
)

# --- CSS OPTIMISÉ POUR MOBILE ---
st.markdown("""
    <style>
    /* Cacher le menu hamburger et le footer Streamlit pour faire 'App Native' */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Couleurs et style */
    .stProgress > div > div > div > div { background-color: #d97706; }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        border-left: 5px solid #d97706;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Petit effet d'ombre joli */
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
    /* Gros bouton pour les doigts tactiles */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTION INTELLIGENTE DE LA CLÉ API ---
# Sur mobile, on ne veut pas de barre latérale qui gêne.
# On cherche la clé en arrière-plan.
api_key = None

# 1. Essai via les Secrets (Configuration Cloud)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

# 2. Essai via saisie manuelle (uniquement si pas de secret, ex: test local)
if not api_key:
    with st.expander("🔐 Configuration (Admin seulement)"):
        api_key = st.text_input("Clé API Google Gemini", type="password")

# --- FONCTION DE SAUVEGARDE ---
def save_data(furniture_type, style, material, price, score, risk_level):
    file_exists = os.path.exists("data_meubles.csv")
    with open("data_meubles.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Type_Meuble", "Style", "Matiere_Reelle", "Prix_FCFA", "Score_Global", "Niveau_Risque"])
        writer.writerow([datetime.now(), furniture_type, style, material, price, score, risk_level])

# --- FONCTION D'ANALYSE ---
def analyze_image(image, price, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') 

    prompt = f"""
    Tu es un expert en ameublement basé à Niamey, Niger.
    
    CONTEXTE : Analyse d'un meuble d'occasion pour un acheteur potentiel sur mobile.
    PRIX PROPOSÉ : {price} FCFA.
    CLIMAT : Sahélien (Chaleur sèche, Poussière).

    --- ÉTAPE 1 : SÉCURITÉ (GUARDRAIL) ---
    Regarde l'image. Est-ce que l'objet principal est un meuble (Canapé, Lit, Table, Armoire, Chaise, Fauteuil) ?
    Si NON (c'est un animal, voiture, selfie, paysage, électroménager), réponds juste : "ERREUR_NON_MEUBLE".
    Si OUI, passe à l'étape 2.

    --- ÉTAPE 2 : IDENTIFICATION & ANALYSE ---
    Réponds avec ce format exact (sans markdown, une info par ligne) :
    
    TYPE_PRECIS: [Ex: Canapé d'angle, Armoire 3 portes]
    STYLE_DESIGN: [Ex: Louis XV, Moderne, Salon Marocain]
    MATIERE_REELLE: [Matière identifiée vs ce qui est visible]
    ETAT_STRUCTURE: [Bon/Moyen/Mauvais]
    SCORE_CLIMAT_SAHEL: [Note sur 10]
    SCORE_GLOBAL: [Note sur 10]
    VERDICT_PRIX: [Cher/Correct/Affaire]
    ANALYSE_VISUELLE: [3 phrases courtes et percutantes pour lecture mobile]
    CONSEIL_NEGOCIATION: [Une phrase choc courte]
    """

    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return "ERREUR_API"

# --- INTERFACE UTILISATEUR (SIMPLE & ÉPURÉE) ---
st.title("🇳🇪 MarketScanner")
st.caption("L'Expert Meuble dans votre poche")

# Zone de chargement (Appareil photo sur mobile)
uploaded_file = st.file_uploader("Photo du meuble", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")

if not uploaded_file:
    st.info("👆 Appuyez ci-dessus pour prendre une photo ou choisir dans la galerie.")

# Zone de prix
price_input = st.number_input("Prix annoncé (FCFA)", min_value=1000, step=500, format="%d")

# Bouton d'action (Pleine largeur grâce au CSS)
if uploaded_file and price_input > 0:
    if st.button("🔍 SCANNER MAINTENANT"):
        if not api_key:
            st.error("⚠️ Clé API manquante.")
        else:
            image = Image.open(uploaded_file)
            # On affiche l'image en petit pour ne pas prendre tout l'écran mobile
            st.image(image, caption="Analyse en cours...", use_column_width=True)
            
            with st.spinner("🕵️‍♂️ Analyse de l'expert..."):
                result_text = analyze_image(image, price_input, api_key)

            if "ERREUR_NON_MEUBLE" in result_text:
                st.error("🛑 Ce n'est pas un meuble.")
            
            elif "ERREUR_API" in result_text:
                st.error("Erreur de connexion.")
                
            else:
                lines = result_text.split('\n')
                data = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()

                # --- RÉSULTATS (Format Carte Mobile) ---
                st.success("Analyse terminée !")
                
                # Titre et verdict
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

                # Jauges (Empilées pour mobile)
                sahel_val = int(data.get("SCORE_CLIMAT_SAHEL", "0").split('/')[0]) if data.get("SCORE_CLIMAT_SAHEL") else 0
                global_val = int(data.get("SCORE_GLOBAL", "0").split('/')[0]) if data.get("SCORE_GLOBAL") else 0
                
                st.caption("🌵 Résistance Sahel")
                st.progress(sahel_val / 10)
                
                st.caption("⭐ Note Globale")
                st.progress(global_val / 10)
                
                st.markdown("---")

                # Carte d'analyse
                st.markdown("**📝 L'avis de l'expert**")
                st.markdown(f"""
                <div class="metric-card">
                {data.get('ANALYSE_VISUELLE', '...')}
                <hr style="margin:10px 0; opacity:0.3;">
                💡 <i>{data.get('CONSEIL_NEGOCIATION', '')}</i>
                </div>
                """, unsafe_allow_html=True)

                # Sauvegarde silencieuse
                save_data(
                    data.get("TYPE_PRECIS"), 
                    data.get("STYLE_DESIGN"), 
                    data.get("MATIERE_REELLE"),
                    price_input, 
                    global_val, 
                    verdict
                )

# --- FOOTER ADMIN (Discret en bas de page) ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛡️ Zone Admin (Données)"):
    if st.checkbox("Voir les données récoltées"):
        if os.path.exists("data_meubles.csv"):
            with open("data_meubles.csv", "r", encoding="utf-8") as f:
                st.download_button("📥 Télécharger le fichier Excel (CSV)", f, "data_meubles.csv")
        else:
            st.info("Aucune donnée pour l'instant.")