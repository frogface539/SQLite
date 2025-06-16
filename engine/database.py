import sys
from struct import unpack
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.console import Console
from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from compiler.code_generator import CodeGeneration, PlanGenerator
from core.virtual_machine import VirtualMachine
from backend.os_interface import OSInterface, DEFAULT_PAGE_SIZE
from backend.pager import Pager
from backend.b_tree import BTree, BTreeNode
from utils.errors import (
    TokenizationError, ParsingError, CodegenError, ExecutionError, BTreeError
)
from ui.renderer import (
    print_token_table, print_plan_table, print_results_table, render_tree
)

class DatabaseEngine:
    def __init__(self, db_file="example.db"):
        self.console = Console()
        self.os = OSInterface(db_file)
        self.os.open_file()
        self.pager = Pager(self.os, cache_size=4)
        self.btree = BTree(self.pager) 
        self.schema_registry = {
            "products": ["product_id", "name", "price", "stock"]
        }
        self.codegen = CodeGeneration()
        self.planner = PlanGenerator(schema_registry=self.schema_registry)
        self.vm = VirtualMachine(schema_registry=self.schema_registry)

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
            
            if query.strip().upper().startswith("INSERT_BTEST"):
                parts = query.strip().split()
                for num in parts[1:]:
                    self.btree.insert(int(num))
                self.console.print(f"[green]Inserted into BTree: {self.btree.root.keys}[/]")
                return

        except (TokenizationError, ParsingError, CodegenError, ExecutionError) as e:
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

    def inspect_pager(self):
        console = Console()
        console.rule("[bold cyan]Testing Pager Cache Contents[/]")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Page Number", style="cyan")
        table.add_column("Content (Prefix)", style="green")

        try:
            max_page = max(self.pager.cache.keys() or [0])
        except Exception:
            max_page = 0

        for page_num in range(max_page + 1):
            try:
                page = self.pager.get_page(page_num)
                prefix = page.data[:20].decode("utf-8", errors="ignore").strip("\x00")

                if prefix:
                    table.add_row(str(page_num), prefix)
            except Exception as e:
                console.print(f"[red]Error reading page {page_num}:[/] {e}")

        console.print(table)


    def test_btree_paging(self):
        self.console.rule("[bold cyan]Testing B-Tree Paging")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Page Number", style="cyan")
        table.add_column("Node Type", style="green")
        table.add_column("Key Count", style="yellow")
        table.add_column("Keys", style="magenta")

        for page_num in range(self.pager.num_pages):
            try:
                page = self.pager.get_page(page_num)
                node = BTreeNode.deserialize(page.data)
                table.add_row(str(page_num),
                            "Leaf" if node.is_leaf else "Internal",
                            str(len(node.keys)),
                            ", ".join(map(str, node.keys)))
            except Exception:
                table.add_row(str(page_num), "-", "-", "-")

        self.console.print(table)
        self.console.print("[green]✓ B-tree paging test complete.[/]")


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
