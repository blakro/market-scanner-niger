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
    page_title="Gaskiyar Kaya 🇳🇪",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS DESIGN "LUMIÈRE & ÉPURÉ" AVEC EXO 2 ---
st.markdown("""
    <style>
    /* Importation Police Exo 2 (Google Fonts) */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&display=swap');

    /* RESET & BASE */
    * {
        font-family: 'Exo 2', sans-serif !important;
        color: #1f2937;
    }

    /* ARRIÈRE-PLAN CLAIR (Style "Clean App") */
    .stApp {
        background-color: #fafafa; /* Blanc cassé très doux */
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px; /* Petit motif discret */
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* CARTE RÉSULTAT (Style Minimaliste) */
    .tech-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Ombre très douce */
        margin-bottom: 20px;
        border: 1px solid #f3f4f6;
    }
    
    /* TITRES */
    h1 {
        color: #111827 !important;
        font-weight: 800 !important; /* Extra Bold pour Exo 2 */
        letter-spacing: -0.5px;
        text-align: center;
        margin-bottom: 0 !important;
        text-transform: uppercase; /* Style plus impactant */
    }
    .tech-header {
        color: #ea580c; /* Orange Niger */
        font-weight: 700;
        font-size: 1em;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #fff7ed;
        padding-bottom: 5px;
    }
    
    /* TABLEAUX ÉPURÉS */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .styled-table th {
        text-align: left;
        color: #9ca3af;
        font-size: 0.85em;
        text-transform: uppercase;
        padding: 8px 0;
        font-weight: 700;
    }
    .styled-table td {
        padding: 10px 0;
        border-bottom: 1px solid #f3f4f6;
        color: #374151;
        font-weight: 500;
    }
    .styled-table tr:last-child td {
        border-bottom: none;
    }
    
    /* BADGES MODERNES (Pillules) */
    .verdict-badge {
        padding: 6px 12px;
        border-radius: 100px;
        color: white;
        font-weight: 700;
        font-size: 0.85em;
        text-align: center;
        display: inline-block;
    }
    .bg-green { background-color: #10b981; color: white; }
    .bg-orange { background-color: #f59e0b; color: white; }
    .bg-red { background-color: #ef4444; color: white; }

    /* BOUTON PRINCIPAL (Orange Niger) */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background-color: #ea580c;
        color: white !important;
        font-weight: 700;
        border: none;
        font-size: 1.1em;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.2);
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background-color: #c2410c;
        box-shadow: 0 6px 15px rgba(234, 88, 12, 0.3);
        transform: translateY(-1px);
    }

    /* INPUTS ET ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 8px;
        font-weight: 600;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff7ed !important;
        color: #ea580c !important;
    }
    .stNumberInput input {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        background-color: white;
        font-weight: 600;
    }

    /* Mobile Optimisation */
    @media only screen and (max-width: 600px) {
        .main .block-container {
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
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
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

# --- SCANNER AUTO ROBUSTE ---
def find_best_model_dynamic():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            return None, "Aucun modèle trouvé."

        for m in available_models:
            if 'flash' in m.lower(): return m, None
        for m in available_models:
            if 'pro' in m.lower() and 'vision' not in m.lower(): return m, None
        return available_models[0], None
    except Exception as e:
        return "models/gemini-1.5-flash", str(e)

# --- ANALYSE ---
def analyze_image_pro(image, price, api_key):
    genai.configure(api_key=api_key)
    model_name, scan_error = find_best_model_dynamic()
    
    if not model_name: return None, scan_error
    
    prompt = f"""
    Tu es un expert menuisier et tapissier à Niamey. Analyse ce meuble (Prix: {price} FCFA).
    Si ce n'est pas un meuble, renvoie un JSON avec {{"is_furniture": false}}.
    Sinon, renvoie un JSON valide :
    {{
        "is_furniture": true,
        "titre": "Type court (ex: Canapé d'angle)",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
        "score_global": 5,
        "score_sahel": 5,
        "composition_materiau": [
            {{"couche": "Surface", "compo": "ex: Simili", "etat": "ex: Usé"}},
            {{"couche": "Structure", "compo": "ex: Bois", "etat": "ex: OK"}}
        ],
        "resistance_usure": 3,
        "avis_menuisier": "Avis structure...",
        "avis_tapissier": "Avis tissu...",
        "matrice_decision": [
            {{"option": "Réparer", "difficulte": "Difficile", "cout": "Cher", "resultat": "Moyen"}},
            {{"option": "Housse", "difficulte": "Facile", "cout": "Faible", "resultat": "Bon"}},
            {{"option": "Jeter", "difficulte": "Moyen", "cout": "Nul", "resultat": "Nul"}}
        ],
        "recommandation_finale": "Conseil court."
    }}
    """
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return clean_json_response(response.text), model_name
    except Exception as e:
        if "429" in str(e):
            time.sleep(2)
            try:
                response = model.generate_content([prompt, image])
                return clean_json_response(response.text), model_name
            except: return None, "Surcharge serveur"
        return None, str(e)

# --- INTERFACE MOBILE ÉPURÉE ---
st.title("Gaskiyar Kaya 🇳🇪")
st.markdown("<p style='text-align:center; color:#6b7280; margin-top:-10px; margin-bottom:20px; font-weight:500;'>L'Expert Meuble de confiance</p>", unsafe_allow_html=True)

# Onglets stylisés
tab_cam, tab_upload = st.tabs(["📸 Prendre Photo", "📂 Galerie"])

img_file_buffer = None

with tab_cam:
    camera_img = st.camera_input("Cadrez le meuble", label_visibility="collapsed")
    if camera_img:
        img_file_buffer = camera_img

with tab_upload:
    upload_img = st.file_uploader("Choisir une image", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")
    if upload_img:
        img_file_buffer = upload_img

# Input Prix (Step 50 000)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<span style="font-weight:700; color:#1f2937">💰 Prix annoncé (FCFA)</span>', unsafe_allow_html=True)
price_input = st.number_input("Prix", min_value=0, step=50000, value=0, format="%d", label_visibility="collapsed")

# Bouton d'action
st.markdown("<br>", unsafe_allow_html=True)
if img_file_buffer and price_input >= 0:
    if st.button("LANCER L'ANALYSE"):
        if not api_key:
            st.error("⚠️ Clé API manquante")
        else:
            image = Image.open(img_file_buffer)
            st.image(image, width=120) # Miniature discrète
            
            with st.spinner("🔍 Analyse détaillée en cours..."):
                json_str, info_msg = analyze_image_pro(image, price_input, api_key)
            
            if not json_str:
                st.error("Erreur technique.")
                st.caption(info_msg)
            else:
                try:
                    data = json.loads(json_str)
                    
                    if not data.get("is_furniture"):
                        st.error("🛑 Pas un meuble reconnu.")
                    else:
                        
                        # En-tête Clean
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        c1, c2 = st.columns([2,1])
                        with c1:
                            st.markdown(f"<h3 style='margin:0; font-size:1.4em; font-weight:800'>{data.get('titre')}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#6b7280; font-size:0.9em; font-weight:500'>{data.get('style')}</span>", unsafe_allow_html=True)
                        with c2:
                            v = data.get('verdict_prix', 'N/A')
                            color = "bg-green" if "Affaire" in v else "bg-orange" if "Correct" in v else "bg-red"
                            st.markdown(f'<div style="text-align:right"><span class="verdict-badge {color}">{v}</span></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 1. Matériau
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">🧬 Composition</div>', unsafe_allow_html=True)
                        html_table = '<table class="styled-table"><thead><tr><th>Zone</th><th>Matière</th><th>État</th></tr></thead><tbody>'
                        for row in data.get('composition_materiau', []):
                            html_table += f"<tr><td>{row['couche']}</td><td>{row['compo']}</td><td>{row['etat']}</td></tr>"
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 2. Avis Experts
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">📊 Audit Technique</div>', unsafe_allow_html=True)
                        st.write("Note d'usure globale")
                        st.progress(data.get('resistance_usure')/10)
                        st.markdown(f"""
                        <div style="margin-top:15px; padding:15px; background:#f9fafb; border-radius:8px; font-size:0.95em; line-height:1.6;">
                            🪑 <b>Menuisier :</b> {data.get('avis_menuisier')}<br><br>
                            🧵 <b>Tapissier :</b> {data.get('avis_tapissier')}
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 3. Décision
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">⚖️ Scénarios</div>', unsafe_allow_html=True)
                        matrix_html = '<table class="styled-table"><thead><tr><th>Option</th><th>Coût</th><th>Résultat</th></tr></thead><tbody>'
                        for opt in data.get('matrice_decision', []):
                            matrix_html += f"<tr><td><b>{opt['option']}</b></td><td>{opt['cout']}</td><td>{opt['resultat']}</td></tr>"
                        matrix_html += "</tbody></table>"
                        st.markdown(matrix_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 4. Conseil Final
                        st.markdown(f"""
                        <div class="tech-card" style="background:#ecfdf5; border:1px solid #10b981; border-top:none;">
                            <div style="color:#047857; font-weight:bold; margin-bottom:5px; text-transform:uppercase; font-size:0.9em;">💡 Le Conseil du Gwani</div>
                            <p style="color:#065f46; margin:0; font-weight:600;">{data.get('recommandation_finale')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        save_data(data.get('titre'), price_input, data.get('score_global'), data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur lecture IA.")
elif not img_file_buffer:
    # Empty state simple
    st.markdown("""
    <div style='text-align:center; padding:40px; color:#9ca3af;'>
        <p style="font-size:3em;">📸</p>
        <p style="font-weight:600;">Prenez une photo pour commencer</p>
    </div>
    """, unsafe_allow_html=True)
