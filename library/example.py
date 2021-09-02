import netprogress

PROGRESS_KEY = "<your-project-api-key>"

if __name__ == '__main__':
    # wrap your program in this to set up the library
    with netprogress.ProgressUpdater(PROGRESS_KEY, frequency=0.2, endpoints=[netprogress.Udp]) as PROGRESS:
        input()
        # Outer progress bar. Argument is number of steps
        with PROGRESS.bar(3000000) as obar:
            # Iterator wrapper form
            # Convenient but won't reliably report errors
            # Iterator needs to correctly implement len()
            for i in PROGRESS(range(1000000), name="Phase 1"):
                obar.increment()  # increment the outer progress bar
                # Iterator bar automatically incremented
                print(i)
            # Explicit form
            # Needs to be manually incremented
            with PROGRESS.bar(1000000, "Phase 2") as bar:
                for i in range(1000000):
                    obar.increment()
                    bar.increment()  # Needs to be incremented manually
                    print(i)
            # Hybrid form (Recommended over iterator wrapper form)
            # Avoids needing to manually increment
            # Will correctly report errors
            with PROGRESS(range(1000000), "Phase 3") as iterator:
                for i in iterator:
                    obar.increment()
                    # Iterator bar automatically incremented
