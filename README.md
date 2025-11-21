# **🛋️ MarketScanner Niger 🇳🇪**

**L'Expert Meuble IA dans votre poche. Analysez, négociez et achetez malin à Niamey.**

## **📖 À Propos (About)**

**MarketScanner Niger** est une application web "Mobile First" conçue spécialement pour aider les acheteurs de meubles d'occasion au Niger (marché de Katako, Wadata, Facebook Marketplace, etc.).  
Acheter un canapé ou un lit d'occasion à Niamey est souvent un pari risqué :

* ❓ **Le prix est-il juste ?**  
* 🐜 **Le bois va-t-il résister aux termites ?**  
* ☀️ **Le tissu va-t-il supporter la poussière et la chaleur sahélienne ?**

Grâce à l'intelligence artificielle de **Google Gemini**, cette application analyse une simple photo pour vous donner un verdict d'expert immédiat, comme si vous aviez un menuisier professionnel à côté de vous.

## **✨ Fonctionnalités Clés**

* 📸 **Analyse Visuelle IA** : Identifie le style (Louis XV, Marocain, Moderne) et les matériaux réels cachés.  
* 💰 **Verdict Prix** : Compare le prix annoncé avec la valeur estimée du marché local (en FCFA).  
* 🌵 **Score "Sahel-Proof"** : Évalue la résistance du meuble au climat extrême (chaleur sèche, poussière, harmattan).  
* 🛡️ **Garde-fous Intelligents** : Rejette automatiquement les photos qui ne sont pas des meubles.  
* 💡 **Conseils de Négociation** : Vous donne l'argument "choc" pour faire baisser le prix face au vendeur.  
* 📱 **100% Mobile** : Interface épurée et optimisée pour une utilisation fluide sur smartphone en 3G/4G.

## **🚀 Comment l'utiliser ?**

C'est très simple, pas besoin d'être un expert en informatique :

1. **Ouvrez l'application** via le lien web (aucune installation nécessaire).  
2. **Prenez une photo** du meuble ou importez-la depuis votre galerie.  
3. **Entrez le prix** annoncé par le vendeur (en FCFA).  
4. Cliquez sur le bouton **SCANNER**.  
5. Obtenez votre rapport d'expert en **5 secondes** \!

## **🛠️ Installation Locale (Pour les développeurs)**

Si vous souhaitez modifier le code ou l'héberger vous-même, voici la marche à suivre :

### **Pré-requis**

* Python 3.8 ou plus  
* Une clé API Google Gemini (gratuite sur [Google AI Studio](https://aistudio.google.com/))

### **Étapes d'installation**

1. **Clonez le dépôt :**  
   git clone \[https://github.com/blakro/market-scanner-niger.git\](https://github.com/blakro/market-scanner-niger.git)  
   cd market-scanner-niger

2. **Installez les dépendances :**  
   pip install \-r requirements.txt

3. **Lancez l'application :**  
   streamlit run app.py

## **🏗️ Architecture Technique**

* **Frontend** : [Streamlit](https://streamlit.io/) (Python) pour une interface rapide et responsive.  
* **Backend IA** : [Google Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/) pour l'analyse d'image ultra-rapide et gratuite.  
* **Logique** : Algorithme de basculement automatique (*Auto-Fallback*) qui teste plusieurs modèles d'IA pour contourner les erreurs de quotas (429) ou de disponibilité (404).

## **🤝 Contribuer**

Les contributions sont les bienvenues \! Si vous avez des idées pour améliorer la précision des prix à Niamey ou ajouter de nouvelles fonctionnalités :

1. Forkez le projet.  
2. Créez votre branche (git checkout \-b feature/AmazingFeature).  
3. Commitez vos changements (git commit \-m 'Add some AmazingFeature').  
4. Pushez vers la branche (git push origin feature/AmazingFeature).  
5. Ouvrez une Pull Request.

## **📄 Licence**

Distribué sous la licence **MIT**. Voir le fichier LICENSE pour plus d'informations.  
\<div align="center"\>  
Developed with ❤️ for \<b\>Niger\</b\> 🇳🇪  
\</div\>
