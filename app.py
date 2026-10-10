import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageOps
import os
from datetime import datetime
import time
import json
import math
import re
import html
import io
import base64
import queue
import threading
import uuid
from urllib.parse import quote
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

    :root {
        --track-color: #f3f4f6;
        --circle-inner-bg: white;
    }

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
    .stNumberInput button:disabled {
        color: #9ca3af !important;
    }
    /* En mode sombre, Streamlit colore ces icônes en blanc translucide :
       invisibles sur le fond clair imposé ci-dessus. */
    .stNumberInput button svg {
        fill: currentColor !important;
        color: currentColor !important;
    }
    /* Exemple affiché dans le champ vide : gris et non gras, pour ne pas être
       confondu avec un prix déjà saisi (la règle ci-dessus force le noir). */
    .stNumberInput input::placeholder {
        color: #6b7280 !important;
        -webkit-text-fill-color: #6b7280 !important;
        font-weight: 500 !important;
        opacity: 1;
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
        color: #c2410c !important;
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
        color: rgba(255,255,255,0.96) !important;
        font-size: 0.88em;
        margin: 2px 0 0;
        font-weight: 600;
    }
    /* Teintes foncées : texte blanc lisible (contraste AA), même en plein soleil au marché */
    .vh-green  { background: linear-gradient(135deg, #047857, #065f46); }
    .vh-orange { background: linear-gradient(135deg, #c2410c, #9a3412); }
    .vh-red    { background: linear-gradient(135deg, #b91c1c, #7f1d1d); }
    .vh-blue   { background: linear-gradient(135deg, #1d4ed8, #1e3a8a); }

    /* IDENTITÉ DU MEUBLE */
    .item-title {
        margin: 0 0 4px 0 !important;
        font-size: 1.35em !important;
        font-weight: 800 !important;
        padding: 0 !important;
    }
    .item-style {
        color: #6b7280 !important;
        font-size: 0.9em;
        font-weight: 500;
    }

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
        background: var(--circle-inner-bg, white);
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
    .price-box.highlight .pb-value { color: #c2410c !important; }
    .price-compare.single { grid-template-columns: 1fr; }
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
        color: #c2410c !important;
        font-size: 0.9em;
    }
    /* 3 colonnes même sur mobile : contenu court, évite ~900px de défilement */
    .scenario-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }
    .scenario-icon {
        font-size: 1.7em;
        margin-bottom: 5px;
    }

    /* PLAN DE NÉGOCIATION */
    .nego-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    .nego-box {
        border-radius: 12px;
        padding: 12px 8px;
        text-align: center;
        border: 1px solid;
    }
    .nego-box.offer { background: #ecfdf5; border-color: #6ee7b7; }
    .nego-box.ceiling { background: #fef2f2; border-color: #fca5a5; }
    .nego-label {
        font-size: 0.68em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #4b5563 !important;
    }
    .nego-value {
        font-size: 1.15em;
        font-weight: 800;
        margin-top: 4px;
    }
    .nego-box.offer .nego-value { color: #047857 !important; }
    .nego-box.ceiling .nego-value { color: #b91c1c !important; }
    .nego-hint {
        font-size: 0.85em;
        color: #4b5563 !important;
        margin-top: 10px;
        line-height: 1.45;
    }

    /* LISTES (arguments, vérifications) */
    .tip-title {
        font-weight: 700;
        font-size: 0.9em;
        margin: 14px 0 4px;
    }
    ul.tip-list {
        list-style: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    ul.tip-list li {
        display: flex;
        gap: 10px;
        align-items: flex-start;
        margin: 0 !important;
        padding: 7px 0 !important;
        font-size: 0.9em;
        line-height: 1.45;
        border-bottom: 1px dashed #e5e7eb;
    }
    ul.tip-list li:last-child { border-bottom: none; }
    .tip-icon { flex: 0 0 auto; }

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
    .styled-table small.compo-state { color: #c2410c !important; }

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
        background: linear-gradient(135deg, #dc4f0c, #b93e0c);
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
    /* Action principale (type="primary") : dégradé orange et texte blanc. Sans
       cela, la règle globale de couleur du texte assombrissait son libellé. */
    .stButton > button[kind="primary"] * {
        color: white !important;
    }
    /* Le paragraphe interne de Streamlit annulait le gras prévu ci-dessus */
    .stButton > button p {
        font-weight: 700 !important;
    }
    .stButton > button:disabled {
        background: #e5e7eb !important;
        color: #9ca3af !important;
        box-shadow: none !important;
        border: none !important;
        cursor: not-allowed;
    }
    .stButton > button:disabled * {
        color: #6b7280 !important;
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

    /* BOUTON POPOVER (ex: Partager) */
    button[data-testid="stPopoverButton"] {
        min-height: 3.6em;
        border-radius: 12px !important;
    }
    button[data-testid="stPopoverButton"] p {
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    button[data-testid="stPopoverButton"],
    button[data-testid="stPopoverButton"]:hover,
    button[data-testid="stPopoverButton"]:focus,
    button[data-testid="stPopoverButton"]:active,
    button[kind="secondary"][data-testid="stPopoverButton"] {
        background-color: white !important;
        color: #ea580c !important;
        border: 1.5px solid #ea580c !important;
    }

    /* BOUTON WHATSAPP */
    a[href^="https://wa.me/"] {
        background: linear-gradient(135deg, #128c7e, #075e54) !important;
        border: none !important;
        border-radius: 12px !important;
        min-height: 3.4em;
        box-shadow: 0 6px 16px rgba(7, 94, 84, 0.28);
    }
    a[href^="https://wa.me/"] * {
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.02em;
    }

    /* CARTE FEEDBACK (conteneur Streamlit nommé "feedback_card") */
    .st-key-feedback_card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #f3f4f6;
        margin-bottom: 8px;
    }
    .feedback-thanks {
        color: #4b5563 !important;
        font-weight: 600;
    }
    /* 👍 / 👎 côte à côte, même sur mobile (Streamlit empile les colonnes) */
    .st-key-feedback_card [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 10px !important;
    }
    .st-key-feedback_card [data-testid="stColumn"] {
        min-width: 0 !important;
        width: auto !important;
        flex: 1 1 0 !important;
    }
    .st-key-feedback_card .stButton > button {
        height: 3.2em;
        font-size: 0.9em;
        letter-spacing: 0.5px;
    }

    /* CARTES D'ERREUR */
    .error-card {
        background: #fef2f2;
        border-color: #fecaca;
    }
    .error-title {
        color: #b91c1c !important;
        font-weight: 700;
        font-size: 1.05em;
    }
    .error-text {
        color: #7f1d1d !important;
        font-size: 0.9em;
        margin-top: 6px;
        line-height: 1.45;
    }

    /* MENTION "ESTIMATION INDICATIVE" */
    .disclaimer {
        font-size: 0.78em;
        color: #6b7280 !important;
        text-align: center;
        margin: -4px 8px 16px;
        line-height: 1.5;
    }

    /* CAMÉRA */
    div[data-testid="stCameraInput"] button {
        background: linear-gradient(135deg, #dc4f0c, #b93e0c) !important;
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
        gap: 8px;
        margin: 10px 0 14px;
    }
    .preview-wrap img {
        border-radius: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        border: 3px solid white;
    }
    .preview-single img {
        width: 100%;
        max-width: 220px;
    }
    .preview-multi img {
        width: calc((100% - 16px) / 3);
        max-width: 160px;
        aspect-ratio: 3 / 4;
        object-fit: cover;
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

    /* AVIS MENUISIER / TAPISSIER */
    .avis-box {
        margin-top: 14px;
        padding: 14px;
        background: #f9fafb;
        border-radius: 10px;
        font-size: 0.9em;
        border-left: 3px solid #ea580c;
    }

    /* BANNIÈRE D'AVERTISSEMENT (prix/photo manquant) */
    .warning-banner {
        text-align: center;
        color: #92400e !important;
        background: #fffbeb;
        border: 1px solid #fde68a;
        padding: 10px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9em;
        margin-bottom: 1rem;
    }

    /* BANNIÈRE D'AIDE (information, non bloquante) */
    .hint-banner {
        text-align: center;
        color: #1e3a8a !important;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        padding: 10px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.88em;
        line-height: 1.45;
        margin-bottom: 1rem;
    }
    /* MENTION "FACULTATIF" À CÔTÉ DU PRIX */
    .optional-tag {
        font-size: 0.72em;
        font-weight: 600;
        color: #4b5563 !important;
        background: #f3f4f6;
        border-radius: 100px;
        padding: 2px 8px;
        margin-left: 4px;
        vertical-align: middle;
    }

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
        :root {
            color-scheme: dark;
            --track-color: #334155;
            --circle-inner-bg: #1e293b;
        }

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
        .price-box .pb-value { color: #e5e7eb !important; }
        .price-box .pb-label { color: #94a3b8 !important; }
        .styled-table td { border-bottom-color: #334155; color: #e5e7eb !important; }
        .scenario-title { color: #cbd5e1 !important; }
        .scenario-cost { color: #94a3b8 !important; }
        .gauge-bg { background: #334155; }
        .avis-box { background: #16202f; }
        .warning-banner { background: #3a2412; border-color: #78350f; color: #fcd34d !important; }
        .hint-banner { background: #1e2f4d; border-color: #2c4a75; color: #cfe2ff !important; }
        .optional-tag { background: #334155; color: #cbd5e1 !important; }
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
        /* Le survol clair du mode jour rendait "Partager" illisible une fois ouvert */
        button[kind="secondary"]:hover:not(:disabled) {
            background: #273449 !important;
        }
        button[data-testid="stPopoverButton"],
        button[data-testid="stPopoverButton"]:hover,
        button[data-testid="stPopoverButton"]:focus,
        button[data-testid="stPopoverButton"]:active,
        button[kind="secondary"][data-testid="stPopoverButton"] {
            background-color: #1e293b !important;
            color: #f59e0b !important;
            border-color: #f59e0b !important;
        }
        .streamlit-expanderHeader, div[data-testid="stExpander"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
        }
        .tech-header { border-bottom-color: #334155; color: #fb923c !important; }
        .item-style { color: #94a3b8 !important; }
        .price-box.highlight .pb-value, .scenario-result,
        .styled-table small.compo-state { color: #fb923c !important; }
        .delta-good    { background: #064e3b; color: #a7f3d0 !important; }
        .delta-bad     { background: #450a0a; color: #fecaca !important; }
        .delta-neutral { background: #422006; color: #fde68a !important; }
        .nego-box.offer { background: #052e24; border-color: #047857; }
        .nego-box.offer .nego-value { color: #6ee7b7 !important; }
        .nego-box.ceiling { background: #3b0d0d; border-color: #b91c1c; }
        .nego-box.ceiling .nego-value { color: #fca5a5 !important; }
        .nego-label, .nego-hint, .feedback-thanks { color: #94a3b8 !important; }
        ul.tip-list li { border-bottom-color: #334155; }
        .advice-card {
            background: linear-gradient(135deg, #052e24, #064e3b);
            border-color: #047857;
        }
        .advice-card .advice-title { color: #6ee7b7 !important; }
        .advice-card p { color: #d1fae5 !important; }
        .error-card { background: #3b0d0d; border-color: #7f1d1d; }
        .error-title { color: #fca5a5 !important; }
        .error-text { color: #fecaca !important; }
        .st-key-feedback_card {
            background: #1e293b;
            border-color: #334155;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .preview-wrap img { border-color: #1e293b; }
        .disclaimer { color: #94a3b8 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# META TAGS MOBILE (couleur de barre d'adresse + ajout à l'écran d'accueil "app-like")
# Les scripts passent par st.html : components.html est déprécié (retrait annoncé
# par Streamlit) et son iframe empêchait le partage natif du téléphone.
st.html("""
<script>
(function() {
    const head = document.head;
    function addMeta(name, content) {
        if (head.querySelector(`meta[name="${name}"]`)) return;
        const m = document.createElement('meta');
        m.name = name;
        m.content = content;
        head.appendChild(m);
    }
    addMeta('theme-color', '#ea580c');
    addMeta('apple-mobile-web-app-capable', 'yes');
    addMeta('apple-mobile-web-app-status-bar-style', 'black-translucent');
    addMeta('apple-mobile-web-app-title', 'Gaskiyar Kaya');
})();
</script>
""", unsafe_allow_javascript=True)

# --- ÉTAT DE SESSION ---
# Deux compteurs séparés : on peut vider la photo sans effacer le prix saisi.
if "photo_version" not in st.session_state:
    st.session_state.photo_version = 0
if "price_version" not in st.session_state:
    st.session_state.price_version = 0
if "photo_cache" not in st.session_state:
    st.session_state.photo_cache = {}
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "scroll_to_result" not in st.session_state:
    st.session_state.scroll_to_result = False
if "history" not in st.session_state:
    st.session_state.history = []

def reset_analysis(keep_price=False):
    """Efface le résultat et force le reset des widgets (photo, et prix sauf si keep_price)."""
    st.session_state.last_analysis = None
    st.session_state.processing = False
    st.session_state.photo_version += 1
    if not keep_price:
        st.session_state.price_version += 1
    st.rerun()

def relaunch_analysis():
    """Relance l'analyse avec la même photo et le même prix (ex : après une coupure réseau)."""
    st.session_state.processing = True
    st.rerun()

# --- API KEY ---
api_key = None
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]

if not api_key:
    with st.expander("🔐 Configuration Clé API"):
        api_key = st.text_input("Clé API Google Gemini", type="password")

# --- SAUVEGARDE VERS GOOGLE SHEETS ---
def run_sheet_op(op):
    """Ajoute la ligne d'une analyse, ou renseigne l'avis 👍/👎 du client sur sa ligne."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Si la lecture échoue (réseau...), on n'écrit rien : conn.update() remplace
        # toute la feuille, écrire la seule nouvelle ligne effacerait l'historique.
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        if op["kind"] == "analysis":
            new_data = pd.DataFrame([op["row"]])
            if existing_data.empty:
                updated_data = new_data
            else:
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            if existing_data.empty or "ID_Analyse" not in existing_data.columns:
                return
            match = existing_data["ID_Analyse"].astype(str) == op["id"]
            if not match.any():
                return
            updated_data = existing_data.copy()
            if "Avis_Client" not in updated_data.columns:
                updated_data["Avis_Client"] = None
            # Colonne souvent vide (lue en float) : on la passe en texte avant d'écrire.
            updated_data["Avis_Client"] = updated_data["Avis_Client"].astype(object)
            updated_data.loc[match, "Avis_Client"] = op["value"]
        conn.update(worksheet="Sheet1", data=updated_data)
    except Exception:
        pass

@st.cache_resource
def sheet_writer():
    """File d'attente traitée par un fil d'exécution dédié, partagé par toutes les
    sessions : les écritures Google Sheets (lecture + réécriture de la feuille) se
    font en arrière-plan sans faire attendre le client, et une à la fois, donc deux
    analyses simultanées ne peuvent plus s'écraser. (Les journaux peuvent afficher
    "missing ScriptRunContext" pour ce fil : avertissement sans conséquence.)"""
    ops = queue.Queue()

    def work():
        while True:
            run_sheet_op(ops.get())

    threading.Thread(target=work, daemon=True, name="gk-sheets-writer").start()
    return ops

def queue_sheet_op(op):
    sheet_writer().put(op)

def record_feedback(result, value):
    """Mémorise l'avis 👍/👎 et l'enregistre (il n'était gardé qu'en session)."""
    result["feedback"] = value
    if result.get("id"):
        queue_sheet_op({"kind": "feedback", "id": result["id"],
                        "value": "👍" if value == "up" else "👎"})
    st.rerun()

# --- UTILITAIRES ---
def extract_json(text):
    """Extrait l'objet JSON de la réponse de l'IA, même entouré de ```json ou de
    texte ("Voici mon analyse : {...}"). Renvoie None si rien d'exploitable."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return None

def to_int(value, default=None):
    """Convertit un nombre renvoyé par l'IA en entier : 72, 66.0, "72%", "66/100",
    "90 000 FCFA", "90.000"... Renvoie default si aucun nombre n'est lisible."""
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return int(round(value)) if math.isfinite(value) else default
    match = re.search(r"\d[\d\s.,]*", str(value))
    if not match:
        return default
    number = re.sub(r"\s", "", match.group()).rstrip(".,")
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", number):  # séparateurs de milliers
        number = re.sub(r"[.,]", "", number)
    try:
        return int(round(float(number.replace(",", "."))))
    except ValueError:
        return default

def normalize_analysis(data):
    """Valide et nettoie la réponse de l'IA (types inattendus, valeurs manquantes)
    pour que l'affichage du rapport ne plante jamais."""
    def text(value, default=""):
        return str(value).strip() if value not in (None, "") else default

    def text_list(value, limit):
        if isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            return []
        items = []
        for v in value:
            if isinstance(v, dict):  # ex : [{"argument": "..."}]
                v = " ".join(text(x) for x in v.values() if text(x))
            if text(v):
                items.append(text(v))
        return items[:limit]

    def dict_list(value, limit):
        if not isinstance(value, list):
            return []
        return [v for v in value if isinstance(v, dict)][:limit]

    raw_scores = data.get("scores") if isinstance(data.get("scores"), dict) else {}
    scores = {}
    for name in ("solidite", "materiaux", "restauration", "global"):
        value = to_int(raw_scores.get(name))
        scores[name] = None if value is None else max(0, min(100, value))
    if scores["global"] is None:
        parts = [v for k, v in scores.items() if k != "global" and v is not None]
        scores["global"] = round(sum(parts) / len(parts)) if parts else 50

    prix_min = to_int(data.get("prix_estime_min"))
    prix_max = to_int(data.get("prix_estime_max"))
    if not (prix_min and prix_max and prix_min > 0 and prix_max > 0):
        prix_min = prix_max = None
    elif prix_min > prix_max:
        prix_min, prix_max = prix_max, prix_min

    return {
        "titre": text(data.get("titre"), "Meuble"),
        "style": text(data.get("style")),
        "verdict_prix": text(data.get("verdict_prix")),
        "prix_estime_min": prix_min,
        "prix_estime_max": prix_max,
        "scores": scores,
        "composition_materiau": dict_list(data.get("composition_materiau"), 6),
        "avis_menuisier": text(data.get("avis_menuisier")),
        "avis_tapissier": text(data.get("avis_tapissier")),
        "scenarios": dict_list(data.get("scenarios"), 3),
        "arguments_negociation": text_list(data.get("arguments_negociation"), 4),
        "points_a_verifier": text_list(data.get("points_a_verifier"), 5),
        "recommandation_finale": text(data.get("recommandation_finale")),
    }

def is_furniture_answer(data):
    """Lit le champ is_furniture, y compris s'il est renvoyé en texte ("true", "oui")."""
    value = data.get("is_furniture")
    if isinstance(value, str):
        return value.strip().lower() in ("true", "oui", "yes", "1")
    return bool(value)

def fmt_number(n):
    """125000 -> '125 000' (espaces insécables : le montant ne se coupe pas en fin de ligne)."""
    try:
        return f"{int(n):,}".replace(",", " ")
    except Exception:
        return str(n)

def fmt_fcfa(n):
    """Formate un nombre en FCFA : 125000 -> '125 000 FCFA'."""
    return f"{fmt_number(n)} FCFA"

def fmt_range(low, high):
    """Fourchette avec l'unité une seule fois : '60 000 – 90 000 FCFA'."""
    return f"{fmt_number(low)} – {fmt_number(high)} FCFA"

def esc(value):
    """Échappe un texte venant de l'IA pour l'insérer dans du HTML. Les retours à
    la ligne deviennent <br> : une ligne vide couperait le bloc HTML de st.markdown."""
    return html.escape(str(value)).replace("\n", "<br>")

def score_color(score):
    """Retourne une couleur hex selon le score (rouge / orange / vert)."""
    if score >= 70:
        return "#10b981", "#d1fae5"  # vert
    if score >= 45:
        return "#f59e0b", "#fef3c7"  # orange
    return "#ef4444", "#fee2e2"      # rouge

# --- VERDICT & NÉGOCIATION ---
VERDICTS = {
    "affaire": {"label": "Bonne affaire", "icon": "🎯", "css": "vh-green", "badge": "🟢",
                "sub": "Prix sous la valeur estimée du marché", "sheet": "Affaire"},
    "correct": {"label": "Prix correct", "icon": "⚖️", "css": "vh-orange", "badge": "🟠",
                "sub": "Proche du prix du marché, un petit rabais reste possible", "sheet": "Correct"},
    "cher": {"label": "Trop cher", "icon": "⚠️", "css": "vh-red", "badge": "🔴",
             "sub": "Au-dessus de la valeur estimée, négociez ferme", "sheet": "Cher"},
    "estimation": {"label": "Valeur estimée", "icon": "💡", "css": "vh-blue", "badge": "🔵",
                   "sub": "Ajoutez le prix du vendeur pour savoir si c'est une bonne affaire",
                   "sheet": "Estimation"},
}
# Dépassement toléré au-dessus de l'estimation haute avant de juger le prix
# "trop cher" : la fourchette de l'IA reste approximative.
PRICE_TOLERANCE_PCT = 10

def price_verdict(price, data):
    """Verdict déduit du prix demandé et de la fourchette estimée, pour qu'il soit
    toujours cohérent avec le comparateur (l'IA pouvait annoncer "Affaire" pour un
    prix au-dessus de sa propre estimation). Sans fourchette : verdict de l'IA."""
    if not price:
        return "estimation"
    low, high = data.get("prix_estime_min"), data.get("prix_estime_max")
    if low and high:
        if price < low:
            return "affaire"
        return "correct" if price * 100 <= high * (100 + PRICE_TOLERANCE_PCT) else "cher"
    raw = str(data.get("verdict_prix") or "").lower()
    if "affaire" in raw or "pas cher" in raw:
        return "affaire"
    if "cher" in raw:
        return "cher"
    return "correct"

def round_offer(amount):
    """Arrondit vers le bas à un montant rond, facile à annoncer au vendeur."""
    step = 500 if amount < 20_000 else (1_000 if amount < 200_000 else 5_000)
    return int(amount // step * step)

def negotiation_plan(price, data):
    """Première offre et prix maximum conseillés (None sans fourchette estimée).
    On ouvre environ 10 % sous l'estimation basse pour garder une marge, sans
    jamais conseiller de payer plus que le prix demandé ni que l'estimation haute."""
    low, high = data.get("prix_estime_min"), data.get("prix_estime_max")
    if not (low and high):
        return None
    ceiling = min(price, high) if price else high
    base = min(ceiling, low)
    offer = round_offer(base * 0.9) or base
    return {"offre": min(offer, ceiling), "plafond": ceiling}

def price_delta(price, data):
    """(classe CSS, texte) situant le prix demandé par rapport à la fourchette."""
    low, high = data.get("prix_estime_min"), data.get("prix_estime_max")
    if not (price and low and high):
        return None
    if price < low:
        return "delta-good", f"🎯 Sous le marché : {fmt_fcfa(low - price)} de moins que l'estimation basse"
    if price <= high:
        return "delta-good", "✅ Dans la fourchette du marché"
    if price * 100 <= high * (100 + PRICE_TOLERANCE_PCT):
        return "delta-neutral", f"↗️ Légèrement au-dessus du marché : +{fmt_fcfa(price - high)}"
    pct = (price - high) * 100 / high
    return "delta-bad", (f"⚠️ {fmt_fcfa(price - high)} de plus que l'estimation haute "
                         f"(+{pct:.0f} %)")

def build_summary(data, price, app_url=None):
    """Résumé texte du rapport, prêt à envoyer (WhatsApp, SMS...)."""
    verdict = VERDICTS[price_verdict(price, data)]
    lines = [f"🛋️ Gaskiyar Kaya — {data['titre']}",
             f"{verdict['icon']} Verdict : {verdict['label']}"]
    if price:
        lines.append(f"Prix demandé : {fmt_fcfa(price)}")
    if data.get("prix_estime_min") and data.get("prix_estime_max"):
        lines.append(f"Valeur estimée : {fmt_range(data['prix_estime_min'], data['prix_estime_max'])}")
    plan = negotiation_plan(price, data)
    if plan:
        lines.append(f"🤝 Proposer {fmt_fcfa(plan['offre'])}, ne pas dépasser {fmt_fcfa(plan['plafond'])}")
    lines.append(f"État général : {data['scores']['global']} %")
    if data.get("recommandation_finale"):
        lines.append(f"💡 {data['recommandation_finale']}")
    if app_url:
        lines.append(f"\nAnalysé avec Gaskiyar Kaya : {app_url}")
    return "\n".join(lines)

def public_app_url():
    """Adresse publique de l'app (lien ajouté au message partagé), si connue."""
    try:
        url = st.context.url or ""
    except Exception:
        return None
    url = re.sub(r"/~/\+/?$", "", url.split("?")[0].split("#")[0]).rstrip("/")
    return url if url.startswith("https://") else None

def image_to_data_uri(img, max_dim=480):
    """Miniature JPEG en base64, insérée directement dans le HTML de l'aperçu."""
    thumb = img.copy()
    thumb.thumbnail((max_dim, max_dim))
    buffer = io.BytesIO()
    thumb.save(buffer, format="JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()

def render_preview(images):
    """Affiche 1 à 3 photos centrées : une grande, ou une rangée de miniatures.
    (Un st.image placé entre deux st.markdown("<div>") n'est pas réellement
    enveloppé : on génère donc tout le bloc HTML d'un coup.)"""
    if not images:
        return
    layout = "preview-single" if len(images) == 1 else "preview-multi"
    tags = "".join(
        f'<img src="{image_to_data_uri(img)}" alt="Photo du meuble {i + 1}">'
        for i, img in enumerate(images)
    )
    st.markdown(f'<div class="preview-wrap {layout}">{tags}</div>', unsafe_allow_html=True)

def prepare_image_for_ai(image, max_dim=1280):
    """Redimensionne l'image (photos de téléphone souvent énormes) pour un envoi
    plus rapide et moins coûteux à l'IA, sans perte visible à cette résolution."""
    img = image.copy()
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    return img

def photo_key(uploaded_file):
    return getattr(uploaded_file, "file_id", None) or f"{uploaded_file.name}-{uploaded_file.size}"

def load_photo(uploaded_file):
    """Ouvre une photo envoyée, la redresse selon son orientation EXIF (sinon les
    photos de téléphone apparaissent couchées, pour l'utilisateur comme pour l'IA)
    et la prépare pour l'analyse. Renvoie None si le fichier est illisible.
    Mis en cache par fichier : pas de redécodage à chaque interaction."""
    cache = st.session_state.photo_cache
    key = photo_key(uploaded_file)
    if key not in cache:
        try:
            img = ImageOps.exif_transpose(Image.open(uploaded_file))
            cache[key] = prepare_image_for_ai(img)
        except Exception:
            cache[key] = None
    return cache[key]

def friendly_error_message(raw_msg):
    """Traduit une erreur technique (Gemini/réseau) en message compréhensible."""
    msg = str(raw_msg or "")
    low = msg.lower()
    if "clé api manquante" in low:
        return "Clé API manquante. Ouvrez la section Configuration ci-dessus."
    if "aucune photo lisible" in low:
        return "Aucune photo lisible. Ajoutez une photo JPG ou PNG du meuble."
    if "api key not valid" in low or "api_key_invalid" in low:
        return "Clé API invalide. Vérifiez-la dans la section Configuration ci-dessus."
    if is_overload_error(msg) or "quota" in low or "surcharge" in low:
        return "Le service IA est momentanément surchargé. Réessayez dans quelques secondes."
    if "timeout" in low or "deadline" in low:
        return "La connexion a pris trop de temps. Vérifiez votre réseau et réessayez."
    if "network" in low or "connection" in low or "resolve" in low:
        return "Problème de connexion réseau. Vérifiez votre connexion internet."
    if "response.text" in low or "finish_reason" in low or "blocked" in low or "safety" in low:
        return "L'IA n'a pas pu analyser cette photo. Essayez avec une autre photo, plus nette et bien cadrée."
    if "404" in msg or "not found" in low:
        return "Le modèle d'IA a changé. Réessayez : l'application va choisir automatiquement le bon modèle."
    return "Une erreur inattendue s'est produite pendant l'analyse. Réessayez avec une photo plus nette."

def is_overload_error(msg):
    """Erreurs temporaires côté Google (quota dépassé, modèle surchargé)."""
    low = str(msg).lower()
    return "429" in low or "503" in low or "overloaded" in low or "unavailable" in low

# --- SCANNER MODÈLES GEMINI ---
# Variantes spécialisées (voix, génération d'images, temps réel...) qui acceptent
# generateContent mais ne savent pas analyser une photo et répondre en JSON.
UNSUITABLE_MODEL_HINTS = ("tts", "image", "live", "audio", "embedding", "aqa",
                          "robotics", "computer-use", "gemma", "learnlm")
# Alias maintenu par Google vers le dernier modèle Flash (si la liste est inaccessible).
FALLBACK_MODEL = "models/gemini-flash-latest"

def pick_model(model_names):
    """Choisit le meilleur modèle : Flash (rapide) stable de la version la plus
    récente, puis Flash-Lite, puis Pro ; les préversions passent après."""
    candidates = [n for n in model_names
                  if not any(hint in n.lower() for hint in UNSUITABLE_MODEL_HINTS)]
    if not candidates:
        return model_names[0] if model_names else None

    def rank(name):
        low = name.lower()
        version = re.search(r"gemini-(\d+(?:\.\d+)?)", low)
        if "flash" in low:
            family = 1 if "lite" in low else 0
        else:
            family = 2 if "pro" in low else 3
        unstable = any(tag in low for tag in ("preview", "exp", "thinking"))
        return (family, unstable, -float(version.group(1)) if version else 0.0)

    return min(candidates, key=rank)

def find_best_model_dynamic(api_key):
    # Le modèle disponible ne change pas en cours de session : on évite de
    # rappeler list_models() (aller-retour réseau) à chaque nouvelle analyse.
    cached = st.session_state.get("gemini_model_cache")
    if cached and cached.get("api_key") == api_key:
        return cached["model"], None
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        if not available_models:
            return None, "Aucun modèle trouvé."
        chosen = pick_model(available_models)
        st.session_state.gemini_model_cache = {"api_key": api_key, "model": chosen}
        return chosen, None
    except Exception as e:
        return FALLBACK_MODEL, str(e)

# --- ANALYSE IA ---
AI_TIMEOUT_SECONDS = 90

def analyze_image_pro(images, price, api_key):
    genai.configure(api_key=api_key)
    model_name, scan_error = find_best_model_dynamic(api_key)
    if not model_name:
        return None, scan_error

    if price:
        price_context = f"Prix demandé par le vendeur : {price} FCFA"
    else:
        price_context = "le vendeur n'a pas encore donné de prix : estime seulement sa valeur"
    prompt = f"""
    Tu es un expert menuisier à Niamey (Niger). Analyse ce meuble ({price_context}).
    Tu reçois une ou plusieurs photos (jusqu'à 3 angles différents) qui doivent TOUTES montrer
    LE MÊME meuble : croise les informations entre les photos pour affiner ton diagnostic
    (structure, matériaux, défauts).

    Liste des objets acceptés : Canapé, fauteuil, table basse, meuble TV, lit, armoire, commode, chevet, table à manger, chaise, buffet, bureau, bibliothèque, console, meuble à chaussures, dressing, lit superposé, canapé-lit, banquette, table de cuisine, tabouret, meuble sous-vasque.

    RÈGLE DE VALIDATION STRICTE : examine CHAQUE photo individuellement.
    Si NE SERAIT-CE QU'UNE SEULE des photos fournies ne montre pas un meuble de cette liste
    (objet différent, personne, animal, véhicule, photo floue/vide, etc.), OU si les photos
    montrent visiblement des meubles différents (pas le même objet sous plusieurs angles),
    renvoie {{"is_furniture": false}} pour l'ensemble de la soumission, même si une ou
    plusieurs des autres photos sont valides.

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
        "arguments_negociation": [
            "Défaut visible à montrer au vendeur pour faire baisser le prix"
        ],
        "points_a_verifier": [
            "Vérification rapide à faire sur place avant de payer"
        ],
        "recommandation_finale": "Conseil court et actionnable."
    }}
    RÈGLES :
    - Les scores sont sur 100.
    - prix_estime_min et prix_estime_max sont des nombres entiers en FCFA : la valeur d'occasion
      de CE meuble dans son état réel, cohérente avec le marché de Niamey (Katako, Wadata, Marketplace).
    - verdict_prix compare le prix demandé à ta fourchette : "Affaire" s'il est en dessous,
      "Correct" s'il est dedans, "Cher" s'il est au-dessus (vide si aucun prix n'est donné).
    - arguments_negociation : 2 ou 3 arguments courts et concrets, tirés des défauts visibles
      sur les photos (liste vide si le meuble n'a pas de défaut visible).
    - points_a_verifier : 2 à 4 vérifications rapides adaptées à ce meuble, impossibles à voir
      sur photo (tiroirs, portes, pieds, termites, odeurs, ressorts, mousse...).
    - Écris en français simple, avec des phrases courtes.
    """

    def generate(json_mode=True):
        # Mode JSON natif de Gemini : réponse directement exploitable (moins
        # d'"Erreur de lecture"). Délai max pour ne pas bloquer sur un réseau lent.
        config = {"response_mime_type": "application/json"} if json_mode else None
        model = genai.GenerativeModel(model_name, generation_config=config)
        response = model.generate_content(
            [prompt, *images], request_options={"timeout": AI_TIMEOUT_SECONDS}
        )
        return response.text

    try:
        try:
            return generate(), model_name
        except Exception as e:
            low = str(e).lower()
            if "mime" in low or "json mode" in low:
                return generate(json_mode=False), model_name
            if is_overload_error(e):
                time.sleep(2)
                return generate(), model_name
            raise
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            # Modèle retiré entre-temps : on force un nouveau scan au prochain essai.
            st.session_state.pop("gemini_model_cache", None)
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
            badge = VERDICTS.get(entry.get("verdict_key"), VERDICTS["correct"])["badge"]
            price_txt = fmt_fcfa(entry["price"]) if entry["price"] else "Sans prix"
            col_h1, col_h2 = st.columns([4, 1])
            with col_h1:
                st.markdown(
                    f"{badge} **{html.escape(entry['titre'])}** — {entry['verdict']} · "
                    f"{price_txt} · Score {entry['score']}% · {entry['timestamp']}"
                )
            with col_h2:
                if st.button("Revoir", key=f"hist_{i}", width="stretch"):
                    st.session_state.last_analysis = entry["snapshot"]
                    st.session_state.scroll_to_result = True
                    st.rerun()
        st.caption("Historique valable uniquement pour cette session de navigateur (non partagé, non sauvegardé).")
        history_text = "\n\n".join(
            build_summary(e["snapshot"]["data"], e["price"]) + f"\n({e['timestamp']})"
            for e in st.session_state.history
        )
        st.download_button(
            "⬇️ Télécharger l'historique",
            data=history_text,
            file_name="gaskiyar_kaya_historique.txt",
            mime="text/plain",
            width="stretch",
        )

# --- CAPTURE IMAGE ---
pv = st.session_state.photo_version
tab_cam, tab_upload = st.tabs(["📸 Prendre Photo", "📂 Galerie"])
img_files = []

with tab_cam:
    camera_img = st.camera_input("Cadrez le meuble", label_visibility="collapsed", key=f"camera_{pv}")
    if camera_img:
        img_files = [camera_img]
    # Streamlit démarre toujours la caméra en mode "selfie" (avant) et n'expose pas
    # de paramètre pour choisir la caméra arrière. On simule un clic (une seule fois
    # par caméra affichée, dès qu'il apparaît) sur son bouton interne "changer de
    # caméra" pour basculer automatiquement sur la caméra arrière, plus adaptée à un
    # meuble. Le repère est posé sur l'élément caméra lui-même : quand elle est
    # recréée en mode selfie ("Nouvelle analyse", rechargement de la page), le
    # repère disparaît avec elle et la bascule est refaite.
    st.html(f"""
        <script>
        (function() {{
            // photo_version {pv} : script relancé à chaque nouvelle caméra.
            let attempts = 0;
            const interval = setInterval(function() {{
                attempts++;
                const cam = document.querySelector('[data-testid="stCameraInput"]');
                if (cam && cam.dataset.gkRearCamera) {{
                    clearInterval(interval);
                    return;
                }}
                // Selon la version de Streamlit, l'identifiant est sur le bouton
                // lui-même ou sur un div qui l'enveloppe (un clic sur le div est sans effet).
                const target = cam && cam.querySelector('[data-testid="stCameraInputSwitchButton"]');
                const btn = target && (target.tagName === 'BUTTON' ? target : target.querySelector('button'));
                if (btn) {{
                    cam.dataset.gkRearCamera = '1';
                    btn.click();
                    clearInterval(interval);
                }} else if (attempts > 40) {{
                    clearInterval(interval);
                }}
            }}, 250);
        }})();
        </script>
    """, unsafe_allow_javascript=True)

with tab_upload:
    upload_imgs = st.file_uploader(
        "Choisir une ou plusieurs images (max 3 angles)",
        type=["jpg", "png", "jpeg", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=f"upload_{pv}"
    )
    if upload_imgs:
        img_files = upload_imgs[:3]
        if len(upload_imgs) > 3:
            st.caption("⚠️ Seules les 3 premières photos seront analysées.")

# Décodage (mis en cache) dès l'ajout : une photo illisible est signalée tout de
# suite au lieu de faire planter l'analyse.
photos = []
unreadable = []
for f in img_files:
    img = load_photo(f)
    if img is None:
        unreadable.append(f.name)
    else:
        photos.append(img)
current_keys = {photo_key(f) for f in img_files}
for key in list(st.session_state.photo_cache):
    if key not in current_keys:
        del st.session_state.photo_cache[key]
if unreadable:
    st.markdown(
        '<div class="warning-banner">⚠️ Photo illisible ignorée : '
        f'{html.escape(", ".join(unreadable))}. Essayez une photo JPG ou PNG.</div>',
        unsafe_allow_html=True
    )

# --- PRIX ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<span style="font-weight:700;">💰 Prix annoncé par le vendeur (FCFA)</span> '
    '<span class="optional-tag">facultatif</span>',
    unsafe_allow_html=True
)
# Champ vide par défaut (plus de "0" à effacer avant de taper sur mobile).
price_input = st.number_input(
    "Prix",
    min_value=0,
    step=5000,
    value=None,
    format="%d",
    placeholder="Ex : 75000",
    label_visibility="collapsed",
    help="Entrez le prix proposé par le vendeur pour savoir si c'est une bonne affaire. "
         "Sans prix, vous obtenez l'estimation de sa valeur et un plan de négociation.",
    key=f"price_{st.session_state.price_version}"
) or 0
if price_input > 0:
    st.markdown(
        f'<div style="text-align:right; font-size:0.85em; color:#6b7280; margin-top:-8px;">'
        f'Soit <b style="color:#c2410c;">{fmt_fcfa(price_input)}</b></div>',
        unsafe_allow_html=True
    )
    if price_input < 500:
        st.caption("⚠️ Ce prix semble très bas, vérifiez qu'il est bien exprimé en FCFA.")
    elif price_input > 3_000_000:
        st.caption("⚠️ Ce prix semble très élevé pour un meuble d'occasion, vérifiez votre saisie.")

# --- ÉTAT PRÊT ---
# Seule la photo est indispensable : sans prix, l'IA estime la valeur du meuble
# (utile avant de demander le prix au vendeur, ou pour vendre son propre meuble).
has_image = len(photos) > 0
has_price = price_input > 0
is_ready = has_image

# Message d'aide contextuel
st.markdown("<br>", unsafe_allow_html=True)
if not has_image:
    st.markdown(
        '<div class="empty-state">'
        '<span class="bounce">📸</span>'
        '<div class="es-title">Prenez ou importez une photo pour commencer</div>'
        '<div class="es-hint">Ajoutez le prix demandé pour savoir si c\'est une bonne affaire</div>'
        '</div>',
        unsafe_allow_html=True
    )
elif not has_price:
    st.markdown(
        '<div class="hint-banner">💡 Sans prix, vous obtiendrez l\'estimation de sa valeur. '
        'Ajoutez le prix du vendeur pour savoir si c\'est une bonne affaire.</div>',
        unsafe_allow_html=True
    )

# --- RENDU DU RÉSULTAT (persistant via session_state) ---
def render_result(result):
    status = result["status"]
    images = result.get("images") or []
    price_for_render = result.get("price", 0)

    render_preview(images)

    if status == "error":
        raw_msg = str(result.get("error_msg") or "")
        st.markdown(
            '<div class="tech-card error-card">'
            '<div class="error-title">❌ Analyse impossible</div>'
            f'<div class="error-text">{html.escape(friendly_error_message(raw_msg))}</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if raw_msg:
            with st.expander("Détails techniques"):
                st.code(raw_msg, language=None)
    elif status == "not_furniture":
        st.markdown(
            '<div class="tech-card error-card">'
            '<div class="error-title">🛑 Objet non reconnu</div>'
            '<div class="error-text">'
            'Objets acceptés : Tables, Lits, Canapés, Armoires, Fauteuils, Commodes, Bureaux, Chaises... '
            'Toutes les photos doivent montrer le même meuble.'
            '</div></div>',
            unsafe_allow_html=True
        )
    elif status == "json_error":
        st.markdown(
            '<div class="tech-card error-card">'
            '<div class="error-title">❌ Erreur de lecture</div>'
            '<div class="error-text">'
            'L\'IA a renvoyé un format inattendu. Réessayez, ou utilisez une photo plus nette.'
            '</div></div>',
            unsafe_allow_html=True
        )
    elif status == "success":
        data = result["data"]
        prix_min, prix_max = data["prix_estime_min"], data["prix_estime_max"]
        verdict_key = price_verdict(price_for_render, data)
        verdict = VERDICTS[verdict_key]
        plan = negotiation_plan(price_for_render, data)

        # === VERDICT HERO (bannière top) ===
        # Déduit du prix et de la fourchette : jamais en contradiction avec le comparateur.
        if verdict_key == "estimation" and prix_min:
            vh_sub = f"{fmt_range(prix_min, prix_max)} sur le marché de Niamey"
        else:
            vh_sub = verdict["sub"]
        st.markdown(
            f'<div class="verdict-hero {verdict["css"]}">'
            f'<div class="big-icon">{verdict["icon"]}</div>'
            f'<div style="flex:1;"><p class="v-title">{verdict["label"]}</p>'
            f'<p class="v-sub">{esc(vh_sub)}</p></div></div>',
            unsafe_allow_html=True
        )

        # Chaque carte est générée en un seul st.markdown : ouvrir un <div> dans un
        # appel et le fermer dans un autre laissait une carte vide au-dessus du contenu.

        # === IDENTITÉ MEUBLE ===
        style_html = f'<div class="item-style">{esc(data["style"])}</div>' if data["style"] else ""
        st.markdown(
            f'<div class="tech-card"><h3 class="item-title">{esc(data["titre"])}</h3>{style_html}</div>',
            unsafe_allow_html=True
        )

        # === COMPARATEUR PRIX ===
        if prix_min and prix_max:
            boxes = ""
            if price_for_render:
                boxes += (
                    '<div class="price-box"><div class="pb-label">Prix demandé</div>'
                    f'<div class="pb-value">{fmt_fcfa(price_for_render)}</div></div>'
                )
            boxes += (
                '<div class="price-box highlight"><div class="pb-label">Valeur estimée (IA)</div>'
                f'<div class="pb-value">{fmt_range(prix_min, prix_max)}</div></div>'
            )
            delta = price_delta(price_for_render, data)
            if delta:
                delta_html = f'<div class="price-delta {delta[0]}">{esc(delta[1])}</div>'
            else:
                delta_html = ('<div class="price-delta delta-neutral">💡 Indiquez le prix du vendeur '
                              'pour savoir si c\'est une bonne affaire</div>')
            grid_class = "price-compare" if price_for_render else "price-compare single"
            st.markdown(
                '<div class="tech-card"><div class="tech-header">💸 Comparateur Prix</div>'
                f'<div class="{grid_class}">{boxes}</div>{delta_html}</div>',
                unsafe_allow_html=True
            )

        # === PLAN DE NÉGOCIATION ===
        if plan:
            if verdict_key == "affaire":
                offer_label = "Vous pouvez tenter"
                hint = "Le prix est déjà bon : achetez sans trop tarder, ou tentez un petit rabais."
            else:
                offer_label = "1ʳᵉ offre conseillée"
                hint = ("Commencez par la 1ʳᵉ offre, puis montez petit à petit "
                        "sans dépasser le maximum.")
            args_html = ""
            if data["arguments_negociation"]:
                items = "".join(
                    f'<li><span class="tip-icon">👉</span><span>{esc(a)}</span></li>'
                    for a in data["arguments_negociation"]
                )
                args_html = f'<div class="tip-title">🗣️ Arguments à utiliser</div><ul class="tip-list">{items}</ul>'
            st.markdown(
                '<div class="tech-card"><div class="tech-header">🤝 Plan de négociation</div>'
                '<div class="nego-grid">'
                f'<div class="nego-box offer"><div class="nego-label">{offer_label}</div>'
                f'<div class="nego-value">{fmt_fcfa(plan["offre"])}</div></div>'
                '<div class="nego-box ceiling"><div class="nego-label">Maximum à payer</div>'
                f'<div class="nego-value">{fmt_fcfa(plan["plafond"])}</div></div>'
                f'</div><div class="nego-hint">{hint}</div>{args_html}</div>',
                unsafe_allow_html=True
            )

        # === PERFORMANCE (score circle + jauges dynamiques) ===
        scores = data["scores"]
        global_score = scores["global"]
        col_main, _ = score_color(global_score)
        gauges = [
            ("🧱 Solidité Structurelle", scores["solidite"]),
            ("💎 Qualité Matériaux",     scores["materiaux"]),
            ("🛠️ Facilité Restauration", scores["restauration"]),
        ]
        gauges_html = ""
        # Une jauge non fournie par l'IA est masquée plutôt qu'affichée à 0 %.
        for label, val in [(lbl, v) for lbl, v in gauges if v is not None]:
            g_col, _ = score_color(val)
            gauges_html += (
                '<div class="gauge-container"><div class="gauge-label">'
                f'<span>{label}</span><span style="color:{g_col} !important;">{val}%</span></div>'
                f'<div class="gauge-bg"><div class="gauge-fill" style="width: {val}%; '
                f'background: linear-gradient(90deg, {g_col}99, {g_col});"></div></div></div>'
            )
        st.markdown(
            '<div class="tech-card"><div class="tech-header">📊 Performance</div>'
            '<div class="score-circle-container">'
            f'<div class="score-circle" style="background: conic-gradient({col_main} {global_score}%, '
            'var(--track-color, #f3f4f6) 0);">'
            '<div style="position:absolute; text-align:center;">'
            f'<div class="score-value" style="color:{col_main} !important;">{global_score}%</div>'
            '<span class="score-label">ÉTAT GLOBAL</span></div></div></div>'
            f'{gauges_html}</div>',
            unsafe_allow_html=True
        )

        # === COMPOSITION MATÉRIAUX ===
        rows = "".join(
            f"<tr><td width='30%'><b>{esc(row.get('couche', ''))}</b></td>"
            f"<td>{esc(row.get('compo', ''))}<br><small class='compo-state'>{esc(row.get('etat', ''))}</small></td></tr>"
            for row in data["composition_materiau"]
        )
        table_html = f'<table class="styled-table"><tbody>{rows}</tbody></table>' if rows else ""
        avis_parts = []
        if data["avis_menuisier"]:
            avis_parts.append(f'🪑 <b>Menuisier :</b> {esc(data["avis_menuisier"])}')
        if data["avis_tapissier"]:
            avis_parts.append(f'🧵 <b>Tapissier :</b> {esc(data["avis_tapissier"])}')
        avis_html = f'<div class="avis-box">{"<br><br>".join(avis_parts)}</div>' if avis_parts else ""
        if table_html or avis_html:
            st.markdown(
                f'<div class="tech-card"><div class="tech-header">🧬 Composition</div>{table_html}{avis_html}</div>',
                unsafe_allow_html=True
            )

        # === À VÉRIFIER SUR PLACE ===
        if data["points_a_verifier"]:
            items = "".join(
                f'<li><span class="tip-icon">☑️</span><span>{esc(p)}</span></li>'
                for p in data["points_a_verifier"]
            )
            st.markdown(
                '<div class="tech-card"><div class="tech-header">🔍 À vérifier avant de payer</div>'
                f'<ul class="tip-list">{items}</ul></div>',
                unsafe_allow_html=True
            )

        # === SCÉNARIOS ===
        if data["scenarios"]:
            cards = "".join(
                '<div class="scenario-card">'
                f'<div class="scenario-icon">{esc(scen.get("icone", ""))}</div>'
                f'<div class="scenario-title">{esc(scen.get("titre", ""))}</div>'
                f'<div class="scenario-cost">Coût : {esc(scen.get("cout", ""))}</div>'
                f'<div class="scenario-result">{esc(scen.get("resultat", ""))}</div></div>'
                for scen in data["scenarios"]
            )
            st.markdown(
                '<div class="tech-card"><div class="tech-header">⚖️ Scénarios d\'Action</div>'
                f'<div class="scenario-grid">{cards}</div></div>',
                unsafe_allow_html=True
            )

        # === CONSEIL FINAL ===
        if data["recommandation_finale"]:
            st.markdown(
                '<div class="advice-card"><div class="advice-title">💡 Le Conseil du Gwani</div>'
                f'<p>{esc(data["recommandation_finale"])}</p></div>',
                unsafe_allow_html=True
            )
        st.markdown(
            '<div class="disclaimer">ℹ️ Estimation indicative réalisée par une IA à partir de vos photos. '
            'Vérifiez toujours le meuble sur place avant de payer.</div>',
            unsafe_allow_html=True
        )

        # === FEEDBACK UTILISATEUR ===
        with st.container(key="feedback_card"):
            st.markdown('<div class="tech-header">🗳️ Ce verdict vous semble-t-il juste ?</div>', unsafe_allow_html=True)
            if result.get("feedback"):
                fb_msg = "👍 Merci pour votre retour !" if result["feedback"] == "up" else "👎 Merci, c'est noté."
                st.markdown(f'<div class="feedback-thanks">{fb_msg}</div>', unsafe_allow_html=True)
            else:
                fb_col1, fb_col2 = st.columns(2)
                with fb_col1:
                    if st.button("👍 Oui, pertinent", width="stretch", key="fb_up"):
                        record_feedback(result, "up")
                with fb_col2:
                    if st.button("👎 Pas vraiment", width="stretch", key="fb_down"):
                        record_feedback(result, "down")

        # === ACTIONS : PARTAGER / NOUVELLE ANALYSE ===
        summary = build_summary(data, price_for_render, public_app_url())
        st.markdown("<br>", unsafe_allow_html=True)
        # WhatsApp d'abord : c'est le moyen le plus courant de demander un avis à un proche.
        st.link_button(
            "💬 Envoyer sur WhatsApp",
            "https://wa.me/?text=" + quote(summary),
            width="stretch",
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Nouvelle analyse", width="stretch", type="secondary", key="reset_success"):
                reset_analysis()
        with col_b:
            with st.popover("📤 Partager", width="stretch"):
                st.code(summary, language=None, wrap_lines=True)
                # Script exécuté dans la page (et non plus dans une iframe sans
                # permission "web-share") : navigator.share ouvre la feuille de
                # partage native du téléphone. "</" échappé : le texte vient de l'IA.
                summary_js = json.dumps(summary).replace("</", "<\\/")
                st.html(f"""
                    <button id="share-btn" style="width:100%; padding:10px; border-radius:8px;
                        font-weight:700; font-family:inherit; cursor:pointer;">
                        📱 Partager / Copier en un clic
                    </button>
                    <script>
                    (function() {{
                        const btn = document.getElementById('share-btn');
                        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                        btn.style.background = isDark ? '#1e293b' : 'white';
                        btn.style.color = isDark ? '#f59e0b' : '#c2410c';
                        btn.style.border = '1.5px solid ' + (isDark ? '#f59e0b' : '#ea580c');
                        const text = {summary_js};
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
                    }})();
                    </script>
                """, unsafe_allow_javascript=True)
                st.caption("Ou sélectionnez le texte ci-dessus pour copier manuellement.")
        return

    # Statuts sans rapport détaillé : on garde ce que l'utilisateur a déjà saisi.
    st.markdown("<br>", unsafe_allow_html=True)
    if status == "not_furniture":
        # Mauvaise photo : on vide seulement la photo, le prix reste rempli.
        if st.button("📷 Changer de photo", width="stretch", type="primary", key="change_photo"):
            reset_analysis(keep_price=True)
    else:
        # Erreur réseau / IA : relance avec la même photo et le même prix.
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔁 Réessayer", width="stretch", type="primary", key="retry_same"):
                relaunch_analysis()
        with col_r2:
            if st.button("🔄 Nouvelle analyse", width="stretch", type="secondary", key="reset_other"):
                reset_analysis()


# --- BOUTON D'ANALYSE (toujours visible, désactivé seulement pendant l'analyse) ---
# Il n'est plus grisé tant que le formulaire est incomplet : sur mobile, le prix
# tapé n'est validé qu'à la sortie du champ, donc le 1er tap sur un bouton grisé
# ne faisait que valider le prix et il fallait toucher le bouton une 2e fois.
launch_clicked = st.button(
    "🔍 Lancer l'analyse",
    type="primary",
    disabled=st.session_state.processing,
    width="stretch"
)

# Un clic passe d'abord en état "processing" + rerun immédiat : le bouton se
# grise et le spinner apparaît tout de suite, avant même l'appel (bloquant) à
# l'IA. Ça évite aussi les doubles clics qui déclencheraient deux appels payants.
if launch_clicked and not st.session_state.processing:
    if is_ready:
        st.session_state.processing = True
        st.rerun()
    st.toast("Ajoutez d'abord une photo du meuble (onglet 📸 ou 📂).", icon="📷")

if st.session_state.processing:
    if not api_key or not photos:
        # Message conservé dans le résultat (un simple st.error disparaîtrait au rerun).
        st.session_state.last_analysis = {
            "status": "error",
            "error_msg": "Clé API manquante" if not api_key else "Aucune photo lisible",
            "images": photos, "price": price_input,
        }
        st.session_state.processing = False
        st.session_state.scroll_to_result = True
    else:
        images = photos
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
            raw_text, info_msg = analyze_image_pro(images, price_input, api_key)
            if raw_text:
                status_box.update(label="✅ Rapport d'expertise généré", state="complete", expanded=False)
            else:
                status_box.update(label="❌ Échec de l'analyse", state="error", expanded=False)
        skeleton_placeholder.empty()

        raw_data = extract_json(raw_text) if raw_text else None
        if not raw_text:
            st.session_state.last_analysis = {
                "status": "error", "error_msg": info_msg, "images": images, "price": price_input
            }
        elif raw_data is None:
            st.session_state.last_analysis = {
                "status": "json_error", "images": images, "price": price_input
            }
        elif not is_furniture_answer(raw_data):
            st.session_state.last_analysis = {
                "status": "not_furniture", "images": images, "price": price_input
            }
        else:
            data = normalize_analysis(raw_data)
            global_score = data["scores"]["global"]
            verdict_key = price_verdict(price_input, data)
            # Identifiant de ligne : permet d'y rattacher ensuite l'avis 👍/👎 du client.
            analysis_id = "GK-" + uuid.uuid4().hex[:10]
            queue_sheet_op({"kind": "analysis", "row": {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Type_Meuble": data["titre"],
                "Prix_FCFA": price_input or None,
                "Score_Global": global_score,
                "Verdict_IA": VERDICTS[verdict_key]["sheet"],
                "Estimation_Min_FCFA": data["prix_estime_min"],
                "Estimation_Max_FCFA": data["prix_estime_max"],
                "ID_Analyse": analysis_id,
                "Avis_Client": None,
            }})
            st.session_state.last_analysis = {
                "status": "success", "id": analysis_id, "data": data,
                "images": images, "price": price_input
            }
            st.session_state.history.insert(0, {
                "titre": data["titre"],
                "verdict": VERDICTS[verdict_key]["label"],
                "verdict_key": verdict_key,
                "score": global_score,
                "price": price_input,
                "timestamp": datetime.now().strftime("%H:%M"),
                "snapshot": st.session_state.last_analysis,
            })
            st.session_state.history = st.session_state.history[:5]

        st.session_state.processing = False
        st.session_state.scroll_to_result = True

    st.rerun()

if st.session_state.last_analysis:
    st.markdown('<div id="result-top"></div>', unsafe_allow_html=True)
    render_result(st.session_state.last_analysis)
    if st.session_state.pop("scroll_to_result", False):
        # Le jeton unique rend le contenu différent à chaque fois : le script est
        # bien ré-exécuté même si l'élément précédent est encore affiché.
        st.html(
            f"""
            <script>
                // {uuid.uuid4().hex}
                setTimeout(function() {{
                    var el = document.getElementById('result-top');
                    if (el) {{ el.scrollIntoView({{behavior: 'smooth', block: 'start'}}); }}
                }}, 150);
            </script>
            """,
            unsafe_allow_javascript=True,
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
