# SISTA QC — Plateforme de Contrôle Qualité automatisé des enquêtes

**SISTA Consult Mauritanie** — Cabinet d'études & conseil

Application **Python (Streamlit)** qui automatise le contrôle qualité après la
collecte de données. Elle fonctionne sur **n'importe quel type d'enquête** et
**n'importe quel format de fichier**.

## 🎯 Les 3 niveaux

**Niveau 1 — Profilage automatique (sans IA)**
Dès l'import : nombre de variables, combien sont numériques / catégorielles /
texte / date / identifiants, taux de remplissage, statistiques par variable.

**Niveau 2 — QC basique générique (sans IA, gratuit, instantané)**
Tests universels valables pour tout fichier : doublons (lignes + identifiants),
valeurs manquantes, outliers (IQR), durées de questionnaire, intervalle entre
questionnaires, GPS manquant, variables constantes. Chaque problème est
rattaché à l'enquêteur.

**Niveau 3 — QC intelligent (avec IA, optionnel)**
Un agent (Google Gemini, gratuit) lit les variables et leurs libellés, génère
des **règles de cohérence logique propres à l'enquête** (ex : « un homme ne peut
pas être enceint », « âge de l'enfant < âge de la mère »), puis Python les
exécute sur tout le fichier et rattache chaque incohérence à l'enquêteur.

## 📂 Formats supportés
CSV, TSV, Excel (.xlsx, .xls), **SPSS (.sav)**, **Stata (.dta)**, **SAS (.sas7bdat)**.
Les formats SPSS/Stata/SAS apportent en plus les **libellés de variables et de
modalités**, ce qui rend l'agent IA beaucoup plus pertinent.

---

## 🚀 Lancer dans VSCode

### 1. Prérequis
- [Python 3.10+](https://www.python.org/) (vérifiez : `python --version`)

### 2. Installation
Ouvrez le dossier `sista-qc-py` dans VSCode, puis dans le terminal :

```bash
pip install -r requirements.txt
```

### 3. Lancer
```bash
streamlit run app.py
```
Le navigateur s'ouvre automatiquement (sinon : http://localhost:8501).

### 4. Utilisation
1. Dans la barre latérale, importez votre fichier (et le dictionnaire si vous l'avez).
2. Ajustez les paramètres si besoin (durée min, sensibilité outliers…).
3. Cliquez « Analyser le fichier ».
4. Parcourez les onglets : Aperçu, QC basique, QC intelligent, Bilan enquêteurs.

Pour le **QC intelligent**, collez votre clé API Gemini gratuite
(https://aistudio.google.com/apikey) dans la barre latérale.

### Fichiers d'exemple
Le dossier `exemples/` contient la même base en 3 formats (CSV, Excel, SPSS)
avec des anomalies intégrées, pour tester immédiatement.

---

## 🏗️ Architecture
```
sista-qc-py/
├── app.py              Interface Streamlit
├── core/
│   ├── loader.py       Lecture universelle des fichiers (+ libellés)
│   ├── profiler.py     Profilage / typage automatique (Niveau 1)
│   ├── qc_basic.py     QC générique sans IA (Niveau 2)
│   └── ai_agent.py     Agent IA Gemini : règles de cohérence (Niveau 3)
├── exemples/           Fichiers de test (CSV, XLSX, SAV)
├── logo_sista.png
└── requirements.txt
```

Le découpage est volontaire : les niveaux 1 et 2 ne nécessitent **aucune IA ni
clé API** et fonctionnent hors ligne. L'IA n'intervient qu'au niveau 3, et
seulement pour *générer* les règles — c'est Python qui les *exécute*, ce qui
limite le coût et garantit la rapidité.
