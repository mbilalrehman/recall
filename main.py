import click
from rich.console import Console
from rich.panel import Panel

from commands.setup import run_setup
from commands.query import run_query
from commands.history import show_history
from commands.error import fix_error
from commands.workflow import save_wf, run_wf, list_wf
from commands.upgrade import run_upgrade
from auth import get_token

console = Console()

@click.command()
@click.option('--setup', 'do_setup', is_flag=True, help='Setup your account')
@click.option('--history', 'do_history', is_flag=True, help='Show past queries')
@click.option('--error', 'error_text', default=None, help='Fix an error')
@click.option('--save', 'save_name', default=None, help='Save a workflow')
@click.option('--run', 'run_name', default=None, help='Run a workflow')
@click.option('--list-workflows', 'do_list', is_flag=True, help='List all workflows')
@click.option('--upgrade', 'do_upgrade', is_flag=True, help='Upgrade to Pro')
@click.argument('query', nargs=-1)
def recall(do_setup, do_history, error_text, save_name, run_name, do_list, do_upgrade, query):

    if not any([query, do_setup, do_history, error_text, save_name, run_name, do_list, do_upgrade]):
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

    if do_history:
        show_history()
        return

    if error_text:
        fix_error(error_text)
        return

    if save_name:
        save_wf(save_name)
        return

    if run_name:
        run_wf(run_name)
        return

    if do_list:
        list_wf()
        return

    if do_upgrade:
        run_upgrade()
        return

    if not get_token():
        console.print()
        console.print(Panel(
            "[yellow]Welcome to Recall![/yellow]\n\n"
            "Please setup first:\n"
            "[bold cyan]recall --setup[/bold cyan]",
            title="[bold]⚡ Setup Required[/bold]",
            border_style="yellow"
        ))
        return

    run_query(' '.join(query))


if __name__ == '__main__':
    recall()