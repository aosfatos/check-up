import signal
from functools import partial


class PlayerTimeoutError(Exception):
    pass


def handle_timeout(signum, frame, message):
    raise PlayerTimeoutError(message)


class PlayTimeout:
    def __init__(self, seconds, name):
        self.seconds = seconds
        self.name = name

    def __enter__(self):
        message = f"Player '{self.name}' did not finish before {self.seconds} seconds."
        _handle_timeout = partial(handle_timeout, message=message)
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)
