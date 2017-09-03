#!/usr/bin/python
import os
def run(**args):
    print "[*] In dirlister module."
    f = os.listdir(".")
    return str(f)
