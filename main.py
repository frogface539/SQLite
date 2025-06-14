import sys
import os
from rich.console import Console
from engine.database import DatabaseEngine

def main():
    console = Console()
    db = DatabaseEngine()
    db.test_pager_write_read()

    try:
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            if not os.path.isfile(filepath):
                console.print(f"[red]Error:[/] File '{filepath}' does not exist.")
                return
            with open(filepath, 'r') as f:
                sql_script = f.read()
            statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
            console.print(f"[bold blue]Executing SQL script from {filepath}[/]")
            for i, stmt in enumerate(statements, 1):
                console.print(f"\n[cyan]>> Statement {i}:[/] [white]{stmt}[/]")
                db.execute(stmt + ";")
        else:
            console.print("[bold blue]SQLite-like Database Shell[/]")
            console.print("[yellow]Type 'exit' to quit[/]\n")
            while True:
                try:
                    query = input("SQL> ").strip()
                    if query.lower() in ('exit', 'quit'):
                        break
                    if query:
                        db.execute(query)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Exiting...[/]")
                    break
                except EOFError:
                    break
    finally:
        db.close()

if __name__ == "__main__":
    main()
