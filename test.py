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
            
            # Pokud je v result klíč "gLabel" a má jazyk "cs", vytvoř název češtině.
            if "gLabel" in result \
                and "xml:lang" in result["gLabel"] \
                and result["gLabel"]["xml:lang"] == "cs":
                title_cs = result["gLabel"]["value"]
            else:
                title_cs = ""
                
            # Pokud je v reslut klíč "gLabel" a má jazyk "en", vytvoř název v angličtině.    
            if "gLabel" in result \
                and "xml:lang" in result["gLabel"] \
                and result["gLabel"]["xml:lang"] == "en":
                title_en = result["gLabel"]["value"]
            else:
                title_en = ""   
                
            # Pokud je v reslut klíč "gDefinition" a má jazyk "cs", vytvoř popis v češtině.    
            if "gDefinition" in result and "xml:lang" in result["gDefinition"] and result["gDefinition"]["xml:lang"] == "cs":
                description_cs = result["gDefinition"]["value"]
            else:
                description_cs = ""
                
            # Pokud je v reslut klíč "gDefinition" a má jazyk "en", vytovř popis v angličtině.    
            if "gDefiniton" in result and "xml:lang" in result["gDefinition"] and result["gDefinition"]["xml:lang"] == "en":
                description_en = result["gDefinition"]["value"]
            else:
                description_en = ""
                
            graf_dict = {
                "graf": graf,
                "typ": result["grafTypStrPole"]["value"]
            }
            
            # Pokud je v reslut klíč "grafCreated", přidej hodnotu do slovníku.
            if "grafCreated" in result and "value" in result["grafCreated"]:
                if "created" not in graf_dict:
                    graf_dict["created"] = result["grafCreated"]["value"]
        
            # Pokud není v graf_dict klíč "title", přidej prázdný slovník.
            if "title" not in graf_dict:
                graf_dict["title"] = {}

            # Přidej český a anglický název do slovníku, pokud jsou k dispozici.
            if title_cs:
                graf_dict["title"]["cs"] = title_cs
                
            if title_en:
                graf_dict["title"]["en"] = title_en
            
            # Pokud není v graf_dict klíč "description", přidej prázdný slovník.
            if "description" not in graf_dict:
                graf_dict["description"] = {}
            
            # Přidej český a anglický popis do slovníku, pokud jsou k dispozici.
            if description_cs:
                graf_dict["description"]["cs"] = description_cs
            
            if description_en:
                graf_dict["description"]["en"] = description_en
                
            # Přidej graf_dict do slovníku grafy pod klíčem graf.
            grafy[graf] = graf_dict
        
    for key,graf in grafy.items():
        
        # Print the graph information
        print(f"Graph URI: {graf['graf']}")
        if graf.get("created"):
            print(f"Created: {graf['created']}")
        if "title" in graf:
            print(f"Title: {graf['title']}")
        if graf.get("description"):
            print(f"Description: {graf['description']}")
        print(f"Type: {graf['typ']}")
        print("-" * 40)

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
        
        
        # with open(output, "w", encoding="utf-8") as f:
            
                        
        #     # Serialize the graph data to JSON-LD format
        #     json_ld = serializuj_slovnik_do_jsonld(graf)
        #     f.write(json_ld)
        #     f.write("\n")
               
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
    



