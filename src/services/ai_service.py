import google.generativeai as genai
import streamlit as st
import time
from src.utils import clean_json_response

@st.cache_data(ttl=3600)
def find_best_model_dynamic(_api_key_placeholder):
    """
    Scanne les modèles disponibles pour trouver le meilleur (Flash ou Pro).
    Cache le résultat pour 1 heure pour éviter des appels API inutiles.
    L'argument _api_key_placeholder sert uniquement à invalider le cache si la clé change.
    """
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)

        if not available_models: return None, "Aucun modèle trouvé."

        # Priorité : Flash -> Pro -> Premier disponible
        for m in available_models:
            if 'flash' in m.lower(): return m, None
        for m in available_models:
            if 'pro' in m.lower() and 'vision' not in m.lower(): return m, None
        return available_models[0], None
    except Exception as e:
        # Fallback safe
        return "models/gemini-1.5-flash", str(e)

def analyze_image_pro(image, price, api_key):
    """
    Analyse l'image avec Google Gemini pour extraire les données du meuble.
    """
    if not api_key:
        return None, "Clé API manquante"

    genai.configure(api_key=api_key)

    # On passe l'api key pour que le cache soit lié à la clé utilisée
    model_name, scan_error = find_best_model_dynamic(api_key)

    if not model_name: return None, scan_error

    prompt = f"""
    Tu es un expert menuisier à Niamey. Analyse ce meuble (Prix: {price} FCFA).

    Liste des objets acceptés : Canapé, fauteuil, table basse, meuble TV, lit, armoire, commode, chevet, table à manger, chaise, buffet, bureau, bibliothèque, console, meuble à chaussures, dressing, lit superposé, canapé-lit, banquette, table de cuisine, tabouret, meuble sous-vasque.

    Si l'objet n'est PAS un meuble de cette liste (ou similaire), renvoie {{"is_furniture": false}}.

    Sinon, renvoie un JSON valide :
    {{
        "is_furniture": true,
        "titre": "Type précis (ex: Table de chevet)",
        "style": "Style identifié",
        "verdict_prix": "Cher / Correct / Affaire",
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
        "recommandation_finale": "Conseil court."
    }}
    NOTE: Les scores sont sur 100.
    """

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image])
        return clean_json_response(response.text), model_name
    except Exception as e:
        # Retry logic simple pour 429 (Too Many Requests)
        if "429" in str(e):
            time.sleep(2)
            try:
                response = model.generate_content([prompt, image])
                return clean_json_response(response.text), model_name
            except: return None, "Surcharge serveur"
        return None, str(e)
