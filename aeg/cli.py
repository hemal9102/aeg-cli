import typer
from pathlib import Path
import os
from aeg.core.vault import KnowledgeVault

app = typer.Typer(help="Autonomous Engineering & Growth CLI (AEG)")

@app.command()
def init(name: str, type: str = "web_application"):
    """
    Initialize an AEG project in the current directory.
    """
    cwd = os.getcwd()
    vault = KnowledgeVault(cwd)
    vault.init_vault(project_name=name, project_type=type)
    typer.echo(f"Initialized AEG project: {name} in {cwd}/.aeg")

@app.command()
def analyze():
    """
    Analyze the current project architecture (Stub).
    """
    typer.echo("Analyzing project via LSP...")

@app.command()
def loop(task: str):
    """
    Start the MAS execution loop for a specific task.
    """
    cwd = os.getcwd()
    typer.echo(f"Starting execution pipeline for task: {task} in {cwd}")
    
    try:
        from aeg.orchestrator.event_loop import ExecutionLoop
        vault = KnowledgeVault(cwd)
        pipeline = ExecutionLoop(vault, cwd)
        pipeline.start(task)
    except Exception as e:
        typer.echo(f"[ERROR] Pipeline failed: {str(e)}", err=True)

@app.command()
def evidence():
    """
    List all stored evidence.
    """
    typer.echo("Listing verified evidence (Stub)")

if __name__ == "__main__":
    app()
