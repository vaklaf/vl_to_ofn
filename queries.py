query_all_grahps = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT  ?graf  ?created ?titleCs ?titleEn ?descriptionCs ?descriptionEn
WHERE {
  GRAPH ?graf {
    ?slovník a owl:Ontology.
        ?slovník dcterms:created ?created.
        ?slovník dcterms:title ?titleCs FILTER(LANG(?titleCs) = "cs").
        OPTIONAL{?slovník dcterms:title ?titleEn FILTER(LANG(?TitleEn) = "en")}.
        OPTIONAL{?slovník dcterms:description ?descriptionCs FILTER(LANG(?descriptionCs) = "cs")}.
        OPTIONAL{?slovník dcterms:description ?descriptionEn FILTER(LANG(?descriptionEn) = "en")}
  }
}
"""

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
#(COALESCE(STR(?gLabelCs),"") as ?grafLabelCs) 
#(COALESCE(STR(?gLabelEn),"") as ?grafLabelEn)
#(COALESCE(STR(?gdefinitionCs),"") as ?grafDefinitionCs) 
#(COALESCE(STR(?gDefinitionEn),"") as ?grafDefinitionEn)
(COALESCE(CONCAT(STR(YEAR(?gCreated)),"-",
    IF(STRLEN(STR(MONTH(?gCreated)))=1, CONCAT("0",STR(MONTH(?gCreated))),STR(MONTH(?gCreated))),"-",
    IF(STRLEN(STR(DAY(?gCreated)))=1, CONCAT("0",STR(DAY(?gCreated))),STR(DAY(?gCreated))))
    ,"") as ?grafCreated) 
WHERE {
   
    ?g a  owl:Ontology, z-sgov:glosář, skos:ConceptScheme;
       a ?gTyp;
       dcterms:created ?gCreated;
       dcterms:title ?gLabel . #FILTER(LANG(?gLabelCs) = "cs");
       OPTIONAL{?g skos:definition ?gDefinition} . 
       # OPTIONAL{?g skos:prefLabel ?gLabelEn FILTER(LANG(?gLabelEn) = "en")}.
       #OPTIONAL{?g skos:definition ?gDefinitionCs FILTER(LANG(?gDefinitionCs) = "cs")}.
       #OPTIONAL{?g skos:definition ?gDefinitionEn FILTER(LANG(?gDefinitionEn) = "en")}.
    
    BIND(IF(?gTyp = owl:Ontology, "Slovník", IF(?gTyp = z-sgov:glosář, "Tezaurus", IF(?gTyp = owl:NamedIndividual, "NamedIndividual", "Konceptuální model"))) AS ?gTypStr)
}
GROUP BY ?g ?gLabel ?gDefinition ?gCreated
"""

qurey_items = """
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX z-sgov-pojem: <https://slovník.gov.cz/základní/pojem/>

SELECT DISTINCT  
?pojem
(COALESCE(STR(?labelCs),"") as ?labelCsStr)
(COALESCE(STR(?labelEn),"") as ?labelEnStr)
(COALESCE(STR(?altLabelCs),"") as ?saltLabelCsStr)
(COALESCE(STR(?altLabelEn),"") as ?saltLabelEnStr)
(COALESCE(STR(?definitionCs),"") as ?definitionCsStr)
(COALESCE(STR(?definitionEn),"") as ?definitionEnStr)
(COALESCE(STR(?pojemZdroj),"") as ?pojemZdrojStr)
(COALESCE(STR(?poznamkaCs),"") as ?poznamkaCsStr)
(COALESCE(STR(?poznamkaEn),"") as ?poznamkaEnStr)
(GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole) 
(GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS  ?pojemJePodtridouPole)
(GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS  ?nadrazenyPojemPole)
?rdfType

WHERE {
    GRAPH <https://slovník.gov.cz/legislativní/sbírka/256/2013/glosář> {
        ?g skos:hasTopConcept ?pojem.
        ?pojem skos:prefLabel ?labelCs FILTER(LANG(?labelCs) = "cs").
        ?pojem a ?rdfType.
        OPTIONAL { ?pojem skos:prefLabel ?labelEn FILTER(LANG(?labelEn) = "en") }.
        OPTIONAL { ?pojem skos:altLabel ?altLabelCs FILTER(LANG(?altLabelCs) = "cs") }.
        OPTIONAL { ?pojem skos:altLabel ?altLabelEn FILTER(LANG(?altLabelEn) = "en") }.
        OPTIONAL { ?pojem skos:definition ?definitionCs FILTER(LANG(?definitionCs) = "cs") }.
        OPTIONAL { ?pojem skos:definition ?definitionEn FILTER(LANG(?definitionEn) = "en") }.
        OPTIONAL { ?pojem skos:scopeNote ?poznamkaCs FILTER(LANG(?poznamkaCs) = "cs") }.
        OPTIONAL { ?pojem skos:scopeNote ?poznamkaEn FILTER(LANG(?poznamkaEn) = "en") }.
        OPTIONAL { ?pojem skos:broader ?nadrazenyPojem }.
        
    }
    GRAPH <https://slovník.gov.cz/legislativní/sbírka/256/2013/model> {
        ?pojem a ?typObjektu.
        OPTIONAL{?pojem dc:source ?pojemZdroj}.
        BIND (IF(?typObjektu = z-sgov-pojem:typ-vztahu, "vztah", 
            IF(?typObjektu = z-sgov-pojem:typ-objektu, "objekt", 
                IF(?typObjektu=z-sgov-pojem:role, "role","typ vlastnosti"))) AS ?typObjektuStr)
        OPTIONAL { ?pojem rdfs:subClassOf ?pojemJePodtridou }.
        
        
        FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
    }
}
GROUP BY ?pojem ?labelCs ?labelEn ?definitionCs ?definitionEn ?pojemZdroj  ?altLabelCs ?altLabelEn  ?poznamkaCs ?poznamkaEn ?rdfType
ORDER BY ?pojem
"""

