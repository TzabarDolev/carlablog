## The following code is a part of disparity measurements section at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/09/20/disparity-in-stereo-cameras-measuring-understanding-and-its-crucial-role/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.


import cv2
from PIL import Image
import numpy as np
from tqdm import *
import matplotlib.pyplot as plt
import os

BLOCK_SIZE = 7
SEARCH_BLOCK_SIZE = 56


def sum_of_abs_diff(pixel_vals_1, pixel_vals_2):
    if pixel_vals_1.shape != pixel_vals_2.shape:
        return -1

    return np.sum(abs(pixel_vals_1 - pixel_vals_2))


def compare_blocks(y, x, block_left, right_array, block_size=5):

    # Get search range for the right image
    x_min = max(0, x - SEARCH_BLOCK_SIZE)
    x_max = min(right_array.shape[1], x + SEARCH_BLOCK_SIZE)

    first = True
    min_sad = None
    min_index = None
    for x in range(x_min, x_max):
        block_right = right_array[y: y+block_size,
                                  x: x+block_size]
        sad = sum_of_abs_diff(block_left, block_right)

        if first:
            min_sad = sad
            min_index = (y, x)
            first = False
        else:
            if sad < min_sad:
                min_sad = sad
                min_index = (y, x)

    return min_index


def get_disparity_map(left_img, right_img):

    left_array = cv2.cvtColor(left_img, cv2.COLOR_RGB2GRAY)
    right_array = cv2.cvtColor(right_img, cv2.COLOR_RGB2GRAY)

    left_array = left_array.astype(int)
    right_array = right_array.astype(int)
    if left_array.shape != right_array.shape:
        raise "Left-Right image shape mismatch!"
    h, w = left_array.shape
    disparity_map = np.zeros((h, w))
    # Go over each pixel position
    for y in tqdm(range(BLOCK_SIZE, h-BLOCK_SIZE)):
        for x in range(BLOCK_SIZE, w-BLOCK_SIZE):
            block_left = left_array[y:y + BLOCK_SIZE,
                                    x:x + BLOCK_SIZE]
            min_index = compare_blocks(y, x, block_left,
                                       right_array,
                                       block_size=BLOCK_SIZE)
            disparity_map[y, x] = abs(min_index[1] - x)

    cv2.imwrite('disp.png', disparity_map)

    return disparity_map


if __name__ == '__main__':
    # loading the images
    left_img = cv2.cvtColor(cv2.imread("img_l.png"), cv2.COLOR_BGR2RGB)
    right_img = cv2.cvtColor(cv2.imread("img_r.png"), cv2.COLOR_BGR2RGB)

    disparity_map = get_disparity_map(left_img, right_img)

    plt.style.use('seaborn-white')
    plotting_data = [left_img, right_img, disparity_map]
    plotting_titles = ['left image', 'right image', 'disparity map']
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(12, 4))
    for i, ax in enumerate(axs.flatten()):
        plt.sca(ax)
        plt.imshow(plotting_data[i])
        plt.axis('off')
        # plt.title(plotting_titles[i])

    plt.tight_layout()
    # plt.suptitle('Disparity measurements')
    plt.savefig('plot.jpg')
    plt.show()

