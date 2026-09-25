import getopt
import print_util
import sys

threading = False
postingMode = "catch-up"

def usage():
    print(f"Usage: python {sys.argv[0]} [options] arguments")
    print("Options:")
    print("  -h, --help          Show this help message and exit")
    print("  -v, --verbose       Enable verbose mode")
    print("  -d, --debug         Enable debug logs")
    print("  -t, --threading     Posting threads to meta threads")

def getOptions(args):
    options = "hvdt::o:"
    long_options = ["help", "verbose", "debug", "threading=?", "output="]
    try:
        arguments, values = getopt.getopt(args, options, long_options)
        for currentArg, currentVal in arguments:
            currentArg = currentArg.lower()
            if currentArg in ("-h", "--help"):
                usage()
                sys.exit(2)
            elif currentArg in ("-v", "--verbose"):
                print_util.setVerbose(True)
            elif currentArg in ("-d", "--debug"):
                print_util.setDebug(True)
            elif currentArg in ("-t", "--threading"):
                global threading, postingMode
                # TODO: use this in game.py
                if currentVal:
                    match currentVal:
                        case "catch-up":
                            pass
                        case "live-only":
                            pass
                        case _:
                            usage()
                            sys.exit(2)
                    postingMode = currentVal
                print(postingMode)
                threading = True
            elif currentArg in ("-o", "--output"):
                print("Output mode:", currentVal)
    except getopt.error as err:
        print(f"Error in augments: {err}")
        usage()
        sys.exit(2)
