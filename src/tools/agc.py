from math import log2, pow, exp

import cv2
import numpy as np


def normalize_array(array):
    normalized = (array - array.min()) / (array.max() - array.min())
    return normalized


def agc_bright(v, gamma):
    return pow(v, gamma)


def agc_dark(v, gamma, mean):
    numerator = pow(v, gamma)
    denominator = pow(v, gamma) + (1 - pow(v, gamma)) * pow(mean, gamma)
    return numerator / denominator


def agc_low_contrast(v_flat, mean, std):
    gamma = -log2(std)
    if 0.5 - mean <= 0:
        # I_out = I_in^gamma
        v_flat_processed = [agc_bright(v, gamma) for v in v_flat]
    else:
        # I_out = I_in^gamma / (I_in^gamma + (1 - I_in^gamma)*(mean^gamma))
        v_flat_processed = [agc_dark(v, gamma, mean) for v in v_flat]
    return np.array(v_flat_processed)


def agc_high_contrast(v_flat, mean, std):
    gamma = exp((1 - (mean+std)) / 2)
    if 0.5 - mean <= 0:
        # I_out = I_in^gamma
        v_flat_processed = [agc_bright(v, gamma) for v in v_flat]
    else:
        # I_out = I_in^gamma / (I_in^gamma + (1 - I_in^gamma)*(mean^gamma))
        v_flat_processed = [agc_dark(v, gamma, mean) for v in v_flat]
    return np.array(v_flat_processed)


def adaptive_gamma_correction(rgb_image):
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv_image)
    r, c = v.shape
    v_flat = np.reshape(hsv_image[:, :, -1], (r*c))
    v_normalized = normalize_array(v_flat)
    mean = v_normalized.mean()
    std = v_normalized.std()
    d = (mean + 2*std) - (mean - 2*std)
    t = 3
    if d <= 1/t:
        # Low contrast
        v_flat_processed = agc_low_contrast(v_normalized, mean, std)
    else:
        # High contrast
        v_flat_processed = agc_high_contrast(v_normalized, mean, std)
    v_processed = np.reshape(v_flat_processed * 255, (r, c)).astype(np.uint8)
    hsv_image_processed = cv2.merge([h, s, v_processed])
    rgb_image_processed = cv2.cvtColor(hsv_image_processed, cv2.COLOR_HSV2RGB)
    return rgb_image_processed