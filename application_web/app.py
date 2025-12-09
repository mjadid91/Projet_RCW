import os
# Force le script à ignorer le proxy pour les adresses locales
os.environ['NO_PROXY'] = '127.0.0.1,localhost'

from flask import Flask, render_template, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/projet"

def run_sparql(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
        return results["results"]["bindings"]
    except Exception as e:
        print(f"Erreur SPARQL: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/densite')
def get_densite():
    query = """
    PREFIX mesure: <http://www.semanticweb.org/medja/ontologies/2025/10/untitled-ontology-3#>
    SELECT ?nom ?densite
    WHERE {
        ?dept mesure:nomDepartement ?nom ;
              mesure:superficie ?superficie .
        {
            SELECT ?dept (COUNT(?m) AS ?nb) WHERE {
                ?m mesure:estLocaliseeDans ?dept ;
                   mesure:vitesseMesuree ?v ;
                   mesure:vitesseLimite ?l .
                FILTER (?v > ?l)
            } GROUP BY ?dept
        }
        BIND ((?nb / ?superficie) AS ?densite)
    }
    ORDER BY DESC(?densite)
    LIMIT 15
    """
    data = run_sparql(query)
    clean_data = [{"nom": row["nom"]["value"], "densite": float(row["densite"]["value"])} for row in data]
    return jsonify(clean_data)

@app.route('/api/carte')
def get_carte():
    query = """
    PREFIX mesure: <http://www.semanticweb.org/medja/ontologies/2025/10/untitled-ontology-3#>
    # On ajoute ?date dans le SELECT
    SELECT ?lat ?long ?vitesse ?limite ?date
    WHERE {
        ?m mesure:latitude ?lat ;
           mesure:longitude ?long ;
           mesure:vitesseMesuree ?vitesse ;
           mesure:vitesseLimite ?limite ;
           mesure:aDate ?date .  # On récupère la date ici (propriété 'aDate')
        FILTER(?vitesse > ?limite)
    }
    LIMIT 500
    """
    data = run_sparql(query)
    clean_data = [{
        "lat": float(row["lat"]["value"]),
        "long": float(row["long"]["value"]),
        "vitesse": row["vitesse"]["value"],
        "limite": row["limite"]["value"],
        "date": row["date"]["value"]  # On ajoute la date au JSON
    } for row in data]
    return jsonify(clean_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
