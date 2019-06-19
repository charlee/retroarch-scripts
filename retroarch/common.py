import os

def abspath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))