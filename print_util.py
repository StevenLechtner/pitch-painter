verbose = False

def vprint(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

def setVerbose(_verbose):
    global verbose
    verbose = _verbose