import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import pyroexr


def detect_empty(file, chan):
    """Detects empty .exrs."""
    pyro_file = pyroexr.load(file)
    channel = pyro_file.channel(chan)
    if np.all(channel == 0):
        return file


def detect_change(files, chan):
    """Detects 32x32 grid changes between frames"""
    files = files
    grid_size = 32
    # pyro_file = pyroexr.load(files[0])
    # channel = pyro_file.channel(chan)

    # print(channel.shape)

    pyro_file1 = pyroexr.load(files[0])
    channel1 = pyro_file1.channel(chan)

    pyro_file2 = pyroexr.load(files[1])
    channel2 = pyro_file2.channel(chan)

    pyro_file3 = pyroexr.load(files[2])
    channel3 = pyro_file3.channel(chan)

    num_grids_x = channel1.shape[0] // grid_size
    num_grids_y = channel1.shape[1] // grid_size

    grid_mean = np.zeros_like(channel1)
    thresh = 500

    for i in range(num_grids_x):
        for j in range(num_grids_y):
            row_start = i * grid_size
            row_end = (i + 1) * grid_size
            col_start = j * grid_size
            col_end = (j + 1) * grid_size

            grid1 = channel1[row_start:row_end, col_start:col_end]
            grid2 = channel2[row_start:row_end, col_start:col_end]
            grid3 = channel3[row_start:row_end, col_start:col_end]

            diff = np.abs(grid1 - grid2) + np.abs(grid2 - grid3) + np.abs(grid3 - grid1)
            if np.sum(grid2) == 0:
                # if diff > thresh:
                #     grid_mean[row_start:row_end, col_start:col_end] = 1
                grid_mean[row_start:row_end, col_start:col_end] = diff

    if np.any(grid_mean == 1):
        return files[1]          
    # plt.imshow(channel2)
    # plt.imshow(grid_mean, alpha=0.5)
    # plt.show()


def detect_edges(file, chan):
    """Tries to detect horizontal lines in an .exr images using a detect_edges kernel and some post processing"""
    pyro_file = pyroexr.load(file)

    channel = pyro_file.channel(chan)
    od_chan = np.where(channel == 0, 1000, channel)

    kernel_s = np.array([-1, 1])
    kernel = np.repeat(kernel_s[:, np.newaxis], 3, axis=1)

    edges = signal.convolve2d(od_chan, kernel, boundary="symm", mode="same")
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
            if np.all(edges[x, y : y + feature_size] == 1):
                grid_idx = (x // bucket_size, y // bucket_size)
                start_idx = grid_idx[1] * bucket_size
                end_idx = grid_idx[1] * bucket_size + bucket_size

                if set(list(range(y, y + feature_size))).issubset(
                    set(list(range(start_idx, end_idx)))
                ):
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
        viz[row_idx : row_idx + feature_size, col_idx : col_idx + feature_size] = 1

    if np.any(edges == 1):
        return file
