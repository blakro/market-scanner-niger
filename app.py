import streamlit as st
from PIL import Image
import json
import os
import io

# Import modules refactorisés
from src.ui.components import render_header, render_footer, render_result_card
from src.services.ai_service import analyze_image_pro
from src.services.sheets_service import save_data_to_sheets
from src.services.pdf_service import generate_pdf_report

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Gaskiyar Kaya 🇳🇪",
    page_icon="🛋️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CHARGEMENT CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("assets/style.css")

# --- API KEY ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    with st.expander("🔐 Configuration"):
        api_key = st.text_input("Clé API", type="password")

# --- INTERFACE ---
render_header()

st.info("📸 **Astuce :** Une seule photo bien cadrée suffit. Formats acceptés : JPG, PNG, WEBP (Max 200Mo)", icon="ℹ️")

tab_cam, tab_upload = st.tabs(["📸 Prendre Photo", "📂 Galerie"])
img_file_buffer = None

with tab_cam:
    camera_img = st.camera_input("Cadrez le meuble", label_visibility="collapsed")
    if camera_img: img_file_buffer = camera_img

with tab_upload:
    upload_img = st.file_uploader("Choisir une image", type=["jpg", "png", "jpeg", "webp"], label_visibility="collapsed")
    if upload_img: img_file_buffer = upload_img

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<span style="font-weight:700; color:#1f2937 !important">💰 Prix annoncé (FCFA)</span>', unsafe_allow_html=True)

price_input = st.number_input("Prix", min_value=0, step=5000, value=0, format="%d", label_visibility="collapsed")

# --- LOGIQUE DE BLOCAGE SI PRIX NUL ---
is_ready = False
error_msg = ""

if img_file_buffer:
    if price_input > 0:
        is_ready = True
    else:
        error_msg = "⚠️ Veuillez entrer le prix du meuble pour lancer l'analyse."
else:
    error_msg = ""

st.markdown("<br>", unsafe_allow_html=True)

# Affichage du bouton ou de l'erreur
if is_ready:
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
                if info_msg:
                    st.caption(info_msg)
            else:
                try:
                    data = json.loads(json_str)
                    if not data.get("is_furniture"):
                        st.error("🛑 Pas un meuble reconnu.")
                        st.caption("Objets acceptés : Tables, Lits, Canapés, Armoires, Fauteuils...")
                    else:
                        # Rendu du résultat via composant
                        render_result_card(data)

                        # Génération PDF
                        try:
                            # Sauvegarde temporaire de l'image pour le PDF
                            with io.BytesIO() as buf:
                                image.save(buf, format='PNG')
                                buf.seek(0)
                                pdf_bytes = generate_pdf_report(data, buf) # buf est lu, pas un path, FPDF2 gère

                                # Si generate_pdf_report retourne bytes directement
                                st.download_button(
                                    label="📄 Télécharger le Rapport PDF",
                                    data=bytes(pdf_bytes),
                                    file_name=f"Rapport_Gaskiyar_{data.get('titre')}.pdf",
                                    mime="application/pdf"
                                )
                        except Exception as e:
                            st.warning(f"PDF non disponible: {str(e)}")

                        # Sauvegarde via service
                        scores = data.get('scores', {})
                        global_score = scores.get('global', 50)
                        save_data_to_sheets(data.get('titre'), price_input, global_score, data.get('verdict_prix'))

                except json.JSONDecodeError:
                    st.error("Erreur lecture IA.")
elif error_msg:
    st.warning(error_msg)
elif not img_file_buffer:
    st.markdown("""
    <div style='text-align:center; padding:40px; color:#9ca3af; background:white; border-radius:12px; border:1px dashed #e5e7eb;'>
        <p style="font-size:3em; margin-bottom:10px;">📸</p>
        <p style="font-weight:600;">Prenez une photo pour commencer</p>
    </div>
    """, unsafe_allow_html=True)

render_footer()
