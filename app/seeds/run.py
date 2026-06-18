import typer
from .service import run_users, run_tags, run_categories, run_all

app = typer.Typer(help="Seeds: users,categories,tags")

@app.command("all") # este define un comando para el cmd
def all_():
    run_all()
    typer.echo("Usuarios, tags, categories cargados")


@app.command("users") # este define un comando para el cmd
def users():
    run_users()
    typer.echo("Usuarios cargados")

@app.command("tags") # este define un comando para el cmd
def tags():
    run_tags()
    typer.echo("tags cargados")

@app.command("categories") # este define un comando para el cmd
def categories():
    run_categories()
    typer.echo("categories cargados")