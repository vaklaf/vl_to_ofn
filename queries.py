all_glossaries = """
PREFIX a-popis-dat-pojem: <http://onto.fel.cvut.cz/ontologies/slovník/agendový/popis-dat/pojem/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT 
?vocabulary
?gLabel
?gDefinition
(STR(?gCreated) as ?grafCreated)
(STR(?gModified) as ?grafModified)
WHERE {
  GRAPH ?vocabulary  {
    ?vocabulary a owl:Ontology, a-popis-dat-pojem:slovník.
    OPTIONAL {?vocabulary dcterms:title ?gLabel}.
    OPTIONAL {?vocabulary dcterms:description ?gDefinition}. 
    OPTIONAL {?vocabulary dcterms:created ?gCreated}.
    OPTIONAL {?vocabulary dcterms:modified ?gModified}.
  }
}
ORDER BY ?vocabulary
limit 5
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
?definicniObor
(GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole) 
(GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS ?pojemJePodtridouPole)
(GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS ?nadrazenyPojemPole)
(GROUP_CONCAT(DISTINCT ?pojemExactMatch ; SEPARATOR=", ") AS ?pojemExactMatchPole)
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
    OPTIONAL {{ ?pojem skos:exactMatch ?pojemExactMatch }}.
 
  }}
  GRAPH <{model_graph}> {{
    OPTIONAL {{ ?pojem a ?typObjektu }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}.
    OPTIONAL {{ ?pojem rdfs:domain ?definicniObor }}
    BIND (IF(?typObjektu = z-sgov-pojem:vztah, "vztah", 
              IF(?typObjektu=z-sgov-pojem:role, "role","objekt")) AS ?typObjektuStr)
    OPTIONAL {{ ?pojem rdfs:subClassOf ?pojemJePodtridou 
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "https://slovník.gov.cz/veřejný-sektor/pojem/"))
    }}.
    # FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
  }}
}}
GROUP BY ?pojem ?label ?altLabel ?definition ?poznamka ?pojemZdroj ?definicniObor
ORDER BY ?pojem
"""

query_term_type_template="""
select ?type
where {{
  bind(<{term}> as ?term).
  VALUES ?type {{
    {terms_types}
  }}
  ?term a ?type.
}}
"""

query_term_alt_subject_objects_template="""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?typObjSbj
WHERE 
{{
  BIND(<{term}> AS ?term).
  ?term ^skos:narrowerTransitive ?altSubjectObject .
  ?altSubjectObject a <http://onto.fel.cvut.cz/ontologies/ufo/object>, owl:Class;
    skos:prefLabel ?label FILTER(LANG(LCASE(?label))="cs" && STRENDS(LCASE(?label),"práva")) .
    ?altSubjectObject skos:inScheme <https://slovník.gov.cz/veřejný-sektor/glosář> .
  BIND (IF(STRSTARTS(lcase(str(?label)),"objekt"),"Typ objektu práva","Typ subjektu práva") AS ?typObjSbj)
}}
"""
query_term_restrictions_template="""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?term ?onProperty ?inverseOnProperty ?restrictionPred ?onClass ?target
FROM <{vocabulary_graph}>
FROM <{graph_model}>
FROM <{graph_glossary}>
WHERE 
{{
  BIND(<{term}> AS ?term).
  ?term rdfs:subClassOf ?restriction .
  ?restriction a owl:Restriction .
  OPTIONAL {{ ?restriction owl:onProperty ?onProperty .
    FILTER(!ISBLANK(?onProperty)) }}
  OPTIONAL {{ ?restriction owl:onProperty [owl:inverseOf ?inverseOnProperty] . }}
  OPTIONAL {{ ?restriction owl:onClass ?onClass . }}
  FILTER(bound(?onProperty) || bound(?inverseOnProperty))
  VALUES ?restrictionPred {{
    {restrictions}
  }}
  ?restriction ?restrictionPred ?target .
  FILTER(!ISBLANK(?target))
}}
ORDER BY ?term ?onProperty ?inverseOnProperty ?restrictionPred ?onClass ?target

"""

query_items_full_template = """
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX z-sgov-pojem: <https://slovník.gov.cz/základní/pojem/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT  
  ?pojem
  ?label
  ?altLabel
  ?definition
  ?poznamka
  ?pojemZdroj
  ?definicniObor
  (GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole)
  (GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS ?pojemJePodtridouPole)
  (GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS ?nadrazenyPojemPole)
  (GROUP_CONCAT(DISTINCT ?pojemExactMatch ; SEPARATOR=", ") AS ?pojemExactMatchPole)
  (GROUP_CONCAT(DISTINCT ?type ; SEPARATOR=", ") AS ?types)
  (GROUP_CONCAT(DISTINCT ?typObjSbj ; SEPARATOR=", ") AS ?typObjSbjPole)
WHERE {{
  GRAPH <{glosar_graph}> {{
    ?pojem a skos:Concept .
    OPTIONAL {{ ?pojem skos:prefLabel ?label }}
    OPTIONAL {{ ?pojem skos:altLabel ?altLabel }}
    OPTIONAL {{ ?pojem skos:definition ?definition }}
    OPTIONAL {{ ?pojem skos:scopeNote ?poznamka }}
    OPTIONAL {{ ?pojem skos:broader ?nadrazenyPojem }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}
    OPTIONAL {{ ?pojem skos:exactMatch ?pojemExactMatch }}.
    # --- typObjSbj (alt subject objects) ---
    OPTIONAL {{
      ?pojem ^skos:narrowerTransitive ?altSubjectObject .
      ?altSubjectObject a <http://onto.fel.cvut.cz/ontologies/ufo/object>, owl:Class ;
        skos:prefLabel ?altLabelSbj .
      FILTER(LANG(LCASE(?altLabelSbj))="cs" && STRENDS(LCASE(?altLabelSbj),"práva"))
      ?altSubjectObject skos:inScheme <https://slovník.gov.cz/veřejný-sektor/glosář> .
      BIND (IF(STRSTARTS(lcase(str(?altLabelSbj)),"objekt"),"Typ objektu práva","Typ subjektu práva") AS ?typObjSbj)
    }}
  }}
  GRAPH <{model_graph}> {{
    OPTIONAL {{ ?pojem a ?typObjektu }}.
    OPTIONAL {{ ?pojem dc:source ?pojemZdroj }}.
    OPTIONAL {{ ?pojem rdfs:domain ?definicniObor }}
    BIND (IF(?typObjektu = z-sgov-pojem:vztah, "vztah", 
              IF(?typObjektu=z-sgov-pojem:role, "role","objekt")) AS ?typObjektuStr)
    OPTIONAL {{ ?pojem rdfs:subClassOf ?pojemJePodtridou 
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
      FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "https://slovník.gov.cz/veřejný-sektor/pojem/"))
    }}.
    # --- typy pojmu podle zadaných typů ---
    OPTIONAL {{
      VALUES ?type {{ {terms_types} }}
      ?pojem a ?type .
    }}
  }}
}}
GROUP BY ?pojem ?label ?altLabel ?definition ?poznamka ?pojemZdroj ?definicniObor
ORDER BY ?pojem
"""

