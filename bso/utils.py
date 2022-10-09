import time


class Tracker:
    durations_dict = dict()
    frequencies_dict = dict()

    @staticmethod
    def Track(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter_ns()
            fit = func(*args, **kwargs)
            finnish = time.perf_counter_ns()
            time_taken = (finnish - start) / 10 ** 9

            Tracker.durations_dict[func.__name__] = Tracker.durations_dict.get(func.__name__, 0) + time_taken
            Tracker.frequencies_dict[func.__name__] = Tracker.frequencies_dict.get(func.__name__, 0) + 1

            return fit

        return wrapper
