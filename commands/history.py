from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from memory import get_history

console = Console()

def show_history():
    results = get_history()

    if not results:
        console.print(Panel(
            "[yellow]No history yet![/yellow]\n\n"
            "Try: [cyan]recall \"how to check running ports\"[/cyan]",
            title="[bold]📜 Recall History[/bold]",
            border_style="yellow"
        ))
        return

    table = Table(
        title="📜 Recall History",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Query", style="white", min_width=30)
    table.add_column("Command", style="green", min_width=25)
    table.add_column("Time", style="dim", min_width=20)

    for i, (query, command, timestamp) in enumerate(results, 1):
        table.add_row(str(i), query, command, timestamp)

    console.print()
    console.print(table)
    console.print()