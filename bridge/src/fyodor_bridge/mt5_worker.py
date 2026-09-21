from __future__ import annotations

import importlib
import queue
import threading
from concurrent.futures import Future, TimeoutError as FutureTimeoutError
from dataclasses import asdict, dataclass
from time import monotonic
from typing import Any, Callable

from .mt5_process import MultipleTerminalProcessesError, find_terminal_process
from .runtime_activity import ActivityLedger, utc_milliseconds
from .settings import BridgeSettings


class Mt5UnavailableError(RuntimeError):
    pass


class SupersededRequest(RuntimeError):
    pass


@dataclass
class Mt5Status:
    process_running: bool = False
    process_id: int | None = None
    terminal_path: str | None = None
    connected: bool = False
    state: str = "starting"
    generation: int = 0
    last_attempt_at: int | None = None
    last_success_at: int | None = None
    last_error: str | None = None
    package_version: str | None = None
    account_login: int | None = None
    account_server: str | None = None


@dataclass(order=True)
class _QueuedCall:
    priority: int
    order: int
    category: str
    generation: int
    operation: Callable[[Any], Any]
    future: Future[Any]


class Mt5Worker:
    def __init__(self, settings: BridgeSettings, activity: ActivityLedger) -> None:
        self._settings = settings
        self._activity = activity
        self._status = Mt5Status()
        self._status_lock = threading.RLock()
        self._queue: queue.PriorityQueue[_QueuedCall] = queue.PriorityQueue()
        self._latest_generation: dict[str, int] = {}
        self._generation_lock = threading.RLock()
        self._order = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._mt5: Any | None = None
        self._last_status_check = 0.0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="fyodor-mt5-worker", daemon=True)
        self._thread.start()
        self._activity.append("Bridge", "MT5 worker started", severity="success")

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)
            if self._thread.is_alive():
                self._activity.append("MT5", "Worker shutdown timed out", "Process exit will release the daemon worker", "warning")
                return
        self._shutdown_mt5()

    def snapshot(self) -> dict[str, object]:
        with self._status_lock:
            return asdict(self._status)

    def submit(
        self,
        category: str,
        operation: Callable[[Any], Any],
        *,
        priority: int = 10,
        timeout: float | None = None,
    ) -> Any:
        future: Future[Any] = Future()
        with self._generation_lock:
            generation = self._latest_generation.get(category, 0) + 1
            self._latest_generation[category] = generation
            self._order += 1
            queued = _QueuedCall(priority, self._order, category, generation, operation, future)
        self._queue.put(queued)
        try:
            return future.result(timeout=timeout or self._settings.mt5_call_timeout_seconds)
        except FutureTimeoutError as error:
            future.cancel()
            raise Mt5UnavailableError(f"MT5 call timed out after {timeout or self._settings.mt5_call_timeout_seconds:.1f}s") from error

    def _run(self) -> None:
        while not self._stop.is_set():
            self._refresh_connection_if_due()
            try:
                queued = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if queued.future.cancelled():
                continue
            with self._generation_lock:
                latest = self._latest_generation.get(queued.category)
            if latest != queued.generation:
                queued.future.set_exception(SupersededRequest("A newer request replaced this one"))
                continue

            try:
                self._ensure_connected()
                result = queued.operation(self._mt5)
            except Exception as error:
                self._record_operation_error(error)
                if not queued.future.cancelled():
                    queued.future.set_exception(error)
            else:
                if not queued.future.cancelled():
                    queued.future.set_result(result)

        self._shutdown_mt5()

    def _refresh_connection_if_due(self) -> None:
        now = monotonic()
        if now - self._last_status_check < self._settings.mt5_status_interval_seconds:
            return
        self._last_status_check = now
        self._refresh_connection()

    def _ensure_connected(self) -> None:
        self._refresh_connection_if_due()
        with self._status_lock:
            if not self._status.connected or self._mt5 is None:
                raise Mt5UnavailableError(self._status.last_error or "MT5 is not connected")

    def _refresh_connection(self) -> None:
        try:
            process = find_terminal_process(self._settings.mt5_terminal_path)
        except MultipleTerminalProcessesError as error:
            with self._status_lock:
                self._status.process_running = True
                self._status.process_id = None
                self._status.terminal_path = None
            self._set_error(str(error), "terminal-selection-required")
            return
        if process is None:
            self._set_terminal_absent()
            return

        with self._status_lock:
            previous_pid = self._status.process_id
            was_connected = self._status.connected
            self._status.process_running = True
            self._status.process_id = process.pid
            self._status.terminal_path = process.executable

        if previous_pid and previous_pid != process.pid:
            self._shutdown_mt5()

        if self._mt5 is None:
            try:
                self._mt5 = importlib.import_module("MetaTrader5")
            except ModuleNotFoundError:
                self._set_error("Python package MetaTrader5 is not installed", "package-missing")
                return
            with self._status_lock:
                self._status.package_version = getattr(self._mt5, "__version__", None)

        if was_connected and previous_pid == process.pid:
            try:
                terminal_info = self._mt5.terminal_info()
                if terminal_info and bool(getattr(terminal_info, "connected", False)):
                    with self._status_lock:
                        self._status.last_success_at = utc_milliseconds()
                        self._status.last_error = None
                    return
            except Exception:
                pass
            self._shutdown_mt5()
            with self._status_lock:
                self._status.connected = False

        with self._status_lock:
            self._status.last_attempt_at = utc_milliseconds()

        initialized = False
        try:
            initialized = bool(self._mt5.initialize(process.executable, timeout=5000))
        except Exception as error:
            self._set_error(f"MT5 initialize failed: {error}", "initialization-failed")
            return

        if not initialized:
            self._set_error(self._last_mt5_error("MT5 initialize failed"), "initialization-failed")
            return

        terminal_info = self._mt5.terminal_info()
        connected = bool(terminal_info and getattr(terminal_info, "connected", False))
        if not connected:
            self._set_error(self._last_mt5_error("Terminal is running but broker connection is unavailable"), "terminal-disconnected")
            return

        account_info = self._mt5.account_info()
        with self._status_lock:
            self._status.connected = True
            self._status.state = "connected"
            self._status.last_success_at = utc_milliseconds()
            self._status.last_error = None
            self._status.account_login = int(account_info.login) if account_info else None
            self._status.account_server = str(account_info.server) if account_info else None
            if not was_connected:
                self._status.generation += 1
                generation = self._status.generation
            else:
                generation = None
        if generation is not None:
            self._activity.append(
                "MT5",
                "Terminal connected",
                f"PID {process.pid} · generation {generation}",
                "success",
            )

    def _set_terminal_absent(self) -> None:
        with self._status_lock:
            changed = self._status.process_running or self._status.state != "waiting-for-terminal"
            self._status.process_running = False
            self._status.process_id = None
            self._status.terminal_path = None
            self._status.connected = False
            self._status.state = "waiting-for-terminal"
            self._status.last_error = "MT5 terminal process is not running"
            self._status.account_login = None
            self._status.account_server = None
        if changed:
            self._activity.append("MT5", "Terminal not running", severity="warning")
        self._shutdown_mt5(clear_status=False)

    def _set_error(self, message: str, state: str) -> None:
        with self._status_lock:
            changed = self._status.state != state or self._status.last_error != message
            self._status.connected = False
            self._status.state = state
            self._status.last_error = message
        if changed:
            self._activity.append("MT5", "Connection unavailable", message, "error")

    def _last_mt5_error(self, prefix: str) -> str:
        if self._mt5 is None:
            return prefix
        try:
            code, description = self._mt5.last_error()
            return f"{prefix}: [{code}] {description}"
        except Exception:
            return prefix

    def _record_operation_error(self, error: Exception) -> None:
        message = str(error)
        ipc_failure = any(code in message for code in ("[-10000]", "[-10001]", "[-10002]", "[-10003]", "[-10005]"))
        if not ipc_failure:
            return
        with self._status_lock:
            self._status.connected = False
            self._status.state = "ipc-recovery"
            self._status.last_error = message
        self._activity.append("MT5", "IPC failure detected", message, "error")
        self._shutdown_mt5()
        self._last_status_check = 0.0

    def _shutdown_mt5(self, clear_status: bool = True) -> None:
        if self._mt5 is not None:
            try:
                self._mt5.shutdown()
            except Exception:
                pass
            self._mt5 = None
        if clear_status:
            with self._status_lock:
                self._status.connected = False
