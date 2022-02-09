import cv2
import numpy as np
import skimage


def imread_rgb(path):
    img = cv2.imread(str(path))
    # OpenCV by default uses BGR while matplotlib uses RGB
    # conversion is necessary to explicitly use RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def imread_gray(path):
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return img


def get_rgb_values(rgb_img):
    r, c, ch = rgb_img.shape
    rgb_list = rgb_img.reshape((r*c, ch))
    return rgb_list


def get_ycrcb_values(rgb_img):
    ycrcb_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2YCrCb)
    r, c, ch = ycrcb_img.shape
    ycrcb_list = ycrcb_img.reshape((r*c, ch))
    return ycrcb_list


def get_hsv_values(rgb_img):
    hsv_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV)
    r, c, ch = hsv_img.shape
    hsv_list = hsv_img.reshape((r*c, ch))
    return hsv_list


def get_lab_values(rgb_img):
    lab_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2LAB)
    r, c, ch = lab_img.shape
    lab_list = lab_img.reshape((r*c, ch))
    return lab_list


def get_lbp_values(rgb_image):
    gray_img = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    radius = 1
    n = 8 * radius
    lbp_img = skimage.feature.local_binary_pattern(gray_img, n, radius, method='default')
    r, c = lbp_img.shape
    lbp_list = lbp_img.reshape((r*c), 1)
    return lbp_list.astype(np.uint8)


def get_lbp_ror_values(rgb_image):
    gray_img = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
    radius = 1
    n = 8 * radius
    lbp_img = skimage.feature.local_binary_pattern(gray_img, n, radius, method='ror')
    r, c = lbp_img.shape
    lbp_list = lbp_img.reshape((r*c), 1)
    return lbp_list.astype(np.uint8)


def unpack_channels(channels):
    ch1 = channels[:, 0].reshape(-1, 1)
    ch2 = channels[:, 1].reshape(-1, 1)
    ch3 = channels[:, 2].reshape(-1, 1)
    return ch1, ch2, ch3


def get_color_features(skin, noskin, extractor):
    skin_xyz_features = extractor(skin)
    noskin_xyz_features = extractor(noskin)
    xyz_features = np.concatenate((skin_xyz_features, noskin_xyz_features))
    return unpack_channels(xyz_features)

