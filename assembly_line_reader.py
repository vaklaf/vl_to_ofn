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

try:
    # Set the SPARQL query
    sparql.setQuery(all_glossaries)
    results = sparql.queryAndConvert()
    
       
    grafy = {}

    
    
    for result in results["results"]["bindings"]:
        graf = result["graf"]["value"]

        # Inicializace slovníku pro graf, pokud ještě neexistuje
        if graf not in grafy:
            grafy[graf] = {
                "typ": [result["grafTypStrPole"]["value"]],
                "title": {}
            }
            if "grafCreated" in result and "value" in result["grafCreated"]:
                grafy[graf]["created"] = result["grafCreated"]["value"]

        # Uložení názvu podle jazyka
        if "gLabel" in result and "xml:lang" in result["gLabel"]:
            lang = result["gLabel"]["xml:lang"]
            value = result["gLabel"]["value"]
            grafy[graf]["title"][lang] = value
            
        # Uložení popisu podle jazyka
        if "gDescription" in result and "xml:lang" in result["gDescription"]:
            if "description" not in grafy[graf]:
                grafy[graf]["description"] = {}
            lang = result["gDescription"]["xml:lang"]
            value = result["gDescription"]["value"]
            grafy[graf]["description"][lang] = value
            
            
        grafy[graf]["pojmy"] = []
        
        # Get dictionary items
        basic_graf = graf.rsplit("/", 1)[0] + "/" 
        
        glosar_graph = f"{basic_graf}glosář"
        model_graph = f"{basic_graf}model"
        
        query_items = query_items_template.format(glosar_graph=glosar_graph, model_graph=model_graph)
        

        sparql.setQuery(query_items)
        items_results = sparql.queryAndConvert()
          
        for result in items_results["results"]["bindings"]:
            pojem = {}
            pojem["iri"] = result["pojem"]["value"]
            pojem["typObjektu"] = [to.strip() for to in  result["typObjektuPole"]["value"].split(',') if len(to)>=2];
            pojem["nazev"] = {}
            if "labelCsStr" in result:
                pojem["nazev"]["cs"] = result["labelCsStr"]["value"]
            if "labelEnStr" in result and result["labelEnStr"]["value"]:
                pojem["nazev"]["en"] = result["labelEnStr"]["value"]
                
            # Definice – vytvoř pouze pokud existuje alespoň jedna hodnota
            definice = {}
            if "definitionCsStr" in result and result["definitionCsStr"]["value"]:
                definice["cs"] = result["definitionCsStr"]["value"]
            if "definitionEnStr" in result and result["definitionEnStr"]["value"]:
                definice["en"] = result["definitionEnStr"]["value"]
            if definice:
                pojem["definice"] = definice
            if result.get("nadrazenyPojemPole", {}).get("value"):
                pojem["nadrazenyPojem"] = list(map(lambda x:x.strip(),result["nadrazenyPojemPole"]["value"].split(',')))
            if result.get("pojemZdroj", {}).get("value"):
                pojem["zdroj"] = result.get("pojemZdroj",{}).get("value")
            
            
            grafy[graf]["pojmy"].append(pojem)
            
    files_glossaries = {}
    
    json_file = create_target_filename(OUTPUT_DIR)
    
    files_glossaries[glosar_graph] = json_file.name
    
    print(f"Glossary graph: {files_glossaries}")
            

    
    data = serializuj_slovnik_do_jsonld(graf,grafy[graf])
    
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(data)
        print(f"Saved glossary to {json_file}")

                     
except requests.exceptions.RequestException as e:
    print(f"Error connecting to SPARQL endpoint: {e}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)