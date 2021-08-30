import json
import time
from collections import defaultdict

import requests

DEFAULT_URL = "https://netprogress.thomasbruce.co.uk"


class ProgressUpdater:
    def __init__(self, key, url=DEFAULT_URL, frequency=1):
        if url[-1] == "/":
            url = url[:-1]
        self.key = key
        self.url = url
        self.session_key = None
        self.names = set()
        self.awaiting_update = defaultdict(dict)
        self.frequency = frequency
        self.updated = time.monotonic()
        self.init()

    def init(self):
        response = requests.post(self.url + "/api/init/", data={"key": self.key})
        if response.ok:
            self.session_key = response.json()['key']
        else:
            raise RuntimeError("Unable to initiate session")

    def bar(self, maximum=100, name="Main"):
        if name in self.names:
            if name == "Main":
                raise ValueError("Multiple unnamed bars. Please name a bar if using more than one per application")
            else:
                raise ValueError("Multiple identically named bars. Please ensure that each bar is distinct")
        if maximum <= 0 or int(maximum) != maximum:
            raise ValueError("Maximum should be a positive integer")
        self.names.update(name)
        self.awaiting_update[name]['max'] = maximum
        self.awaiting_update[name]['val'] = 0
        return ProgressBar(name, maximum, self)

    def flush(self):
        self.frequency=0
        self._report()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        return False

    def __call__(self, iterable, maximum=None, **kwargs):
        if maximum is None:
            try:
                maximum = len(iterable)
            except (TypeError, AttributeError):
                maximum = 100
        else:
            maximum = 100
        bar = self.bar(maximum, **kwargs)
        return IterableWrapper(iterable, bar)


    def _update(self, bar, value):
        self.awaiting_update[bar]['val'] = value
        self._report()

    def _finish(self, bar):
        self.awaiting_update[bar]['done'] = True
        self._report()

    def _error(self, bar):
        self.awaiting_update[bar]['error'] = True
        self._report()

    def _report(self):
        if self.session_key is None:
            self.init()
        if time.monotonic() >= self.updated + self.frequency:
            data = {
                "key": self.session_key,
                "updates": json.dumps(self.awaiting_update)
            }
            requests.post(self.url + "/api/update/", data=data)
            self.awaiting_update.clear()
            self.updated = time.monotonic()


class ProgressBar:
    def __init__(self, name, maximum, parent):
        self.name = name
        self.parent: ProgressUpdater = parent
        self.max = maximum
        self.current = 0
        self.done = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error()
        else:
            self.finish()
        return False

    def increment(self):
        if self.max > self.current:
            self.current = self.current + 1
            self.parent._update(self.name, self.current)

    def set_value(self, value):
        if self.max < value:
            self.current = value

    def finish(self):
        if not self.done:
            self.done = True
            self.parent._finish(self.name)

    def error(self):
        if not self.done:
            self.done = True
            self.parent._error(self.name)


class IterableWrapper:
    def __init__(self, iterable, bar):
        self.bar = bar
        self.iterable = iterable

    def __iter__(self):
        try:
            for obj in self.iterable:
                self.bar.increment()
                yield obj
        except Exception as e:
            self.bar.error()
            raise e
        finally:
            self.bar.finish()

    def close(self):
        self.bar.finish()

    def __len__(self):
        return len(self.iterable)