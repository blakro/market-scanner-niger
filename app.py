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
    /* Importation Police Exo 2 */
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700;800&display=swap');

    /* RESET & BASE */
    * {
        font-family: 'Exo 2', sans-serif !important;
        color: #1f2937;
    }

    .stApp {
        background-color: #fafafa;
        background-image: radial-gradient(#e5e7eb 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* CARTE RÉSULTAT */
    .tech-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #f3f4f6;
    }
    
    /* TITRES */
    h1 {
        color: #111827 !important;
        font-weight: 800 !important;
        text-align: center;
        text-transform: uppercase;
    }
    .tech-header {
        color: #ea580c;
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
    
    /* CERCLE DE SCORE (CSS PUR) */
    .score-circle-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#ea580c var(--percent), #f3f4f6 0);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .score-circle::before {
        content: "";
        width: 100px;
        height: 100px;
        background: white;
        border-radius: 50%;
        position: absolute;
    }
    .score-value {
        position: relative;
        font-size: 1.8em;
        font-weight: 800;
        color: #ea580c;
    }
    .score-label {
        position: relative;
        display: block;
        text-align: center;
        font-size: 0.7em;
        color: #6b7280;
        font-weight: 600;
        margin-top: -5px;
    }

    /* JAUGES CUSTOM */
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
        background: linear-gradient(90deg, #fcd34d, #ea580c);
        border-radius: 5px;
    }

    /* CARTE SCENARIO */
    .scenario-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        height: 100%;
    }
    .scenario-title {
        font-weight: 800;
        color: #374151;
        margin-bottom: 5px;
        text-transform: uppercase;
        font-size: 0.9em;
    }
    .scenario-cost {
        font-size: 0.8em;
        color: #6b7280;
        margin-bottom: 10px;
    }
    .scenario-result {
        font-weight: 700;
        color: #ea580c;
        font-size: 1em;
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
    }

    /* BADGES */
    .verdict-badge {
        padding: 6px 12px;
        border-radius: 100px;
        color: white;
        font-weight: 700;
        font-size: 0.85em;
    }
    .bg-green { background-color: #10b981; }
    .bg-orange { background-color: #f59e0b; }
    .bg-red { background-color: #ef4444; }

    /* BOUTON */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background-color: #ea580c;
        color: white !important;
        font-weight: 700;
        border: none;
        font-size: 1.1em;
        text-transform: uppercase;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #fff7ed !important;
        color: #ea580c !important;
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
    Si ce n'est pas un meuble, renvoie {{"is_furniture": false}}.
    Sinon, renvoie un JSON valide :
    {{
        "is_furniture": true,
        "titre": "Type court",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
        "scores": {{
            "solidite": 75,
            "materiaux": 60,
            "restauration": 90,
            "global": 70
        }},
        "composition_materiau": [
            {{"couche": "Surface", "compo": "ex: Cuir", "etat": "ex: Bon"}},
            {{"couche": "Structure", "compo": "ex: Bois", "etat": "ex: OK"}}
        ],
        "avis_menuisier": "Avis structure...",
        "avis_tapissier": "Avis tissu...",
        "scenarios": [
            {{"titre": "Réparer", "icone": "🛠️", "cout": "Cher", "resultat": "Moyen"}},
            {{"titre": "Housse", "icone": "🛋️", "cout": "Faible", "resultat": "Bon"}},
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

# --- INTERFACE ---
st.title("Gaskiyar Kaya 🇳🇪")
st.markdown("<p style='text-align:center; color:#6b7280; margin-top:-10px; margin-bottom:20px; font-weight:500;'>L'Expert Meuble de confiance</p>", unsafe_allow_html=True)

tab_cam, tab_upload = st.tabs(["📸 Prendre Photo", "📂 Galerie"])
img_file_buffer = None

with tab_cam:
    camera_img = st.camera_input("Cadrez le meuble", label_visibility="collapsed")
    if camera_img: img_file_buffer = camera_img

with tab_upload:
    upload_img = st.file_uploader("Choisir une image", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")
    if upload_img: img_file_buffer = upload_img

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<span style="font-weight:700; color:#1f2937">💰 Prix annoncé (FCFA)</span>', unsafe_allow_html=True)
price_input = st.number_input("Prix", min_value=0, step=50000, value=0, format="%d", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
if img_file_buffer and price_input >= 0:
    if st.button("LANCER L'ANALYSE"):
        if not api_key:
            st.error("⚠️ Clé API manquante")
        else:
            image = Image.open(img_file_buffer)
            st.image(image, width=120)
            
            with st.spinner("🔍 Analyse visuelle approfondie..."):
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
                        # EN-TÊTE
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

                        # SCORE CIRCULAIRE
                        scores = data.get('scores', {})
                        global_score = scores.get('global', 50)
                        
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">📊 Performance</div>', unsafe_allow_html=True)
                        
                        # Cercle HTML
                        st.markdown(f"""
                        <div class="score-circle-container">
                            <div class="score-circle" style="--percent: {global_score}%">
                                <div style="position:absolute; text-align:center;">
                                    <div class="score-value">{global_score}%</div>
                                    <span class="score-label">ÉTAT GLOBAL</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Barres de progression
                        gauges = [
                            ("🧱 Solidité Structurelle", scores.get('solidite', 0)),
                            ("💎 Qualité Matériaux", scores.get('materiaux', 0)),
                            ("🛠️ Facilité Restauration", scores.get('restauration', 0))
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

                        # MATÉRIAU
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">🧬 Composition</div>', unsafe_allow_html=True)
                        html_table = '<table class="styled-table"><tbody>'
                        for row in data.get('composition_materiau', []):
                            html_table += f"<tr><td width='30%'><b>{row['couche']}</b></td><td>{row['compo']} <br><small style='color:#ea580c'>{row['etat']}</small></td></tr>"
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div style="margin-top:15px; padding:15px; background:#f9fafb; border-radius:10px; font-size:0.9em; border-left: 3px solid #ea580c;">
                            🪑 <b>Menuisier :</b> {data.get('avis_menuisier')}<br><br>
                            🧵 <b>Tapissier :</b> {data.get('avis_tapissier')}
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # SCÉNARIOS (MODE CARTES)
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">⚖️ Scénarios</div>', unsafe_allow_html=True)
                        
                        scenarios = data.get('scenarios', [])
                        cols = st.columns(3)
                        for i, col in enumerate(cols):
                            if i < len(scenarios):
                                scen = scenarios[i]
                                col.markdown(f"""
                                <div class="scenario-card">
                                    <div style="font-size:1.5em; margin-bottom:5px;">{scen['icone']}</div>
                                    <div class="scenario-title">{scen['titre']}</div>
                                    <div class="scenario-cost">Coût: {scen['cout']}</div>
                                    <div class="scenario-result">{scen['resultat']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # CONSEIL FINAL
                        st.markdown(f"""
                        <div class="tech-card" style="background:#ecfdf5; border:1px solid #10b981; border-top:none;">
                            <div style="color:#047857; font-weight:800; margin-bottom:5px; text-transform:uppercase; font-size:0.9em;">💡 Le Conseil du Gwani</div>
                            <p style="color:#065f46; margin:0; font-weight:600;">{data.get('recommandation_finale')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        save_data(data.get('titre'), price_input, global_score, data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur lecture IA.")
elif not img_file_buffer:
    st.markdown("""
    <div style='text-align:center; padding:40px; color:#9ca3af;'>
        <p style="font-size:3em;">📸</p>
        <p style="font-weight:600;">Prenez une photo pour commencer</p>
    </div>
    """, unsafe_allow_html=True)
