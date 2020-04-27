from contextlib import contextmanager
from time import sleep
from typing import Iterator

from rush import quota
from rush import throttle
from rush.limiters import periodic
from rush.stores import dictionary


class LocalRateLimiter:
    """Wraps the 'rush' throttler in a context manager"""

    def __init__(self, *, key: str, rate_per_sec: int) -> None:
        self._key = key
        self._throttle = throttle.Throttle(
            limiter=periodic.PeriodicLimiter(store=dictionary.DictionaryStore()),
            rate=quota.Quota.per_second(count=rate_per_sec,),
        )

    @contextmanager
    def __call__(self) -> Iterator[None]:
        while True:
            result = self._throttle.check(self._key, 1)
            if not result.limited:
                break

            sleep(result.retry_after.total_seconds())
        yield


file_diff_update_throttle = LocalRateLimiter(rate_per_sec=5, key="file_diff_update")
file_merged_update_throttle = LocalRateLimiter(rate_per_sec=4, key="file_merged_update")
