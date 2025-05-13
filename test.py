# This script queries a SPARQL endpoint and saves the results to JSON-LD file.

import os

from pathlib import Path
import sys
# Add the parent directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests
import pandas as pd

from dotenv import load_dotenv

from queries import query_all_grahps
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
    sparql.setQuery(query_all_grahps)
    results = sparql.queryAndConvert()
    
    # Categorize grpaphs by their path, excluding the last part of the URI
    categorized_graphs = {}
    paths:list = []
    for result in results["results"]["bindings"]:
        graph = result["graf"]["value"]
        path = graph.split("/")[3]  # Extract the path from the graph URI
        
        if path not in paths:
            paths.append(path)
    
    
        if path not in categorized_graphs:
            categorized_graphs[path] = []
        categorized_graphs[path].append({
            "graf": graph,
            "created": result["created"]["value"],
            "titleCs": result["titleCs"]["value"],
            "descriptionCs": result.get("descriptionCs", {}).get("value", ""),
            "titleEn": result.get("titleEn", {}).get("value", ""),
            "descriptionEn": result.get("descriptionEn", {}).get("value", "")
        })
        
    # Print the paths
    # print("Paths:")
    # print(paths)
    # # # Print the categorized graphs
    # for path, graphs in categorized_graphs.items():
    #     print(f"Path: {path}")
    #     for graph in graphs:
    #         print(f"  Graph: {graph['graf']}")
    #         print(f"  Created: {graph['created']}")
    #         print(f"  Title (CS): {graph['titleCs']}")
    #         print(f"  Description (CS): {graph['descriptionCs']}")
    #         print(f"  Title (EN): {graph['titleEn']}")
    #         print(f"  Description (EN): {graph['descriptionEn']}")
    
    for path in paths:
        # Get the graphs for the current path
        graphs = categorized_graphs[path]
        
        for graph in graphs:
            
            try:
                name = f'{path}_{graph["graf"].split("/")[4]}'
            except IndexError:
                print(f"Graf URI nemá dostatek segmentů: {graph['graf']}")
                name = f'{path}_{graph["graf"].split("/")[-1] }' 
                print(f"Using name: {name}")
            
            output = Path.cwd() / "outputs" /   f"{name}.jsonld"
            print(f"Output file: {output}")
       
            with open(output, "w", encoding="utf-8") as f:
                
                # Serialize the graph data to JSON-LD format
                json_ld = serializuj_slovnik_do_jsonld(graph)
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
    



