# Převodník dat z Výrobní linky do OFN
---

Cílem tohto kódu je převod dat z [Výrobní linky konceptuálních modelů](https://oha03.dia.gov.cz/modelujeme/sluzby/auth-server/realms/assembly-line/protocol/openid-connect/auth?client_id=al-mission-control&redirect_uri=https%3A%2F%2Foha03.dia.gov.cz%2Fmodelujeme%2Foidc-signin-callback.html%3Fforward_uri%3DaHR0cHM6Ly9vaGEwMy5kaWEuZ292LmN6L21vZGVsdWplbWUvc2x1emJ5Lw%3D%3D&response_type=code&scope=openid&state=a5d673efc39740f38c8862a93df8139d&code_challenge=4Ft38QcjLuVUxp9-ast9yMYoBHAPa7-z2Xp-oNDVZTQ&code_challenge_method=S256&response_mode=query) do [Otevřené formální normy (OFN)](https://data.gov.cz/ofn/) podle standardu definovaného v [Slovníky](https://ofn.gov.cz/slovn%C3%ADky/draft/#konceptu%C3%A1ln%C3%AD-model-p%C5%99%C3%ADklady).

Kromě převodu dat je zahrnuta i validace porti [JSON Schema](https://ofn.gov.cz/slovn%C3%ADky/draft/#konceptu%C3%A1ln%C3%AD-model-p%C5%99%C3%ADklady:~:text=model%20v%20JSON%2DLD%2C-,JSON%20Schema,-%2C%20JSON%2DLD%20kontext).

## Způsoby zpuštění

Kód lze spustit třemi způsoby podle toho, zda chceme zpracovat

1.  všechny slovníky uložené v databázi
2.  několik jednolivých slovníků zadaných jako seznam IRI oddělených čárkou
3.  více slovníků definovancýh jako seznam IRI v textovém souboru.
   
```powershell
>python .\main process --all-graphs
```

Pro případ, že cheme zpracovat kompletní obsah databáze.

<div style="background-color: #f8d7da; color: #721c24; padding: 10px; border: 1px solid #f5c6cb; border-radius: 5px; border-left: 3px solid red; margin: 10px 0;;">
  🚨 <strong>ISSUE:</strong> Pomalé. Zpracování celé databáze může trvat i několik hodin.
</div>



```powershell
>python .\main.py process --graphs https://slovník.gov.cz/legislativní/sbírka/361/2000,https://slovník.gov.cz/legislativní/sbírka/56/2001/
```

Pro případ, že chceme zpracovat několik málo jednotlivých slovníků.

```powershell
>python .\main.py process --graph-file .\seznam.txt
```

Pro případ, že chceme zpracovat seznam IRI definovaný v textovém souboru.

V případě potřeby je možné vyvolat nápovědu pomocí:

```powershell
>python .\main.py process --help
```

## Jak se ukládají výsledky

Zpracované slovníky se ukládají do složky `output` jako soubory `*.json-ld`. Konkrétní příklad: `2fbba82a-f300-4e5d-9c48-f3372ef2455b.json-ld`

Do složky `docs` se ukládají sobury `glossaries_files.json` obsahující mapování mezi názvy zpracovaných slovníků a soubory. Například

```json
{
    "https://slovník.gov.cz/legislativní/sbírka/361/2000/glosář": "2138c3c1-88c2-4e64-a342-b21e5fd48d63.json-ld",
    "https://slovník.gov.cz/legislativní/sbírka/56/2001/glosář": "ce8967d6-07fa-40f7-bed6-4d37c2d9f235.json-ld",
    "https://slovník.gov.cz/datový/turistické-cíle/glosář": "79d9d300-c03b-4218-af48-a643bdf28b6f.json-ld"
}
```
Do stejné složky se dále ukládá soubor `validation-report.json` obsahující výsledky procesu validace. Například:

```json
{
    "https://slovník.gov.cz/legislativní/sbírka/361/2000/glosář": {
        "status": "ERROR",
        "file": "./output/2138c3c1-88c2-4e64-a342-b21e5fd48d63.json-ld",
        "error": "'https://esbirka.opendata.cz/zdroj/předpis/361/2000/sekce/2/g' does not match '^https\\\\://opendata\\\\.eselpoint\\\\.cz/esel-esb/eli/cz/sb/.*$'\n\nFailed validating 'pattern' in schema['allOf'][1]['properties']['pojmy']['items']['properties']['související-ustanovení-právního-předpisu']['items']:\n    {'type': 'string',\n     'format': 'iri',\n     'pattern': '^https\\\\://opendata\\\\.eselpoint\\\\.cz/esel-esb/eli/cz/sb/.*$',\n     'examples': ['https://opendata.eselpoint.cz/esel-esb/eli/cz/sb/1999/106/2024-01-01/dokument/norma/cast_1/par_3a/odst_3']}\n\nOn instance['pojmy'][0]['související-ustanovení-právního-předpisu'][0]:\n    'https://esbirka.opendata.cz/zdroj/předpis/361/2000/sekce/2/g'",
        "path": "pojmy/0/související-ustanovení-právního-předpisu/0"
    },
    "https://slovník.gov.cz/legislativní/sbírka/56/2001/glosář": {
        "status": "ERROR",
        "file": "./output/ce8967d6-07fa-40f7-bed6-4d37c2d9f235.json-ld",
        "error": "'https://esbirka.opendata.cz/zdroj/předpis/56/2001/sekce/3/2/c' does not match '^https\\\\://opendata\\\\.eselpoint\\\\.cz/esel-esb/eli/cz/sb/.*$'\n\nFailed validating 'pattern' in schema['allOf'][1]['properties']['pojmy']['items']['properties']['související-ustanovení-právního-předpisu']['items']:\n    {'type': 'string',\n     'format': 'iri',\n     'pattern': '^https\\\\://opendata\\\\.eselpoint\\\\.cz/esel-esb/eli/cz/sb/.*$',\n     'examples': ['https://opendata.eselpoint.cz/esel-esb/eli/cz/sb/1999/106/2024-01-01/dokument/norma/cast_1/par_3a/odst_3']}\n\nOn instance['pojmy'][0]['související-ustanovení-právního-předpisu'][0]:\n    'https://esbirka.opendata.cz/zdroj/předpis/56/2001/sekce/3/2/c'",
        "path": "pojmy/0/související-ustanovení-právního-předpisu/0"
    },
    "https://slovník.gov.cz/datový/turistické-cíle/glosář": {
        "status": "OK",
        "file": "./output/79d9d300-c03b-4218-af48-a643bdf28b6f.json-ld"
    }
}
```

## Zobrazení výsledků

Pro pohldlnější práci s výsledky zpracování byl přidán modul `streamlit-app` založený na [STREAMLIT](https://streamlit.io/). Tento modul lze spustit následujícím příkazem.

```powershell
>python .\main.py show
```

