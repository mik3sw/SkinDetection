import cv2
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import utils.imgtools as imgtools
from utils.lbp import adjust_mask, remove_contour



def remove_mask_noise(mask, close_iter, open_iter):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # little closing
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=close_iter)
    # a slightly bigger opening
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=open_iter)
    return mask


def postprocess(mask):
    mask = mask.astype(np.double)
    r, c = mask.shape
    mask = remove_mask_noise(mask, int(c/500), int(c/300))
    mask = adjust_mask(mask, 9, int(c/130), int(c/130))
    mask = remove_contour(mask, int(c/300), int(c/300))
    uint8_mask = np.uint8(mask)
    return uint8_mask


def plot_masks_and_postprocessed(mask_postprocessed_pairs):
    cols = 2
    rows = len(mask_postprocessed_pairs)
    plt.figure(1)
    for idx, (img, preproccesed) in enumerate(mask_postprocessed_pairs):
        plt.subplot2grid((rows, cols), (idx, 0))
        plt.imshow(img, 'gray')
        plt.subplot2grid((rows, cols), (idx, 1))
        plt.imshow(preproccesed, 'gray')


if __name__ == '__main__':
    proj_dir = Path(__file__).parent.parent
    masks = [imgtools.imread_bin(proj_dir / Path(f'test_data/mask{idx}.png'))
             for idx in range(4)]
    postprocessed = [postprocess(mask) for mask in masks]
    mask_postprocessed_pairs = list(zip(masks, postprocessed))
    plot_masks_and_postprocessed(mask_postprocessed_pairs)
    plt.show()