import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
from memory import save_workflow, get_workflow, get_all_workflows
from commands.error import fix_error

console = Console()

def save_wf(name: str):
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
        console.print("[red]No commands entered.[/red]")
        return

    save_workflow(name, ' && '.join(commands))

    console.print()
    console.print(Panel(
        f"[green]✓ Workflow saved![/green]\n\n"
        f"[dim]Commands:[/dim]\n" +
        "\n".join([f"  {i+1}. {c}" for i, c in enumerate(commands)]) +
        f"\n\n[dim]Run:[/dim] [cyan]recall --run \"{name}\"[/cyan]",
        title=f"[bold green]✓ Workflow: {name}[/bold green]",
        border_style="green"
    ))

def run_wf(name: str):
    result = get_workflow(name)
    if not result:
        console.print(Panel(
            f"[red]Workflow '{name}' not found![/red]\n\n"
            f"Save it: [cyan]recall --save \"{name}\"[/cyan]",
            title="[bold red]✗ Not Found[/bold red]",
            border_style="red"
        ))
        return

    commands = result.split(' && ')
    console.print()
    console.print(Panel(
        f"Running [bold cyan]{len(commands)} steps[/bold cyan]",
        title=f"[bold]⚡ Workflow: {name}[/bold]",
        border_style="cyan"
    ))

    for i, cmd in enumerate(commands, 1):
        console.print(f"\n  [dim]{i}/{len(commands)}[/dim] [cyan]▶[/cyan] {cmd}")
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

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

def list_wf():
    results = get_all_workflows()
    if not results:
        console.print(Panel(
            "[yellow]No workflows saved yet![/yellow]\n\n"
            "Save one: [cyan]recall --save \"name\"[/cyan]",
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