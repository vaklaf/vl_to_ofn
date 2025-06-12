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
  GRAPH <https://slovník.gov.cz/datový/turistické-cíle/glosář> {
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
(COALESCE(STR(?labelCs), "") AS ?labelCsStr)
(COALESCE(STR(?labelEn), "") AS ?labelEnStr)
(COALESCE(STR(?altLabelCs), "") AS ?altLabelCsStr)
(COALESCE(STR(?altLabelEn), "") AS ?altLabelEnStr)
(COALESCE(STR(?definitionCs), "") AS ?definitionCsStr)
(COALESCE(STR(?definitionEn), "") AS ?definitionEnStr)
(COALESCE(STR(?poznamkaCs), "") AS ?poznamkaCsStr)
(COALESCE(STR(?poznamkaEn), "") AS ?poznamkaEnStr)
?pojemZdroj
(GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole) 
(GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS ?pojemJePodtridouPole)
(GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS ?nadrazenyPojemPole)
WHERE {{
  GRAPH <{glosar_graph}> {{
    ?g skos:hasTopConcept ?pojem .
    ?pojem a ?rdfType .
    OPTIONAL {{ ?pojem skos:prefLabel ?labelCs FILTER(LANG(?labelCs) = "cs") }}
    OPTIONAL {{ ?pojem skos:prefLabel ?labelEn FILTER(LANG(?labelEn) = "en") }}
    OPTIONAL {{ ?pojem skos:altLabel ?altLabelCs FILTER(LANG(?altLabelCs) = "cs") }}
    OPTIONAL {{ ?pojem skos:altLabel ?altLabelEn FILTER(LANG(?altLabelEn) = "en") }}
    OPTIONAL {{ ?pojem skos:definition ?definitionCs FILTER(LANG(?definitionCs) = "cs") }}
    OPTIONAL {{ ?pojem skos:definition ?definitionEn FILTER(LANG(?definitionEn) = "en") }}
    OPTIONAL {{ ?pojem skos:scopeNote ?poznamkaCs FILTER(LANG(?poznamkaCs) = "cs") }}
    OPTIONAL {{ ?pojem skos:scopeNote ?poznamkaEn FILTER(LANG(?poznamkaEn) = "en") }}
    OPTIONAL {{ ?pojem skos:broader ?nadrazenyPojem }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}
  }}
  GRAPH <{model_graph}> {{
    OPTIONAL {{ ?pojem a ?typObjektu }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}.
    BIND (IF(?typObjektu = z-sgov-pojem:typ-vztahu, "vztah", 
              IF(?typObjektu=z-sgov-pojem:role, "role","objekt")) AS ?typObjektuStr)
    OPTIONAL {{ ?pojem rdfs:subClassOf ?pojemJePodtridou 
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
    }}.
    FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
  }}
}}
GROUP BY ?pojem ?labelCs ?labelEn ?altLabelCs ?altLabelEn ?definitionCs ?definitionEn ?poznamkaCs ?poznamkaEn ?pojemZdroj
ORDER BY ?pojem
"""