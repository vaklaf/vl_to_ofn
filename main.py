import subprocess

import typer

from rich import print
from pathlib import Path

# Importing custom modules
from assembly_line_reader import run_assebmly_line_reader
from validator import validate_glossaries
from setup import prepare_environment


app = typer.Typer()

@app.command()
def process(
    all_graphs: bool = typer.Option(
        False, "--all-graphs", help="Zpracovat všechny grafy v databázi (pomalejší, zobrazí varování)"
    ),
    graphs: str = typer.Option(
        None, "--graphs", help="Seznam grafů oddělených čárkou"
    ),
    graphs_file: Path = typer.Option(
        None, "--graphs-file", help="Cesta k souboru se seznamem grafů (jeden na řádek)"
    ),

):
    """Process the SPARQL queries and generate output."""
    print("[bold blue]Spouštím zpracování SPARQL dotazů a generování výstupu...[/bold blue]")
    # Prepare environment
    settings = prepare_environment()
    
    if all_graphs:
        print("[yellow]Zpracovávám všechny grafy v databázi. Může to chvíli trvat...[/yellow]")
        # Run assembly line reader with provided settings
        run_assebmly_line_reader(
            sparql_endpoint=settings["sparql_endpoint"],
            output_dir=settings["output_dir"],
            glossaries_file=settings["glossaries_file"],
        )
    else:
        selected_graphs = []
        if graphs:
            selected_graphs = [g.strip() for g in graphs.split(",") if g.strip()]
        elif graphs_file:
            with open(graphs_file, encoding="utf-8") as f:
                selected_graphs = [line.strip() for line in f if line.strip()]
        else:
            typer.echo("Musíte zadat --all-graphs, --graphs nebo --graphs-file.")
            raise typer.Exit(1)
        # Předpokládáme, že run_assebmly_line_reader umí přijmout seznam grafů jako parametr
        run_assebmly_line_reader(sparql_endpoint=settings["sparql_endpoint"],
                                 output_dir=settings["output_dir"],
                                 glossaries_file=settings["glossaries_file"],
                                 graphs_to_process = selected_graphs)    
    print("[bold blue]Provádím validaci slovníků...[/bold blue]")
    # Validate glossaries after reading data
    validate_glossaries(glossaries_file=settings["glossaries_file"],
                        report_file=settings["validation_report_file"],
                        output_dir=settings["output_dir"])
    print("[green]Validace slovníků dokončena.[/green]")
    print("[green]Zpracování dokončeno.[/green]")
            
def main():
    app()
    
if __name__ == "__main__":
    main()