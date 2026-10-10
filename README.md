# **🛋️ Gaskiyar Kaya 🇳🇪**

**L'Expert Meuble IA pour le Niger. Analysez l'état et le prix des meubles d'occasion (Katako, Marketplace) en une photo. Propulsé par Google Gemini.**

## **📖 À Propos (About)**

**Gaskiyar Kaya** (signifiant *"La Vérité du Matériel"* en Haoussa) est une application web "Mobile First" conçue pour sécuriser les achats de meubles d'occasion au Niger.  
Que vous soyez au marché de **Katako**, à **Wadata**, ou sur **Facebook Marketplace**, ne vous faites plus avoir sur la qualité ou le prix. Notre intelligence artificielle agit comme un expert menuisier dans votre poche.

## **✨ Fonctionnalités Clés**

* 📸 **Analyse Multi-Angles** : Prenez une photo (Caméra) ou importez jusqu'à 3 photos depuis votre galerie pour croiser les angles et affiner le diagnostic.  
* 🧠 **Cerveau IA Hybride** : Scanne automatiquement les modèles disponibles (Flash/Pro), avec mise en cache du modèle pour des analyses plus rapides.  
* 🧬 **Analyse Matériaux Profonde** : Révèle la "vérité" sous le vernis (Vrai cuir vs Simili, Bois massif vs Contreplaqué).  
* 🛡️ **Filtre Intelligent** : Rejette automatiquement les photos qui ne sont pas des meubles (Motos, Animaux, etc.).  
* 🎯 **Verdict Clair** : « Bonne affaire », « Prix correct » ou « Trop cher », toujours cohérent avec l'estimation de prix, avec l'écart chiffré en FCFA.  
* 🤝 **Plan de Négociation** : La 1ʳᵉ offre à proposer, le prix maximum à payer et les arguments concrets à utiliser face au vendeur.  
* 🔍 **À Vérifier sur Place** : Les contrôles à faire avant de payer (tiroirs, termites, ressorts...), invisibles sur une photo.  
* 💡 **Estimation sans Prix** : Pas encore de prix du vendeur ? Obtenez la valeur estimée du meuble (pratique aussi pour vendre le vôtre).  
* ⚖️ **Matrice de Décision** : Tableaux comparatifs clairs pour vous aider à décider : Réparer, Négocier ou Laisser tomber ?  
* 🕘 **Historique de Session** : Retrouvez vos 5 dernières analyses, revoyez un rapport ou téléchargez le récapitulatif.  
* 🌗 **Mode Sombre Automatique** : L'interface s'adapte aux préférences de votre téléphone ou navigateur.  
* 💬 **Partage WhatsApp en 1 Clic** : Envoyez le résumé (verdict, estimation, plan de négociation) à un proche pour avoir son avis, ou partagez/copiez-le.  
* 👍 **Feedback Utilisateur** : Donnez votre avis sur la pertinence de chaque verdict (enregistré avec l'analyse pour améliorer l'outil).  
* 📐 **Guide de Cadrage** : Des conseils intégrés pour prendre une photo qui donne les meilleurs résultats.  
* 🎨 **Design Moderne & Fluide** : Interface épurée aux couleurs chaudes du Niger, responsive du mobile au desktop.

## **🚀 Comment l'utiliser ?**

1. **Accédez à l'app** : [market-scanner-niger.streamlit.app](https://www.google.com/search?q=https://market-scanner-niger.streamlit.app)  
2. **Choisissez votre mode** : Onglet **📸 Prendre Photo** ou **📂 Galerie** (jusqu'à 3 photos).  
3. **Entrez le prix** proposé par le vendeur (en FCFA). *Facultatif* : sans prix, vous obtenez la valeur estimée du meuble.  
4. Cliquez sur **🔍 Lancer l'analyse**.  
5. Recevez votre audit technique complet en quelques secondes, suivez le plan de négociation, envoyez-le sur WhatsApp ou donnez votre avis avec 👍/👎.

## **🛠️ Installation Locale (Pour les développeurs)**

Si vous souhaitez contribuer au code :

### **Pré-requis**

* Python 3.9+  
* Clé API Google Gemini ([Google AI Studio](https://aistudio.google.com/))

### **Étapes**

1. **Cloner le dépôt :**  
   git clone \[https://github.com/blakro/market-scanner-niger.git\](https://github.com/blakro/market-scanner-niger.git)  
   cd market-scanner-niger

2. **Installer les dépendances :**  
   pip install \-r requirements.txt

3. Configurer la Clé API :  
   Créez le fichier .streamlit/secrets.toml :  
   GOOGLE\_API\_KEY \= "votre\_clé\_ici"

4. **Lancer l'application :**  
   streamlit run app.py

### **Journal des analyses (optionnel)**

Si une connexion `gsheets` ([st-gsheets-connection](https://github.com/streamlit/gsheets-connection)) est configurée dans `.streamlit/secrets.toml`, chaque analyse réussie ajoute une ligne à l'onglet `Sheet1`, en arrière-plan (le client n'attend pas l'écriture) :
`Date`, `Type_Meuble`, `Prix_FCFA` (vide si aucun prix saisi), `Score_Global`, `Verdict_IA`, `Estimation_Min_FCFA`, `Estimation_Max_FCFA`, `ID_Analyse` et `Avis_Client` (👍/👎, renseigné quand le client donne son avis). Les anciennes lignes sont conservées telles quelles.

## **📄 Licence**

Distribué sous la licence **MIT**. Voir le fichier LICENSE pour plus d'informations.  
\<div align="center"\>  
Développé avec ❤️ pour le \<b\>Niger\</b\> 🇳🇪  
\</div\>