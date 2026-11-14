"""Convert command line print arguments to logic.

verbose flag shows vprint in the console.
debug flag shows dprint in the console.
tweet flag sets tweet. TODO: remove.
"""
# pylint: disable=invalid-name, global-statement
verbose = False
debug = False
tweet = False


def vprint(*args, **kwargs):
    """Print vprint to stdout if verbose flag toggled."""
    if verbose:
        print(*args, **kwargs)


def setVerbose(_verbose):
    """Set verbose flag."""
    global verbose
    verbose = _verbose


def dprint(*args, **kwargs):
    """Print dprint to stdout if debug flag toggled."""
    if debug:
        print(*args, **kwargs)


def setDebug(_debug):
    """Set debug flag."""
    global debug
    debug = _debug


# TODO: remove
def setTweet(_tweet):
    """Set tweet flag."""
    global tweet
    tweet = _tweet
