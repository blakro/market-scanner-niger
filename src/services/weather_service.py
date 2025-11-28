import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_niamey_weather():
    """
    Récupère la météo actuelle de Niamey via Open-Meteo API.
    Retourne un dictionnaire avec la température et le code météo.
    """
    try:
        # Coordonnées de Niamey: 13.5116° N, 2.1254° E
        url = "https://api.open-meteo.com/v1/forecast?latitude=13.5116&longitude=2.1254&current=temperature_2m,weather_code&timezone=Africa%2FLagos"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        return {
            "temp": current.get("temperature_2m"),
            "code": current.get("weather_code"),
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_weather_icon(code):
    """Retourne une icône emoji basée sur le code WMO."""
    if code is None: return "🌍"
    if code == 0: return "☀️"
    if code in [1, 2, 3]: return "⛅"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65]: return "🌧️"
    if code in [80, 81, 82]: return "🌦️"
    if code >= 95: return "⛈️"
    return "🌡️"