qurey_items_template = """
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX z-sgov-pojem: <https://slovník.gov.cz/základní/pojem/>

SELECT DISTINCT  
?pojem
(COALESCE(STR(?labelCs),"") as ?labelCsStr)
(COALESCE(STR(?labelEn),"") as ?labelEnStr)
(COALESCE(STR(?altLabelCs),"") as ?saltLabelCsStr)
(COALESCE(STR(?altLabelEn),"") as ?saltLabelEnStr)
(COALESCE(STR(?definitionCs),"") as ?definitionCsStr)
(COALESCE(STR(?definitionEn),"") as ?definitionEnStr)
(COALESCE(STR(?pojemZdroj),"") as ?pojemZdrojStr)
(COALESCE(STR(?poznamkaCs),"") as ?poznamkaCsStr)
(COALESCE(STR(?poznamkaEn),"") as ?poznamkaEnStr)
(GROUP_CONCAT(DISTINCT ?typObjektuStr ; SEPARATOR=", ") AS ?typObjektuPole) 
(GROUP_CONCAT(DISTINCT ?pojemJePodtridou ; SEPARATOR=", ") AS  ?pojemJePodtridouPole)
(GROUP_CONCAT(DISTINCT ?nadrazenyPojem ; SEPARATOR=", ") AS  ?nadrazenyPojemPole)
WHERE {{
    GRAPH <{glosar_graph}> {{
        ?g skos:hasTopConcept ?pojem.
        ?pojem skos:prefLabel ?labelCs FILTER(LANG(?labelCs) = "cs").
        ?pojem a ?rdfType.
        OPTIONAL {{ ?pojem skos:prefLabel ?labelEn FILTER(LANG(?labelEn) = "en") }}.
        OPTIONAL {{ ?pojem skos:altLabel ?altLabelCs FILTER(LANG(?altLabelCs) = "cs") }}.
        OPTIONAL {{ ?pojem skos:altLabel ?altLabelEn FILTER(LANG(?altLabelEn) = "en") }}.
        OPTIONAL {{ ?pojem skos:definition ?definitionCs FILTER(LANG(?definitionCs) = "cs") }}.
        OPTIONAL {{ ?pojem skos:definition ?definitionEn FILTER(LANG(?definitionEn) = "en") }}.
        OPTIONAL {{ ?pojem skos:scopeNote ?poznamkaCs FILTER(LANG(?poznamkaCs) = "cs") }}.
        OPTIONAL {{ ?pojem skos:scopeNote ?poznamkaEn FILTER(LANG(?poznamkaEn) = "en") }}.
        OPTIONAL {{ ?pojem skos:broader ?nadrazenyPojem }}.
        OPTIONAL{{?pojem dc:source ?pojemZdroj}}.
    }}
    GRAPH <{model_graph}> {{
        ?pojem a ?typObjektu.
        OPTIONAL{{?pojem dc:source ?pojemZdroj}}.
        BIND (IF(?typObjektu = z-sgov-pojem:typ-vztahu, "vztah", 
            IF(?typObjektu = z-sgov-pojem:typ-objektu, "objekt", 
                IF(?typObjektu=z-sgov-pojem:role, "role","typ vlastnosti"))) AS ?typObjektuStr)
        OPTIONAL {{ ?pojem rdfs:subClassOf ?pojemJePodtridou 
          FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
        }}.
        FILTER(!STRSTARTS(LCASE(STR(?pojemJePodtridou)), "_:"))
    }}
}}
GROUP BY ?pojem ?labelCs ?labelEn ?definitionCs ?definitionEn ?pojemZdroj  ?altLabelCs ?altLabelEn  ?poznamkaCs ?poznamkaEn ?rdfType
ORDER BY ?pojem
"""
