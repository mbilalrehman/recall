import click
import sqlite3
import os
import subprocess
import platform
import requests
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm

console = Console()
BACKEND_URL = "http://100.53.1.66:8000"

# ══════════════════════════════════════
# TOKEN HELPERS
# ══════════════════════════════════════

def get_token():
    config_path = os.path.expanduser("~/.recall/config")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith("TOKEN="):
                    return line.strip().split("=", 1)[1]
    return None

def require_login():
    token = get_token()
    if not token:
        console.print()
        console.print(Panel(
            "[yellow]Not logged in![/yellow]\n\n"
            "Run: [bold cyan]recall --setup[/bold cyan]",
            title="[bold]⚡ Login Required[/bold]",
            border_style="yellow"
        ))
        exit(1)
    return token

# ══════════════════════════════════════
# LOCAL MEMORY
# ══════════════════════════════════════

def get_db_path():
    db_dir = os.path.expanduser("~/.recall")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "memory.db")

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.execute('''CREATE TABLE IF NOT EXISTS memory
                 (query TEXT, command TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS workflows
                 (name TEXT UNIQUE, commands TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

def save_to_memory(query, command):
    conn = get_connection()
    conn.execute(
        "INSERT INTO memory VALUES (?, ?, datetime('now'))",
        (query, command)
    )
    conn.commit()
    conn.close()

def search_memory(query):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT command FROM memory WHERE query LIKE ? ORDER BY timestamp DESC LIMIT 1",
        (f'%{query}%',)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_recent_history(limit=10):
    conn = get_connection()
    cursor = conn.execute(
        "SELECT query, command, timestamp FROM memory ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

# ══════════════════════════════════════
# SETUP
# ══════════════════════════════════════

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

        # Token save karo
        config_dir = os.path.expanduser("~/.recall")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config")
        with open(config_path, 'w') as f:
            f.write(f"TOKEN={token}\n")
            f.write(f"EMAIL={email}\n")

        limit_text = "Unlimited" if plan == "pro" else f"{queries_used}/50 queries used"

        console.print()
        console.print(Panel(
            f"[green]✓ Logged in![/green]\n\n"
            f"Email:  [cyan]{email}[/cyan]\n"
            f"Plan:   [{'green' if plan == 'pro' else 'yellow'}]{plan.upper()}[/{'green' if plan == 'pro' else 'yellow'}]\n"
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

# ══════════════════════════════════════
# FEATURE 1 — HISTORY
# ══════════════════════════════════════

def show_history():
    require_login()
    results = get_recent_history()

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

# ══════════════════════════════════════
# FEATURE 2 — ERROR INTELLIGENCE
# ══════════════════════════════════════

def fix_error(error_text):
    token = get_token()
    if not token:
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
        except:
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

# ══════════════════════════════════════
# FEATURE 3 — WORKFLOW SAVE
# ══════════════════════════════════════

def save_workflow(name):
    require_login()
    console.print()
    console.print(Panel(
        f"Saving workflow: [bold cyan]{name}[/bold cyan]\n"
        f"Type commands one by one.\n"
        f"Type [bold]done[/bold] when finished.",
        title="[bold]⚡ Save Workflow[/bold]",
        border_style="cyan"
    ))

    commands = []
    while True:
        cmd = Prompt.ask(f"  [cyan]Command {len(commands)+1}[/cyan]")
        if cmd.lower() == 'done':
            break
        if cmd.strip():
            commands.append(cmd.strip())

    if not commands:
        console.print("[red]No commands entered. Workflow not saved.[/red]")
        return

    workflow = ' && '.join(commands)
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO workflows VALUES (?, ?, datetime('now'))",
        (name, workflow)
    )
    conn.commit()
    conn.close()

    console.print()
    console.print(Panel(
        f"[green]✓ Workflow saved![/green]\n\n"
        f"[dim]Commands:[/dim]\n" +
        "\n".join([f"  {i+1}. {c}" for i, c in enumerate(commands)]) +
        f"\n\n[dim]Run it:[/dim] [cyan]recall --run \"{name}\"[/cyan]",
        title=f"[bold green]✓ Workflow: {name}[/bold green]",
        border_style="green"
    ))

# ══════════════════════════════════════
# FEATURE 4 — WORKFLOW RUN
# ══════════════════════════════════════

def run_workflow(name):
    require_login()
    conn = get_connection()
    cursor = conn.execute(
        "SELECT commands FROM workflows WHERE name=?", (name,)
    )
    result = cursor.fetchone()
    conn.close()

    if not result:
        console.print(Panel(
            f"[red]Workflow '{name}' not found![/red]\n\n"
            f"[dim]Save it:[/dim] [cyan]recall --save \"{name}\"[/cyan]",
            title="[bold red]✗ Not Found[/bold red]",
            border_style="red"
        ))
        return

    commands = result[0].split(' && ')

    console.print()
    console.print(Panel(
        f"Running [bold cyan]{len(commands)} steps[/bold cyan]",
        title=f"[bold]⚡ Workflow: {name}[/bold]",
        border_style="cyan"
    ))

    for i, cmd in enumerate(commands, 1):
        console.print(f"\n  [dim]{i}/{len(commands)}[/dim] [cyan]▶[/cyan] {cmd}")

        proc = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True
        )

        if proc.returncode == 0:
            console.print(f"  [green]✓ Done[/green]")
            if proc.stdout.strip():
                console.print(f"  [dim]{proc.stdout.strip()[:200]}[/dim]")
        else:
            console.print(f"  [red]✗ Failed[/red]")
            if proc.stderr.strip():
                fix_error(proc.stderr.strip())
            if not Confirm.ask("  Continue workflow?"):
                console.print("\n  [yellow]⚠ Workflow stopped.[/yellow]\n")
                return

    console.print()
    console.print(Panel(
        "[green]All steps completed successfully![/green]",
        title="[bold green]✓ Workflow Complete[/bold green]",
        border_style="green"
    ))

# ══════════════════════════════════════
# FEATURE 5 — LIST WORKFLOWS
# ══════════════════════════════════════

def list_workflows():
    require_login()
    conn = get_connection()
    cursor = conn.execute(
        "SELECT name, commands, timestamp FROM workflows ORDER BY timestamp DESC"
    )
    results = cursor.fetchall()
    conn.close()

    if not results:
        console.print(Panel(
            "[yellow]No workflows saved yet![/yellow]\n\n"
            "Save one: [cyan]recall --save \"workflow-name\"[/cyan]",
            title="[bold]⚡ Saved Workflows[/bold]",
            border_style="yellow"
        ))
        return

    table = Table(
        title="⚡ Saved Workflows",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="bold white", min_width=20)
    table.add_column("Steps", style="cyan", width=6)
    table.add_column("Commands", style="dim", min_width=30)
    table.add_column("Saved", style="dim", min_width=20)

    for i, (name, commands, timestamp) in enumerate(results, 1):
        cmds = commands.split(' && ')
        table.add_row(
            str(i), name, str(len(cmds)),
            " → ".join(cmds[:2]) + (" → ..." if len(cmds) > 2 else ""),
            timestamp
        )

    console.print()
    console.print(table)
    console.print()

# ══════════════════════════════════════
# MAIN
# ══════════════════════════════════════

@click.command()
@click.option('--setup', 'do_setup', is_flag=True, help='Setup Recall')
@click.option('--history', is_flag=True, help='Show past queries')
@click.option('--error', default=None, help='Fix an error')
@click.option('--save', default=None, help='Save a workflow')
@click.option('--run', default=None, help='Run a workflow')
@click.option('--list-workflows', 'list_wf', is_flag=True, help='List saved workflows')
@click.option('--upgrade', is_flag=True, help='Upgrade to Pro')
@click.argument('query', nargs=-1)
def recall(do_setup, history, error, save, run, list_wf, upgrade, query):

    if not any([query, do_setup, history, error, save, run, list_wf, upgrade]):
        console.print()
        console.print(Panel(
            "[bold cyan]✦ RECALL — Your AI Terminal Brain[/bold cyan]\n\n"
            "[white]recall \"your question\"[/white]         [dim]→ Natural language to command[/dim]\n"
            "[white]recall --history[/white]               [dim]→ See past queries[/dim]\n"
            "[white]recall --error \"error text\"[/white]   [dim]→ Fix any error[/dim]\n"
            "[white]recall --save \"name\"[/white]          [dim]→ Save a workflow[/dim]\n"
            "[white]recall --run \"name\"[/white]           [dim]→ Run a workflow[/dim]\n"
            "[white]recall --list-workflows[/white]        [dim]→ List all workflows[/dim]\n"
            "[white]recall --upgrade[/white]               [dim]→ Upgrade to Pro ($12/mo)[/dim]\n"
            "[white]recall --setup[/white]                 [dim]→ Setup your account[/dim]",
            title="[bold]⚡ Recall Help[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))
        console.print()
        return

    if do_setup:
        run_setup()
        return

    if history:
        show_history()
        return

    if error:
        fix_error(error)
        return

    if save:
        save_workflow(save)
        return

    if run:
        run_workflow(run)
        return

    if list_wf:
        list_workflows()
        return

    if upgrade:
        token = require_login()
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
        return

    # Login check
    token = get_token()
    if not token:
        console.print()
        console.print(Panel(
            "[yellow]Welcome to Recall![/yellow]\n\n"
            "Please setup first:\n"
            "[bold cyan]recall --setup[/bold cyan]",
            title="[bold]⚡ Setup Required[/bold]",
            border_style="yellow"
        ))
        return

    # Natural language query
    q = ' '.join(query)

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
            console.print(Panel("[red]Cannot connect to Recall server![/red]", border_style="red"))
            return

    if response.status_code == 401:
        console.print(Panel(
            "[red]Session expired![/red]\n\nRun: [cyan]recall --setup[/cyan]",
            border_style="red"
        ))
        return

    if response.status_code == 403:
        console.print(Panel(
            "[red]Account banned![/red]\n\nContact support.",
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


if __name__ == '__main__':
    recall()