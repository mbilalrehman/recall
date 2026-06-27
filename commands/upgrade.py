import webbrowser
import requests
from rich.console import Console
from rich.panel import Panel
from auth import get_token
from config import BACKEND_URL

console = Console()

def run_upgrade():
    token = get_token()
    if not token:
        console.print(Panel(
            "[yellow]Please login first![/yellow]\n\n"
            "Run: [bold cyan]recall --setup[/bold cyan]",
            border_style="yellow"
        ))
        return

    try:
        response = requests.post(
            f"{BACKEND_URL}/create-checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()

        if response.status_code == 400 and "Already Pro" in str(data):
            console.print(Panel(
                "[green]You are already Pro![/green]\n\n"
                "Unlimited queries. No limits.",
                title="[bold green]✦ PRO MEMBER[/bold green]",
                border_style="green"
            ))
            return

        url = data.get("checkout_url")
        if url:
            console.print(Panel(
                f"[green]Opening checkout in browser...[/green]\n\n"
                f"[dim]Or open manually:[/dim]\n[cyan]{url}[/cyan]",
                title="[bold]💳 Upgrade to Pro — $12/month[/bold]",
                border_style="cyan"
            ))
            webbrowser.open(url)
        else:
            console.print(Panel(
                f"[red]Error: {data.get('detail', 'Unknown error')}[/red]",
                border_style="red"
            ))

    except requests.exceptions.ConnectionError:
        console.print(Panel("[red]Cannot connect to server![/red]", border_style="red"))
    except Exception as e:
        console.print(Panel(f"[red]Error: {e}[/red]", border_style="red"))