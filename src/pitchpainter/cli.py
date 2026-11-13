"""Process command line arguments."""


# pylint: disable=invalid-name, global-statement
import getopt
import sys
from pitchpainter import print_util

threading = False
posting_mode = "catch-up"


def usage():
    """Print command line arguments help message."""
    print(f"Usage: python {sys.argv[0]} [options] arguments")
    print("Options:")
    print("  -h, --help          Show this help message and exit")
    print("  -v, --verbose       Enable verbose mode")
    print("  -d, --debug         Enable debug logs")
    print("  -t, --threading     Posting Threads to Meta Threads")


def get_options(args):
    """Parge command line arguments."""
    options = "hvdt::o:"
    long_options = ["help", "verbose", "debug", "threading=?", "output="]
    try:
        arguments, _ = getopt.getopt(args, options, long_options)
        for current_arg, current_val in arguments:
            current_arg = current_arg.lower()
            if current_arg in ("-h", "--help"):
                usage()
                sys.exit(2)
            elif current_arg in ("-v", "--verbose"):
                print_util.setVerbose(True)
            elif current_arg in ("-d", "--debug"):
                print_util.setDebug(True)
            elif current_arg in ("-t", "--threading"):
                global threading, posting_mode
                # TODO: use this in game.py
                if current_val:
                    match current_val:
                        case "catch-up":
                            pass
                        case "live-only":
                            pass
                        case _:
                            usage()
                            sys.exit(2)
                    posting_mode = current_val
                print(posting_mode)
                threading = True
            elif current_arg in ("-o", "--output"):
                print("Output mode:", current_val)
    except getopt.error as err:
        print(f"Error in augments: {err}")
        usage()
        sys.exit(2)
