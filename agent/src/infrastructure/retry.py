import time

def with_retry(func, retries=3):
    for _ in range(retries):
        try:
            return func()
        except Exception:
            time.sleep(1)
    raise Exception('Max retries exceeded')
