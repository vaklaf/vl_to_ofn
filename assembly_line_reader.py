# This script queries a SPARQL endpoint and saves the results to JSON-LD file.

import os
import json

from pathlib import Path
import sys
# Add the parent directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests

from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv

from queries import all_glossaries, query_items_template
from serializers import serializuj_slovnik_do_jsonld;
from utilities import create_target_filename, clear_output_folder


# Load environment variables from .env file
load_dotenv()

# Get the SPARQL endpoint URL from the environment variable
SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT")

# Check output directory from environment variable
OUTPUT_DIR = Path.cwd() / os.getenv("OUTPUT_DIR")
if not OUTPUT_DIR.is_dir():
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
else:
    
    clear_output_folder(output_dir=OUTPUT_DIR)

# Check if the SPARQL endpoint URL is set
if not SPARQL_ENDPOINT:
    print("SPARQL_ENDPOINT environment variable is not set.")
    exit(1)

sparql = SPARQLWrapper(SPARQL_ENDPOINT)
sparql.setReturnFormat(JSON)

GLOSSARIES_FILES = {}


def register_glossary_file(glosar_graph, file_name):
    """ Registers the glossary file path for a given graph."""
    GLOSSARIES_FILES[glosar_graph] = file_name
    print(f"Registered glossary graph: {glosar_graph} with file: {file_name}")
    
def get_restrictions():
    """ Returns the restrictions from the SPARQL endpoint."""
    sparql.setQuery("""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?restriction ?list
    WHERE {
        ?restriction a owl:Restriction .
        ?restriction owl:intersectionOf ?list .
    }
    """)
    
    results = sparql.queryAndConvert()
    
    return results["results"]["bindings"]

def read_data_from_assembly_line():
    """ Reads data from the assembly line and returns it."""
    try:
        sparql.setQuery(all_glossaries)
        results = sparql.queryAndConvert()
        glossaries = {}

        for result in results["results"]["bindings"]:
            vocabulary = result["vocabulary"]["value"]
            glossary = glossaries.setdefault(vocabulary, {
                #"typ": [t.strip() for t in result["grafTypStrPole"]["value"].split(",")],
                "title": {},
                "pojmy": []
            })
            # Název podle jazyka
            if "gLabel" in result and "xml:lang" in result["gLabel"]:
                glossary["title"][result["gLabel"]["xml:lang"]] = result["gLabel"]["value"]
            # Popis podle jazyka
            if "gDescription" in result and "xml:lang" in result["gDescription"]:
                glossary.setdefault("description", {})[result["gDescription"]["xml:lang"]] = result["gDescription"]["value"]
            # Datum vytvoření
            if "grafCreated" in result and "value" in result["grafCreated"]:
                glossary["created"] = result["grafCreated"]["value"]

        for vocabulary, glossary in glossaries.items():
            # Sestavení názvů grafů
            #basic_graf = graf.rsplit("/", 1)[0] + "/"
            glosar_graph = f"{vocabulary}/glosář"
            model_graph = f"{vocabulary}/model"
            query_items = query_items_template.format(glosar_graph=glosar_graph, model_graph=model_graph)
            
            print(query_items)
            
         
            sparql.setQuery(query_items)
            items_results = sparql.queryAndConvert()

            for result in items_results["results"]["bindings"]:
                pojem_iri = result["pojem"]["value"]

                # Najdi nebo vytvoř pojem podle IRI
                concept = next((p for p in glossary["pojmy"] if p["iri"] == pojem_iri), None)
                if not concept:
                    concept = {
                        "iri": pojem_iri,
                        "label": {},
                        "altLabel": {},
                        "definition": {},
                        "poznamka": {},  # <-- přidat tuto inicializaci
                        "typObjektu": [to.strip() for to in result.get("typObjektuPole", {}).get("value", "").split(',') if len(to.strip()) > 1],
                    }
                    # # Přidej poznámku, pokud existuje
                    # if "poznamka" in result and "xml:lang" in result["poznamka"]:
                    #     lang = result["poznamka"]["xml:lang"]
                    #     concept["poznamka"][lang] = result["poznamka"]["value"]
                    # Nadřazený pojem
                    # if result.get("nadrazenyPojemPole", {}).get("value"):
                    #     concept["nadrazenyPojem"] = [x.strip() for x in result["nadrazenyPojemPole"]["value"].split(',') if x.strip()]
                    # ISSUE 0003-BUG-not-correct-usage-skos-borader
                    # nesprávné použití skos:broader
                    # oprava 24.6.2025 - VJ
                    if result.get("pojemJePodtridouPole", {}).get("value"):
                        concept["nadrazenyPojem"] = [x.strip() for x in result["pojemJePodtridouPole"]["value"].split(',') if x.strip()]
                    # Zdroj
                    if result.get("pojemZdroj", {}).get("value"):
                        concept["zdroj"] = [x.strip() for x in  result["pojemZdroj"]["value"].split(',') if x.strip()]
                    # Exact match
                    if result.get("pojemExactMatchPole", {}).get("value"):
                        concept["exactMatch"] = [x.strip() for x in result["pojemExactMatchPole"]["value"].split(',') if x.strip()]
                    glossary["pojmy"].append(concept)

                # label
                if "label" in result and "xml:lang" in result["label"]:
                    lang = result["label"]["xml:lang"]
                    concept["label"][lang] = result["label"]["value"]
                # altLabel
                if "altLabel" in result and "xml:lang" in result["altLabel"]:
                    lang = result["altLabel"]["xml:lang"]
                    concept["altLabel"][lang] = result["altLabel"]["value"]
                # definition
                if (
                    "definition" in result 
                    and "xml:lang" in result["definition"]
                    and result["definition"].get("value", "").strip()  # pouze pokud není prázdné
                ):
                    lang = result["definition"]["xml:lang"]
                    concept["definition"][lang] = result["definition"]["value"]
                # poznámka – stejně jako label, přidávej pouze pokud jsou data
                if (
                    "poznamka" in result
                    and "xml:lang" in result["poznamka"]
                    and result["poznamka"].get("value", "").strip()  # pouze pokud není prázdné
                ):
                    lang = result["poznamka"]["xml:lang"]
                    concept["poznamka"][lang] = result["poznamka"]["value"]

        return glossaries

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SPARQL endpoint: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
        
def write_data_to_jsonl(glosar_graph, data):
    """ Writes the data to a JSON-LD file."""
    
    json_file = create_target_filename(OUTPUT_DIR)
    
    register_glossary_file(glosar_graph, json_file.name)
            
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(data)
        print(f"Saved glossary to {json_file}")
    
def write_glossaries_and_files_to_json():
    """ Writes the glossary files and their paths to a JSON file."""
    
    output_file = OUTPUT_DIR / "glossaries_files.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(GLOSSARIES_FILES, f, ensure_ascii=False, indent=4)
        
    print(f"Glossary files saved to {output_file}")
        
def run_assebmly_line_reader(
    output_dir=OUTPUT_DIR,
    sparql_endpoint=SPARQL_ENDPOINT
):
    """ Main function to read data from the assembly line and write it to JSON-LD files."""
    
    grafy = read_data_from_assembly_line()
    for graf, data in grafy.items():
        json_ld_data = serializuj_slovnik_do_jsonld(graf, data)
        
        write_data_to_jsonl(graf, json_ld_data)
    write_glossaries_and_files_to_json()



