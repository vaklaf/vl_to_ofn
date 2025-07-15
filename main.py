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
    typer.secho("[Spouštím zpracování SPARQL dotazů a generování výstupu...]", fg=typer.colors.BLUE, bold=True)
    # Prepare environment
    settings = prepare_environment()
    
    if all_graphs:
        typer.secho("Zpracovávám všechny grafy v databázi. Může to chvíli trvat...", fg=typer.colors.YELLOW, bold=True)
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
    typer.secho("Provádím validaci slovníků...", fg=typer.colors.GREEN, bold=True)
    # Validate glossaries after reading data
    validate_glossaries(glossaries_file=settings["glossaries_file"],
                        report_file=settings["validation_report_file"],
                        output_dir=settings["output_dir"])
    typer.secho("Validace slovníků dokončena.", fg=typer.colors.GREEN, bold=True)
    typer.secho("Zpracování dokončeno.", fg=typer.colors.GREEN, bold=True)
    
@app.command()
def show():
    """Show the Streamlit application for browsing glossaries."""
    typer.secho("Spouštím Streamlit aplikaci pro prohlížení slovníků...", fg=typer.colors.BLUE, bold=True)
    # Import here to avoid circular import issues
    subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)

def main():
    app()
    
if __name__ == "__main__":
    main()