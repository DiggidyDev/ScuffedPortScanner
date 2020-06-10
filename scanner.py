#!/usr/bin/python3


import argparse
import concurrent.futures
import socket
import sys

from collections.abc import Iterable
from datetime import datetime as dt


# Colours for making the terminal look pretty
class clr:
    BLUE    = "\033[94m"
    FAIL    = "\033[91m"
    GREEN   = "\033[92m" 
    WARNING = "\033[93m"
    
    RESET   = "\033[0m"


# Outputting a list of given args in a "banner"
# Also can take in an iterable as one of the args
def bannerise(*args):
    content = "\n"
    content += f"*{'=' * 50}*\n||\n"
    for a in args:
        if isinstance(a, Iterable) and type(a) != str:
            for i in a:
                content += f"|| {i}\n"
        else:
            content += f"|| {a}\n"
    content += f"||\n*{'=' * 50}*\n"
    print(content)


def check_port(conn_tuple):
    hostname, port = conn_tuple
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(.5)
    resp = s.connect_ex((hostname, port))
    print(f"connected to port {port}!")
    status = f"{clr.GREEN}OPEN{clr.RESET}" if resp == 0 else f"{clr.FAIL}CLOSED{clr.RESET}"
    s.close()
    return f"PORT {clr.BLUE}{port}{clr.RESET}: {status}"


parser = argparse.ArgumentParser(description=bannerise("Scan an IP for ports."))
parser.add_argument("target",
                    action="store",
                    metavar="Target",
                    help="The IP/Domain that you wish to scan"
                    )
parser.add_argument("--ports",
                    action="store",
                    metavar="p",
                    nargs="*"
                    )
args = parser.parse_args()

print(args)


if len(sys.argv) > 1:
    hostname = sys.argv[1]
    try:
        start, end = map(int, sys.argv[2].split("-"))
    except IndexError:
        sys.exit(0)
else:
    bannerise(
        f"{clr.WARNING}ERROR:{clr.RESET} HOSTNAME parameter not filled.",
        f"{clr.BLUE}SYNTAX:{clr.RESET} python3 scanner.py 10.10.10.191 80-500"
    )
    sys.exit(0)


with concurrent.futures.ThreadPoolExecutor() as ex:
    results = ex.map(check_port,  [(hostname, i) for i in range(start, end+ 1)])
    bannerise(results)
    
