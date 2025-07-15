import json

from enums.enum_term_types import EnumTermTypes

def serializuj_slovnik_do_jsonld(graf, data):
    enum_term_types_to_strins = {
        EnumTermTypes.VLASTNOST: "Vlastnost",
        EnumTermTypes.VZTAH: "Vztah",   
        EnumTermTypes.OBJEKT: "Třída"
    }
    
    
    json_ld_data = {
        "@context": "https://ofn.gov.cz/slovníky/draft/kontexty/slovníky.jsonld",
        "iri": graf,
        #"typ": data["typ"],
        # Nazhrazuji konstatnotu
        "typ": ["Slovník", "Tezaurus", "Konceptuální model"],
        "název": data.get("title", {}),
        # "vytvořeno": {
        #     "typ": "Časový okamžik",
        #     "datum": data.get("created")
        #},
        # Přidej časový okamžik vytvoření, pokud existuje
        
    }
    
    # Přidej časový okamžik vytvoření, pokud existuje
    if "created" in data:
        json_ld_data["vytvořeno"] = {
            "typ": "Časový okamžik",
            "datum": data["created"]
        }
    
    json_ld_data["pojmy"] = []

    # Přidej popis jen pokud existuje a není prázdný
    if data.get("description") and data["description"]:
        json_ld_data["popis"] = data["description"]

    for pojem in data["pojmy"]:
        pojem_json = {
            "iri": pojem["iri"],
            #"typ": pojem.get("typObjektu", [])
            "typ":["Koncept", "Pojem"],
        }
        
        # Rozšířit pojem_json s typem objektu, pokud existuje   
        if "typObjektu" in pojem:
            if isinstance(pojem["typObjektu"], list):
                pojem_json["typ"].extend(pojem["typObjektu"])
            else:
                pojem_json["typ"].append(pojem["typObjektu"])
        
        # Přidej jazykové varianty, pokud existují
        if pojem.get("label"):
            pojem_json["název"] = pojem["label"]
        if pojem.get("altLabel"):
            pojem_json["alternativní-název"] = pojem["altLabel"]
        if pojem.get("definition"):
            pojem_json["definice"] = pojem["definition"]
        if pojem.get("zdroj"):
            pojem_json["související-ustanovení-právního-předpisu"] = pojem["zdroj"]
        if pojem.get("nadrazenyPojem") and enum_term_types_to_strins[EnumTermTypes.OBJEKT] in pojem_json["typ"]:
            pojem_json["nadřazená-třída"] = pojem["nadrazenyPojem"]
        
        if pojem.get("definicniObor") and enum_term_types_to_strins[EnumTermTypes.VZTAH] in pojem_json["typ"]:
            pojem_json["definiční-obor"] = pojem["definicniObor"]
            if pojem.get("oborHodnot"):
                pojem_json["obor-hodnot"] = pojem["oborHodnot"]
            if pojem.get("nadrazenyPojem"):
                pojem_json["nadřazený-vztah"] = pojem["nadrazenyPojem"]
        
        if pojem.get("definicniObor") and enum_term_types_to_strins[EnumTermTypes.VLASTNOST] in pojem_json["typ"]:
            pojem_json["definiční-obor"] = pojem["definicniObor"]
            # Obor hodnot se přidává jako konstantní hodnota ke všem vlastnostem
        
        if enum_term_types_to_strins[EnumTermTypes.VLASTNOST] in pojem_json["typ"]:
            pojem_json["obor-hodnot"] = "https://www.w3.org/2000/01/rdf-schema#Literal"
        
        if pojem.get("poznamka"):
            pojem_json["poznámka"] = pojem["poznamka"]
        
        if pojem.get("exactMatch"):
            pojem_json["ekvivalentní-pojem"] = pojem["exactMatch"]
        
        

        json_ld_data["pojmy"].append(pojem_json)

    return json.dumps(json_ld_data, ensure_ascii=False, indent=4)