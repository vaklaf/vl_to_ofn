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
