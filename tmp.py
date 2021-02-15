#!/usr/local/bin/python3.9

import os, sys

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        text = f.read()
        text = text.replace("database_client", "database_client")
        #  text = text.replace("config.db", "config.db")
    with open(filename, "w") as f:
        f.write(text)
