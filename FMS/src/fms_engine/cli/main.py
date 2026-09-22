import typer
from rich.console import Console

app = typer.Typer(
    name="fms",
    help="Fyodor Macro Signal (FMS) quantitative workbench and research CLI.",
    add_completion=False,
)
console = Console()

@app.command()
def status():
    """Check FMS engine environment status."""
    console.print("[bold green]Fyodor Macro Signal (FMS) Engine v0.1.0[/bold green]")
    console.print("Status: [cyan]Operational[/cyan]")

@app.command()
def backtest(
    event: str = typer.Option("US Non-Farm Payrolls", "--event", "-e", help="Macro event name to backtest"),
    symbol: str = typer.Option("EURUSD", "--symbol", "-s", help="Target currency pair"),
    timeframe: str = typer.Option("H4", "--timeframe", "-t", help="Analysis timeframe (H1, H4, D1)"),
    horizon: int = typer.Option(60, "--horizon", "-h", help="Max candle holding horizon"),
):
    """Execute quantitative backtest on specified event family and symbol."""
    console.print(f"[bold cyan]Running FMS Backtest:[/bold cyan] Event: [yellow]{event}[/yellow] | Symbol: [green]{symbol}[/green] | TF: [magenta]{timeframe}[/magenta] | Horizon: [blue]{horizon} bars[/blue]")
    console.print("[dim]Analyzing historical MFE / MAE distributions...[/dim]")

if __name__ == "__main__":
    app()
