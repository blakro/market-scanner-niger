import re

def clean_json_response(text):
    """
    Nettoie la réponse texte d'un LLM pour extraire le JSON valide.
    Supprime les balises markdown ```json et ```.
    """
    if not text:
        return ""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()
