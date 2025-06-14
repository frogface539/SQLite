from rich.table import Table
from rich.tree import Tree
from rich.console import Console

console = Console()

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

def print_token_table(tokens):
    table = Table(title="Token Stream", show_lines=True)
    table.add_column("Type", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Position", style="yellow")
    for token in tokens:
        table.add_row(token.token_type, str(token.value), str(token.position))
    console.print(table)

def print_plan_table(plan):
    table = Table(show_header=True, show_lines=True)
    table.add_column("Opcode", style="cyan")
    table.add_column("Operands", style="magenta")
    for op in plan:
        if isinstance(op, str):
            op = (op,)
        opcode = op[0]
        operands = str(op[1:]) if len(op) > 1 else ""
        table.add_row(opcode, operands)
    console.print(table)

def print_results_table(rows):
    if not rows:
        console.print("[yellow]No results.[/]")
        return
    table = Table(show_header=True, header_style="bold magenta")
    for col in rows[0].keys():
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(row[col]) for col in row])
    console.print(table)
