from collections import Counter

class Metrics:
    def __init__(self):
        self.counters = Counter()

    def incr(self, key, by=1):
        self.counters[key] += by

    def get(self, key):
        return self.counters.get(key, 0)

    def snapshot(self):
        return dict(self.counters)
