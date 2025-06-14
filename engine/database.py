import sys
from rich.console import Console

from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from compiler.code_generator import CodeGeneration, PlanGenerator
from core.virtual_machine import VirtualMachine
from backend.os_interface import OSInterface, DEFAULT_PAGE_SIZE
from backend.pager import Pager
from utils.errors import TokenizationError, ParsingError, CodegenError
from ui.renderer import (
    print_token_table,
    print_plan_table,
    print_results_table,
    render_tree
)

class DatabaseEngine:
    def __init__(self, db_file="example.db"):
        self.console = Console()
        self.schema_registry = {"products": ["product_id", "name", "price", "stock"]}
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
            print_token_table(tokens)

            parser = Parser(tokens, schema_registry=self.schema_registry)
            parsed = parser.parse()
            self._update_schema_if_needed(parsed)

            self.console.print("\n[bold green]Parsed Result Tree:[/]")
            self.console.print(render_tree(parsed, label="SQL"))

            plan = self._generate_execution_plan(parsed)
            print_plan_table(plan)

            self.console.print("[bold green]Executing plan...[/]")
            result = self.vm.execute(plan)

            if parsed["type"] == "SELECT" and result:
                print_results_table(result)

        except (TokenizationError, ParsingError, CodegenError) as e:
            self.console.print(f"[bold red]{type(e).__name__}:[/] {e}")
        except Exception as e:
            self.console.print(f"[bold red]Unexpected Error:[/] {e}")
            raise

    def _update_schema_if_needed(self, parsed):
        if parsed["type"] == "CREATE":
            table_name = parsed["table_name"]
            columns = [col["name"] for col in parsed["columns"]]
            self.schema_registry[table_name] = columns
            self.console.print(f"[bold yellow]Updated schema with table '{table_name}'[/]")
            self.console.print(f"[yellow]Current schema: {list(self.schema_registry.keys())}[/]")

    def _generate_execution_plan(self, parsed):
        command = self.codegen.gen(parsed)
        return self.planner.generate_plan(command)

    def test_pager_write_read(self):
        from rich.table import Table
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
