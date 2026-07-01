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
* ⚖️ **Matrice de Décision** : Tableaux comparatifs clairs pour vous aider à décider : Réparer, Négocier ou Laisser tomber ?  
* 🕘 **Historique de Session** : Retrouvez vos 5 dernières analyses, revoyez un rapport ou téléchargez le récapitulatif.  
* 🌗 **Mode Sombre Automatique** : L'interface s'adapte aux préférences de votre téléphone ou navigateur.  
* 📤 **Partage en 1 Clic** : Partagez ou copiez votre rapport (partage natif mobile avec repli presse-papier).  
* 👍 **Feedback Utilisateur** : Donnez votre avis sur la pertinence de chaque verdict.  
* 📐 **Guide de Cadrage** : Des conseils intégrés pour prendre une photo qui donne les meilleurs résultats.  
* 🎨 **Design Moderne & Fluide** : Interface épurée aux couleurs chaudes du Niger, responsive du mobile au desktop.

## **🚀 Comment l'utiliser ?**

1. **Accédez à l'app** : [market-scanner-niger.streamlit.app](https://www.google.com/search?q=https://market-scanner-niger.streamlit.app)  
2. **Choisissez votre mode** : Onglet **📸 Prendre Photo** ou **📂 Galerie** (jusqu'à 3 photos).  
3. **Entrez le prix** proposé par le vendeur (en FCFA).  
4. Cliquez sur **🔍 Lancer l'analyse**.  
5. Recevez votre audit technique complet en quelques secondes, partagez-le ou donnez votre avis avec 👍/👎.

## **🛠️ Installation Locale (Pour les développeurs)**

Si vous souhaitez contribuer au code :

### **Pré-requis**

* Python 3.8+  
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

## **📄 Licence**

Distribué sous la licence **MIT**. Voir le fichier LICENSE pour plus d'informations.  
\<div align="center"\>  
Développé avec ❤️ pour le \<b\>Niger\</b\> 🇳🇪  
\</div\>