import sys
import time
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ..config import settings
from ..contracts.setup_models import SetupDirection, QuantMethod, RegisteredSetupDTO
from ..ingestion.candle_loader import CandleLoader
from ..ingestion.calendar_loader import CalendarLoader
from ..ingestion.sync_mt5 import sync_mt5_candles
from ..analytics.surprise_engine import SurpriseEngine
from ..analytics.excursion_engine import ExcursionEngine
from ..analytics.zone_detector import ZoneDetector
from ..analytics.macro_divergence_engine import MacroDivergenceEngine, PAIR_MAPPINGS
from ..analytics.policy_spread_engine import PolicySpreadEngine
from ..analytics.terms_of_trade_engine import TermsOfTradeEngine
from ..analytics.carry_unwind_engine import CarryUnwindEngine
from ..analytics.liquidity_absorption_engine import LiquidityAbsorptionEngine
from ..strategy.setup_registry import SetupRegistry


app = typer.Typer(
    name="fms",
    help="Fyodor Macro Signal (FMS) quantitative research workbench & backtesting CLI.",
    add_completion=False,
)
console = Console()

@app.command()
def status():
    """Inspect FMS local data caches, database records, and engine health."""
    settings.ensure_directories()
    candle_loader = CandleLoader()
    calendar_loader = CalendarLoader()

    cal_df = calendar_loader.load_cached_calendar()
    cal_count = len(cal_df) if cal_df is not None else 0

    console.print(Panel.fit(
        "[bold green]Fyodor Macro Signal (FMS) Engine v0.1.0[/bold green]\n"
        "[dim]Isolated Quantitative Research & Signal Engine[/dim]",
        border_style="green",
    ))

    # Data Cache Table
    cache_table = Table(title="Local Parquet Caches (fms/data/cache)")
    cache_table.add_column("Symbol", style="cyan")
    cache_table.add_column("Timeframe", style="magenta")
    cache_table.add_column("Cached Bars", justify="right", style="green")
    cache_table.add_column("Status", style="yellow")

    total_bars = 0
    for sym in settings.major_forex_extended:
        df = candle_loader.load_cached_candles(sym, "H4")
        if df is not None and not df.is_empty():
            count = len(df)
            total_bars += count
            cache_table.add_row(sym, "H4", str(count), "[green]Ready[/green]")
        else:
            cache_table.add_row(sym, "H4", "0", "[red]Missing (run fms sync)[/red]")

    console.print(cache_table)
    console.print(f"Total Cached H4 Bars: [bold green]{total_bars:,}[/bold green]")
    console.print(f"Cached Calendar Releases: [bold green]{cal_count:,}[/bold green]")

    # SQLite Store Table
    registry = SetupRegistry()
    active_setups = registry.get_active_setups()
    console.print(f"Registered Setups in SQLite: [bold cyan]{len(active_setups)}[/bold cyan]")

@app.command()
def sync(
    count: int = typer.Option(5000, "--count", "-c", help="Number of H4 bars to fetch per symbol"),
):
    """Synchronize institutional tick history from MT5 for all Major Forex Extended pairs."""
    console.print(f"[bold cyan]Syncing up to {count} H4 candles per pair from MT5...[/bold cyan]")
    with console.status("[bold green]Pulling tick data from MT5 environment...[/bold green]"):
        try:
            results = sync_mt5_candles(timeframe="H4", count=count)
        except Exception as e:
            console.print(f"[bold red]Sync error:[/bold red] {e}")
            raise typer.Exit(1)

    table = Table(title="Sync Results (Major Forex Extended)")
    table.add_column("Symbol", style="cyan")
    table.add_column("Bars Cached", justify="right", style="green")

    for sym, num_bars in results.items():
        table.add_row(sym, f"{num_bars:,}")

    console.print(table)
    console.print("[bold green]Sync completed successfully![/bold green]")

