"""Helper functions non-related to GUI custom tkinter class"""
import re
import os

import constants as c


def sequence_collector(directory, sequence, mode, sframe, eframe):
    """ Takes a selected filename and uses it to find the sequence that it belongs to from a source folder """
    files = os.listdir(directory)
    pattern = rf"{os.path.splitext(sequence)[0]}{c.FRAME_PATTERN}{os.path.splitext(sequence)[1]}"
    matched = [os.path.normpath(os.path.join(directory, f)) for f in files if re.match(pattern, f)]
    
    if mode:
        matched_range = []
        for m in matched:
            frame = int(re.findall(f"{c.FRAME_PATTERN}\.", m)[-1].strip('.'))
            if frame >= sframe and frame <= eframe:
                matched_range.append(m)
        return matched_range
    return matched

def sequence_sorter(directory):
    """ Finds all frame sequences in a folder """
    pattern = r"[^\.]*\.\d+\.[a-zA-Z0-9]+"
    filelist = [f for f in os.listdir(directory) if re.match(pattern, f)]

    stripped = {re.sub(r'\.\d{1,10}', "", f):  f.split('.')[-2] for f in filelist}
    stripped_inverse = {re.sub(r'\.\d{1,10}', "", f):  f.split('.')[-2] for f in filelist[::-1]}
    seq = list(dict.fromkeys(stripped))
    eframes = list(dict.values(stripped))
    sframes = list(dict.values(stripped_inverse))

    viz = []
    for i in range(len(seq)):
        viz.append(f"{os.path.splitext(seq[i])[0]}.{sframes[i]}-{eframes[i]}{os.path.splitext(seq[i])[-1]}")

    return seq, eframes, sframes, viz

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = os.path.dirname(__file__)
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    sequence_sorter(r'X:\JFT\01_SHOTS\SC0200_PTERODACTYL\Render\LGT\Camera2_3_4\layout\v16')
    # sequence_sorter(r'X:/JFT/01_SHOTS/SC0700_BRACHIOSAURUS/Render/LGT/Camera_500offset_550_600_700_v03/layout/v36')

    files = sequence_collector(r'X:\JFT\01_SHOTS\SC0200_PTERODACTYL\Render\LGT\Camera2_3_4\layout\v16', "sc0200_layout_cryptomatte_asset00_v16.exr", 1, 500, 1000)
    for file in files:
        print(file)