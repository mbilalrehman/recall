import platform
import requests
from rich.console import Console
from rich.panel import Panel
from auth import get_token
from memory import save_to_memory, search_memory
from config import BACKEND_URL

console = Console()

def run_query(q: str):
    token = get_token()
    if not token:
        console.print(Panel(
            "[yellow]Please login first![/yellow]\n\n"
            "Run: [bold cyan]recall --setup[/bold cyan]",
            title="[bold]⚡ Setup Required[/bold]",
            border_style="yellow"
        ))
        return

    # Memory check first
    cached = search_memory(q)
    if cached:
        console.print()
        console.print(Panel(
            f"[bold green]{cached}[/bold green]\n\n"
            f"[dim]↳ from memory[/dim]",
            title="[bold]✦ Recall[/bold]",
            border_style="green"
        ))
        console.print()
        return

    # Backend query
    with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": q, "os_type": platform.system()},
                headers={"Authorization": f"Bearer {token}"}
            )
        except requests.exceptions.ConnectionError:
            console.print(Panel(
                "[red]Cannot connect to Recall server![/red]",
                border_style="red"
            ))
            return

    if response.status_code == 401:
        console.print(Panel(
            "[red]Session expired![/red]\n\nRun: [cyan]recall --setup[/cyan]",
            border_style="red"
        ))
        return

    if response.status_code == 403:
        console.print(Panel(
            "[red]Account banned! Contact support.[/red]",
            border_style="red"
        ))
        return

    if response.status_code == 429:
        console.print(Panel(
            "[red]Free limit reached! (50 queries/month)[/red]\n\n"
            "Upgrade: [cyan]recall --upgrade[/cyan]",
            border_style="red"
        ))
        return

    if response.status_code != 200:
        console.print(Panel(
            f"[red]Server error: {response.text}[/red]",
            border_style="red"
        ))
        return

    data = response.json()
    command = data.get("command", "")
    limit = data.get("limit", "")

    if not command:
        console.print(Panel("[red]No command returned.[/red]", border_style="red"))
        return

    save_to_memory(q, command)

    console.print()
    console.print(Panel(
        f"[bold green]{command}[/bold green]\n\n"
        f"[dim]↳ AI generated · {platform.system()} · {limit}[/dim]",
        title="[bold]✦ Recall[/bold]",
        border_style="cyan"
    ))
    console.print()