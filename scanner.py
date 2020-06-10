#!/usr/bin/python3


import argparse
import concurrent.futures
import socket
import sys

from collections.abc import Iterable
from datetime import datetime as dt


# Overriding the default class to catch errors
class ArgumentParser(argparse.ArgumentParser):
    
    def error(self, message):
        if message.startswith("the following arguments"):
                print(bannerise(
                    f"{clr.WARNING}ERROR:{clr.RESET} HOSTNAME parameter not filled.", "",
                    f"{clr.BLUE}SYNTAXES:{clr.RESET} python3 scanner.py 10.10.10.191 --ports 22 80 443",
                    f"{' '*10}python3 scanner.py 10.10.10.191 --range 80 100"
                ))
                sys.exit(0)


# Colours for making the terminal look pretty
class clr:
    BLUE    = "\033[94m"
    FAIL    = "\033[91m"
    GREEN   = "\033[92m" 
    RESET   = "\033[0m"
    WARNING = "\033[93m"


# Outputting a list of given args in a "banner"
# Also can take in an iterable as one of the args
def bannerise(*args):
    padding = len(max(["%r" % a if type(a) == str else max([i for i in a]) for a in args]))
    content = "\n"
    content += f"*{'=' * padding}*\n|{' ' * padding}|\n"
    for a in args:
        if isinstance(a, Iterable) and type(a) != str:
            for i in a:
                content += f"|{i:^{padding + get_colours(i)}}|\n"
        else:
            content += f"|{a:^{padding + get_colours(a)}}|\n"
    content += f"|{' ' * padding}|\n*{'=' * padding}*\n"
    return content


def check_port(conn_tuple):
    target, port = conn_tuple
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(.5)
    resp = s.connect_ex((target, port))
    status = f"{clr.GREEN}OPEN{clr.RESET}" if resp == 0 else f"{clr.FAIL}CLOSED{clr.RESET}"
    s.close()
    
    return f"PORT {clr.BLUE}{port}{clr.RESET}: {status}"


def get_colours(string):
    formatted = "%r" % string
    return 4 * formatted.count("\\x") + formatted.count("\\x") // 2 if formatted.count("\\x") >= 1 else 0


parser = ArgumentParser(description=bannerise("Scan an IP for ports."))
parser.add_argument("target",
                    action="store",
                    metavar="Target",
                    help="The IP/Domain that you wish to scan"
                    )
parser.add_argument("--ports",
                    action="store",
                    metavar="p",
                    nargs="*",
                    help="Scan a list of specific ports"
                    )
parser.add_argument("--range",
                    action="store",
                    metavar="r",
                    nargs="*",
                    help="Scan all ports within a certain range (start and end included)"
                    )

args = parser.parse_args()
target = args.target

if args.range:
    if len(args.range) != 2:
        qty = "Too few" if len(args.range) < 2 else "Too many"
        print(bannerise(
                f"{clr.WARNING}ERROR:{clr.RESET} {qty} arguments given. 2 are required.", "",
                f"{clr.BLUE}SYNTAX:{clr.RESET} python3 scanner.py 10.10.10.191 --range 22 80"
        ))
        sys.exit()
    else:
        ports = [x for x in range(int(args.range[0]), int(args.range[1])+1)]
else:
    ports = [i for i in map(int, args.ports)]
 
with concurrent.futures.ThreadPoolExecutor() as ex:
    results = [r for r in ex.map(check_port, [(target, port) for port in ports])]
    print(bannerise(results))
    
