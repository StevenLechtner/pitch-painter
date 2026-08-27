verbose = False
debug = False

def vprint(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)

def setVerbose(_verbose):
    global verbose
    verbose = _verbose

def dprint(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

def setDebug(_debug):
    global debug
    debug = _debug
