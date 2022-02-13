#from lbp import fix_masks
import cv2
import numpy as np
import configparser
from tools.lbp import adjust_mask, remove_contour


'''
def remove_mask_noise(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.erode(mask, kernel, iterations=3)
    mask = cv2.dilate(mask, kernel, iterations=3)
    return mask


def adjust_mask(mask, ellipse, iteration_dilate, iteration_erode):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ellipse, ellipse))
    mask = cv2.dilate(mask, kernel, iterations=iteration_dilate)
    mask = cv2.erode(mask, kernel, iterations=iteration_erode)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    return mask


def remove_contour(mask, ellipse, iteration_dilate):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ellipse, ellipse))
    mask = cv2.dilate(mask, kernel, iterations=iteration_dilate)
    return mask
'''


def postprocess(mask):
    config = configparser.ConfigParser()
    config.read('config.ini')
    mask = mask.astype(np.double)
    mask = adjust_mask(mask, int(config["adjust_mask"]["ellipse"]), int(config["adjust_mask"]["iteration_dilate"]), int(config["adjust_mask"]["iteration_erode"]))
    mask = remove_contour(mask, int(config["remove_contour"]["ellipse"]), int(config["remove_contour"]["iteration_dilate"]))
    uint8_mask = np.uint8(mask)
    return uint8_mask
