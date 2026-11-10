verbose = False
debug = False
tweet = False

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

def setTweet(_tweet):
    global tweet
    tweet = _tweet
