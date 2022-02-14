#from lbp import fix_masks
import cv2
import numpy as np
import configparser
from src.tools.lbp import adjust_mask, remove_contour


def postprocess(mask):
    config = configparser.ConfigParser()
    config.read('config.ini')
    mask = mask.astype(np.double)

    # Effettuo una open per eliminare i dettagli 
    # come occhi, sopracciglia, labbra ...
    # Contro: elimina anche accessori tipo 
    # bracciali, collane e simili
    mask = adjust_mask(mask, int(config["adjust_mask"]["ellipse"]), int(config["adjust_mask"]["iteration_dilate"]), int(config["adjust_mask"]["iteration_erode"]))
    
    # Effettuo una dilate (per rimuovere il contorno di pelle non rimossa)
    mask = remove_contour(mask, int(config["remove_contour"]["ellipse"]), int(config["remove_contour"]["iteration_dilate"]))
    return mask
