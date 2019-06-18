import os
import requests

def abspath(path):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

def download_file(url, filename):
    r = requests.get(url)
    if r.status_code != 200:
        print('Error: request %s returned %s' % (url, r.status_code))
        return
    open(filename, 'wb').write(r.content)