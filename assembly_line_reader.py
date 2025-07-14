# This script queries a SPARQL endpoint and saves the results to JSON-LD file.

import json
import time

from random import randint
from pathlib import Path
import sys
# Add the parent directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests

from SPARQLWrapper import SPARQLWrapper, JSON

from queries import all_glossaries, query_items_full_template,query_term_restrictions_template
from serializers import serializuj_slovnik_do_jsonld;
from utilities import generate_target_filename
from enums.enum_restrictions import EnumRestrictions
from enums.enum_term_types import EnumTermTypes


GLOSSARIES_FILES = {}

def setup_sparql_connection(sparql_endpoint):
    """ Sets up the SPARQL connection with the given endpoint."""
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setReturnFormat(JSON)    
    print(f"SPARQL connection set up with endpoint: {sparql_endpoint}")
    return sparql

def register_glossary_file(glosar_graph, file_name):
    """ Registers the glossary file path for a given graph."""
    GLOSSARIES_FILES[glosar_graph] = file_name
    print(f"Registered glossary graph: {glosar_graph} with file: {file_name}")
    
# def get_restrictions(connection,term,vocabulary,glossary,model):
    
#     query = query_term_restrictions_template.format(
#         vocabulary_graph = vocabulary,
#         graph_model = model,
#         graph_glossary = glossary,
#         term = term,
#         restrictions = " ".join(EnumRestrictions.to_list())
#     )
#     connection.setQuery(query)
#     results = connection.queryAndConvert()
#     return results["results"]["bindings"]

# def get_term_type(connection,term):
    
#     query = query_term_type_template.format(
#         term = term,
#         terms_types=" ".join(EnumTermTypes.to_list())
#     )

#     connection.setQuery(query)
    
#     results = connection.queryAndConvert()
    
#    return  EnumTermTypes.from_value(results['results']['bindings'][0]['type']['value']) if results['results']['bindings'] else None

# def get_term_alt_subject_objects(connection, term):
#     """ Returns the alternative subject objects for a given term."""
#     query = query_term_alt_subject_objects_template.format(term=term)
#     connection.setQuery(query)
    
#     results = connection.queryAndConvert()
    
#     return results['results']['bindings'][0]['typObjSbj']['value'] if results['results']['bindings'] else None

def vocabulary_to_json(glosar_graph, data,output_dir):
    """ Writes the data to a JSON-LD file."""
    print(__name__, "vocabulary_to_json")
    json_file = generate_target_filename(output_dir)
    
    register_glossary_file(glosar_graph, json_file.name)
            
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(data)
        print(f"Saved glossary to {json_file}")
    
def write_glossaries_and_files_to_json(output_path):
    """ Writes the glossary files and their paths to a JSON file."""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(GLOSSARIES_FILES, f, ensure_ascii=False, indent=4)
        
    print(f"Glossary files saved to {output_path}")




