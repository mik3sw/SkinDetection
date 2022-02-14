from src.tools.agc import adaptive_gamma_correction
from src.tools.lbp import erase_colors, white_balance
import configparser


def preprocess(image):
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Controllo il file config.ini ed in base alle impostazioni
    # esegue o meno certe operazioni di preprocessing

    if config["preprocess"]["gamma_correction"] == "True":
        image = adaptive_gamma_correction(image)
    if config["preprocess"]["white_balance"] == "True":
        image = white_balance(image)
    
    if config["preprocess"]["erase_red"] == "True":
        r = True
    else:
        r = False
    
    if config["preprocess"]["erase_yellow"] == "True":
        y = True
    else:
        y = False
    
    if config["preprocess"]["erase_white"] == "True":
        w = True
    else:
        w = False
    
    if config["preprocess"]["erase_orange"] == "True":
        o = True
    else:
        o = False
    
    image = erase_colors(image, red=r, yellow=y, white=w, orange=o)
    return image
