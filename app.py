import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime
import time
import json
import re
import html
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

# --- CSS DESIGN "LUMIÈRE & ÉPURÉ" v2 (Micro-interactions + Palette dynamique) ---
st.markdown("""
    <style>
    /* Importation Police Exo 2 */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800;900&display=swap');

    /* 1. POLICE GLOBALE */
    html, body, [class*="css"] {
        font-family: 'Exo 2', sans-serif;
    }

    /* 2. COULEURS TEXTE GLOBALES */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
        color: #1f2937 !important;
    }

    /* 3. INPUTS LISIBLES (fix Dark Mode) */
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 1px solid #d1d5db !important;
        caret-color: #ea580c !important;
        font-weight: 700 !important;
        font-size: 1.05em !important;
        border-radius: 10px !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .stNumberInput input:focus {
        border-color: #ea580c !important;
        box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.15) !important;
    }
    .stNumberInput button {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
    }

    /* 4. ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: white;
        border-radius: 12px;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        border: 1px solid #e5e7eb;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        border-radius: 8px;
        font-weight: 600;
        color: #6b7280 !important;
        background-color: transparent !important;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #fafafa !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #fff7ed !important;
        color: #ea580c !important;
    }

    /* 5. UPLOAD ZONE */
    div[data-testid="stFileUploader"] {
        background-color: #f9fafb;
        border: 1.5px dashed #d1d5db;
        border-radius: 12px;
        padding: 20px;
        transition: border-color 0.2s, background-color 0.2s;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #ea580c;
        background-color: #fffbf7;
    }
    div[data-testid="stFileUploader"] section > div {
        color: #4b5563 !important;
    }
    div[data-testid="stFileUploader"] button {
        background-color: white !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
    }

    /* Exceptions texte blanc */
    .stButton > button, .verdict-badge, div[data-testid="stCameraInput"] button,
    .hero-chip, .verdict-hero *, .btn-secondary {
        color: white !important;
    }
    .stCaption, div[data-testid="stCaptionContainer"] p {
        color: #6b7280 !important;
    }

    /* ARRIÈRE-PLAN */
    .stApp {
        background-color: #fafafa;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* HERO HEADER */
    .hero-wrap {
        text-align: center;
        padding: 10px 0 18px 0;
    }
    .hero-chip {
        display: inline-block;
        background: linear-gradient(90deg, #ea580c, #f59e0b);
        padding: 4px 14px;
        border-radius: 100px;
        font-size: 0.7em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.25);
    }
    .hero-title {
        font-weight: 900 !important;
        font-size: 2rem !important;
        margin: 0 !important;
        background: linear-gradient(135deg, #1f2937, #ea580c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        color: #6b7280 !important;
        font-weight: 500;
        margin-top: 4px;
        font-size: 0.95em;
    }

    /* CARTE RÉSULTAT (avec fade-in) */
    .tech-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 16px;
        border: 1px solid #f3f4f6;
        animation: fadeUp 0.4s ease-out both;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* HEADER DE CARTE */
    .tech-header {
        color: #ea580c !important;
        font-weight: 700;
        font-size: 0.95em;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 2px solid #fff7ed;
        padding-bottom: 6px;
    }

    /* VERDICT HERO BANNER */
    .verdict-hero {
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        animation: fadeUp 0.4s ease-out both;
    }
    .verdict-hero .big-icon {
        font-size: 2.4em;
        line-height: 1;
    }
    .verdict-hero .v-title {
        color: white !important;
        font-weight: 800;
        font-size: 1.2em;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .verdict-hero .v-sub {
        color: rgba(255,255,255,0.92) !important;
        font-size: 0.85em;
        margin: 0;
        font-weight: 500;
    }
    .vh-green  { background: linear-gradient(135deg, #10b981, #059669); }
    .vh-orange { background: linear-gradient(135deg, #f59e0b, #ea580c); }
    .vh-red    { background: linear-gradient(135deg, #ef4444, #b91c1c); }

    /* CERCLE DE SCORE (palette dynamique) */
    .score-circle-container {
        display: flex;
        justify-content: center;
        margin: 16px 0 10px;
    }
    .score-circle {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        transition: transform 0.3s;
    }
    .score-circle::before {
        content: "";
        width: 108px;
        height: 108px;
        background: white;
        border-radius: 50%;
        position: absolute;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.04);
    }
    .score-value {
        position: relative;
        font-size: 1.95em;
        font-weight: 800;
    }
    .score-label {
        position: relative;
        display: block;
        text-align: center;
        font-size: 0.65em;
        color: #6b7280 !important;
        font-weight: 700;
        margin-top: -4px;
        letter-spacing: 1px;
    }

    /* JAUGES */
    .gauge-container {
        margin-bottom: 12px;
    }
    .gauge-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.85em;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .gauge-bg {
        height: 10px;
        background: #f3f4f6;
        border-radius: 5px;
        overflow: hidden;
    }
    .gauge-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.6s ease-out;
    }

    /* COMPARATEUR PRIX */
    .price-compare {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 10px;
    }
    .price-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
    }
    .price-box.highlight {
        background: #fff7ed;
        border-color: #fdba74;
    }
    .price-box .pb-label {
        font-size: 0.7em;
        font-weight: 700;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .price-box .pb-value {
        font-size: 1.15em;
        font-weight: 800;
        color: #1f2937 !important;
        margin-top: 4px;
    }
    .price-box.highlight .pb-value { color: #ea580c !important; }
    .price-delta {
        text-align: center;
        margin-top: 10px;
        font-weight: 700;
        font-size: 0.9em;
        padding: 6px;
        border-radius: 8px;
    }
    .delta-good { background: #ecfdf5; color: #047857 !important; }
    .delta-bad  { background: #fef2f2; color: #b91c1c !important; }
    .delta-neutral { background: #fffbeb; color: #92400e !important; }

    /* CARTES SCENARIOS */
    .scenario-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .scenario-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,0,0.06);
    }
    .scenario-title {
        font-weight: 800;
        color: #374151 !important;
        margin-bottom: 5px;
        text-transform: uppercase;
        font-size: 0.75em;
    }
    .scenario-cost {
        font-size: 0.72em;
        color: #6b7280 !important;
        margin-bottom: 5px;
    }
    .scenario-result {
        font-weight: 700;
        color: #ea580c !important;
        font-size: 0.9em;
    }

    /* TABLEAUX */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }
    .styled-table td {
        padding: 10px 0;
        border-bottom: 1px solid #f3f4f6;
        color: #1f2937 !important;
    }

    /* BADGES */
    .verdict-badge {
        padding: 6px 12px;
        border-radius: 100px;
        font-weight: 700;
        font-size: 0.85em;
    }
    .bg-green { background-color: #10b981; }
    .bg-orange { background-color: #f59e0b; }
    .bg-red { background-color: #ef4444; }

    /* BOUTONS */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.6em;
        background: linear-gradient(135deg, #ea580c, #f97316);
        color: white !important;
        font-weight: 700;
        border: none;
        font-size: 1.05em;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 6px 16px rgba(234, 88, 12, 0.28);
        transition: transform 0.15s, box-shadow 0.15s, opacity 0.2s;
    }
    .stButton > button:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(234, 88, 12, 0.35);
    }
    .stButton > button:active:not(:disabled) {
        transform: translateY(0);
    }
    .stButton > button:disabled {
        background: #e5e7eb !important;
        color: #9ca3af !important;
        box-shadow: none !important;
        cursor: not-allowed;
    }

    /* BOUTON SECONDAIRE (Reset) */
    .stButton.secondary-btn > button,
    button[kind="secondary"] {
        background: white !important;
        color: #ea580c !important;
        border: 1.5px solid #ea580c !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover:not(:disabled) {
        background: #fff7ed !important;
    }

    /* CAMÉRA */
    div[data-testid="stCameraInput"] button {
        background: linear-gradient(135deg, #ea580c, #f97316) !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        border: 2px solid white !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25) !important;
    }

    /* PREVIEW IMAGE */
    .preview-wrap {
        display: flex;
        justify-content: center;
        margin: 10px 0 14px;
    }
    .preview-wrap img {
        max-width: 220px;
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        border: 3px solid white;
    }

    /* EMPTY STATE ANIMÉ */
    .empty-state {
        text-align: center;
        padding: 34px 20px;
        color: #9ca3af;
    }
    .empty-state .bounce {
        font-size: 3.2em;
        display: inline-block;
        animation: bounce 2.2s ease-in-out infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-8px); }
    }
    .empty-state .es-title {
        font-weight: 700;
        margin-top: 6px;
        color: #6b7280 !important;
    }
    .empty-state .es-hint {
        font-size: 0.85em;
        color: #9ca3af !important;
        margin-top: 4px;
    }

    /* INFO COMPACT CHIP */
    .info-chip {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a !important;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.82em;
        font-weight: 500;
        margin-bottom: 14px;
    }
    .info-chip b { color: #1e3a8a !important; }

    /* CONSEIL FINAL */
    .advice-card {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid #10b981;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 16px;
        animation: fadeUp 0.4s ease-out both;
    }
    .advice-card .advice-title {
        color: #047857 !important;
        font-weight: 800;
        margin-bottom: 6px;
        text-transform: uppercase;
        font-size: 0.85em;
        letter-spacing: 1px;
    }
    .advice-card p {
        color: #065f46 !important;
        margin: 0;
        font-weight: 600;
        line-height: 1.5;
    }

    /* MOBILE */
    @media only screen and (max-width: 600px) {
        .main .block-container {
            padding-top: 1.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 120px !important;
        }
        .hero-title { font-size: 1.55rem !important; }
        .score-circle { width: 110px; height: 110px; }
        .score-circle::before { width: 90px; height: 90px; }
        .score-value { font-size: 1.6em; }
        .price-compare { grid-template-columns: 1fr; }
    }

    /* DESKTOP : un peu plus de largeur pour respirer sur grand écran */
    @media only screen and (min-width: 1024px) {
        .main .block-container {
            max-width: 900px !important;
        }
    }

    /* SKELETON LOADER (pendant l'analyse) */
    .skeleton-shimmer {
        background: linear-gradient(90deg, #eef0f2 25%, #f7f8fa 50%, #eef0f2 75%);
        background-size: 200% 100%;
        animation: shimmer 1.4s infinite;
        border-radius: 8px;
    }
    @keyframes shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .skeleton-line { height: 14px; margin-bottom: 12px; }
    .skeleton-line:last-child { margin-bottom: 0; }

    /* MODE SOMBRE (auto, basé sur les préférences système) */
    @media (prefers-color-scheme: dark) {
        :root { color-scheme: dark; }

        .stApp {
            background-color: #0f172a;
            background-image: radial-gradient(#1e293b 1px, transparent 1px);
        }
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, td, th {
            color: #e5e7eb !important;
        }
        .stCaption, div[data-testid="stCaptionContainer"] p {
            color: #94a3b8 !important;
        }
        .tech-card, .scenario-card, .price-box {
            background: #1e293b;
            border-color: #334155;
        }
        .tech-card { box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .price-box.highlight { background: #3a2a1a; border-color: #ea580c; }
        .styled-table td { border-bottom-color: #334155; }
        .skeleton-shimmer {
            background: linear-gradient(90deg, #1e293b 25%, #273449 50%, #1e293b 75%);
            background-size: 200% 100%;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1e293b;
            border-color: #334155;
        }
        .stTabs [data-baseweb="tab"]:hover { background-color: #273449 !important; }
        .stTabs [aria-selected="true"] { background-color: #3a2412 !important; }
        div[data-testid="stFileUploader"] {
            background-color: #1e293b;
            border-color: #334155;
        }
        div[data-testid="stFileUploader"] button {
            background-color: #0f172a !important;
            color: #e5e7eb !important;
            border-color: #334155 !important;
        }
        .info-chip {
            background: #1e2f4d;
            border-color: #2c4a75;
            color: #cfe2ff !important;
        }
        .info-chip b { color: #cfe2ff !important; }
        button[kind="secondary"] {
            background: #1e293b !important;
        }
        .streamlit-expanderHeader, div[data-testid="stExpander"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- ÉTAT DE SESSION ---
if "widget_version" not in st.session_state:
    st.session_state.widget_version = 0
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "scroll_to_result" not in st.session_state:
    st.session_state.scroll_to_result = False
if "history" not in st.session_state:
    st.session_state.history = []

def reset_analysis():
    """Efface le résultat et force le reset des widgets (photo, prix)."""
    st.session_state.last_analysis = None
    st.session_state.processing = False
    st.session_state.widget_version += 1
    st.rerun()

# --- API KEY ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    with st.expander("🔐 Configuration Clé API"):
        api_key = st.text_input("Clé API Google Gemini", type="password")

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
        except Exception:
            updated_data = new_data
        conn.update(worksheet="Sheet1", data=updated_data)
    except Exception:
        pass

# --- UTILITAIRES ---
def clean_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

def fmt_fcfa(n):
    """Formate un nombre en FCFA avec espaces : 125000 -> '125 000 FCFA'."""
    try:
        return f"{int(n):,} FCFA".replace(",", " ")
    except Exception:
        return f"{n} FCFA"

def score_color(score):
    """Retourne une couleur hex selon le score (rouge / orange / vert)."""
    if score >= 70:
        return "#10b981", "#d1fae5"  # vert
    if score >= 45:
        return "#f59e0b", "#fef3c7"  # orange
    return "#ef4444", "#fee2e2"      # rouge

def render_preview(images):
    """Affiche 1 à 3 photos : une seule photo centrée, ou une rangée de miniatures."""
    if not images:
        return
    if len(images) == 1:
        st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
        st.image(images[0], width=220)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(len(images))
        for c, img in zip(cols, images):
            with c:
                st.image(img, use_container_width=True)

# --- SCANNER MODÈLES GEMINI ---
def find_best_model_dynamic():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        if not available_models:
            return None, "Aucun modèle trouvé."
        for m in available_models:
            if 'flash' in m.lower():
                return m, None
        for m in available_models:
            if 'pro' in m.lower() and 'vision' not in m.lower():
                return m, None
        return available_models[0], None
    except Exception as e:
        return "models/gemini-1.5-flash", str(e)

# --- ANALYSE IA ---
def analyze_image_pro(images, price, api_key):
    genai.configure(api_key=api_key)
    model_name, scan_error = find_best_model_dynamic()
    if not model_name:
        return None, scan_error

    prompt = f"""
    Tu es un expert menuisier à Niamey (Niger). Analyse ce meuble (Prix demandé : {price} FCFA).
    Tu reçois une ou plusieurs photos du même meuble (jusqu'à 3 angles différents) : croise les
    informations entre les photos pour affiner ton diagnostic (structure, matériaux, défauts).

    Liste des objets acceptés : Canapé, fauteuil, table basse, meuble TV, lit, armoire, commode, chevet, table à manger, chaise, buffet, bureau, bibliothèque, console, meuble à chaussures, dressing, lit superposé, canapé-lit, banquette, table de cuisine, tabouret, meuble sous-vasque.

    Si l'objet n'est PAS un meuble de cette liste (ou similaire), renvoie {{"is_furniture": false}}.

    Sinon, renvoie un JSON valide STRICT :
    {{
        "is_furniture": true,
        "titre": "Type précis (ex: Table de chevet)",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
        "prix_estime_min": 15000,
        "prix_estime_max": 25000,
        "scores": {{
            "solidite": 75,
            "materiaux": 60,
            "restauration": 90,
            "global": 70
        }},
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
        "recommandation_finale": "Conseil court et actionnable."
    }}
    RÈGLES :
    - Les scores sont sur 100.
    - prix_estime_min et prix_estime_max sont en FCFA, cohérents avec le marché de Niamey (Katako, Wadata, Marketplace).
    """

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, *images])
        return clean_json_response(response.text), model_name
    except Exception as e:
        if "429" in str(e):
            time.sleep(2)
            try:
                response = model.generate_content([prompt, *images])
                return clean_json_response(response.text), model_name
            except Exception:
                return None, "Surcharge serveur"
        return None, str(e)

# --- HERO ---
st.markdown("""
<div class="hero-wrap">
    <span class="hero-chip">🇳🇪 Expert Meuble · IA</span>
    <h1 class="hero-title">Gaskiyar Kaya</h1>
    <p class="hero-subtitle">Scannez. Comparez. Négociez en toute confiance.</p>
</div>
""", unsafe_allow_html=True)

# INFO CHIP COMPACT (remplace st.info)
st.markdown("""
<div class="info-chip">
    <span style="font-size:1.2em;">ℹ️</span>
    <div><b>Une photo suffit</b>, ajoutez jusqu'à 3 angles pour une analyse plus précise. JPG · PNG · WEBP</div>
</div>
""", unsafe_allow_html=True)

with st.expander("📐 Conseils pour une photo réussie"):
    st.markdown("""
- ✅ **Lumière naturelle** : évitez le flash direct qui écrase les détails.
- ✅ Cadrez **tout le meuble**, y compris les pieds et les angles.
- ✅ Ajoutez une **photo de détail** (rayure, tissu, assemblage) si vous le pouvez.
- ❌ Évitez les photos floues ou prises de trop loin.
- ❌ Évitez les arrière-plans encombrés qui perturbent l'analyse.
""")

# --- HISTORIQUE DE SESSION ---
if st.session_state.history:
    with st.expander(f"🕘 Historique de cette session ({len(st.session_state.history)})"):
        for i, entry in enumerate(st.session_state.history):
            v = entry["verdict"]
            badge = "🟢" if "Affaire" in v else ("🟠" if "Correct" in v else "🔴")
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.markdown(
                    f"{badge} **{html.escape(entry['titre'])}** — "
                    f"{fmt_fcfa(entry['price'])} · Score {entry['score']}% · {entry['timestamp']}"
                )
            with col_h2:
                if st.button("Revoir", key=f"hist_{i}", use_container_width=True):
                    st.session_state.last_analysis = entry["snapshot"]
                    st.session_state.scroll_to_result = True
                    st.rerun()
        st.caption("Historique valable uniquement pour cette session de navigateur (non partagé, non sauvegardé).")

# --- CAPTURE IMAGE ---
wv = st.session_state.widget_version
tab_cam, tab_upload = st.tabs(["📸 Prendre Photo", "📂 Galerie"])
img_files = []

with tab_cam:
    camera_img = st.camera_input("Cadrez le meuble", label_visibility="collapsed", key=f"camera_{wv}")
    if camera_img:
        img_files = [camera_img]

with tab_upload:
    upload_imgs = st.file_uploader(
        "Choisir une ou plusieurs images (max 3 angles)",
        type=["jpg", "png", "jpeg", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"upload_{wv}"
    )
    if upload_imgs:
        img_files = upload_imgs[:3]
        if len(upload_imgs) > 3:
            st.caption("⚠️ Seules les 3 premières photos seront analysées.")

# --- PRIX ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<span style="font-weight:700; color:#1f2937 !important">💰 Prix annoncé par le vendeur (FCFA)</span>',
    unsafe_allow_html=True
)
price_input = st.number_input(
    "Prix",
    min_value=0,
    step=5000,
    value=0,
    format="%d",
    label_visibility="collapsed",
    help="Entrez le prix proposé par le vendeur pour comparer à l'estimation IA.",
    key=f"price_{wv}"
)
if price_input > 0:
    st.markdown(
        f'<div style="text-align:right; font-size:0.85em; color:#6b7280; margin-top:-8px;">'
        f'Soit <b style="color:#ea580c;">{fmt_fcfa(price_input)}</b></div>',
        unsafe_allow_html=True
    )
    if price_input < 500:
        st.caption("⚠️ Ce prix semble très bas, vérifiez qu'il est bien exprimé en FCFA.")
    elif price_input > 3_000_000:
        st.caption("⚠️ Ce prix semble très élevé pour un meuble d'occasion, vérifiez votre saisie.")

# --- ÉTAT PRÊT ---
has_image = len(img_files) > 0
has_price = price_input > 0
is_ready = has_image and has_price

# Message d'aide contextuel
st.markdown("<br>", unsafe_allow_html=True)
if not has_image and not has_price:
    st.markdown(
        '<div class="empty-state">'
        '<span class="bounce">📸</span>'
        '<div class="es-title">Prenez ou importez une photo pour commencer</div>'
        '<div class="es-hint">Puis indiquez le prix demandé</div>'
        '</div>',
        unsafe_allow_html=True
    )
elif has_image and not has_price:
    st.markdown(
        '<div style="text-align:center; color:#92400e; background:#fffbeb; border:1px solid #fde68a; '
        'padding:10px; border-radius:10px; font-weight:600; font-size:0.9em;">'
        '⚠️ Saisissez le prix demandé pour lancer l\'analyse'
        '</div>',
        unsafe_allow_html=True
    )
elif has_price and not has_image:
    st.markdown(
        '<div style="text-align:center; color:#92400e; background:#fffbeb; border:1px solid #fde68a; '
        'padding:10px; border-radius:10px; font-weight:600; font-size:0.9em;">'
        '📷 Ajoutez une photo du meuble pour lancer l\'analyse'
        '</div>',
        unsafe_allow_html=True
    )

# --- RENDU DU RÉSULTAT (persistant via session_state) ---
def render_result(result):
    status = result["status"]
    images = result.get("images") or []
    price_for_render = result.get("price", 0)

    render_preview(images)

    if status == "error":
        st.markdown(
            f'<div class="tech-card" style="background:#fef2f2; border-color:#fecaca;">'
            f'<div style="color:#b91c1c !important; font-weight:700;">❌ Erreur technique</div>'
            f'<div style="color:#991b1b !important; font-size:0.85em; margin-top:4px;">{html.escape(str(result.get("error_msg") or ""))}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    elif status == "not_furniture":
        st.markdown(
            '<div class="tech-card" style="background:#fef2f2; border-color:#fecaca;">'
            '<div style="color:#b91c1c !important; font-weight:700; font-size:1.05em;">🛑 Objet non reconnu</div>'
            '<div style="color:#7f1d1d !important; font-size:0.9em; margin-top:6px;">'
            'Objets acceptés : Tables, Lits, Canapés, Armoires, Fauteuils, Commodes, Bureaux, Chaises...'
            '</div></div>',
            unsafe_allow_html=True
        )
    elif status == "json_error":
        st.markdown(
            '<div class="tech-card" style="background:#fef2f2; border-color:#fecaca;">'
            '<div style="color:#b91c1c !important; font-weight:700;">❌ Erreur de lecture</div>'
            '<div style="color:#991b1b !important; font-size:0.85em; margin-top:4px;">'
            'L\'IA a renvoyé un format inattendu. Réessayez avec une photo plus nette.'
            '</div></div>',
            unsafe_allow_html=True
        )
    elif status == "success":
        data = result["data"]

        # === VERDICT HERO (bannière top) ===
        v_raw = data.get('verdict_prix', 'N/A')
        titre_safe = html.escape(str(data.get('titre', '')))
        style_safe = html.escape(str(data.get('style', '')))

        if "Affaire" in v_raw:
            vh_class, vh_icon, vh_sub = "vh-green", "🎯", "Bonne affaire à saisir"
        elif "Correct" in v_raw:
            vh_class, vh_icon, vh_sub = "vh-orange", "⚖️", "Prix cohérent, possibilité de négocier"
        else:
            vh_class, vh_icon, vh_sub = "vh-red", "⚠️", "Prix élevé, négociez ferme"

        st.markdown(f"""
        <div class="verdict-hero {vh_class}">
            <div class="big-icon">{vh_icon}</div>
            <div style="flex:1;">
                <p class="v-title">{html.escape(str(v_raw))}</p>
                <p class="v-sub">{vh_sub}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # === IDENTITÉ MEUBLE ===
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='margin:0 0 4px 0; font-size:1.35em; font-weight:800'>{titre_safe}</h3>"
            f"<span style='color:#6b7280; font-size:0.9em; font-weight:500'>{style_safe}</span>",
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # === COMPARATEUR PRIX ===
        prix_min = data.get('prix_estime_min')
        prix_max = data.get('prix_estime_max')
        if prix_min and prix_max:
            try:
                prix_min_i = int(prix_min)
                prix_max_i = int(prix_max)
                prix_mid = (prix_min_i + prix_max_i) // 2
                delta = price_for_render - prix_mid
                pct = (delta / prix_mid) * 100 if prix_mid else 0

                if price_for_render <= prix_max_i and price_for_render >= prix_min_i:
                    delta_class = "delta-good"
                    delta_text = f"✅ Dans la fourchette du marché"
                elif price_for_render < prix_min_i:
                    delta_class = "delta-good"
                    delta_text = f"🎯 Sous le marché ({abs(pct):.0f}% moins cher)"
                else:
                    delta_class = "delta-bad" if pct > 25 else "delta-neutral"
                    delta_text = f"⚠️ Au-dessus du marché (+{pct:.0f}%)"

                st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                st.markdown('<div class="tech-header">💸 Comparateur Prix</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="price-compare">
                    <div class="price-box">
                        <div class="pb-label">Prix demandé</div>
                        <div class="pb-value">{fmt_fcfa(price_for_render)}</div>
                    </div>
                    <div class="price-box highlight">
                        <div class="pb-label">Estimation IA</div>
                        <div class="pb-value">{fmt_fcfa(prix_min_i)} – {fmt_fcfa(prix_max_i).replace(' FCFA','')}</div>
                    </div>
                </div>
                <div class="price-delta {delta_class}">{delta_text}</div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            except (ValueError, TypeError):
                pass

        # === PERFORMANCE (score circle + jauges dynamiques) ===
        scores = data.get('scores', {})
        global_score = int(scores.get('global', 50))
        col_main, col_bg = score_color(global_score)

        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown('<div class="tech-header">📊 Performance</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="score-circle-container">
            <div class="score-circle" style="background: conic-gradient({col_main} {global_score}%, #f3f4f6 0);">
                <div style="position:absolute; text-align:center;">
                    <div class="score-value" style="color:{col_main};">{global_score}%</div>
                    <span class="score-label">ÉTAT GLOBAL</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauges = [
            ("🧱 Solidité Structurelle", int(scores.get('solidite', 0))),
            ("💎 Qualité Matériaux",     int(scores.get('materiaux', 0))),
            ("🛠️ Facilité Restauration", int(scores.get('restauration', 0))),
        ]
        for label, val in gauges:
            g_col, _ = score_color(val)
            st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-label">
                    <span>{label}</span>
                    <span style="color:{g_col};">{val}%</span>
                </div>
                <div class="gauge-bg">
                    <div class="gauge-fill" style="width: {val}%; background: linear-gradient(90deg, {g_col}99, {g_col});"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # === COMPOSITION MATÉRIAUX ===
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown('<div class="tech-header">🧬 Composition</div>', unsafe_allow_html=True)
        html_table = '<table class="styled-table"><tbody>'
        for row in data.get('composition_materiau', []):
            couche_safe = html.escape(str(row.get('couche', '')))
            compo_safe = html.escape(str(row.get('compo', '')))
            etat_safe = html.escape(str(row.get('etat', '')))
            html_table += (
                f"<tr><td width='30%'><b>{couche_safe}</b></td>"
                f"<td>{compo_safe}<br><small style='color:#ea580c'>{etat_safe}</small></td></tr>"
            )
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)

        avis_menuisier_safe = html.escape(str(data.get('avis_menuisier', '')))
        avis_tapissier_safe = html.escape(str(data.get('avis_tapissier', '')))
        st.markdown(f"""
        <div style="margin-top:14px; padding:14px; background:#f9fafb; border-radius:10px;
                     font-size:0.9em; border-left: 3px solid #ea580c;">
            🪑 <b>Menuisier :</b> {avis_menuisier_safe}<br><br>
            🧵 <b>Tapissier :</b> {avis_tapissier_safe}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # === SCÉNARIOS ===
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown('<div class="tech-header">⚖️ Scénarios d\'Action</div>', unsafe_allow_html=True)
        scenarios = data.get('scenarios', [])
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if i < len(scenarios):
                scen = scenarios[i]
                icone_safe = html.escape(str(scen.get('icone', '')))
                titre_scen_safe = html.escape(str(scen.get('titre', '')))
                cout_safe = html.escape(str(scen.get('cout', '')))
                resultat_safe = html.escape(str(scen.get('resultat', '')))
                col.markdown(f"""
                <div class="scenario-card">
                    <div style="font-size:1.7em; margin-bottom:5px;">{icone_safe}</div>
                    <div class="scenario-title">{titre_scen_safe}</div>
                    <div class="scenario-cost">Coût : {cout_safe}</div>
                    <div class="scenario-result">{resultat_safe}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # === CONSEIL FINAL ===
        reco_safe = html.escape(str(data.get('recommandation_finale', '')))
        st.markdown(f"""
        <div class="advice-card">
            <div class="advice-title">💡 Le Conseil du Gwani</div>
            <p>{reco_safe}</p>
        </div>
        """, unsafe_allow_html=True)

        # === FEEDBACK UTILISATEUR ===
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown('<div class="tech-header">🗳️ Ce verdict vous semble-t-il juste ?</div>', unsafe_allow_html=True)
        if result.get("feedback"):
            fb_msg = "👍 Merci pour votre retour !" if result["feedback"] == "up" else "👎 Merci, c'est noté."
            st.markdown(f'<div style="color:#6b7280; font-weight:600;">{fb_msg}</div>', unsafe_allow_html=True)
        else:
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                if st.button("👍 Oui, pertinent", use_container_width=True, key="fb_up"):
                    result["feedback"] = "up"
                    st.rerun()
            with fb_col2:
                if st.button("👎 Pas vraiment", use_container_width=True, key="fb_down"):
                    result["feedback"] = "down"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # === ACTIONS : NOUVELLE ANALYSE / PARTAGER ===
        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Nouvelle analyse", use_container_width=True, type="secondary", key="reset_success"):
                reset_analysis()
        with col_b:
            # Mini-résumé à copier / partager
            summary = (
                f"Gaskiyar Kaya - {data.get('titre', '')}\n"
                f"Verdict : {v_raw}\n"
                f"Score global : {global_score}%\n"
                f"Prix demandé : {fmt_fcfa(price_for_render)}\n"
            )
            if prix_min and prix_max:
                summary += f"Estimation IA : {fmt_fcfa(prix_min)} – {fmt_fcfa(prix_max)}\n"
            summary += f"Conseil : {data.get('recommandation_finale', '')}"
            with st.popover("📤 Partager", use_container_width=True):
                st.code(summary, language=None)
                components.html(f"""
                    <button id="share-btn" style="width:100%; padding:10px; border-radius:8px;
                        border:1.5px solid #ea580c; background:white; color:#ea580c; font-weight:700;
                        font-family:inherit; cursor:pointer;">
                        📱 Partager / Copier en un clic
                    </button>
                    <script>
                        const btn = document.getElementById('share-btn');
                        const text = {json.dumps(summary)};
                        btn.addEventListener('click', async () => {{
                            try {{
                                if (navigator.share) {{
                                    await navigator.share({{ title: 'Gaskiyar Kaya', text: text }});
                                    return;
                                }}
                            }} catch (e) {{ /* annulé ou non supporté, on tente la copie */ }}
                            try {{
                                await navigator.clipboard.writeText(text);
                                btn.innerText = '✅ Copié !';
                                setTimeout(() => btn.innerText = '📱 Partager / Copier en un clic', 1500);
                            }} catch (e) {{ /* copie impossible : le texte reste sélectionnable ci-dessus */ }}
                        }});
                    </script>
                """, height=52)
                st.caption("Ou sélectionnez le texte ci-dessus pour copier manuellement.")
        return

    # Statuts sans rapport détaillé (erreur / non reconnu) : bouton pour recommencer
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Réessayer", use_container_width=True, type="secondary", key="reset_other"):
        reset_analysis()


# --- BOUTON D'ANALYSE (toujours visible, disabled si pas prêt ou en cours) ---
launch_clicked = st.button(
    "🔍 Lancer l'analyse",
    disabled=not is_ready or st.session_state.processing,
    use_container_width=True
)

# Un clic passe d'abord en état "processing" + rerun immédiat : le bouton se
# grise et le spinner apparaît tout de suite, avant même l'appel (bloquant) à
# l'IA. Ça évite aussi les doubles clics qui déclencheraient deux appels payants.
if launch_clicked and is_ready and not st.session_state.processing:
    st.session_state.processing = True
    st.rerun()

if st.session_state.processing:
    if not api_key:
        st.error("⚠️ Clé API manquante. Ouvrez la section Configuration ci-dessus.")
        st.session_state.processing = False
    else:
        images = [Image.open(f) for f in img_files]
        render_preview(images)

        # Squelette animé pendant le calcul (retiré dès que le résultat est prêt)
        skeleton_placeholder = st.empty()
        skeleton_placeholder.markdown("""
        <div class="tech-card skeleton-card">
            <div class="skeleton-shimmer skeleton-line" style="width:55%"></div>
            <div class="skeleton-shimmer skeleton-line" style="width:90%"></div>
            <div class="skeleton-shimmer skeleton-line" style="width:80%"></div>
            <div class="skeleton-shimmer skeleton-line" style="width:40%"></div>
        </div>
        """, unsafe_allow_html=True)

        # Étapes affichées pendant le vrai temps d'attente de l'IA (pas de délai artificiel)
        with st.status("🔎 Analyse de votre meuble...", expanded=True) as status_box:
            st.write("🔎 Reconnaissance de l'objet...")
            st.write("🧬 Analyse des matériaux et de la structure...")
            st.write("⚖️ Comparaison aux prix du marché nigérien...")
            json_str, info_msg = analyze_image_pro(images, price_input, api_key)
            if json_str:
                status_box.update(label="✅ Rapport d'expertise généré", state="complete", expanded=False)
            else:
                status_box.update(label="❌ Échec de l'analyse", state="error", expanded=False)
        skeleton_placeholder.empty()

        if not json_str:
            st.session_state.last_analysis = {
                "status": "error", "error_msg": info_msg, "images": images, "price": price_input
            }
        else:
            try:
                data = json.loads(json_str)
                if not data.get("is_furniture"):
                    st.session_state.last_analysis = {
                        "status": "not_furniture", "images": images, "price": price_input
                    }
                else:
                    global_score = int(data.get('scores', {}).get('global', 50))
                    save_data_to_sheets(
                        data.get('titre'),
                        price_input,
                        global_score,
                        data.get('verdict_prix')
                    )
                    st.session_state.last_analysis = {
                        "status": "success", "data": data, "images": images, "price": price_input
                    }
                    st.session_state.history.insert(0, {
                        "titre": data.get('titre', 'Meuble'),
                        "verdict": data.get('verdict_prix', 'N/A'),
                        "score": global_score,
                        "price": price_input,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "snapshot": st.session_state.last_analysis,
                    })
                    st.session_state.history = st.session_state.history[:5]
            except json.JSONDecodeError:
                st.session_state.last_analysis = {
                    "status": "json_error", "images": images, "price": price_input
                }

        st.session_state.processing = False
        st.session_state.scroll_to_result = True

    st.rerun()

if st.session_state.last_analysis:
    st.markdown('<div id="result-top"></div>', unsafe_allow_html=True)
    render_result(st.session_state.last_analysis)
    if st.session_state.pop("scroll_to_result", False):
        components.html(
            """
            <script>
                setTimeout(function() {
                    var el = window.parent.document.getElementById('result-top');
                    if (el) { el.scrollIntoView({behavior: 'smooth', block: 'start'}); }
                }, 150);
            </script>
            """,
            height=0,
        )

# --- FOOTER ---
st.markdown("""
    <div style='text-align: center; margin-top: 50px; color: #6b7280; font-size: 0.85em;'>
        <div>Made in Niger with ❤️ by <b>Moh</b></div>
        <div style="margin-top:4px; font-size:0.9em; opacity:0.8;">
            Propulsé par Google Gemini · <a href="https://github.com/blakro/market-scanner-niger" target="_blank" style="color:#ea580c; text-decoration:none;">GitHub</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
