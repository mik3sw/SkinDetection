from src.tools.agc import adaptive_gamma_correction
from src.tools.lbp import erase_colors, white_balance
import configparser


def preprocess(image):
    config = configparser.ConfigParser()
    config.read('config.ini')
    if bool(config["preprocess"]["gamma_correction"]):
        image = adaptive_gamma_correction(image)
    if bool(config["preprocess"]["white_balance"]):
        image = white_balance(image)
    
    image = erase_colors(image, red=bool(config["preprocess"]["erase_red"]), yellow=bool(config["preprocess"]["erase_yellow"]), white=bool(config["preprocess"]["erase_white"]))
    return image
