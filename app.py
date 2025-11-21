import streamlit as st
import google.generativeai as genai
from PIL import Image
import csv
import os
from datetime import datetime
import time
import json
import re

# --- CONFIGURATION ---
st.set_page_config(
    page_title="MarketScanner Niger",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS PRO (Design "Carte") ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Style global */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Cartes blanches avec ombre */
    .tech-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-top: 4px solid #d97706;
    }
    
    /* Titres de section */
    .tech-header {
        color: #1f2937;
        font-weight: 800;
        font-size: 1.1em;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tables personnalisées */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .styled-table th {
        background-color: #f3f4f6;
        color: #374151;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #e5e7eb;
    }
    .styled-table td {
        padding: 8px;
        border-bottom: 1px solid #eee;
        color: #4b5563;
    }
    
    /* Badges */
    .verdict-badge {
        padding: 5px 10px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        font-size: 0.9em;
        text-align: center;
        display: inline-block;
    }
    .bg-green { background-color: #10b981; }
    .bg-orange { background-color: #f59e0b; }
    .bg-red { background-color: #ef4444; }

    /* Bouton */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #d97706;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background-color: #b45309;
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
def save_data(furniture_type, price, score, verdict):
    try:
        file_exists = os.path.exists("data_meubles.csv")
        with open("data_meubles.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Date", "Type", "Prix", "Score", "Verdict"])
            writer.writerow([datetime.now(), furniture_type, price, score, verdict])
    except Exception:
        pass

# --- UTILITAIRE JSON ---
def clean_json_response(text):
    """Nettoie la réponse de l'IA pour extraire le JSON pur."""
    text = text.strip()
    # Enlever les balises markdown ```json ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

# --- ANALYSE AVANCÉE (JSON) ---
def analyze_image_pro(image, price, api_key):
    genai.configure(api_key=api_key)
    
    # Modèle robuste avec fallback
    models = ["gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-pro"]
    
    # Prompt structuré pour forcer le format JSON riche
    prompt = f"""
    Tu es un expert menuisier et tapissier à Niamey. Analyse ce meuble (Prix: {price} FCFA).
    
    Si ce n'est pas un meuble, renvoie un JSON avec {{"is_furniture": false}}.
    
    Sinon, renvoie un JSON valide avec exactement cette structure :
    {{
        "is_furniture": true,
        "titre": "Type précis du meuble",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
        "score_global": 5,
        "score_sahel": 5,
        "composition_materiau": [
            {{"couche": "1. Surface", "compo": "ex: Cuir PU", "etat": "ex: Craquelé"}},
            {{"couche": "2. Structure", "compo": "ex: Bois rouge", "etat": "ex: Solide"}}
        ],
        "resistance_usure": 3,
        "avis_menuisier": "Analyse structurelle courte...",
        "avis_tapissier": "Analyse tissu/mousse courte...",
        "matrice_decision": [
            {{"option": "Réparation", "difficulte": "⭐⭐⭐", "cout": "Cher", "resultat": "Moyen"}},
            {{"option": "Housse", "difficulte": "⭐", "cout": "Faible", "resultat": "Bon"}},
            {{"option": "Jeter", "difficulte": "⭐", "cout": "Nul", "resultat": "Nul"}}
        ],
        "recommandation_finale": "Conseil final court et direct."
    }}
    """
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            # On force la réponse en JSON (mode text pour compatibilité flash, on parse manuellement)
            response = model.generate_content([prompt, image])
            return clean_json_response(response.text), model_name
        except Exception as e:
            if "429" in str(e): time.sleep(1)
            continue
            
    return None, "Erreur"

# --- INTERFACE ---
st.title("🇳🇪 MarketScanner PRO")
st.caption("L'Expert Meuble : Analyse Technique Complète")

uploaded_file = st.file_uploader("Photo", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")

if not uploaded_file:
    st.info("📸 Prenez une photo pour commencer l'audit technique.")

price_input = st.number_input("Prix Vendeur (FCFA)", min_value=0, step=500, value=0, format="%d")

if uploaded_file and price_input > 0:
    if st.button("🔍 LANCER L'AUDIT TECHNIQUE"):
        if not api_key:
            st.error("⚠️ Clé API manquante")
        else:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            with st.spinner("🧠 Analyse structurelle et matériaux en cours..."):
                json_str, model_used = analyze_image_pro(image, price_input, api_key)
            
            if not json_str:
                st.error("Erreur technique (IA non disponible). Réessayez.")
            else:
                try:
                    data = json.loads(json_str)
                    
                    if not data.get("is_furniture"):
                        st.error("🛑 Ce n'est pas un meuble.")
                    else:
                        # --- 1. EN-TÊTE ---
                        st.success("Analyse terminée !")
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"### {data.get('titre')}")
                            st.caption(f"Style : {data.get('style')}")
                        with col2:
                            v = data.get('verdict_prix', 'N/A')
                            c = "bg-green" if "Affaire" in v else "bg-orange" if "Correct" in v else "bg-red"
                            st.markdown(f'<div class="verdict-badge {c}">{v}</div>', unsafe_allow_html=True)

                        # --- 2. IDENTIFICATION MATÉRIAU (Tableau) ---
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">🧬 1. Composition du Matériau</div>', unsafe_allow_html=True)
                        
                        # Construction du tableau HTML manuel pour le style
                        html_table = '<table class="styled-table"><thead><tr><th>Couche</th><th>Composition</th><th>État détecté</th></tr></thead><tbody>'
                        for row in data.get('composition_materiau', []):
                            html_table += f"<tr><td><b>{row['couche']}</b></td><td>{row['compo']}</td><td>{row['etat']}</td></tr>"
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # --- 3. RÉSISTANCE & AUDIT ---
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">📊 2. Résistance & Audit Expert</div>', unsafe_allow_html=True)
                        
                        res_score = data.get('resistance_usure', 0)
                        st.write(f"**Résistance à l'usure : {res_score}/10**")
                        st.progress(res_score/10)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.info(f"🪑 **Menuisier :**\n{data.get('avis_menuisier')}")
                        with c2:
                            st.warning(f"🧵 **Tapissier :**\n{data.get('avis_tapissier')}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # --- 4. MATRICE DE DÉCISION ---
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">⚖️ 3. Matrice de Décision (Que faire ?)</div>', unsafe_allow_html=True)
                        
                        matrix_html = '<table class="styled-table"><thead><tr><th>Option</th><th>Difficulté</th><th>Coût</th><th>Résultat</th></tr></thead><tbody>'
                        for opt in data.get('matrice_decision', []):
                            matrix_html += f"<tr><td><b>{opt['option']}</b></td><td>{opt['difficulte']}</td><td>{opt['cout']}</td><td>{opt['resultat']}</td></tr>"
                        matrix_html += "</tbody></table>"
                        st.markdown(matrix_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # --- 5. CONCLUSION ---
                        st.markdown(f"""
                        <div class="tech-card" style="border-top: 4px solid #10b981;">
                            <div class="tech-header">💡 Recommandation Finale</div>
                            <p style="font-size: 1.1em;">{data.get('recommandation_finale')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Sauvegarde
                        save_data(data.get('titre'), price_input, data.get('score_global'), data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur de lecture des données structurées. L'IA a renvoyé un format invalide.")
                    st.code(json_str) # Debug
