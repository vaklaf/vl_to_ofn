all_glossaries = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX z-sgov: <http://onto.fel.cvut.cz/ontologies/slovník/agendový/popis-dat/pojem/>

SELECT DISTINCT (?g as ?graf)
(GROUP_CONCAT(DISTINCT ?gTyp; SEPARATOR=", ") as ?grafTypPole)
(GROUP_CONCAT(DISTINCT ?gTypStr; SEPARATOR=", ") as ?grafTypStrPole)
?gLabel
?gDefinition
(STR(?gCreated) as ?grafCreated)
WHERE {
#  GRAPH <https://slovník.gov.cz/legislativní/sbírka/183/2006/glosář> {
#   GRAPH <https://slovník.gov.cz/veřejný-sektor/glosář> {
  GRAPH ?g {
    ?g a owl:Ontology, z-sgov:glosář, skos:ConceptScheme;
       a ?gTyp.
    OPTIONAL {?g dcterms:title ?gLabel}.
    OPTIONAL {?g skos:definition ?gDefinition}. #FILTER(LANG(?gLabelCs) = "cs").
    OPTIONAL {?g dcterms:created ?gCreated}.
    BIND(IF(?gTyp = owl:Ontology, "Slovník", IF(?gTyp = z-sgov:glosář, "Tezaurus", IF(?gTyp = owl:NamedIndividual, "NamedIndividual", "Konceptuální model"))) AS ?gTypStr)
  }
}
GROUP BY ?g ?gLabel ?gDefinition ?gCreated
"""

query_items_template = """
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX z-sgov-pojem: <https://slovník.gov.cz/základní/pojem/>

SELECT DISTINCT  
?pojem
?label
?altLabel
?definition
?poznamka
?pojemZdroj
(GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole) 
(GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS ?pojemJePodtridouPole)
(GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS ?nadrazenyPojemPole)
WHERE {{
  GRAPH <{glosar_graph}> {{
    # ?g skos:hasTopConcept ?pojem .
    ?pojem a skos:Concept . # Vrací lepší výsledky
    ?pojem a ?rdfType .
    OPTIONAL {{ ?pojem skos:prefLabel ?label }}
    OPTIONAL {{ ?pojem skos:altLabel ?altLabel }}
    OPTIONAL {{ ?pojem skos:definition ?definition }}
    OPTIONAL {{ ?pojem skos:scopeNote ?poznamka }}
    OPTIONAL {{ ?pojem skos:broader ?nadrazenyPojem }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}
  }}
  GRAPH <{model_graph}> {{
    OPTIONAL {{ ?pojem a ?typObjektu }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}.
    BIND (IF(?typObjektu = z-sgov-pojem:vztah, "vztah", 
              IF(?typObjektu=z-sgov-pojem:role, "role","objekt")) AS ?typObjektuStr)
    OPTIONAL {{ ?pojem rdfs:subClassOf ?pojemJePodtridou 
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
    }}.
    # FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
  }}
}}
GROUP BY ?pojem ?label ?altLabel ?definition ?poznamka ?pojemZdroj
ORDER BY ?pojem
"""