import json

def serializuj_slovnik_do_jsonld(graf, data):
    json_ld_data = {
        "@context": "https://ofn.gov.cz/slovníky/draft/kontexty/slovníky.jsonld",
        "iri": graf,
        "typ": data["typ"],
        "název": {"cs": data["title"]["cs"]} if data["title"].get("cs") else {},
        "popis": {"cs": data["descriptionCs"]} if data.get("descriptionCs") else {},
        "vytvořeno": {
            "typ": "Časový okamžik",
            "datum": data["created"]
        },
        "pojmy": [pojem for pojem in data["pojmy"]]
    }
    # Podmíněně přidej "en" do názvu
    if data["title"].get("en"):
        json_ld_data["název"]["en"] = data["title"]["en"]
    # Podmíněně přidej "en" do popisu
    if data.get("descriptionEn"):
        json_ld_data["popis"]["en"] = data["descriptionEn"]

    return json.dumps(json_ld_data, ensure_ascii=False, indent=4)