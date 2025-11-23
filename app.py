# ... (tout le reste du code reste identique jusqu'à la ligne 439) ...

# --- ZONE ADMIN SÉCURISÉE ---
st.markdown("<br><br><br>", unsafe_allow_html=True)

# On utilise un expander discret
with st.expander("🔐 Espace Admin"):
    # 1. Demande de mot de passe
    password = st.text_input("Mot de passe administrateur", type="password")
    
    # 2. Vérification (Changez "Niamey2024" par votre mot de passe secret !)
    if password == "Niamey2024": 
        st.success("Accès autorisé ✅")
        
        if os.path.exists("data_meubles.csv"):
            # Lecture rapide pour afficher un aperçu (optionnel mais pratique)
            try:
                with open("data_meubles.csv", "r", encoding="utf-8") as f:
                    stats_lines = len(f.readlines()) - 1 # -1 pour l'en-tête
                st.caption(f"📊 Total analyses récoltées : {stats_lines}")
                
                # Bouton de téléchargement
                with open("data_meubles.csv", "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📥 Télécharger le fichier CSV complet",
                        data=f,
                        file_name="gaskiyar_kaya_data.csv",
                        mime="text/csv"
                    )
            except Exception:
                st.error("Erreur de lecture du fichier.")
        else:
            st.info("La base de données est vide pour le moment.")
            
    elif password:
        st.error("Mot de passe incorrect ⛔")
