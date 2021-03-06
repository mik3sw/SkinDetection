import cv2
import numpy as np
from utils.lbp import diff_mask


def process_frame(skin_clf, img, bg):
    """Takes a BGR image (a opencv frame) and return a BGR processed image"""
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Trovo la "pre-maschera" attraverso 
    # differenza tra sfondo e frame
    canvas = diff_mask(rgb_img, bg)

    # Estraggo la maschera tramite il classificatore
    mask = skin_clf.extract_mask(canvas)
    mask_3d = np.dstack((mask, mask, mask))

    # sostituisco i pixel della maschera con i 
    # corrispondenti pixel dello sfondo
    is_skin = mask_3d == np.array([1, 1, 1])
    skin_replaced = np.where(is_skin, bg, rgb_img).astype(np.uint8)

    bgr_skin_replaced = cv2.cvtColor(skin_replaced, cv2.COLOR_RGB2BGR)
    return bgr_skin_replaced