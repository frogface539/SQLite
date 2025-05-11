from rich.table import Table
from rich.console import Console
from rich.tree import Tree
from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from utils.errors import TokenizationError, ParsingError, CodegenError
from compiler.code_generator import CodeGeneration, PlanGenerator

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
    def __init__(self):
        # Initialize with the products table schema
        self.schema_registry = {
            "products": ["product_id", "name", "price", "stock"],
            # Add other initial tables if needed
        }
        self.codegen = CodeGeneration()
        self.planner = PlanGenerator(schema_registry=self.schema_registry)
        self.console = Console()
        
    def execute(self, query):
        tokenizer = Tokenizer()
        
        try:
            # Tokenization
            tokens = tokenizer.tokenize(query)
            
            # Display tokens
            self._display_token_table(tokens)

            # Parsing
            parser = Parser(tokens)
            parsed = parser.parse()
            
            # Update schema if CREATE TABLE
            self._update_schema_if_needed(parsed)

            # Display parse tree
            self._display_parse_tree(parsed)

            # Plan generation and execution
            plan = self._generate_execution_plan(parsed)
            self._display_execution_plan(plan)
            
            return plan
            
        except TokenizationError as e:
            self.console.print(f"[bold red]Tokenization Error:[/] {e}")
        except ParsingError as e:
            self.console.print(f"[bold red]Parsing Error:[/] {e}") 
        except CodegenError as e:
            self.console.print(f"[bold red]Code Generation Error:[/] {e}")
        except Exception as e:
            self.console.print(f"[bold red]Unexpected Error:[/] {e}")
            raise

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
        self.console.print("\n[bold green]Execution Plan:[/]")
        plan_table = Table(show_header=True, show_lines=True)
        plan_table.add_column("Opcode", style="cyan")
        plan_table.add_column("Operands", style="magenta")
        for op in plan:
            plan_table.add_row(str(op[0]), str(op[1:]))
        self.console.print(plan_table)

def main():
    console = Console()
    db = DatabaseEngine()
    
    console.print("[bold blue]SQLite-like Database Shell[/]")
    console.print("[yellow]Initial tables: products[/]")
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

if __name__ == "__main__":
    main()