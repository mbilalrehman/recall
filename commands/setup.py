import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from auth import save_token
from config import BACKEND_URL

console = Console()

def run_setup():
    console.print()
    console.print(Panel(
        "[bold cyan]Welcome to Recall![/bold cyan]\n\n"
        "Login or create your account.",
        title="[bold]✦ Recall Setup[/bold]",
        border_style="cyan"
    ))
    console.print()

    email = Prompt.ask("  [cyan]Email[/cyan]")
    password = Prompt.ask("  [cyan]Password[/cyan]", password=True)

    try:
        # Pehle login try karo
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": email, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            plan = data.get("plan", "free")
            queries_used = data.get("queries_used", 0)
        else:
            # Login fail — signup karo
            response = requests.post(
                f"{BACKEND_URL}/signup",
                json={"email": email, "password": password}
            )
            data = response.json()
            token = data.get("token")
            plan = "free"
            queries_used = 0

        if not token:
            console.print(Panel(
                f"[red]Error: {data.get('detail', 'Unknown error')}[/red]",
                border_style="red"
            ))
            return

        save_token(token, email)

        limit_text = "Unlimited" if plan == "pro" else f"{queries_used}/50 queries used"
        plan_color = "green" if plan == "pro" else "yellow"

        console.print()
        console.print(Panel(
            f"[green]✓ Logged in![/green]\n\n"
            f"Email:  [cyan]{email}[/cyan]\n"
            f"Plan:   [{plan_color}]{plan.upper()}[/{plan_color}]\n"
            f"Usage:  [dim]{limit_text}[/dim]\n\n"
            "Try: [bold cyan]recall \"how to check ports\"[/bold cyan]",
            title="[bold green]✓ Welcome to Recall![/bold green]",
            border_style="green"
        ))

    except requests.exceptions.ConnectionError:
        console.print(Panel(
            "[red]Cannot connect to Recall server![/red]",
            border_style="red"
        ))