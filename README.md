# 🛋️ Gaskiyar Kaya 🇳🇪

**L'expert meuble IA du Niger : une photo suffit pour connaître l'état d'un meuble d'occasion, son juste prix et la façon de le négocier.** Propulsé par Google Gemini.

👉 **[Ouvrir l'application](https://market-scanner-niger.streamlit.app)**

## 📖 À propos

**Gaskiyar Kaya** (*« La vérité du matériel »* en haoussa) est une application web pensée d'abord pour le téléphone, qui sécurise l'achat de meubles d'occasion au Niger.

Au marché de **Katako**, à **Wadata** ou sur **Facebook Marketplace**, ne vous faites plus avoir sur la qualité ou le prix : l'IA joue le rôle d'un menuisier expert dans votre poche. Elle juge l'état et les matériaux du meuble, estime sa valeur sur le marché de Niamey et vous dit jusqu'où négocier.

## ✨ Fonctionnalités

**L'analyse**
* 📸 **Analyse multi-photos** : prenez une photo (la caméra arrière est sélectionnée automatiquement) ou importez jusqu'à 3 photos, ou captures d'écran d'une annonce : plusieurs angles du même meuble, des gros plans de détail (tissu, pied, rayure...) ou les différentes pièces d'un même ensemble (salon 7 places, chambre à coucher...), même sans vue d'ensemble.
* 📝 **Précisions sur l'offre** : indiquez ce que propose le vendeur (« salon 7 places, table basse comprise », « matelas compris »...) pour une estimation de l'offre complète, même si les photos ne montrent pas tout.
* 📶 **Pensée pour les connexions lentes** : les photos de la galerie sont allégées sur le téléphone avant l'envoi (quelques centaines de Ko au lieu de plusieurs Mo).
* 🧬 **Matériaux et état** : la « vérité » sous le vernis (vrai cuir ou simili, bois massif ou contreplaqué), avec des notes de solidité, de qualité des matériaux et de facilité de restauration.
* 🛡️ **Filtre intelligent** : les photos qui ne montrent pas un meuble (moto, animal...) sont refusées, avec la raison du refus.
* 📐 **Guide de cadrage** : des conseils intégrés pour prendre la photo qui donne les meilleurs résultats.

**La décision**
* 🎯 **Verdict clair** : « Bonne affaire », « Prix correct » ou « Trop cher », toujours cohérent avec l'estimation de prix, avec l'écart chiffré en FCFA.
* 🤝 **Plan de négociation** : la 1ʳᵉ offre à proposer, le prix maximum à payer et les arguments concrets à utiliser face au vendeur.
* 🔍 **À vérifier sur place** : les contrôles à faire avant de payer (tiroirs, termites, ressorts...), invisibles sur une photo.
* ⚖️ **Scénarios d'action** : réparer, rhabiller (housse, vernis) ou négocier ?
* 💡 **Estimation sans prix** : pas encore de prix du vendeur ? Obtenez la valeur estimée du meuble (pratique aussi pour vendre le vôtre).

**Le confort**
* 💬 **Partage WhatsApp en 1 clic** : envoyez le résumé (verdict, estimation, plan de négociation) à un proche pour avoir son avis, ou partagez/copiez-le.
* 🕘 **Historique de session** : retrouvez vos 5 dernières analyses, revoyez un rapport ou téléchargez le récapitulatif.
* 👍 **Avis utilisateur** : donnez votre avis sur chaque verdict ; il est enregistré avec l'analyse pour améliorer l'outil.
* 🔁 **Reprise en un clic** après une coupure réseau, sans perdre la photo ni le prix saisis.
* 🧠 **Choix automatique du modèle Gemini** (le modèle Flash stable le plus récent), mis en cache pour des analyses plus rapides.
* 🎨 **Design moderne** aux couleurs chaudes du Niger, du mobile au grand écran, avec mode sombre automatique et contrastes renforcés pour une lecture en plein soleil.

## 🚀 Comment l'utiliser ?

1. **Ouvrez l'application** sur votre téléphone : [market-scanner-niger.streamlit.app](https://market-scanner-niger.streamlit.app).
2. **Ajoutez une photo** : onglet **📸 Prendre Photo**, ou **📂 Galerie** (jusqu'à 3 photos).
3. **Entrez le prix** demandé par le vendeur, en FCFA. *Facultatif* : sans prix, vous obtenez la valeur estimée du meuble.
4. *Facultatif* : précisez **ce que propose le vendeur** (ex : salon 7 places), surtout si les photos ne montrent pas tout.
5. Touchez **🔍 Lancer l'analyse**.
6. Lisez le verdict, suivez le plan de négociation, faites les vérifications indiquées, puis envoyez le résumé sur WhatsApp ou donnez votre avis avec 👍/👎.

> ℹ️ Les estimations sont indicatives et réalisées par une IA à partir de vos photos : vérifiez toujours le meuble sur place avant de payer.

## 🛠️ Installation locale (développeurs)

### Prérequis

* Python 3.10 ou plus récent recommandé (3.9 fonctionne, mais avec Streamlit 1.50/1.51 : les photos n'y sont pas allégées dans le navigateur avant l'envoi)
* Une clé API Google Gemini ([Google AI Studio](https://aistudio.google.com/))

### Étapes

1. **Cloner le dépôt et installer les dépendances :**

   ```bash
   git clone https://github.com/blakro/market-scanner-niger.git
   cd market-scanner-niger
   pip install -r requirements.txt
   ```

2. **Configurer la clé API** dans le fichier `.streamlit/secrets.toml` (exclu de git) :

   ```toml
   GOOGLE_API_KEY = "votre_clé_ici"
   ```

   Sans ce fichier, l'application propose de saisir la clé dans une section « Configuration Clé API ».

3. **Lancer l'application :**

   ```bash
   streamlit run app.py
   ```

### Journal des analyses (optionnel)

Si une connexion `gsheets` ([st-gsheets-connection](https://github.com/streamlit/gsheets-connection)) est configurée dans `.streamlit/secrets.toml`, chaque analyse réussie ajoute une ligne à l'onglet `Sheet1`, en arrière-plan (le client n'attend pas l'écriture) :
`Date`, `Type_Meuble`, `Prix_FCFA` (vide si aucun prix saisi), `Score_Global`, `Verdict_IA`, `Estimation_Min_FCFA`, `Estimation_Max_FCFA`, `ID_Analyse` et `Avis_Client` (👍/👎, renseigné quand le client donne son avis). Les anciennes lignes sont conservées telles quelles.

### Structure du projet

| Fichier | Rôle |
| --- | --- |
| `app.py` | L'application Streamlit complète : interface, appel à Gemini, rapport, journal Google Sheets |
| `requirements.txt` | Dépendances Python |
| `.gitignore` | Exclut les secrets locaux (`.streamlit/secrets.toml`) et les fichiers temporaires Python |

## 📄 Licence

Distribué sous la licence **MIT**. Voir le fichier [LICENSE](LICENSE).

<div align="center">

Développé avec ❤️ pour le <b>Niger</b> 🇳🇪

</div>
