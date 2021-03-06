from numpy.lib.function_base import append
import dataset.basic as basic_dataset
#import imgtools as tools
import numpy as np
import cv2
from skimage import img_as_ubyte
#from matplotlib import pyplot as plt


def percentile_whitebalance(image, percentile_value):
    # sostituito con funzione nuova 
    whitebalanced = img_as_ubyte((image*1.0 / np.percentile(image, percentile_value, axis=(0, 1))).clip(0, 1))
    return whitebalanced


def selective_wb(image): 
    # sostituito con funzione nuova
    (n, bins) = np.histogram(image.ravel(), 256)
    r = image.shape[0]
    c = image.shape[1]
    size = r * c
    white = n[255]
    perc = white / size * 100
    if perc > 5:
        image = percentile_whitebalance(image, 65)
    return image


def fix_masks(image):
    # non usata in postprocessing
    image = np.uint8(image)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    image = cv2.erode(image, kernel, iterations = 6)
    image = cv2.dilate(image, kernel, iterations = 5)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return image


def adjust_mask(mask, size, iteration_dilate, iteration_erode):
    # esegue una dilate e una erode per eliminare dettagli come occhi ecc ecc
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    mask = cv2.dilate(mask, kernel, iterations=iteration_dilate)
    mask = cv2.erode(mask, kernel, iterations=iteration_erode)
    mask = cv2.GaussianBlur(mask, (3, 3), 0)
    return mask


def remove_contour(mask, size, iteration_dilate):
    # effettua un'ulteriore dilate per eliminare quanto 
    # più possibile il "contorno" che si crea intorno alla maschera
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    mask = cv2.dilate(mask, kernel, iterations=iteration_dilate)
    return mask


def equalize_y(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    image[:, :, 0] = cv2.equalizeHist(image[:, :, 0])
    image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)
    return image


# ritorna true se l'immagine è rumorosa
def noisy(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([image], [1], None, [256], [0, 256])
    p = 0.05
    hist_perc = np.sum(hist[int(p * 255):-1]) / np.prod(image.shape[0:2])
    threshold = 0.5
    return hist_perc < threshold


def mean_filter(image):
    kernel = np.ones((5,5), np.float32) / 25
    dst = cv2.filter2D(image,-1,kernel)
    return dst


# sostituita da acg.py
def gamma_correction(image, gamma):
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	return cv2.LUT(image, table)


def white_balance(img):
    # Lavora con spazio colore LAB
    # L per la luminosità e a e b per le dimensioni colore
    # (contiene tutti i colori visibili)
    result = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    # L: result[:, :, 0]
    # A: result[:, :, 1]
    # B: result[:, :, 2]

    # In opencv per le immagini a 8 bit 
    # c'è questa configurazione default:
    # L: L / 100 * 255
    # A: A + 128
    # B: B + 128  

    # Trovo il valore medio dei canali A e B
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])

    # (AVG - 128) * ((L/255)*1.1)

    # Ricalcolo ogni pixel
    # il valore che abbiamo modificato è '1.1'
    # aumentandolo l'immagine assume sempre di più
    # colori freddi, tendenti al blu
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)

    # Trasformo da LAB ad RGB
    result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
    return result


def erase_colors(image, red = False, yellow = False, white = False, orange = False):
    image_hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    output_image = image.copy()

    min_red1 = np.array([161, 155, 84])
    max_red1 = np.array([179, 255, 255])
    min_red2 = np.array([0, 50, 70])
    max_red2 = np.array([9, 255, 255])
    min_red3 = np.array([116,116,0])
    max_red3 = np.array([255,255,255])
    min_yellow = np.array([25, 50, 70])
    max_yellow = np.array([35, 255, 255])
    min_yellow2 = np.array([0, 150, 150])
    max_yellow2 = np.array([255, 255, 255])
    min_white = np.array([0, 0, 213])
    max_white = np.array([180, 18, 255])

    min_orange = np.array([0, 167, 0])
    max_orange = np.array([179, 255, 255])

    if red:
        mask = cv2.inRange(image_hsv, min_red1, max_red1)
        output_image[np.where(mask!=0)] = 0
        mask = cv2.inRange(image_hsv, min_red2, max_red2)
        output_image[np.where(mask!=0)] = 0
        mask = cv2.inRange(image_hsv, min_red3, max_red3)
        output_image[np.where(mask!=0)] = 0
    if yellow:
        mask = cv2.inRange(image_hsv, min_yellow, max_yellow)
        output_image[np.where(mask!=0)] = 0
        mask = cv2.inRange(image_hsv, min_yellow2, max_yellow2)
        output_image[np.where(mask!=0)] = 0
    if white:
        mask = cv2.inRange(image_hsv, min_white, max_white)
        output_image[np.where(mask!=0)] = 0
    if orange:
        mask = cv2.inRange(image_hsv, min_orange, max_orange)
        output_image[np.where(mask!=0)] = 0

    return output_image


def diff_mask(img, bg):
    diff = bg.copy()

    # differenza tra frame e sfondo:
    # otteniamo che dove i pixel sono uguali il valore
    # della differenza è 0 (nero)
    cv2.absdiff(bg, img, diff)
    mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Attraverso un thresholding otteniamo 
    # una sorta di maschera che ci fa capire 
    # più o meno in che regione del frame si trovano
    # le differenza tra frame e sfondo
    # Quindi verosimilmente dove si trova il soggetto del video
    (T, thresh) = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)

    # Adesso facciamo una dilate molto pesante 
    # per cercare di avere una maschera il più
    # omogenea possibile (senza buchi in mezzo)
    # e che identifica la regione in cui si 
    # trova il soggetto del video
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    thresh = cv2.dilate(thresh, kernel, iterations=10)

    # Aggiustiamo la maschera con delle erode e blur
    #thresh = cv2.erode(thresh, kernel, iterations=1)
    #thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

    # creo e ritorno la maschera a colori (RGB)
    th = 1
    imask =  thresh>th
    canvas = np.zeros_like(img, np.uint8)
    canvas[imask] = img[imask]
    canvas = erase_colors(canvas, white=True)
    return canvas


def main():
    # main usato solo per test
    imgs = basic_dataset.get_test_imgs()
    img = imgs[1]

    img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    min_yellow = np.array([200, 255, 0])
    max_yellow = np.array([255, 255, 255])
    mask = cv2.inRange(img_hsv, min_yellow, max_yellow)
    output_img = img.copy()
    output_img[np.where(mask!=0)] = 0

    #plt.imshow(output_img)
    #plt.show()

if __name__ == "__main__":
    main()
