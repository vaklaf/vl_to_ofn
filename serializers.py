import json

JSONLD_CONTEXT = "https://ofn.gov.cz/slovníky/draft/kontexty/slovníky.jsonld"

def serializuj_slovnik_do_jsonld(slovnikData):
    """
    Serializes the given dictionary into JSON-LD format.
    
    Args:
        slovnikData (dict): The dictionary to serialize.
        
    Returns:
        str: The serialized JSON-LD string.
    """
    json_ld_data = {
        "@context": JSONLD_CONTEXT,
        "iri": slovnikData["graf"],
        "typ": ["Slovník","Tezaurus","Konceptuální model"],
        "název": {
            "cs": slovnikData["titleCs"],
            "en": slovnikData["titleEn"],
        },
        "popis": {
            "cs": slovnikData["descriptionCs"],
            "en": slovnikData["descriptionEn"],
        },
        "pojmy": []
    }
    
    return json.dumps(json_ld_data, ensure_ascii=False, indent=4)