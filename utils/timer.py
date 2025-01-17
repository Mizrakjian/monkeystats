from functools import wraps
from time import perf_counter_ns


def timer(func):
    """
    Decorator to time the execution of a non-async function.
    Prints the elapsed time in milliseconds (ms).
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter_ns()
        result = func(*args, **kwargs)
        elapsed_time = (perf_counter_ns() - start_time) / 1_000_000  # Convert ns to ms
        print(f"Function '{func.__name__}' took {elapsed_time:.0f}ms")
        return result

    return wrapper
