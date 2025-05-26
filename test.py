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

from queries import all_glossaries,qurey_items_template
from serializers import serializuj_slovnik_do_jsonld;


# Load environment variables from .env file
load_dotenv()
# Get the SPARQL endpoint URL from the environment variable
SPARQL_ENDPOINT = os.getenv("SPARQL_ENDPOINT")

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
    paths:list = []

    for result in results["results"]["bindings"]:
    
        graf = result["graf"]["value"]
 
        if graf not in grafy:
            grafy[graf] = {
                "graf": graf,
                "created": result["grafCreated"]["value"],
                "titleCs": result["grafLabelCs"]["value"],
                "descriptionCs": result["grafDefinitionCs"]["value"],
                "titleEn": result["grafLabelEn"]["value"],
                "descriptionEn": result["grafDefinitionEn"]["value"],
                "typ": result["grafTypStrPole"]["value"]
            }
        
    for key,graf in grafy.items():
        

        try:
            name = key.split("/")[4]
        except IndexError:
            print(f"Graf URI nemá dostatek segmentů: {graf['graf']}")
            name = key.split("/")[-1]
            print(f"Using name: {name}")
        
        # Create the output directory if it doesn't exist
        output_dir = Path.cwd() / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output = output_dir /  f"{name}.jsonld"
        
        # Get dictionary items
        basic_graf = graf['graf'].rsplit("/", 1)[0] + "/" 
        glosar_graph = f"{basic_graf}glosář"
        model_graph = f"{basic_graf}model"
        qurey_items = qurey_items_template.format(glosar_graph=glosar_graph, model_graph=model_graph)
    #    
        #print(qurey_items)
                 
        sparql.setQuery(qurey_items)
        results = sparql.queryAndConvert()
        print(f"Processing graph: {graf['graf']}")
        print(results)
        
        
        with open(output, "w", encoding="utf-8") as f:
            
                        
            # Serialize the graph data to JSON-LD format
            json_ld = serializuj_slovnik_do_jsonld(graf)
            f.write(json_ld)
            f.write("\n")
               
    print(f"JSON-LD files have been saved to the outputs directory.");
    
except requests.exceptions.RequestException as e:
    print(f"Error connecting to SPARQL endpoint: {e}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)
    



