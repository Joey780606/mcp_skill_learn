"""Executes skill functions in a thread pool, capturing stdout."""
import io
import contextlib
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="skill-worker")


def run_skill(
    fn: Callable,
    output_cb: Callable[[str], None],
    done_cb: Callable[[], None],
) -> None:
    """Run a skill function in a worker thread (non-blocking)."""

    def _execute():
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                result = fn()
            captured = buf.getvalue()
            text = captured
            if result:
                text = f"{captured}\n{result}" if captured else result
            output_cb(text.strip())
        except Exception as e:
            output_cb(f"ERROR ({type(e).__name__}): {e}")
        finally:
            done_cb()

    _pool.submit(_execute)
