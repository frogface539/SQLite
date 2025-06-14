import sys
import os
from rich.table import Table
from rich.console import Console
from rich.tree import Tree
from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from utils.errors import TokenizationError, ParsingError, CodegenError
from compiler.code_generator import CodeGeneration, PlanGenerator
from core.virtual_machine import VirtualMachine
from backend.os_interface import OSInterface, DEFAULT_PAGE_SIZE
from backend.pager import Pager

def render_tree(data, label="root"):
    tree = Tree(f"[bold]{label}[/bold]")
    if isinstance(data, dict):
        for key, value in data.items():
            subtree = render_tree(value, label=str(key))
            tree.add(subtree)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            subtree = render_tree(item, label=f"[{index}]")
            tree.add(subtree)
    else:
        tree.add(f"[green]{data}[/green]")
    return tree

class DatabaseEngine:
    def __init__(self, db_file="example.db"):
        self.console = Console()

        # Core DB components
        self.schema_registry = {
            "products": ["product_id", "name", "price", "stock"],
        }
        self.codegen = CodeGeneration()
        self.planner = PlanGenerator(schema_registry=self.schema_registry)
        self.vm = VirtualMachine(schema_registry=self.schema_registry)

        self.os = OSInterface(db_file)
        self.os.open_file()
        self.pager = Pager(self.os, cache_size=4)

    def execute(self, query):
        tokenizer = Tokenizer()

        try:
            tokens = tokenizer.tokenize(query)
            self._display_token_table(tokens)

            parser = Parser(tokens, schema_registry=self.schema_registry)
            parsed = parser.parse()
            self._update_schema_if_needed(parsed)

            self._display_parse_tree(parsed)

            plan = self._generate_execution_plan(parsed)
            self._display_execution_plan(plan)

            self.console.print("[bold green]Executing plan...[/]")
            result = self.vm.execute(plan)

            if parsed["type"] == "SELECT" and result:
                self._print_results_table(result)

        except TokenizationError as e:
            self.console.print(f"[bold red]Tokenization Error:[/] {e}")
        except ParsingError as e:
            self.console.print(f"[bold red]Parsing Error:[/] {e}")
        except CodegenError as e:
            self.console.print(f"[bold red]Code Generation Error:[/] {e}")
        except Exception as e:
            self.console.print(f"[bold red]Unexpected Error:[/] {e}")
            raise

    def test_pager_write_read(self):
        try:
            for i in range(5):
                page = self.pager.get_page(i)
                label = f"Page{i}".encode("utf-8")
                page.data = label + b'\x00' * (DEFAULT_PAGE_SIZE - len(label))
                self.pager.mark_dirty(page)
                self.console.print(f"[green]-> Page {i} marked dirty and cached.[/]")
            
            self.pager.flush_all()

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Page Number", style="cyan")
            table.add_column("Content", style="green")

            for i in range(5):
                page = self.pager.get_page(i)
                prefix = page.data[:10].decode("utf-8", errors="ignore").strip("\x00")
                table.add_row(str(i), prefix)

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Pager test failed: {e}[/]")

    def _display_token_table(self, tokens):
        table = Table(title="Token Stream", show_lines=True)
        table.add_column("Type", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_column("Position", style="yellow")
        for token in tokens:
            table.add_row(token.token_type, str(token.value), str(token.position))
        self.console.print(table)

    def _update_schema_if_needed(self, parsed):
        if parsed["type"] == "CREATE":
            table_name = parsed["table_name"]
            columns = [col["name"] for col in parsed["columns"]]
            self.schema_registry[table_name] = columns
            self.console.print(f"[bold yellow]Updated schema with table '{table_name}'[/]")
            self.console.print(f"[yellow]Current schema: {list(self.schema_registry.keys())}[/]")

    def _display_parse_tree(self, parsed):
        self.console.print("\n[bold green]Parsed Result Tree:[/]")
        self.console.print(render_tree(parsed, label="SQL"))

    def _generate_execution_plan(self, parsed):
        command = self.codegen.gen(parsed)
        return self.planner.generate_plan(command)

    def _display_execution_plan(self, plan):
        plan_table = Table(show_header=True, show_lines=True)
        plan_table.add_column("Opcode", style="cyan")
        plan_table.add_column("Operands", style="magenta")

        for op in plan:
            if isinstance(op, str):
                op = (op,)
            opcode = op[0]
            operands = str(op[1:]) if len(op) > 1 else ""
            plan_table.add_row(opcode, operands)

        self.console.print(plan_table)

    def _print_results_table(self, rows):
        if not rows:
            self.console.print("[yellow]No results.[/]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        for col in rows[0].keys():
            table.add_column(col)

        for row in rows:
            table.add_row(*[str(row[col]) for col in row])

        self.console.print(table)

    def close(self):
        try:
            self.console.rule("[cyan]Closing database...[/]")
            self.pager.flush_all()
            self.console.print("[green] All dirty pages flushed.[/]")
        except Exception as e:
            self.console.print(f"[red]Failed to flush pages:[/] {e}")

        try:
            self.os.close_file()
            self.console.print("[green] File handle closed.[/]")
        except Exception as e:
            self.console.print(f"[red]Failed to close file:[/] {e}")
    
    def __del__(self):
        self.close()


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

            for i, stmt in enumerate(statements, start=1):
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
                    if not query:
                        continue
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
