import json

def serializuj_slovnik_do_jsonld(graf, data):
    json_ld_data = {
        "@context": "https://ofn.gov.cz/slovníky/draft/kontexty/slovníky.jsonld",
        "iri": graf,
        "typ": data["typ"],
        "název": data.get("title", {}),
        "popis": data.get("description", {}),
        "vytvořeno": {
            "typ": "Časový okamžik",
            "datum": data.get("created")
        },
        "pojmy": []
    }

    for pojem in data["pojmy"]:
        pojem_json = {
            "iri": pojem["iri"],
            "typObjektu": pojem.get("typObjektu", [])
        }
        # Přidej jazykové varianty, pokud existují
        if pojem.get("label"):
            pojem_json["nazev"] = pojem["label"]
        if pojem.get("altLabel"):
            pojem_json["alternativniNazev"] = pojem["altLabel"]
        if pojem.get("definition"):
            pojem_json["definice"] = pojem["definition"]
        if pojem.get("poznamka"):
            pojem_json["poznamka"] = pojem["poznamka"]
        if pojem.get("nadrazenyPojem"):
            pojem_json["nadrazenyPojem"] = pojem["nadrazenyPojem"]
        if pojem.get("zdroj"):
            pojem_json["zdroj"] = pojem["zdroj"]

        json_ld_data["pojmy"].append(pojem_json)

    return json.dumps(json_ld_data, ensure_ascii=False, indent=4)