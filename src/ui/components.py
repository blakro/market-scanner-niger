import streamlit as st
from datetime import datetime
from src.services.weather_service import get_niamey_weather, get_weather_icon

def render_weather_widget():
    """Affiche un petit widget météo et heure."""
    weather = get_niamey_weather()
    now = datetime.now()
    time_str = now.strftime("%H:%M")

    if weather["success"]:
        temp = weather["temp"]
        icon = get_weather_icon(weather["code"])
        weather_display = f"{icon} {temp}°C"
    else:
        # Fallback si API en erreur
        print(f"Weather Error: {weather.get('error')}") # Log pour debug
        weather_display = "🌍 --°C"

    # Ajout d'une couleur plus visible (var css)
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; padding: 10px 20px; color: var(--text-color); font-size: 0.9em; font-weight: 600; opacity: 0.8;">
        <span>🇳🇪 Niamey</span>
        <span>{weather_display} | {time_str}</span>
    </div>
    """, unsafe_allow_html=True)

def render_header():
    render_weather_widget()
    st.markdown('<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.title("Gaskiyar Kaya 🇳🇪")
    st.markdown("<p style='color:#6b7280 !important; font-weight:500; font-size: 1.1em;'>L'Expert Meuble de confiance</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div style='text-align: center; margin-top: 50px; color: #6b7280; font-size: 0.9em; padding-bottom: 20px;'>
        Made in Niger with ❤️ by <b>Moh</b>
    </div>
    """, unsafe_allow_html=True)

def render_result_card(data):
    """Affiche la carte principale de résultat."""

    # 1. EN-TÊTE
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

    # 2. SCORE CIRCULAIRE ET JAUGES
    scores = data.get('scores', {})
    global_score = scores.get('global', 50)

    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.markdown('<div class="tech-header">📊 Performance</div>', unsafe_allow_html=True)

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

    # 3. MATÉRIAU
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.markdown('<div class="tech-header">🧬 Composition</div>', unsafe_allow_html=True)
    html_table = '<table class="styled-table"><tbody>'
    for row in data.get('composition_materiau', []):
        html_table += f"<tr><td width='35%'><b>{row['couche']}</b></td><td>{row['compo']} <br><small style='color:#ea580c'>{row['etat']}</small></td></tr>"
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:20px; padding:15px; background:#f9fafb; border-radius:10px; font-size:0.95em; border-left: 4px solid #ea580c;">
        <p style="margin-bottom: 10px;">🪑 <b>Menuisier :</b> {data.get('avis_menuisier')}</p>
        <p style="margin-bottom: 0;">🧵 <b>Tapissier :</b> {data.get('avis_tapissier')}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. SCÉNARIOS
    st.markdown('<div class="tech-card">', unsafe_allow_html=True)
    st.markdown('<div class="tech-header">⚖️ Scénarios</div>', unsafe_allow_html=True)

    scenarios = data.get('scenarios', [])
    cols = st.columns(3)
    for i, col in enumerate(cols):
        if i < len(scenarios):
            scen = scenarios[i]
            col.markdown(f"""
            <div class="scenario-card">
                <div style="font-size:1.8em; margin-bottom:8px;">{scen['icone']}</div>
                <div class="scenario-title">{scen['titre']}</div>
                <div class="scenario-cost">Coût: {scen['cout']}</div>
                <div class="scenario-result">{scen['resultat']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. CONSEIL FINAL
    st.markdown(f"""
    <div class="tech-card" style="background:#ecfdf5; border:1px solid #10b981; border-top:none;">
        <div style="color:#047857; font-weight:800; margin-bottom:8px; text-transform:uppercase; font-size:0.95em;">💡 Le Conseil du Gwani</div>
        <p style="color:#065f46; margin:0; font-weight:600; font-size: 1.05em;">{data.get('recommandation_finale')}</p>
    </div>
    """, unsafe_allow_html=True)
