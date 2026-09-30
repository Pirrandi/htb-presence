import pytest

from htb_presence.lock import AlreadyRunningError, SingleInstanceLock


def test_second_lock_fails_until_first_is_released(tmp_path):
    path = tmp_path / "x.lock"
    first = SingleInstanceLock(path)
    first.acquire()
    try:
        with pytest.raises(AlreadyRunningError):
            SingleInstanceLock(path).acquire()
    finally:
        first.release()

    with SingleInstanceLock(path):
        pass
