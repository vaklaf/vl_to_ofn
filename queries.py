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