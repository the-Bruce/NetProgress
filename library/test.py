from time import sleep

import netprogress
from netprogress.endpoint import Udp

PROGRESS_KEY = "56Asv8rkTS8ICi3leQKTVsbA5AUhrcepNb6IkAng6KmIK6nTq58iBPZr2W5MaHbfObbqmqfRO9LEMBYSIjv4FJOOy4EnsbRIbkf2IuFb4w7WhaZbIqBoC8fiGZ2528fa"

if __name__ == '__main__':
    with netprogress.ProgressUpdater(PROGRESS_KEY, frequency=0.2, endpoints=[Udp]) as PROGRESS:
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