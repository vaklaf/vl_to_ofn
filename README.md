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
    "https://slovník.gov.cz/legislativní/sbírka/361/2000/glosář": "9e278282-fb45-4bd4-acd8-af336964425b.json-ld",
    "https://slovník.gov.cz/legislativní/sbírka/56/2001/glosář": "2fbba82a-f300-4e5d-9c48-f3372ef2455b.json-ld",
    "https://slovník.gov.cz/datový/turistické-cíle/glosář": "9e0b457a-f3c0-427c-8bb4-4679c74617ac.json-ld"
}
```
Do stejné složky se dále ukládá soubor `validation-report.txt` obsahující výsledky procesu validace. Například:

```txt
Glossary 1 (./output/9e278282-fb45-4bd4-acd8-af336964425b.json-ld): ERROR
'https://esbirka.opendata.cz/zdroj/předpis/361/2000/sekce/2/g' does not match '^https\\://opendata\\.eselpoint\\.cz/esel-esb/eli/cz/sb/.*$'
Path: pojmy/0/související-ustanovení-právního-předpisu/0

Glossary 2 (./output/2fbba82a-f300-4e5d-9c48-f3372ef2455b.json-ld): ERROR
'https://esbirka.opendata.cz/zdroj/předpis/56/2001/sekce/3/2/c' does not match '^https\\://opendata\\.eselpoint\\.cz/esel-esb/eli/cz/sb/.*$'
Path: pojmy/0/související-ustanovení-právního-předpisu/0

Glossary 3 (./output/9e0b457a-f3c0-427c-8bb4-4679c74617ac.json-ld): OK
```
