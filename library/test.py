from time import sleep

import netprogress

PROGRESS_KEY = "4llkYIe7qHXJe5KXTH1y0PPfrw1qq9w8oUbaYQ75ATI0M0Y8fMQAb8Mw16NqEXdGzKgehQzBpkN5TKcrAh2d7RVaOE1quowwIM54N8NXyO61GOPvBHE8FUG2gSMixiSx"

if __name__ == '__main__':
    with netprogress.ProgressUpdater(PROGRESS_KEY, frequency=0.2, endpoints=[netprogress.Http]) as PROGRESS:
        input()
        with PROGRESS.bar(2000000) as obar:
            for i in PROGRESS(range(1000000), name="Phase 1"):
                obar.increment()
                print(i)
            with PROGRESS.bar(1000000, "Phase 2") as bar:
                for i in range(1000000):
                    obar.increment()
                    bar.increment()
                    print(i)