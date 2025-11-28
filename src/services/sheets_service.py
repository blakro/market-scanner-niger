from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit as st
from datetime import datetime

def save_data_to_sheets(furniture_type, price, score, verdict):
    """Envoie les données vers Google Sheets."""
    try:
        # 1. Connexion
        conn = st.connection("gsheets", type=GSheetsConnection)

        # 2. Préparation de la nouvelle ligne
        new_data = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Type_Meuble": furniture_type,
            "Prix_FCFA": price,
            "Score_Global": score,
            "Verdict_IA": verdict
        }])

        # 3. Lecture et Mise à jour (AVEC FIX CACHE TTL=0)
        try:
            existing_data = conn.read(worksheet="Sheet1", ttl=0)
            if existing_data.empty:
                 updated_data = new_data
            else:
                 updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        except:
            updated_data = new_data

        # 4. Envoi
        conn.update(worksheet="Sheet1", data=updated_data)

    except Exception:
        # Silencieux pour l'utilisateur
        pass