def read_data_from_assembly_line(sparql_endpoint, output_dir, graphs_to_process=None):
    """ Reads data from the assembly line and returns it."""
    try:
        sparql = setup_sparql_connection(sparql_endpoint)
        # Pokud je zadán seznam grafů, vytvoř dotaz pouze na ně
        if graphs_to_process:
            glossaries = {}
            for vocabulary in graphs_to_process:
                print(f"Processing vocabulary: {vocabulary}")
                glosar_graph = f"{vocabulary}/glosář"
                model_graph = f"{vocabulary}/model"
                glossary = {
                    "title": {},
                    "pojmy": []
                }
                # Dotaz na metadata slovníku (název, popis, created)
                # Pokud potřebuješ, můžeš zde přidat dotaz na metadata
                requiered_types = " ".join(EnumTermTypes.to_list())
                query_items = query_items_full_template.format(
                    glosar_graph=glosar_graph, 
                    model_graph=model_graph,
                    terms_types=requiered_types )
                sparql.setQuery(query_items)
                items_results = sparql.queryAndConvert()
                for result in items_results["results"]["bindings"]:
                    pojem_iri = result["pojem"]["value"]
                    print(f"Processing concept: {pojem_iri}")
                    concept = next((p for p in glossary["pojmy"] if p["iri"] == pojem_iri), None)
                    if not concept:
                        concept = {
                            "iri": pojem_iri,
                            "label": {},
                            "altLabel": {},
                            "definition": {},
                            "poznamka": {},
                            "typObjektu": [],
                        }
                        if result.get("pojemJePodtridouPole", {}).get("value"):
                            concept["nadrazenyPojem"] = [x.strip() for x in result["pojemJePodtridouPole"]["value"].split(',') if x.strip()]
                        if result.get("pojemZdroj", {}).get("value"):
                            concept["zdroj"] = [x.strip() for x in  result["pojemZdroj"]["value"].split(',') if x.strip()]
                        if result.get("definicniObor", {}).get("value"):
                            concept["definicniObor"] = [x.strip() for x in result["definicniObor"]["value"].split(',') if x.strip()]
                        print(f"Getting term type for: {pojem_iri}")
                        type = EnumTermTypes.from_value(
                            result.get("types", {}).get("value", "").split(",")[0] 
                            if result.get("types") else None)
                        if type and type[1] not in concept["typObjektu"]:
                            concept["typObjektu"].append(type[1])
                        if type and type[0] == EnumTermTypes.OBJEKT:
                            print(f"Getting alternative subject objects of right for: {pojem_iri}")
                            altSubjObj = result.get("typObjSbjPole", {}).get("value","").split(",")[0] if result.get("typObjSbjPole") else None
                            if not altSubjObj is None and altSubjObj.strip() != '':
                                concept["typObjektu"].append(altSubjObj.strip())
                        if result.get("pojemExactMatchPole", {}).get("value"):
                            concept["exactMatch"] = [x.strip() for x in result["pojemExactMatchPole"]["value"].split(',') if x.strip()]
                        glossary["pojmy"].append(concept)
                    if "label" in result and "xml:lang" in result["label"]:
                        lang = result["label"]["xml:lang"]
                        concept["label"][lang] = result["label"]["value"]
                    if "altLabel" in result and "xml:lang" in result["altLabel"]:
                        lang = result["altLabel"]["xml:lang"]
                        concept["altLabel"][lang] = result["altLabel"]["value"]
                    if (
                        "definition" in result 
                        and "xml:lang" in result["definition"]
                        and result["definition"].get("value", "").strip()
                    ):
                        lang = result["definition"]["xml:lang"]
                        concept["definition"][lang] = result["definition"]["value"]
                    if (
                        "poznamka" in result
                        and "xml:lang" in result["poznamka"]
                        and result["poznamka"].get("value", "").strip()
                    ):
                        lang = result["poznamka"]["xml:lang"]
                        concept["poznamka"][lang] = result["poznamka"]["value"]
                    time.sleep(randint(1, 3))
                json_ld_data = serializuj_slovnik_do_jsonld(vocabulary, glossary)
                vocabulary_to_json(glosar_graph, json_ld_data, output_dir)
                time.sleep(randint(1, 3))
        else:
            # Původní chování: zpracuj všechny slovníky v databázi
            sparql.setQuery(all_glossaries)
            results = sparql.queryAndConvert()
            glossaries = {}
            for result in results["results"]["bindings"]:
                vocabulary = result["vocabulary"]["value"]
                glossary = glossaries.setdefault(vocabulary, {
                    "title": {},
                    "pojmy": []
                })
                if "gLabel" in result and "xml:lang" in result["gLabel"]:
                    glossary["title"][result["gLabel"]["xml:lang"]] = result["gLabel"]["value"]
                if "gDescription" in result and "xml:lang" in result["gDescription"]:
                    glossary.setdefault("description", {})[result["gDescription"]["xml:lang"]] = result["gDescription"]["value"]
                if "grafCreated" in result and "value" in result["grafCreated"]:
                    glossary["created"] = result["grafCreated"]["value"]
            requiered_types = " ".join(EnumTermTypes.to_list())
            for vocabulary, glossary in glossaries.items():
                print(f"Processing vocabulary: {vocabulary}")
                glosar_graph = f"{vocabulary}/glosář"
                model_graph = f"{vocabulary}/model"
                query_items = query_items_full_template.format(
                    glosar_graph=glosar_graph, 
                    model_graph=model_graph,
                    terms_types=requiered_types )
                sparql.setQuery(query_items)
                items_results = sparql.queryAndConvert()
                for result in items_results["results"]["bindings"]:
                    pojem_iri = result["pojem"]["value"]
                    print(f"Processing concept: {pojem_iri}")
                    concept = next((p for p in glossary["pojmy"] if p["iri"] == pojem_iri), None)
                    if not concept:
                        concept = {
                            "iri": pojem_iri,
                            "label": {},
                            "altLabel": {},
                            "definition": {},
                            "poznamka": {},
                            "typObjektu": [],
                        }
                        if result.get("pojemJePodtridouPole", {}).get("value"):
                            concept["nadrazenyPojem"] = [x.strip() for x in result["pojemJePodtridouPole"]["value"].split(',') if x.strip()]
                        if result.get("pojemZdroj", {}).get("value"):
                            concept["zdroj"] = [x.strip() for x in  result["pojemZdroj"]["value"].split(',') if x.strip()]
                        if result.get("definicniObor", {}).get("value"):
                            concept["definicniObor"] = [x.strip() for x in result["definicniObor"]["value"].split(',') if x.strip()]
                        print(f"Getting term type for: {pojem_iri}")
                        type = EnumTermTypes.from_value(
                            result.get("types", {}).get("value", "").split(",")[0] 
                            if result.get("types") else None)
                        if type and type[1] not in concept["typObjektu"]:
                            concept["typObjektu"].append(type[1])
                        if type and type[0] == EnumTermTypes.OBJEKT:
                            print(f"Getting alternative subject objects of right for: {pojem_iri}")
                            altSubjObj = result.get("typObjSbjPole", {}).get("value","").split(",")[0] if result.get("typObjSbjPole") else None
                            if not altSubjObj is None and altSubjObj.strip() != '':
                                concept["typObjektu"].append(altSubjObj.strip())
                        if result.get("pojemExactMatchPole", {}).get("value"):
                            concept["exactMatch"] = [x.strip() for x in result["pojemExactMatchPole"]["value"].split(',') if x.strip()]
                        glossary["pojmy"].append(concept)
                    if "label" in result and "xml:lang" in result["label"]:
                        lang = result["label"]["xml:lang"]
                        concept["label"][lang] = result["label"]["value"]
                    if "altLabel" in result and "xml:lang" in result["altLabel"]:
                        lang = result["altLabel"]["xml:lang"]
                        concept["altLabel"][lang] = result["altLabel"]["value"]
                    if (
                        "definition" in result 
                        and "xml:lang" in result["definition"]
                        and result["definition"].get("value", "").strip()
                    ):
                        lang = result["definition"]["xml:lang"]
                        concept["definition"][lang] = result["definition"]["value"]
                    if (
                        "poznamka" in result
                        and "xml:lang" in result["poznamka"]
                        and result["poznamka"].get("value", "").strip()
                    ):
                        lang = result["poznamka"]["xml:lang"]
                        concept["poznamka"][lang] = result["poznamka"]["value"]
                    time.sleep(randint(1, 3))
                json_ld_data = serializuj_slovnik_do_jsonld(vocabulary, glossary)
                vocabulary_to_json(glosar_graph, json_ld_data, output_dir)
                time.sleep(randint(1, 3))
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SPARQL endpoint: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

def run_assebmly_line_reader(
    sparql_endpoint,
    output_dir,
    glossaries_file,
    graphs_to_process=None
):
    """ Main function to read data from the assembly line and write it to JSON-LD files."""
    read_data_from_assembly_line(sparql_endpoint, output_dir, graphs_to_process)
    write_glossaries_and_files_to_json(glossaries_file)



