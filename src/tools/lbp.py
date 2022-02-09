from numpy.lib.function_base import append
import src.data.basic as basic_dataset
#import imgtools as tools
import numpy as np
import cv2
from skimage import img_as_ubyte
from matplotlib import pyplot as plt


def percentile_whitebalance(image, percentile_value): 
    whitebalanced = img_as_ubyte((image*1.0 / np.percentile(image, percentile_value, axis=(0, 1))).clip(0, 1))
    return whitebalanced


def selective_wb(image): 
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
    image = np.uint8(image)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    image = cv2.erode(image, kernel, iterations = 6)
    image = cv2.dilate(image, kernel, iterations = 5)
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return image


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


def equalize_y(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    image[:, :, 0] = cv2.equalizeHist(image[:, :, 0])
    image = cv2.cvtColor(image, cv2.COLOR_YCrCb2BGR)
    return image


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


def gamma_correction(image, gamma):
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	return cv2.LUT(image, table)


def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
    return result

'''
def stupid(img):
    rgb_planes = cv2.split(img)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)
    result = cv2.merge(result_planes)
    return result
'''

def erase_colors(image, red = False, yellow = False, white = False):
    image_hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    output_image = image.copy()

    min_red1 = np.array([161, 155, 84])
    max_red1 = np.array([179, 255, 255])
    min_red2 = np.array([0, 50, 70])
    max_red2 = np.array([9, 255, 255])
    min_yellow = np.array([25, 50, 70])
    max_yellow = np.array([35, 255, 255])
    min_white = np.array([0, 0, 213])
    max_white = np.array([180, 18, 255])

    if red:
        mask = cv2.inRange(image_hsv, min_red1, max_red1)
        output_image[np.where(mask!=0)] = 0
        mask = cv2.inRange(image_hsv, min_red2, max_red2)
        output_image[np.where(mask!=0)] = 0
    if yellow:
        mask = cv2.inRange(image_hsv, min_yellow, max_yellow)
        output_image[np.where(mask!=0)] = 0
    if white:
        mask = cv2.inRange(image_hsv, min_white, max_white)
        output_image[np.where(mask!=0)] = 0
    
    return output_image


def main():
    imgs = basic_dataset.get_test_imgs()
    img = imgs[1]

    img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    min_yellow = np.array([200, 255, 0])
    max_yellow = np.array([255, 255, 255])
    mask = cv2.inRange(img_hsv, min_yellow, max_yellow)
    output_img = img.copy()
    output_img[np.where(mask!=0)] = 0

    plt.imshow(output_img)
    plt.show()

if __name__ == "__main__":
    main()