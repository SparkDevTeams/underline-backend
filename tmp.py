#!/usr/local/bin/python3.9

import os, sys

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        text = f.read()
        text = text.replace("db", "database_client")
    with open(filename, "w") as f:
        f.write(text)
