import os

def get_game_name(path):
    filename = os.path.basename(path)
    if filename.endswith('.zip'):
        filename = filename[:-4]

    return filename

