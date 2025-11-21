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

# --- CSS PRO (Design "Carte") ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Importation Police Moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

    /* RESET & BASE */
    * {
        font-family: 'Poppins', sans-serif !important;
    }

    /* ARRIÈRE-PLAN VIBRANT (Gradient "Terre & Ciel du Niger") */
    .stApp {
        background: linear-gradient(135deg, #fcd34d 0%, #ea580c 50%, #7c2d12 100%);
        background-size: 400% 400%;
        animation: gradient 20s ease infinite;
    }
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    /* Cartes blanches avec effet verre */
    .tech-card {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-top: 4px solid #ea580c;
    }
    
    /* Titres de section */
    .tech-header {
        background: -webkit-linear-gradient(45deg, #ea580c, #b45309);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
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
        background-color: #fff7ed;
        color: #9a3412;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #fed7aa;
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
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .bg-green { background: linear-gradient(135deg, #10b981, #059669); }
    .bg-orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .bg-red { background: linear-gradient(135deg, #ef4444, #b91c1c); }

    /* Bouton */
    .stButton > button {
        width: 100%;
        border-radius: 50px;
        height: 4em;
        background: linear-gradient(90deg, #ea580c 0%, #c2410c 100%);
        color: white;
        font-weight: 800;
        border: none;
        font-size: 1.1em;
        box-shadow: 0 4px 15px rgba(194, 65, 12, 0.4);
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }

    /* Mobile Fixes */
    @media only screen and (max-width: 600px) {
        .main .block-container {
            padding-top: 2rem !important;
        }
        h1 { font-size: 1.8rem !important; color: white !important; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .stTabs [data-baseweb="tab"] {
            height: 3.5rem;
            font-weight: 600;
            background-color: rgba(255,255,255,0.9);
            border-radius: 12px 12px 0 0;
            margin-right: 4px;
            color: #ea580c;
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
    """Nettoie la réponse de l'IA pour extraire le JSON pur."""
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
    
    # PROMPT RENFORCÉ : FILTRE STRICT MEUBLES
    prompt = f"""
    Tu es un expert menuisier et tapissier à Niamey. Analyse ce meuble (Prix: {price} FCFA).
    
    📍 TÂCHE 1 : VALIDATION DE L'IMAGE (Garde-fou)
    Regarde attentivement l'image. Est-ce que l'objet PRINCIPAL est un meuble d'ameublement (Table, Armoire, Lit, Canapé, Fauteuil, Commode, Chaise, Buffet) ?
    
    ⛔ SI NON (Ex: Voiture, Animal, Humain, Paysage, Bâtiment, Moto) :
    Renvoie EXACTEMENT : {{ "is_furniture": false }}
    
    ✅ SI OUI (C'est bien un meuble) :
    Renvoie un JSON valide avec cette structure exacte :
    {{
        "is_furniture": true,
        "titre": "Type court (ex: Canapé d'angle, Lit King Size)",
        "style": "Style identifié (ex: Moderne, Rustique, Import Dubaï)",
        "verdict_prix": "Cher / Correct / Affaire",
        "score_global": 5,
        "score_sahel": 5,
        "composition_materiau": [
            {{"couche": "Surface", "compo": "ex: Simili-cuir", "etat": "ex: Griffé/Pelé"}},
            {{"couche": "Structure", "compo": "ex: Bois rouge", "etat": "ex: Robuste"}}
        ],
        "resistance_usure": 3,
        "avis_menuisier": "Analyse courte de la structure et solidité...",
        "avis_tapissier": "Analyse courte du tissu/confort/finitions...",
        "matrice_decision": [
            {{"option": "Réparer", "difficulte": "Difficile", "cout": "Cher", "resultat": "Moyen"}},
            {{"option": "Housse", "difficulte": "Facile", "cout": "Faible", "resultat": "Bon"}},
            {{"option": "Jeter", "difficulte": "Moyen", "cout": "Nul", "resultat": "Nul"}}
        ],
        "recommandation_finale": "Conseil final court et direct pour l'acheteur."
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

# --- INTERFACE MOBILE ---
st.title("🇳🇪 Gaskiyar Kaya")
st.markdown("<p style='color:white; opacity:0.9; margin-top:-15px; font-weight:400;'>L'Expert Meuble : La vérité sur vos biens</p>", unsafe_allow_html=True)

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

# Input Prix
st.markdown('<div class="tech-card" style="padding:15px; margin-bottom:10px;">', unsafe_allow_html=True)
st.markdown('<div class="tech-header" style="margin-bottom:5px;">💰 Prix estimé/Vendeur (FCFA)</div>', unsafe_allow_html=True)
price_input = st.number_input("Prix", min_value=0, step=500, value=0, format="%d", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Bouton d'action
if img_file_buffer:
    if st.button("🔍 LANCER L'ANALYSE EXPERT"):
        if not api_key:
            st.error("⚠️ Clé API manquante")
        else:
            image = Image.open(img_file_buffer)
            st.image(image, width=150) # Miniature
            
            with st.spinner("🧠 Gaskiyar Kaya analyse la qualité..."):
                json_str, info_msg = analyze_image_pro(image, price_input, api_key)
            
            if not json_str:
                st.error("Erreur technique.")
                st.caption(info_msg)
            else:
                try:
                    data = json.loads(json_str)
                    
                    if not data.get("is_furniture"):
                        st.error("🛑 OBJET NON RECONNU")
                        st.warning("Gaskiyar Kaya analyse uniquement les MEUBLES (Lits, Salons, Tables...).")
                    else:
                        st.balloons()
                        
                        # En-tête
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        c1, c2 = st.columns([2,1])
                        with c1:
                            st.markdown(f"<h3 style='margin:0; color:#1f2937'>{data.get('titre')}</h3>", unsafe_allow_html=True)
                            st.markdown(f"<i style='color:#6b7280; font-size:0.9em'>{data.get('style')}</i>", unsafe_allow_html=True)
                        with c2:
                            v = data.get('verdict_prix', 'N/A')
                            color = "bg-green" if "Affaire" in v else "bg-orange" if "Correct" in v else "bg-red"
                            st.markdown(f'<div class="verdict-badge {color}">{v}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 1. Matériau
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">🧬 La Vérité du Matériau</div>', unsafe_allow_html=True)
                        html_table = '<table class="styled-table"><thead><tr><th>Zone</th><th>Matière Réelle</th><th>État</th></tr></thead><tbody>'
                        for row in data.get('composition_materiau', []):
                            html_table += f"<tr><td>{row['couche']}</td><td>{row['compo']}</td><td>{row['etat']}</td></tr>"
                        html_table += "</tbody></table>"
                        st.markdown(html_table, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 2. Avis Experts
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">📊 Audit Technique</div>', unsafe_allow_html=True)
                        st.write(f"**Solidité / Usure : {data.get('resistance_usure')}/10**")
                        st.progress(data.get('resistance_usure')/10)
                        st.info(f"🪑 **Menuisier :** {data.get('avis_menuisier')}")
                        st.warning(f"🧵 **Tapissier :** {data.get('avis_tapissier')}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 3. Décision
                        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
                        st.markdown('<div class="tech-header">⚖️ Vos Options</div>', unsafe_allow_html=True)
                        matrix_html = '<table class="styled-table"><thead><tr><th>Option</th><th>Coût</th><th>Résultat</th></tr></thead><tbody>'
                        for opt in data.get('matrice_decision', []):
                            matrix_html += f"<tr><td><b>{opt['option']}</b></td><td>{opt['cout']}</td><td>{opt['resultat']}</td></tr>"
                        matrix_html += "</tbody></table>"
                        st.markdown(matrix_html, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        # 4. Conseil Final
                        st.markdown(f"""
                        <div class="tech-card" style="border-left: 5px solid #10b981; border-top:none;">
                            <div class="tech-header" style="color:#10b981">💡 Le Conseil du Gwani</div>
                            {data.get('recommandation_finale')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        save_data(data.get('titre'), price_input, data.get('score_global'), data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur lecture IA.")
elif not img_file_buffer:
    st.markdown("""
    <div style='text-align:center; padding:40px; color:white; opacity:0.8;'>
        📸<br><b>Prenez une photo</b> pour révéler la vérité sur ce meuble
    </div>
    """, unsafe_allow_html=True)
