from rich.table import Table
from rich.console import Console
from rich.tree import Tree

from compiler.tokenizer import Tokenizer
from compiler.parser import Parser
from utils.errors import TokenizationError, ParsingError
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


def main():
    console = Console()
    tokenizer = Tokenizer()

    query = input("Enter SQL query: ")
    console.print(f"\n[bold green]Parsing Query:[/bold green] {query}\n")

    try:
        # Tokenize
        tokens = tokenizer.tokenize(query)

        # Display Token Table
        table = Table(title="Token Stream", show_lines=True)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        table.add_column("Position", style="yellow")

        for token in tokens:
            table.add_row(token.token_type, str(token.value), str(token.position))

        console.print(table)

        # Parse
        parser = Parser(tokens)
        parsed_result = parser.parse()

        # Display Parse Tree
        console.print("\n[bold green]Parsed Result Tree:[/bold green]")
        tree = render_tree(parsed_result, label="SQL")
        console.print(tree)

        # Code Generation
        command = CodeGeneration().gen(parsed_result)
        plan = PlanGenerator().generate_plan(command)

        console.print("\n[bold green]Execution Plan:[/bold green]")
        console.print(plan)

    except TokenizationError as e:
        console.print(f"[bold red]Tokenization Error:[/bold red] {e}")
    except ParsingError as e:
        console.print(f"[bold red]Parsing Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
