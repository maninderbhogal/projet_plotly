"""Script qui extrait tous les films avec leurs genres cinématographiques et
leur année de sortie.

Le genre cinématographique extrait correspond à une entité Wikidata. Dans ce script,
on combine les données de la CQ et ceux de Wikidata.
"""
import csv
import multiprocessing
from SPARQLWrapper import SPARQLWrapper, JSON, CSV

CQ_SPARQL_ENDPOINT = "http://data.cinematheque.qc.ca/sparql"
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

def fetch_movie_langues():
    sparql = SPARQLWrapper(CQ_SPARQL_ENDPOINT)

    query = """
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX frbroo: <http://iflastandards.info/ns/fr/frbr/frbroo/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?film ?filmLabel ?langueWikidata ?langueLabel WHERE {
  ?film a frbroo:F1_Work .
  ?film rdfs:label ?filmLabel .
  ?film crm:P2_has_type ?langue .
  ?langue owl:sameAs ?langueWikidata .
  ?langue rdfs:label ?langueLabel .
}
"""
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings']

    dict_data = [{ 'film': r['film']['value'],
                   'filmLabel': r['filmLabel']['value'],
                   'langue': r['langueWikidata']['value'],
                   'langueLabel': r['langueLabel']['value']
                 } for r in results]

    return dict_data

def fetch_wikidata_langues():
    sparql = SPARQLWrapper(WIKIDATA_SPARQL_ENDPOINT)

    query = """
SELECT DISTINCT ?genre
WHERE
{
  ?langue wdt:P31/wdt:279* wd:P364 .
  # SERVICE wikibase:label { bd:serviceParam wikibase:language "fr". }
}
"""

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()['results']['bindings']

    genres = []
    for r in results:
        genres.append(r['langue']['value'])

    return genres

def main():
    movies_langues = fetch_movie_langues()
    wd_langues = fetch_wikidata_langues()
    filtered_movies_langues = filter(lambda m: m['langue'] in wd_langues, movies_langues)

    with open('movie_langues.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['film', 'filmLabel', 'genre', 'genreLabel'])
        writer.writeheader()
        for m in filtered_movies_langues:
            writer.writerow(m)

if __name__ == '__main__':
    main()