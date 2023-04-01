import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import pyroexr

def detect_empty(file):
    pyro_file = pyroexr.load(file)

    channel = pyro_file.channel('A')
    if np.all(channel):
        return file

def detect_edges(file, chan):
    """Tries to detect horizontal lines in an .exr images using a detect_edges kernel and some post processing"""
    pyro_file = pyroexr.load(file)

    channel = pyro_file.channel(chan)
    od_chan = np.where(channel == 0, 1000, channel)

    kernel_s = np.array([-1, 1])
    kernel = np.repeat(kernel_s[:, np.newaxis], 3, axis=1)

    edges = signal.convolve2d(od_chan, kernel, boundary='symm', mode='same')
    edges_max = np.max(edges)
    edges_min = np.min(edges)
    threshold = (edges_max - edges_min) * 0.1 + edges_min
    edges = (edges < threshold).astype(int)

    bucket_size = 32
    feature_size = bucket_size - 2
    rows, cols = np.where(edges == 1)

    # Special Sauce
    for x, y in zip(rows, cols):
        try:
            if np.all(edges[x, y:y + feature_size] == 1):
                grid_idx = (x // bucket_size, y // bucket_size)
                start_idx = grid_idx[1] * bucket_size
                end_idx = grid_idx[1] * bucket_size + bucket_size

                if set(list(range(y, y + feature_size))).issubset(set(list(range(start_idx, end_idx)))):
                    # print("It's a subset\n")
                    edges[x, y] = 1

                else:
                    edges[x, y] = 0
            else:
                edges[x, y] = 0
        except IndexError:
            pass

    row_indices, col_indices = np.where(edges == 1)

    viz = np.zeros_like(edges)

    for row_idx, col_idx in zip(row_indices, col_indices):
        viz[row_idx:row_idx + feature_size, col_idx:col_idx + feature_size] = 1

    # plt.imshow(channel)
    # plt.imshow(viz, alpha=0.7)
    # plt.show()

    if np.any(edges == 1):
        return file

if __name__ == "__main__":
    pass
    import time

    t1 = time.time()
    # result = detect_edges(r'X:\JFT\01_SHOTS\SC0700_BRACHIOSAURUS\Render\LGT\Camera_500offset_550_600_700_v03\layout\v36\test\sc0700_layout_v36.10511.exr', 'R')
    # # print(detect_edges(r'X:\JFT\01_SHOTS\SC0200_PTERODACTYL\Render\LGT\Camera2_3_4\layout\v16\sc0200_layout_lpe_spec-gloss_transmission_indirect_v16.0918.exr', 'R'))
    # result = detect_edges(r'X:\JFT\01_SHOTS\SC1150\Render\Camera_600_700\volume\v27\volume_v27.4638.exr', 'R')
    # # result = detect_edges(r"X:\JFT\01_SHOTS\SC0550_SKELETON\render\LGT\Camera_500offset_550_600_700_v02\layout\v50\sc0550_layout_data_v50.08290.exr", "A")
    result = detect_edges(r"X:\JFT\01_SHOTS\SC0550_SKELETON\render\LGT\Camera_500offset_550_600_700_v02\test\v50\sc0550_layout_v50.08695.exr", "R")
    print(f"detect_edges took {time.time()-t1}s. to complete.")
    if result:
        print("Possible problem detected\n")

    