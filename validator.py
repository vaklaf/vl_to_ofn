import json
from referencing import Registry, Resource
from jsonschema import ValidationError, Draft202012Validator

GLOSSARIES_FILE = "./output/glossaries_files.json"
REPORT_FILE = "./output/validation_report.txt"

# Načti všechna schémata
with open("./schemas/json_schema.json", encoding="utf-8") as f:
    JSON_SCHEMA = json.load(f)
with open("./schemas/slovnik.json", encoding="utf-8") as f:
    slovnik_schema = json.load(f)
with open("./schemas/data_types/text.json", encoding="utf-8") as f:
    dt_text = json.load(f)
with open("./schemas/data_types/věc.json", encoding="utf-8") as f:
    dt_vec = json.load(f)
with open("./schemas/data_types/časový_okamžik.json", encoding="utf-8") as f:
    dt_casovy_okamzik = json.load(f)
with open("./schemas/data_types/digitální_objekt.json", encoding="utf-8") as f:
    dt_digitalni_objekt = json.load(f)

# Vytvoř referencing registry
registry = (
    Registry()
    .with_resource("https://ofn.gov.cz/slovníky/draft/schémata/slovník.json", Resource.from_contents(slovnik_schema))
    .with_resource("https://ofn.gov.cz/základní-datové-typy/2020-07-01/schémata/text.json", Resource.from_contents(dt_text))
    .with_resource("https://ofn.gov.cz/základní-datové-typy/2020-07-01/schémata/věc.json", Resource.from_contents(dt_vec))
    .with_resource("https://ofn.gov.cz/základní-datové-typy/2020-07-01/schémata/časový_okamžik.json", Resource.from_contents(dt_casovy_okamzik))
    .with_resource("https://ofn.gov.cz/základní-datové-typy/2020-07-01/schémata/digitální_objekt.json", Resource.from_contents(dt_digitalni_objekt))
)

def validate_glossaries(glossaries_file, report_file,output_dir):
    with open(glossaries_file, encoding="utf-8") as f:
        glossaries = json.load(f)

    report_lines = []
    for idx, iri in enumerate(glossaries):
        glossary_file = f'{output_dir}/{glossaries[iri]}'
        try:
            with open(glossary_file, encoding="utf-8") as gf:
                glossary_data = json.load(gf)

            # Vytvoř validator s referencing registry
            validator = Draft202012Validator(schema=JSON_SCHEMA, registry=registry)
            validator.validate(glossary_data)
            report_lines.append(f"Glossary {idx+1} ({glossary_file}): OK")
        except ValidationError as e:
            report_lines.append(
                f"Glossary {idx+1} ({glossary_file}): ERROR\n{e.message}\nPath: {'/'.join(map(str, e.path))}\n"
            )
        except Exception as e:
            report_lines.append(
                f"Glossary {idx+1} ({glossary_file}): ERROR\n{str(e)}\n"
            )

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

if __name__ == "__main__":
    validate_glossaries()