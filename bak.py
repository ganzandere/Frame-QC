import time
import os

import numpy as np
import matplotlib.pyplot as plt

from scipy import ndimage
from scipy import signal

import pyroexr


def inspector(file, chan):
    """takes an .exr image and returns True if there's a suspected bucket problem"""
    t1 = time.time()
    pyro_file = pyroexr.load(file)

    channel = pyro_file.channel(chan)

    od_chan = np.where(channel == 0, 1000, channel)
    # edges = ndimage.maximum_filter(od_rgb, size=1)
 
    kernel_s = np.array([-1, 1])
    kernel = np.repeat(kernel_s[:, np.newaxis], 3, axis=1)

    edges = signal.convolve2d(od_chan, kernel, boundary='symm', mode='same')
    # edges = ndimage.sobel(red_chan, axis=0)
    edges_max = np.max(edges)
    edges_min = np.min(edges)

    threshold = (edges_max - edges_min) * 0.1 + edges_min

    edges = (edges < threshold).astype(int)

    kernel_s = np.array([1])
    kernel = np.repeat(kernel_s[:, np.newaxis], 30, axis=1)

    # cols = 28
    # half_n = cols//2

    # x = np.linspace(0, 1, half_n)
    # y = 3 * x
    # kernel = np.concatenate((y, y[::-1]))
    # kernel = np.resize(np.round(kernel).astype(int), [1, cols])
    # kernel = np.where(kernel == 2, 1, kernel)
    # kernel = np.repeat(kernel[np.newaxis, :], cols, axis=0)

    result = signal.convolve2d(
        edges, kernel, mode='same', boundary='fill', fillvalue=0)
    result = np.where(result >= 30, 1, 0)

    # mean = np.mean(edges)
    # std = np.std(edges)
    # normalized_edges = (edges - mean) / std

    # radius = red_chan.shape[0]//2
    # center = (radius, radius)
    # x = np.arange(red_chan.shape[0])
    # y = np.arange(red_chan.shape[1])
    # xx, yy = np.meshgrid(x, y)
    # distance = np.sqrt((xx-center[0])**2 + (yy-center[1])**2)
    # mask = np.where(distance <= (radius-radius*.01), True, False)

    # masked_image = result.copy()
    # masked_image[~mask] = 0

    row_indices, col_indices = np.where(result == 1)
    num_rows = 30
    viz = np.zeros_like(result)

    for row_idx, col_idx in zip(row_indices, col_indices):
        viz[row_idx:row_idx+num_rows, col_idx] = 1

    plt.imshow(channel)
    plt.imshow(ndimage.binary_dilation(edges)*1000, alpha=0.2)
    plt.show()

    plt.imshow(channel)
    plt.imshow(ndimage.binary_dilation(viz)*1000, alpha=0.5)
    plt.show()

    # plt.imshow(masked_image)
    # plt.show()

    t2 = time.time()
    print(f"Checking file: {os.path.split(file)[-1]}")
    print(f"Inspector took {(t2-t1)} seconds to complete.")

    if np.any(result == 1):
        print("Possible problem detected.\n")
        return True
    print("\n")
    return False

if __name__ == "__main__":
    # print(inspector(r'X:\JFT\01_SHOTS\SC0700_BRACHIOSAURUS\Render\LGT\Camera_500offset_550_600_700_v03\layout\v36\test\sc0700_layout_v36.10511.exr', 'R'))
    # print(inspector(r'X:\JFT\01_SHOTS\SC0200_PTERODACTYL\Render\LGT\Camera2_3_4\layout\v16\sc0200_layout_lpe_spec-gloss_transmission_indirect_v16.0918.exr', 'R'))
    print(inspector(r'X:\JFT\01_SHOTS\SC1150\Render\Camera_600_700\volume\v27\volume_v27.4638.exr', 'A'))
    
    
    