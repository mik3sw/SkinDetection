from pathlib import Path

import cv2
import numpy as np

import dataset.cache as cache
import utils.imgtools as tools


adv_dataset_dir = Path(__file__).parent.parent.parent / Path('Datasets/Advanced_Skin_Dataset')
adv_gts = adv_dataset_dir / Path('GT')
adv_original = adv_dataset_dir / Path('ORI')
adv_skin = adv_dataset_dir / Path('SKIN')
adv_noskin = adv_dataset_dir / Path('NS')


def get_skin_imgs():
    skin_folders = sorted([f for f in adv_skin.iterdir() if f.is_dir()])
    for folder in skin_folders[1:]:
        for img_path in folder.iterdir():
            yield tools.imread_rgb(img_path)


def get_noskin_imgs():
    noskin_folders = sorted([f for f in adv_noskin.iterdir() if f.is_dir()])
    for folder in noskin_folders[1:]:
        for img_path in folder.iterdir():
            yield tools.imread_rgb(img_path)


def get_original_imgs():
    for img_path in adv_original.iterdir():
        yield tools.imread_rgb(img_path)


def get_gt_imgs():
    for img_path in adv_gts.iterdir():
        gray_gt = tools.imread_gray(img_path)
        thresh, bin_gt = cv2.threshold(gray_gt, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        yield bin_gt


def get_imgs_features_and_labels(img_generator, label):
    imgs_color_features = []
    labels = []
    for img in img_generator:
        r, g, b = tools.unpack_channels(tools.get_rgb_values(img))
        y, cr, cb = tools.unpack_channels(tools.get_ycrcb_values(img))
        h, s, v = tools.unpack_channels(tools.get_hsv_values(img))
        ciel, ciea, cieb = tools.unpack_channels(tools.get_lab_values(img))
        lbp = tools.get_lbp_values(img)
        lbpror = tools.get_lbp_ror_values(img)
        color_features = np.hstack((r, g, b, y, cr, cb, h, s, v, ciel, ciea, cieb, lbp, lbpror))
        imgs_color_features.append(color_features)
        labels.extend([label for _ in range(len(r))])
    features = np.concatenate(imgs_color_features)
    return features, labels


def get_features_and_labels(use_cache=True):
    """Return a list of features vectors and a list of matching labels."""
    cache_filename = 'advanced'
    if use_cache and cache.cache_exists(cache_filename):
        features_vectors, labels = cache.load_features_and_labels(cache_filename)
    else:
        skin_features, skin_labels = get_imgs_features_and_labels(get_skin_imgs(), 1)
        noskin_features, noskin_labels = get_imgs_features_and_labels(get_noskin_imgs(), 0)
        features = np.concatenate((skin_features, noskin_features))
        labels = np.concatenate((skin_labels, noskin_labels))
        features_no = features.shape[1]
        features_vectors = [features[:, i].reshape(-1, 1) for i in range(features_no)]
        cache.dump_features_and_labels(features_vectors, labels, cache_filename)
    return features_vectors, labels