@app.command()
def research(
    method: str = typer.Option("msd", "--method", "-m", help="Quant method: msd, pys, tot, vrc, lar"),
    min_spread: float = typer.Option(1.75, "--min-spread", "-s", help="Minimum divergence spread Z-score"),
    lookback: int = typer.Option(14, "--lookback", "-l", help="Rolling sentiment lookback window in days"),
    half_life: float = typer.Option(5.0, "--half-life", "-h", help="Exponential decay half-life in days"),
    horizon: int = typer.Option(24, "--horizon", help="Holding horizon in H4 bars (default: 24 bars ~4 days)"),
    zones: bool = typer.Option(True, "--zones/--no-zones", help="Apply Support & Resistance Zone Confluence filter"),
    symbol: Optional[str] = typer.Option(None, "--symbol", help="Target pair (runs all 12 pairs if omitted)"),
    register: bool = typer.Option(False, "--register", "-r", help="Persist passing setups to SQLite registry"),
):
    """
    Run empirical research cruncher on Major Forex Extended across historical market data.
    Supports:
      - msd: Method 1 [M-MSD] Macro Surprise Divergence
      - pys: Method 2 [M-PYS] Policy & Real Yield Spread Momentum
      - tot: Method 3 [M-TOT] Terms-of-Trade & Commodity Pulse
      - vrc: Method 4 [M-VRC] Volatility Regime & Carry Unwind
      - lar: Method 5 [M-LAR] Liquidity Absorption & Sovereign Intervention Rejection
    """
    valid_methods = ["msd", "pys", "tot", "vrc", "lar"]
    if method.lower() not in valid_methods:
        console.print(f"[bold red]Error:[/bold red] Quant method '{method}' not recognized. Supported: {', '.join(valid_methods)}.")
        raise typer.Exit(1)

    candle_loader = CandleLoader()
    calendar_loader = CalendarLoader()
    cal_df = calendar_loader.load_cached_calendar()
    if cal_df.is_empty():
        console.print("[bold red]Error: No calendar events found in cache.[/bold red]")
        raise typer.Exit(1)

    zone_status = "[bold green]ENABLED[/bold green]" if zones else "[dim yellow]DISABLED[/dim yellow]"

    if method.lower() == "pys":
        console.print(Panel.fit(
            f"[bold cyan]Method 2: [M-PYS] Policy & Real Yield Spread Momentum Research Cruncher[/bold cyan]\n"
            f"  * Real Yield Advantage: [yellow]|Delta r_real| >= 1.00% (100 bps)[/yellow]\n"
            f"  * Policy Momentum Window: [magenta]90 days (~1 quarter)[/magenta]\n"
            f"  * Excursion Horizon: [blue]{horizon} H4 bars (~{horizon*4/24:.1f} trading days)[/blue]\n"
            f"  * S&R Zone Confluence: {zone_status}\n"
            f"  * Quality Gate: Respect Rate >= [green]50%[/green] | Net R > [green]0.0R[/green] | R:R >= [green]1.00[/green]",
            border_style="cyan",
        ))

        policy_engine = PolicySpreadEngine(min_real_spread_bps=100.0)
        excursion_engine = ExcursionEngine(max_bars=horizon)
        zone_detector = ZoneDetector(k_window=5, atr_period=14) if zones else None
        registry = SetupRegistry()

        target_symbols = [symbol.upper()] if symbol else settings.major_forex_extended
        results_table = Table(title="[M-PYS] Policy & Real Yield Spread Momentum — Decadal Audit")
        results_table.add_column("Symbol", style="bold cyan")
        results_table.add_column("Dir", style="white")
        results_table.add_column("Trig (N)", justify="right")
        results_table.add_column("W/L", justify="center")
        results_table.add_column("Respect %", justify="right")
        results_table.add_column("TP / SL (pips)", justify="center")
        results_table.add_column("SL ATR", justify="right")
        results_table.add_column("R:R", justify="right")
        results_table.add_column("Net R", justify="right")
        results_table.add_column("EV / trade", justify="right")
        results_table.add_column("Avg Hold", justify="right")
        results_table.add_column("Edge Status", justify="center")

        passing_count = 0
        registered_count = 0

        with console.status("[bold green]Calculating policy spreads, real yields, and forward paths...[/bold green]"):
            for sym in target_symbols:
                if sym not in PAIR_MAPPINGS:
                    continue
                candles = candle_loader.load_cached_candles(sym, "H4")
                if candles is None or candles.is_empty():
                    continue

                for dir_enum in [SetupDirection.BUY, SetupDirection.SELL]:
                    res = policy_engine.backtest_pair_direction(
                        symbol=sym,
                        direction=dir_enum,
                        calendar_df=cal_df,
                        candles_df=candles,
                        excursion_engine=excursion_engine,
                        zone_detector=zone_detector,
                        k_sl=2.0,
                        reward_risk_ratio=1.25,
                    )
                    if res is None:
                        continue

                    is_pass = res.valid_edge
                    if is_pass:
                        passing_count += 1
                        status_str = "[bold green]PASS[/bold green]"
                    else:
                        status_str = "[dim red]FAIL[/dim red]"

                    dir_color = "green" if dir_enum == SetupDirection.BUY else "red"
                    wl_str = f"[green]{res.win_count}[/green]/[red]{res.loss_count}[/red]"
                    tp_sl_str = f"{res.recommended_tp_pips:.0f} / {res.recommended_sl_pips:.0f}"
                    net_r_color = "green" if res.net_realized_r > 0 else "red"

                    results_table.add_row(
                        sym,
                        f"[{dir_color}]{dir_enum.value}[/{dir_color}]",
                        str(res.trigger_count),
                        wl_str,
                        f"{res.respect_rate*100:.0f}%",
                        tp_sl_str,
                        f"{res.k_sl:.1f}x",
                        f"{res.reward_risk_ratio:.2f}",
                        f"[{net_r_color}]{res.net_realized_r:+.1f}R[/{net_r_color}]",
                        f"[{net_r_color}]{res.expected_r_per_trade:+.2f}R[/{net_r_color}]",
                        f"{res.avg_holding_bars:.1f} b",
                        status_str,
                    )

                    if register and is_pass:
                        setup_dto = RegisteredSetupDTO(
                            id=f"PYS_{sym}_{dir_enum.value}",
                            quant_method=QuantMethod.PYS,
                            event_name=f"Policy Real Yield Spread (+1.0% diff)",
                            currency=res.base_currency,
                            symbol=sym,
                            direction=dir_enum,
                            timeframe="H4",
                            respect_rate=res.respect_rate,
                            sample_count=res.trigger_count,
                            median_mfe_pips=res.median_mfe_pips,
                            mae_85_pips=res.mae_85_pips,
                            recommended_sl_pips=res.recommended_sl_pips,
                            recommended_tp_pips=res.recommended_tp_pips,
                            reward_risk_ratio=res.reward_risk_ratio,
                            trigger_state=f"real_yield_spread (SL={res.k_sl:.1f}xATR)",
                            min_z_score=1.00,
                            active=True,
                            created_at=int(time.time()),
                        )
                        registry.save_setup(setup_dto)
                        registered_count += 1

        console.print(results_table)
        console.print(f"\n[bold]Total Combinations Analyzed:[/bold] {len(target_symbols) * 2} | [bold green]Passing Statistical Edge:[/bold green] {passing_count}")
        if register:
            console.print(f"[bold green]Successfully saved {registered_count} passing setups to SQLite registry![/bold green]")
        return

    if method.lower() == "tot":
        console.print(Panel.fit(
            f"[bold cyan]Method 3: [M-TOT] Terms-of-Trade & Commodity Pulse Research Cruncher[/bold cyan]\n"
            f"  * Commodity Pulse Advantage: [yellow]|Delta S_tot| >= 1.00 sigma[/yellow]\n"
            f"  * Excursion Horizon: [blue]{horizon} H4 bars (~{horizon*4/24:.1f} trading days)[/blue]\n"
            f"  * S&R Zone Confluence: {zone_status}\n"
            f"  * Quality Gate: Respect Rate >= [green]50%[/green] | Net R > [green]0.0R[/green] | R:R >= [green]1.00[/green]",
            border_style="cyan",
        ))

        tot_engine = TermsOfTradeEngine(min_pulse_threshold=1.00)
        excursion_engine = ExcursionEngine(max_bars=horizon)
        zone_detector = ZoneDetector(k_window=5, atr_period=14) if zones else None
        registry = SetupRegistry()

        target_symbols = [symbol.upper()] if symbol else settings.major_forex_extended
        results_table = Table(title="[M-TOT] Terms-of-Trade Commodity Pulse — Decadal Audit")
        results_table.add_column("Symbol", style="bold cyan")
        results_table.add_column("Dir", style="white")
        results_table.add_column("Trig (N)", justify="right")
        results_table.add_column("W/L", justify="center")
        results_table.add_column("Respect %", justify="right")
        results_table.add_column("TP / SL (pips)", justify="center")
        results_table.add_column("SL ATR", justify="right")
        results_table.add_column("R:R", justify="right")
        results_table.add_column("Net R", justify="right")
        results_table.add_column("EV / trade", justify="right")
        results_table.add_column("Avg Hold", justify="right")
        results_table.add_column("Edge Status", justify="center")

        passing_count = 0
        registered_count = 0

        with console.status("[bold green]Calculating Terms-of-Trade divergence and forward paths...[/bold green]"):
            for sym in target_symbols:
                candles = candle_loader.load_cached_candles(sym, "H4")
                if candles is None or candles.is_empty():
                    continue

                for dir_enum in [SetupDirection.BUY, SetupDirection.SELL]:
                    res = tot_engine.backtest_pair_direction(
                        symbol=sym,
                        direction=dir_enum,
                        candles_df=candles,
                        excursion_engine=excursion_engine,
                        zone_detector=zone_detector,
                        k_sl=2.0,
                        reward_risk_ratio=1.00,
                    )
                    if res is None:
                        continue

                    is_pass = res.valid_edge
                    if is_pass:
                        passing_count += 1
                        status_str = "[bold green]PASS[/bold green]"
                    else:
                        status_str = "[dim red]FAIL[/dim red]"

                    dir_color = "green" if dir_enum == SetupDirection.BUY else "red"
                    wl_str = f"[green]{res.win_count}[/green]/[red]{res.loss_count}[/red]"
                    tp_sl_str = f"{res.recommended_tp_pips:.0f} / {res.recommended_sl_pips:.0f}"
                    net_r_color = "green" if res.net_realized_r > 0 else "red"

                    results_table.add_row(
                        sym,
                        f"[{dir_color}]{dir_enum.value}[/{dir_color}]",
                        str(res.trigger_count),
                        wl_str,
                        f"{res.respect_rate*100:.0f}%",
                        tp_sl_str,
                        f"{res.k_sl:.1f}x",
                        f"{res.reward_risk_ratio:.2f}",
                        f"[{net_r_color}]{res.net_realized_r:+.1f}R[/{net_r_color}]",
                        f"[{net_r_color}]{res.expected_r_per_trade:+.2f}R[/{net_r_color}]",
                        f"{res.avg_holding_bars:.1f} b",
                        status_str,
                    )

                    if register and is_pass:
                        setup_dto = RegisteredSetupDTO(
                            id=f"TOT_{sym}_{dir_enum.value}",
                            quant_method=QuantMethod.TOT,
                            event_name="Terms of Trade Commodity Pulse",
                            currency=res.base_currency,
                            symbol=sym,
                            direction=dir_enum,
                            timeframe="H4",
                            respect_rate=res.respect_rate,
                            sample_count=res.trigger_count,
                            median_mfe_pips=res.median_mfe_pips,
                            mae_85_pips=res.mae_85_pips,
                            recommended_sl_pips=res.recommended_sl_pips,
                            recommended_tp_pips=res.recommended_tp_pips,
                            reward_risk_ratio=res.reward_risk_ratio,
                            trigger_state=f"tot_pulse (SL={res.k_sl:.1f}xATR)",
                            min_z_score=1.00,
                            active=True,
                            created_at=int(time.time()),
                        )
                        registry.save_setup(setup_dto)
                        registered_count += 1

        console.print(results_table)
        console.print(f"\n[bold]Total Combinations Analyzed:[/bold] {len(target_symbols) * 2} | [bold green]Passing Statistical Edge:[/bold green] {passing_count}")
        if register:
            console.print(f"[bold green]Successfully saved {registered_count} passing setups to SQLite registry![/bold green]")
        return

    if method.lower() == "vrc":
        console.print(Panel.fit(
            f"[bold cyan]Method 4: [M-VRC] Volatility Regime & Carry Unwind Research Cruncher[/bold cyan]\n"
            f"  * Volatility Expansion Shock: [yellow]Z_vol >= 1.50 sigma[/yellow]\n"
            f"  * Excursion Horizon: [blue]{horizon} H4 bars (~{horizon*4/24:.1f} trading days)[/blue]\n"
            f"  * S&R Zone Confluence: {zone_status}\n"
            f"  * Quality Gate: Respect Rate >= [green]50%[/green] | Net R > [green]0.0R[/green] | R:R >= [green]1.00[/green]",
            border_style="cyan",
        ))

        carry_engine = CarryUnwindEngine(min_vol_z=1.50)
        excursion_engine = ExcursionEngine(max_bars=horizon)
        zone_detector = ZoneDetector(k_window=5, atr_period=14) if zones else None
        registry = SetupRegistry()

        target_symbols = [symbol.upper()] if symbol else settings.major_forex_extended
        results_table = Table(title="[M-VRC] Volatility Regime & Carry Unwind — Decadal Audit")
        results_table.add_column("Symbol", style="bold cyan")
        results_table.add_column("Dir", style="white")
        results_table.add_column("Trig (N)", justify="right")
        results_table.add_column("W/L", justify="center")
        results_table.add_column("Respect %", justify="right")
        results_table.add_column("TP / SL (pips)", justify="center")
        results_table.add_column("SL ATR", justify="right")
        results_table.add_column("R:R", justify="right")
        results_table.add_column("Net R", justify="right")
        results_table.add_column("EV / trade", justify="right")
        results_table.add_column("Avg Hold", justify="right")
        results_table.add_column("Edge Status", justify="center")

        passing_count = 0
        registered_count = 0

        with console.status("[bold green]Detecting volatility regime expansions and carry cascades...[/bold green]"):
            for sym in target_symbols:
                candles = candle_loader.load_cached_candles(sym, "H4")
                if candles is None or candles.is_empty():
                    continue

                for dir_enum in [SetupDirection.BUY, SetupDirection.SELL]:
                    res = carry_engine.backtest_pair_direction(
                        symbol=sym,
                        direction=dir_enum,
                        candles_df=candles,
                        excursion_engine=excursion_engine,
                        zone_detector=zone_detector,
                        k_sl=2.0,
                        reward_risk_ratio=1.00,
                    )
                    if res is None:
                        continue

                    is_pass = res.valid_edge
                    if is_pass:
                        passing_count += 1
                        status_str = "[bold green]PASS[/bold green]"
                    else:
                        status_str = "[dim red]FAIL[/dim red]"

                    dir_color = "green" if dir_enum == SetupDirection.BUY else "red"
                    wl_str = f"[green]{res.win_count}[/green]/[red]{res.loss_count}[/red]"
                    tp_sl_str = f"{res.recommended_tp_pips:.0f} / {res.recommended_sl_pips:.0f}"
                    net_r_color = "green" if res.net_realized_r > 0 else "red"

                    results_table.add_row(
                        sym,
                        f"[{dir_color}]{dir_enum.value}[/{dir_color}]",
                        str(res.trigger_count),
                        wl_str,
                        f"{res.respect_rate*100:.0f}%",
                        tp_sl_str,
                        f"{res.k_sl:.1f}x",
                        f"{res.reward_risk_ratio:.2f}",
                        f"[{net_r_color}]{res.net_realized_r:+.1f}R[/{net_r_color}]",
                        f"[{net_r_color}]{res.expected_r_per_trade:+.2f}R[/{net_r_color}]",
                        f"{res.avg_holding_bars:.1f} b",
                        status_str,
                    )

                    if register and is_pass:
                        base_c = sym[:3]
                        setup_dto = RegisteredSetupDTO(
                            id=f"VRC_{sym}_{dir_enum.value}",
                            quant_method=QuantMethod.VRC,
                            event_name="Carry Liquidation Cascade",
                            currency=base_c,
                            symbol=sym,
                            direction=dir_enum,
                            timeframe="H4",
                            respect_rate=res.respect_rate,
                            sample_count=res.trigger_count,
                            median_mfe_pips=res.median_mfe_pips,
                            mae_85_pips=res.mae_85_pips,
                            recommended_sl_pips=res.recommended_sl_pips,
                            recommended_tp_pips=res.recommended_tp_pips,
                            reward_risk_ratio=res.reward_risk_ratio,
                            trigger_state=f"volatility_unwind (SL={res.k_sl:.1f}xATR)",
                            min_z_score=1.50,
                            active=True,
                            created_at=int(time.time()),
                        )
                        registry.save_setup(setup_dto)
                        registered_count += 1

        console.print(results_table)
        console.print(f"\n[bold]Total Combinations Analyzed:[/bold] {len(target_symbols) * 2} | [bold green]Passing Statistical Edge:[/bold green] {passing_count}")
        if register:
            console.print(f"[bold green]Successfully saved {registered_count} passing setups to SQLite registry![/bold green]")
        return

    if method.lower() == "lar":
        console.print(Panel.fit(
            f"[bold cyan]Method 5: [M-LAR] Liquidity Absorption & Sovereign Intervention Rejection[/bold cyan]\n"
            f"  * Volatility Expansion Ratio: [yellow]TR >= 1.50x baseline ATR[/yellow]\n"
            f"  * Rejection Wick Proportion: [yellow]Wick >= 40% total candle range[/yellow]\n"
            f"  * Excursion Horizon: [blue]{horizon} H4 bars (~{horizon*4/24:.1f} trading days)[/blue]\n"
            f"  * S&R Zone Confluence: {zone_status}\n"
            f"  * Quality Gate: Respect Rate >= [green]50%[/green] | Net R > [green]0.0R[/green] | R:R >= [green]1.00[/green]",
            border_style="cyan",
        ))

        lar_engine = LiquidityAbsorptionEngine(min_expansion_ratio=1.50, min_wick_ratio=0.40)
        excursion_engine = ExcursionEngine(max_bars=horizon)
        zone_detector = ZoneDetector(k_window=5, atr_period=14) if zones else None
        registry = SetupRegistry()

        target_symbols = [symbol.upper()] if symbol else settings.major_forex_extended
        results_table = Table(title="[M-LAR] Liquidity Absorption Rejection — Decadal Audit")
        results_table.add_column("Symbol", style="bold cyan")
        results_table.add_column("Dir", style="white")
        results_table.add_column("Trig (N)", justify="right")
        results_table.add_column("W/L", justify="center")
        results_table.add_column("Respect %", justify="right")
        results_table.add_column("TP / SL (pips)", justify="center")
        results_table.add_column("SL ATR", justify="right")
        results_table.add_column("R:R", justify="right")
        results_table.add_column("Net R", justify="right")
        results_table.add_column("EV / trade", justify="right")
        results_table.add_column("Avg Hold", justify="right")
        results_table.add_column("Edge Status", justify="center")

        passing_count = 0
        registered_count = 0

        with console.status("[bold green]Scanning for liquidity absorption footprints and zone rejections...[/bold green]"):
            for sym in target_symbols:
                candles = candle_loader.load_cached_candles(sym, "H4")
                if candles is None or candles.is_empty():
                    continue

                for dir_enum in [SetupDirection.BUY, SetupDirection.SELL]:
                    res = lar_engine.backtest_pair_direction(
                        symbol=sym,
                        direction=dir_enum,
                        candles_df=candles,
                        excursion_engine=excursion_engine,
                        zone_detector=zone_detector,
                        k_sl=2.0,
                        reward_risk_ratio=1.00,
                    )
                    if res is None:
                        continue

                    is_pass = res.valid_edge
                    if is_pass:
                        passing_count += 1
                        status_str = "[bold green]PASS[/bold green]"
                    else:
                        status_str = "[dim red]FAIL[/dim red]"

                    dir_color = "green" if dir_enum == SetupDirection.BUY else "red"
                    wl_str = f"[green]{res.win_count}[/green]/[red]{res.loss_count}[/red]"
                    tp_sl_str = f"{res.recommended_tp_pips:.0f} / {res.recommended_sl_pips:.0f}"
                    net_r_color = "green" if res.net_realized_r > 0 else "red"

                    results_table.add_row(
                        sym,
                        f"[{dir_color}]{dir_enum.value}[/{dir_color}]",
                        str(res.trigger_count),
                        wl_str,
                        f"{res.respect_rate*100:.0f}%",
                        tp_sl_str,
                        f"{res.k_sl:.1f}x",
                        f"{res.reward_risk_ratio:.2f}",
                        f"[{net_r_color}]{res.net_realized_r:+.1f}R[/{net_r_color}]",
                        f"[{net_r_color}]{res.expected_r_per_trade:+.2f}R[/{net_r_color}]",
                        f"{res.avg_holding_bars:.1f} b",
                        status_str,
                    )

                    if register and is_pass:
                        base_c = sym[:3]
                        setup_dto = RegisteredSetupDTO(
                            id=f"LAR_{sym}_{dir_enum.value}",
                            quant_method=QuantMethod.LAR,
                            event_name="Liquidity Absorption Rejection",
                            currency=base_c,
                            symbol=sym,
                            direction=dir_enum,
                            timeframe="H4",
                            respect_rate=res.respect_rate,
                            sample_count=res.trigger_count,
                            median_mfe_pips=res.median_mfe_pips,
                            mae_85_pips=res.mae_85_pips,
                            recommended_sl_pips=res.recommended_sl_pips,
                            recommended_tp_pips=res.recommended_tp_pips,
                            reward_risk_ratio=res.reward_risk_ratio,
                            trigger_state=f"absorption_wick (SL={res.k_sl:.1f}xATR)",
                            min_z_score=1.50,
                            active=True,
                            created_at=int(time.time()),
                        )
                        registry.save_setup(setup_dto)
                        registered_count += 1

        console.print(results_table)
        console.print(f"\n[bold]Total Combinations Analyzed:[/bold] {len(target_symbols) * 2} | [bold green]Passing Statistical Edge:[/bold green] {passing_count}")
        if register:
            console.print(f"[bold green]Successfully saved {registered_count} passing setups to SQLite registry![/bold green]")
        return

    # Method 1 (MSD) execution path below
    console.print(Panel.fit(
        f"[bold cyan]Method 1: [M-MSD] Macro Surprise Divergence Research Cruncher[/bold cyan]\n"
        f"  * Divergence Threshold: [yellow]|Delta S| >= {min_spread:.2f} sigma[/yellow]\n"
        f"  * Lookback Window: [magenta]{lookback} days[/magenta] (Half-Life: [magenta]{half_life} days[/magenta])\n"
        f"  * Excursion Horizon: [blue]{horizon} H4 bars (~{horizon*4/24:.1f} trading days)[/blue]\n"
        f"  * S&R Zone Confluence: {zone_status}\n"
        f"  * Quality Gate: Respect Rate >= [green]50%[/green] | Net R > [green]0.0R[/green] | R:R >= [green]1.00[/green]",
        border_style="cyan",
    ))


    candle_loader = CandleLoader()
    calendar_loader = CalendarLoader()

    # Load and calibrate calendar
    cal_df = calendar_loader.load_cached_calendar()
    if cal_df.is_empty():
        console.print("[bold red]Error: No calendar events found in cache.[/bold red]")
        raise typer.Exit(1)

    surprise_engine = SurpriseEngine(cal_df)
    divergence_engine = MacroDivergenceEngine(
        lookback_days=lookback,
        half_life_days=half_life,
        min_divergence_z=min_spread,
    )
    excursion_engine = ExcursionEngine(max_bars=horizon)
    registry = SetupRegistry()

    # Pre-compute standardized surprise shocks
    events_scored = divergence_engine.compute_currency_scores(cal_df, surprise_engine)

    target_symbols = [symbol.upper()] if symbol else settings.major_forex_extended
    results_table = Table(title="[M-MSD] Empirical Excursion Distributions & Path-Dependent Edge")
    results_table.add_column("Symbol", style="bold cyan")
    results_table.add_column("Dir", style="white")
    results_table.add_column("Trig (N)", justify="right")
    results_table.add_column("W/L", justify="center")
    results_table.add_column("Respect %", justify="right")
    results_table.add_column("TP / SL (pips)", justify="center")
    results_table.add_column("SL ATR", justify="right")
    results_table.add_column("R:R", justify="right")
    results_table.add_column("Net R", justify="right")
    results_table.add_column("EV / trade", justify="right")
    results_table.add_column("Avg Hold", justify="right")
    results_table.add_column("Edge Status", justify="center")

    passing_count = 0
    registered_count = 0

    with console.status("[bold green]Calculating divergence spreads and forward paths...[/bold green]"):
        for sym in target_symbols:
            if sym not in PAIR_MAPPINGS:
                continue

            candles = candle_loader.load_cached_candles(sym, "H4")
            if candles is None or candles.is_empty():
                continue

            triggers = divergence_engine.find_divergence_triggers(sym, events_scored)
            if not triggers:
                continue

            for dir_enum in [SetupDirection.BUY, SetupDirection.SELL]:
                res = divergence_engine.crunch_pair_research(
                    symbol=sym,
                    direction=dir_enum,
                    triggers=triggers,
                    candles=candles,
                    excursion_engine=excursion_engine,
                    use_zone_confluence=zones,
                )
                if res is None:
                    continue

                is_pass = res.valid_edge
                if is_pass:
                    passing_count += 1
                    status_str = "[bold green]PASS[/bold green]"
                else:
                    status_str = "[dim red]FAIL[/dim red]"

                dir_color = "green" if dir_enum == SetupDirection.BUY else "red"
                wl_str = f"[green]{res.win_count}[/green]/[red]{res.loss_count}[/red]"
                tp_sl_str = f"{res.recommended_tp_pips:.0f} / {res.recommended_sl_pips:.0f}"
                net_r_color = "green" if res.net_realized_r > 0 else "red"

                results_table.add_row(
                    sym,
                    f"[{dir_color}]{dir_enum.value}[/{dir_color}]",
                    str(res.trigger_count),
                    wl_str,
                    f"{res.respect_rate*100:.0f}%",
                    tp_sl_str,
                    f"{res.k_sl:.1f}x",
                    f"{res.reward_risk_ratio:.2f}",
                    f"[{net_r_color}]{res.net_realized_r:+.1f}R[/{net_r_color}]",
                    f"[{net_r_color}]{res.expected_r_per_trade:+.2f}R[/{net_r_color}]",
                    f"{res.avg_holding_bars:.1f} b",
                    status_str,
                )

                if register and is_pass:
                    setup_dto = RegisteredSetupDTO(
                        id=f"MSD_{sym}_{dir_enum.value}",
                        quant_method=QuantMethod.MSD,
                        event_name=f"Macro Divergence Spread ({min_spread:.2f} std)",
                        currency=res.base_currency,
                        symbol=sym,
                        direction=dir_enum,
                        timeframe="H4",
                        respect_rate=res.respect_rate,
                        sample_count=res.trigger_count,
                        median_mfe_pips=res.median_mfe_pips,
                        mae_85_pips=res.mae_85_pips,
                        recommended_sl_pips=res.recommended_sl_pips,
                        recommended_tp_pips=res.recommended_tp_pips,
                        reward_risk_ratio=res.reward_risk_ratio,
                        trigger_state=f"macro_divergence_spread (SL={res.k_sl:.1f}xATR)",
                        min_z_score=min_spread,
                        active=True,
                        created_at=int(time.time()),
                    )
                    registry.save_setup(setup_dto)
                    registered_count += 1

    console.print(results_table)
    console.print(f"\n[bold]Total Combinations Analyzed:[/bold] {len(target_symbols) * 2} | [bold green]Passing Statistical Edge:[/bold green] {passing_count}")
    if register:
        console.print(f"[bold green]Successfully saved {registered_count} passing setups to SQLite registry![/bold green]")

