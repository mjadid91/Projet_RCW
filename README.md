# 🚓 Vitesses relevées par les voitures radars à conduite externalisée

**Projet de Représentation des Connaissances sur le Web (RCW)**  
IUT d'Orsay – Année 2025/2026 - BUT 3eme année

Ce projet vise à analyser la densité des infractions routières en France en construisant un graphe RDF depuis des données brutes (vitesses relevées), puis en enrichissant ces données avec des sources externes du Web sémantique (Wikidata) et des services publics (API Géo).

Le but final est de répondre à la question :

> **"Quels départements français présentent le plus fort taux d’infractions, en tenant compte de la superficie et des caractéristiques du territoire ?"**

---

## 📋 Pré-requis

Pour exécuter ce projet, vous aurez besoin de :

- **GraphDB Free (ou Desktop)**  
  Serveur attendu sur : `http://localhost:7200`

- **OntoRefine (intégré à GraphDB)**  
  Utilisé pour l'ETL et la construction du graphe RDF

- **Python 3.8+**  
  Uniquement pour exécuter l'application Web

- **Une connexion Internet**  
  Requise pour les requêtes fédérées Wikidata + API Géo

---

## 📂 Structure du livrable

```
Projet_RCW/
│
├── dataset/
│   └── dataset_projet.csv                  # Données brutes (source : data.gouv.fr)
│
├── data/
│   └── donnees_avec_departements.ttl       # Graphe RDF final
│
├── requetes/
│   ├── enrichissement_wikidata.rq        # Superficie, population
│   ├── ajout_image.rq                    # Blason / image
│   ├── analyse_densite.rq                # Question de recherche
│   └── visualisation_carte.rq            # Données pour l'application web
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
│
└── README.md
```

---

## 📄 Dataset et Prétraitement

**Source des données** : [Jeux de données des vitesses relevées par les voitures radars à conduite externalisée](https://www.data.gouv.fr/datasets/jeux-de-donnees-des-vitesses-relevees-par-les-voitures-radars-a-conduite-externalisee/) (data.gouv.fr)

Le jeu de données source (`dataset_projet.csv`) est issu des relevés des voitures radars à conduite externalisée.
**Note importante :** Le fichier original comportant plus d'un million de lignes, nous avons réalisé un **échantillonnage** pour ne conserver que les **5 000 premières lignes**. Ce choix a été fait pour :
1.  Permettre un enrichissement via l'API Géo dans un temps raisonnable (limitation du nombre de requêtes HTTP).
2.  Garantir la fluidité des visualisations cartographiques dans le navigateur.

## 🛠️ Méthodologie de construction du graphe RDF (OntoRefine)

La construction du graphe s'est faite exclusivement avec OntoRefine, conformément aux consignes du projet RCW.

### 1️⃣ Étape 1 – Import & Nettoyage dans OntoRefine

#### ✔️ Import du CSV

- Fichier : `dataset/dataset_projet.csv`
- Import via : **Import → OntoRefine → Manage Projects → Create Project**

#### ✔️ Typage et nettoyage

- Colonnes numériques (vitesse, limite) → conversion `xsd:decimal` / `xsd:integer`
- Dates → conversion JJ/MM/AAAA → ISO `xsd:dateTime`  
  (via transformation GREL)

#### ✔️ Mapping RDF

Chaque ligne devient une ressource de type `mesure:MesureDeVitesse` :

Exemples de triplets :

- `mesure:Mesure_{row} rdf:type mesure:MesureDeVitesse`
- `mesure:latitude` / `mesure:longitude`
- `mesure:vitesseMesuree`
- `mesure:vitesseLimite`

Ce mapping est entièrement défini dans OntoRefine et exporté en Turtle.

---

### 2️⃣ Étape 2 – Réconciliation géographique via API Géo

Pour déterminer le département correspondant à chaque mesure, OntoRefine a utilisé sa fonction d'appel à des services externes.

#### ✔️ Appel API Géo

- Fonction : **Add column by fetching URLs**
- URL utilisée (formule GREL) :

```grel
"https://geo.api.gouv.fr/communes?lat=" + cells["latitude"].value +
"&lon=" + cells["longitude"].value +
"&fields=codeDepartement&format=json&geometry=centre"
```

#### ✔️ Extraction du code département

```grel
value.parseJson()[0].codeDepartement
```

#### ✔️ Ajout dans le graphe RDF

Création du lien :

```turtle
mesure:Mesure_{row} mesure:estLocaliseeDans dep:Departement_{code}
```

---

### 3️⃣ Étape 3 – Enrichissement sémantique (Wikidata)

Une fois le TTL importé dans GraphDB, nous avons exécuté des requêtes fédérées SPARQL pour enrichir les départements avec :

- Superficie (Wikidata : P2046)
- Population (P1082)
- Nom officiel
- Blasons / images (P94)

Ces enrichissements se trouvent dans :

- `requetes/enrichissement_wikidata.rq`
- `requetes/ajout_image.rq`

Ces requêtes utilisent `SERVICE wikibase:...` conformément aux bonnes pratiques du projet RCW.

---

## 🚀 Guide d'installation

### 1️⃣ Lancer GraphDB

- Accéder à : `http://localhost:7200`
- Créer un dépôt nommé exactement : **`projet`**  
  (Nom obligatoire pour l'application)

### 2️⃣ Importer les données RDF

- Menu : **Import → RDF → Upload RDF files**
- Fichier à charger : `data/donnees_avec_departements.ttl`

### 3️⃣ Exécuter l'enrichissement Wikidata

Dans l'onglet SPARQL :

1. Ouvrir `requetes/enrichissement_wikidata.rq`
2. Coller → Exécuter  
   → "Update executed successfully"
3. Idem pour `ajout_image.rq` si vous souhaitez les images.

### 4️⃣ Lancer l'application Web

Dans un terminal :

```bash
cd app
pip install -r requirements.txt
python app.py
```

Ouvrir :  
👉 `http://127.0.0.1:5000`

---

## 📊 Résultats et Analyse

### Notre question de recherche :

> **"Les départements les plus petits présentent-ils une plus forte densité d'infractions par km² ?"**

### ✔️ Conclusion principale

Les données montrent que :

- **Les territoires urbains compacts (Paris, petite couronne)** →  
  densité d'infractions par km² très élevée, même avec des vitesses moyennes plus faibles.

- **Les départements vastes et ruraux** →  
  densité beaucoup plus faible, même si les vitesses relevées sont plus élevées.

---

## 👥 Auteurs

- Mohamed Jadid
- Chadi Amestoun