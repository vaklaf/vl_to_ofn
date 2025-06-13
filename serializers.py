import json

def serializuj_slovnik_do_jsonld(graf, data):
    json_ld_data = {
        "@context": "https://ofn.gov.cz/slovníky/draft/kontexty/slovníky.jsonld",
        "iri": graf,
        "typ": data["typ"],
        "název": data.get("title", {}),
        "vytvořeno": {
            "typ": "Časový okamžik",
            "datum": data.get("created")
        },
        "pojmy": []
    }

    # Přidej popis jen pokud existuje a není prázdný
    if data.get("description") and data["description"]:
        json_ld_data["popis"] = data["description"]

    for pojem in data["pojmy"]:
        pojem_json = {
            "iri": pojem["iri"],
            "typ": pojem.get("typObjektu", [])
        }
        # Přidej jazykové varianty, pokud existují
        if pojem.get("label"):
            pojem_json["název"] = pojem["label"]
        if pojem.get("altLabel"):
            pojem_json["alternativní-název"] = pojem["altLabel"]
        if pojem.get("definition"):
            pojem_json["definice"] = pojem["definition"]
        if pojem.get("poznamka"):
            pojem_json["poznámka"] = pojem["poznamka"]
        if pojem.get("nadrazenyPojem"):
            pojem_json["nadřazený-pojem"] = pojem["nadrazenyPojem"]
        if pojem.get("zdroj"):
            pojem_json["související-ustanovení-právního-předpisu"] = pojem["zdroj"]

        json_ld_data["pojmy"].append(pojem_json)

    return json.dumps(json_ld_data, ensure_ascii=False, indent=4)