import getopt
import print_util
import sys

def usage():
    print(f"Usage: python {sys.argv[0]} [options] arguments")
    print("Options:")
    print("  -h, --help          Show this help message and exit")
    print("  -v, --verbose       Enable verbose mode")
    print("  -d, --debug         Enable debug logs")

def getOptions(args):
    options = "hvdo:"
    long_options = ["help", "verbose", "debug", "output="]
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
            elif currentArg in ("-o", "--output"):
                print("Output mode:", currentVal)
    except getopt.error as err:
        print("Error in augments")
        usage()
        sys.exit(2)
