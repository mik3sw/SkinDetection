import cv2
import numpy as np


def process_frame(skin_clf, img, bg):
    """Takes a BGR image (a opencv frame) and return a BGR processed image"""
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    diff = cv2.absdiff(bg, rgb_img)
    mask = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    th = 1
    imask =  mask>th
    canvas = np.zeros_like(rgb_img, np.uint8)
    canvas[imask] = rgb_img[imask]

    mask = skin_clf.extract_mask(canvas)
    mask_3d = np.dstack((mask, mask, mask))
    is_skin = mask_3d == np.array([1, 1, 1])
    skin_replaced = np.where(is_skin, bg, rgb_img).astype(np.uint8)
    bgr_skin_replaced = cv2.cvtColor(skin_replaced, cv2.COLOR_RGB2BGR)
    return bgr_skin_replaced