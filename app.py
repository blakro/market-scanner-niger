import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime
import time
import json
import re
# Imports pour Google Sheets
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Gaskiyar Kaya 🇳🇪",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS DESIGN "LUMIÈRE & ÉPURÉ" (OPTIMISÉ ESPACE) ---
st.markdown("""
    <style>
    /* Importation Police Exo 2 */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&display=swap');

    /* 1. FORCER LA POLICE PARTOUT */
    html, body, [class*="css"] {
        font-family: 'Exo 2', sans-serif;
    }

    /* 2. COULEURS TEXTE GLOBALES (Noir force) */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #1f2937 !important; 
    }
    
    /* 3. CORRECTION INPUTS (PRIX) */
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #d1d5db !important;
        caret-color: #ea580c !important;
        font-weight: 700 !important;
    }
    .stNumberInput button {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
    }

    /* 4. CORRECTION ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 2px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        border: 1px solid #e5e7eb;
        margin-bottom: 5px; /* Réduit */
    }
    .stTabs [data-baseweb="tab"] {
        height: 2.5rem;
        border-radius: 8px;
        font-weight: 600;
        color: #6b7280 !important;
        background-color: transparent !important;
        padding-top: 0;
        padding-bottom: 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff7ed !important;
        color: #ea580c !important;
    }

    /* 5. CORRECTION UPLOAD */
    div[data-testid="stFileUploader"] {
        background-color: #f9fafb;
        border: 1px dashed #d1d5db;
        border-radius: 10px;
        padding: 10px;
    }
    div[data-testid="stFileUploader"] section > div {
        color: #4b5563 !important; 
        padding-top: 10px;
        padding-bottom: 10px;
    }
    div[data-testid="stFileUploader"] button {
        background-color: white !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }

    /* EXCEPTIONS TEXTE BLANC */
    .stButton > button, .verdict-badge, div[data-testid="stCameraInput"] button {
        color: white !important;
    }
    /* EXCEPTIONS GRIS */
    .stCaption, div[data-testid="stCaptionContainer"] p {
        color: #6b7280 !important;
    }

    /* ARRIÈRE-PLAN */
    .stApp {
        background-color: #fafafa;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    /* SUPPRESSION TOTALE HEADER ET FOOTER STREAMLIT */
    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stHeader"] { display: none !important; } /* Supprime l'espace vide en haut */

    /* CARTE RÉSULTAT */
    .tech-card {
        background: white;
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 15px;
        border: 1px solid #f3f4f6;
    }
    
    /* TITRES */
    h1 {
        font-weight: 800 !important;
        text-align: center;
        text-transform: uppercase;
        font-size: 1.5rem !important;
        margin-top: -60px !important; /* Remonte le titre violemment vers le haut */
        padding-bottom: 0 !important;
    }
    .tech-header {
        color: #ea580c !important;
        font-weight: 700;
        font-size: 0.95em;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #fff7ed;
        padding-bottom: 5px;
    }
    
    /* CERCLE DE SCORE */
    .score-circle-container {
        display: flex;
        justify-content: center;
        margin: 10px 0;
    }
    .score-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: conic-gradient(#ea580c var(--percent), #f3f4f6 0);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .score-circle::before {
        content: "";
        width: 85px;
        height: 85px;
        background: white;
        border-radius: 50%;
        position: absolute;
    }
    .score-value {
        position: relative;
        font-size: 1.5em;
        font-weight: 800;
        color: #ea580c !important;
    }
    .score-label {
        position: relative;
        display: block;
        text-align: center;
        font-size: 0.6em;
        color: #6b7280 !important;
        font-weight: 600;
        margin-top: -5px;
    }

    /* JAUGES */
    .gauge-container {
        margin-bottom: 8px;
    }
    .gauge-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.8em;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .gauge-bg {
        height: 8px;
        background: #f3f4f6;
        border-radius: 4px;
        overflow: hidden;
    }
    .gauge-fill {
        height: 100%;
        background: linear-gradient(90deg, #fcd34d, #ea580c);
        border-radius: 4px;
    }

    /* CARTES SCENARIOS */
    .scenario-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        height: 100%;
    }
    .scenario-title {
        font-weight: 800;
        color: #374151 !important;
        margin-bottom: 3px;
        text-transform: uppercase;
        font-size: 0.75em;
    }
    .scenario-cost {
        font-size: 0.7em;
        color: #6b7280 !important;
        margin-bottom: 3px;
    }
    .scenario-result {
        font-weight: 700;
        color: #ea580c !important;
        font-size: 0.85em;
    }

    /* TABLEAUX */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85em;
    }
    .styled-table td {
        padding: 8px 0;
        border-bottom: 1px solid #f3f4f6;
        color: #1f2937 !important;
    }

    /* BADGES */
    .verdict-badge {
        padding: 4px 10px;
        border-radius: 100px;
        font-weight: 700;
        font-size: 0.8em;
    }
    .bg-green { background-color: #10b981; }
    .bg-orange { background-color: #f59e0b; }
    .bg-red { background-color: #ef4444; }

    /* BOUTONS */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #ea580c;
        color: white !important;
        font-weight: 700;
        border: none;
        font-size: 1.1em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.2);
        margin-top: 0px;
    }
    
    /* CORRECTION BOUTON CAMÉRA (Orange et Lisible) */
    div[data-testid="stCameraInput"] button {
        background-color: #ea580c !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: 2px solid white !important;
    }

    /* === OPTIMISATION MOBILE CRITIQUE === */
    @media only screen and (max-width: 600px) {
        .main .block-container {
            /* Padding top à 0 pour remonter tout en haut */
            padding-top: 2rem !important; 
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-bottom: 100px !important;
        }
        /* Ajustement spécifique du titre sur mobile */
        h1 {
            font-size: 1.4rem !important;
            margin-top: -40px !important; /* Remonte le titre violemment */
            margin-bottom: 0.2rem !important;
        }
        .stCaption {
            margin-bottom: 0.5rem !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.5rem !important;
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

# --- SAUVEGARDE VERS GOOGLE SHEETS ---
def save_data_to_sheets(furniture_type, price, score, verdict):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        new_data = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Type_Meuble": furniture_type,
            "Prix_FCFA": price,
            "Score_Global": score,
            "Verdict_IA": verdict
        }])
        try:
            existing_data = conn.read(worksheet="Sheet1", ttl=0)
            if existing_data.empty:
                 updated_data = new_data
            else:
                 updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except:
            updated_data = new_data
        conn.update(worksheet="Sheet1", data=updated_data)
    except Exception:
        pass

# --- UTILITAIRE JSON ---
def clean_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

# --- SCANNER AUTO ---
def find_best_model_dynamic():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        if not available_models: return None, "Aucun modèle trouvé."
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
    Tu es un expert menuisier à Niamey. Analyse ce meuble (Prix: {price} FCFA).
    Liste des objets acceptés : Canapé, fauteuil, table basse, meuble TV, lit, armoire, commode, chevet, table à manger, chaise, buffet, bureau, bibliothèque, console, meuble à chaussures, dressing, lit superposé, canapé-lit, banquette, table de cuisine, tabouret, meuble sous-vasque.
    Si l'objet n'est PAS un meuble de cette liste, renvoie {{"is_furniture": false}}.
    Sinon, renvoie un JSON valide :
    {{
        "is_furniture": true,
        "titre": "Type précis",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
        "scores": {{ "solidite": 75, "materiaux": 60, "restauration": 90, "global": 70 }},
        "composition_materiau": [
            {{"couche": "Matière Principale", "compo": "ex: Bois massif", "etat": "ex: Bon"}},
            {{"couche": "Finition/Tissu", "compo": "ex: Vernis", "etat": "ex: Rayé"}}
        ],
        "avis_menuisier": "Avis structure...",
        "avis_tapissier": "Avis finition...",
        "scenarios": [
            {{"titre": "Réparer", "icone": "🛠️", "cout": "Cher", "resultat": "Moyen"}},
            {{"titre": "Housse/Vernis", "icone": "✨", "cout": "Faible", "resultat": "Bon"}},
            {{"titre": "Négocier", "icone": "🤝", "cout": "0", "resultat": "Top"}}
        ],
        "recommandation_finale": "Conseil court."
    }}
    NOTE: Les scores sont sur 100.
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

# --- INTERFACE COMPACTE ---
st.title("Gaskiyar Kaya 🇳🇪")
st.markdown("<p style='text-align:center; color:#6b7280 !important; font-size:0.9em; margin-top:-5px; margin-bottom:10px;'>L'Expert Meuble de confiance</p>", unsafe_allow_html=True)

# Petite info compacte
st.info("📸 Une seule photo bien cadrée suffit.", icon="ℹ️")

# Onglets compacts
tab_cam, tab_upload = st.tabs(["📸 Caméra", "📂 Galerie"])
img_file_buffer = None

with tab_cam:
    camera_img = st.camera_input("Photo", label_visibility="collapsed")
    if camera_img: img_file_buffer = camera_img

with tab_upload:
    upload_img = st.file_uploader("Image", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")
    if upload_img: img_file_buffer = upload_img

# Zone Prix Compacte
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
col_label, col_input = st.columns([1, 2])
with col_label:
    st.markdown('<div style="padding-top: 10px; font-weight:700; color:#1f2937 !important">💰 Prix (FCFA)</div>', unsafe_allow_html=True)
with col_input:
    price_input = st.number_input("Prix", min_value=0, step=5000, value=0, format="%d", label_visibility="collapsed")

# --- LOGIQUE ---
is_ready = False
error_msg = ""

if img_file_buffer:
    if price_input > 0:
        is_ready = True
    else:
        error_msg = "⚠️ Entrez un prix > 0"
else:
    error_msg = ""

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

# BOUTON ACTION
if is_ready:
    if st.button("LANCER L'ANALYSE"):
        if not api_key:
            st.error("⚠️ Clé API manquante")
        else:
            image = Image.open(img_file_buffer)
            # Pas d'affichage d'image en grand pour gagner de la place, juste le spinner
            with st.spinner("🔍 Analyse en cours..."):
                json_str, info_msg = analyze_image_pro(image, price_input, api_key)
            
            if not json_str:
                st.error("Erreur technique.")
            else:
                try:
                    data = json.loads(json_str)
                    if not data.get("is_furniture"):
                        st.error("🛑 Pas un meuble reconnu.")
                    else:
                        # RÉSULTATS
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        c1, c2 = st.columns([2,1])
                        with c1:
                            st.markdown(f"<h3 style='margin:0; font-size:1.3em; font-weight:800'>{data.get('titre')}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#6b7280; font-size:0.85em; font-weight:500'>{data.get('style')}</span>", unsafe_allow_html=True)
                        with c2:
                            v = data.get('verdict_prix', 'N/A')
                            color = "bg-green" if "Affaire" in v else "bg-orange" if "Correct" in v else "bg-red"
                            st.markdown(f'<div style="text-align:right"><span class="verdict-badge {color}">{v}</span></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # SCORE
                        scores = data.get('scores', {})
                        global_score = scores.get('global', 50)
                        
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">📊 Performance</div>', unsafe_allow_html=True)
                        
                        c_score, c_gauges = st.columns([1, 2])
                        with c_score:
                            st.markdown(f"""
                            <div class="score-circle-container">
                                <div class="score-circle" style="--percent: {global_score}%">
                                    <div style="position:absolute; text-align:center;">
                                        <div class="score-value">{global_score}%</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_gauges:
                            gauges = [
                                ("Solidité", scores.get('solidite', 0)),
                                ("Matériaux", scores.get('materiaux', 0)),
                                ("Restaur.", scores.get('restauration', 0))
                            ]
                            for label, val in gauges:
                                st.markdown(f"""
                                <div class="gauge-container">
                                    <div class="gauge-label">
                                        <span>{label}</span>
                                        <span>{val}%</span>
                                    </div>
                                    <div class="gauge-bg">
                                        <div class="gauge-fill" style="width: {val}%;"></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # MATÉRIAU & AVIS
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">🧬 Analyse Expert</div>', unsafe_allow_html=True)
                        html_table = '<table class="styled-table"><tbody>'
                        for row in data.get('composition_materiau', []):
                            html_table += f"<tr><td width='35%'><b>{row['couche']}</b></td><td>{row['compo']} <br><small style='color:#ea580c'>{row['etat']}</small></td></tr>"
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="margin-top:10px; padding:10px; background:#f9fafb; border-radius:8px; font-size:0.85em; line-height:1.5;">
                            🪑 {data.get('avis_menuisier')}<br><br>
                            🧵 {data.get('avis_tapissier')}
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # SCÉNARIOS
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">⚖️ Options</div>', unsafe_allow_html=True)
                        scenarios = data.get('scenarios', [])
                        cols = st.columns(3)
                        for i, col in enumerate(cols):
                            if i < len(scenarios):
                                scen = scenarios[i]
                                col.markdown(f"""
                                <div class="scenario-card">
                                    <div style="font-size:1.2em; margin-bottom:2px;">{scen['icone']}</div>
                                    <div class="scenario-title">{scen['titre']}</div>
                                    <div class="scenario-cost">{scen['cout']}</div>
                                    <div class="scenario-result">{scen['resultat']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # CONSEIL FINAL
                        st.markdown(f"""
                        <div class="tech-card" style="background:#ecfdf5; border:1px solid #10b981; border-top:none; padding:15px;">
                            <div style="color:#047857; font-weight:800; margin-bottom:5px; text-transform:uppercase; font-size:0.85em;">💡 Le Conseil du Gwani</div>
                            <p style="color:#065f46; margin:0; font-weight:600; font-size:0.95em;">{data.get('recommandation_finale')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # SAUVEGARDE SHEETS
                        save_data_to_sheets(data.get('titre'), price_input, global_score, data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur lecture IA.")
elif error_msg:
    st.warning(error_msg)
elif not img_file_buffer:
    pass # Plus d'espace vide inutile

# --- FOOTER ---
st.markdown("""
    <div style='text-align: center; margin-top: 30px; color: #9ca3af; font-size: 0.8em;'>
        Made in Niger 🇳🇪
    </div>
    """, unsafe_allow_html=True)
