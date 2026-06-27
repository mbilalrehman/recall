import platform
import requests
from rich.console import Console
from rich.panel import Panel
from auth import get_token
from memory import save_to_memory
from config import BACKEND_URL

console = Console()

def fix_error(error_text: str):
    token = get_token()
    if not token:
        console.print(Panel(
            "[yellow]Please login first![/yellow]\n\n"
            "Run: [bold cyan]recall --setup[/bold cyan]",
            border_style="yellow"
        ))
        return

    with console.status("[cyan]Analyzing error...[/cyan]", spinner="dots"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/fix-error",
                json={"error": error_text, "os_type": platform.system()},
                headers={"Authorization": f"Bearer {token}"}
            )
            data = response.json()
            cause = data.get("cause", "Unknown")
            fix = data.get("fix", "Check manually")
            confidence = data.get("confidence", "Low")
        except Exception:
            cause = "Could not analyze"
            fix = "Check the error manually"
            confidence = "Low"

    conf_color = "green" if confidence == "High" else "yellow" if confidence == "Medium" else "red"
    save_to_memory(f"error: {error_text}", fix)

    console.print()
    console.print(Panel(
        f"[bold red]✗ Error:[/bold red]   {error_text}\n\n"
        f"[yellow]● Cause:[/yellow]     {cause}\n\n"
        f"[green]● Fix:[/green]       [bold cyan]{fix}[/bold cyan]\n\n"
        f"[{conf_color}]● Confidence: {confidence}[/{conf_color}]",
        title="[bold red]⚡ Error Intelligence[/bold red]",
        border_style="red"
    ))
    console.print()