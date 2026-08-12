import time
from contextlib import contextmanager


# =========================
# SIMPLE TIMER CLASS
# =========================
class Timer:
    """
    Simple performance timer for measuring execution time.
    """

    def __init__(self, name: str = "Task"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def start(self):
        self.start_time = time.time()
        return self

    def stop(self):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        return self.elapsed

    def report(self):
        if self.elapsed is None:
            self.stop()
        print(f"⏱ {self.name} took {self.elapsed:.4f} seconds")


# =========================
# CONTEXT MANAGER TIMER
# =========================
@contextmanager
def timer(name: str = "Task"):
    """
    Usage:
        with timer("embedding"):
            do_something()
    """
    start = time.time()
    yield
    end = time.time()

    print(f"⏱ {name} took {end - start:.4f} seconds")


# =========================
# FUNCTION DECORATOR TIMER
# =========================
def time_it(func):
    """
    Decorator to measure function execution time.
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print(f"⏱ {func.__name__} took {end - start:.4f} seconds")
        return result

    return wrapper