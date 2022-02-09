from src.tools.agc import adaptive_gamma_correction
from src.tools.lbp import erase_colors, white_balance


def preprocess(image):
    image = adaptive_gamma_correction(image)
    image = white_balance(image)
    image = erase_colors(image, red=True, yellow=True, white=True)
    return image