@app.command()
def setups():
    """List all codified setups currently registered in the SQLite registry."""
    registry = SetupRegistry()
    setups_list = registry.get_active_setups()

    if not setups_list:
        console.print("[yellow]No active setups registered yet. Run `fms research --register` to register passing setups.[/yellow]")
        return

    table = Table(title="Codified Registered Setups (SQLite Store)")
    table.add_column("Setup ID", style="dim")
    table.add_column("Method", style="magenta")
    table.add_column("Symbol", style="bold cyan")
    table.add_column("Dir", style="white")
    table.add_column("Win Rate", justify="right", style="green")
    table.add_column("TP / SL (pips)", justify="center")
    table.add_column("R:R", justify="right", style="cyan")
    table.add_column("Sample N", justify="right")

    for s in setups_list:
        dir_color = "green" if s.direction == SetupDirection.BUY else "red"
        table.add_row(
            s.id,
            s.quant_method.value,
            s.symbol,
            f"[{dir_color}]{s.direction.value}[/{dir_color}]",
            f"{s.respect_rate*100:.0f}%",
            f"{s.recommended_tp_pips:.0f} / {s.recommended_sl_pips:.0f}",
            f"{s.reward_risk_ratio:.2f}",
            str(s.sample_count),
        )

    console.print(table)

if __name__ == "__main__":
    app()
