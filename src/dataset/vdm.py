from pathlib import Path
from pickletools import uint8

import numpy as np

import dataset.cache as cache
import utils.imgtools as tools


vdm_dataset_dir = Path(__file__).parent.parent.parent / Path('Datasets/VDM_Dataset')
train = vdm_dataset_dir / Path('train')
test_dir = vdm_dataset_dir / Path('test')


def get_features(img):
    r, g, b = tools.unpack_channels(tools.get_rgb_values(img))
    y, cr, cb = tools.unpack_channels(tools.get_ycrcb_values(img))
    h, s, v = tools.unpack_channels(tools.get_hsv_values(img))
    ciel, ciea, cieb = tools.unpack_channels(tools.get_lab_values(img))
    lbp = tools.get_lbp_values(img)
    lbpror = tools.get_lbp_ror_values(img)
    color_features = np.hstack((r, g, b, y, cr, cb, h, s, v, ciel, ciea, cieb, 
                        lbp, lbpror))
    return color_features


def get_labels(ann_img):
    ann_rgb  = tools.get_rgb_values(ann_img)
    labels = [1 if all(rgb == np.array([255, 0, 0])) else 0 for rgb in ann_rgb]
    return labels


def get_features_and_labels_for_image(raw, ann):
    """Red (255, 0, 0) stands for a skin pixel"""
    raw_img = tools.imread_rgb(raw)
    ann_img = tools.imread_rgb(ann)

    features = get_features(raw_img)
    labels = get_labels(ann_img)

    return features, labels


def balance_dataset(pixels_features, labels, factor):
    skin_pixels = [pixel for pixel, label in zip(pixels_features, labels) if label == 1]
    noskin_pixels = [pixel for pixel, label in zip(pixels_features, labels) if label == 0]
    # Undersample noskin pixels
    undersample_noskin_pixel = noskin_pixels[::factor]
    # Oversample skin pixels
    oversampled_skin_pixels = np.concatenate((skin_pixels, skin_pixels))
    pixels_features = np.concatenate((oversampled_skin_pixels, undersample_noskin_pixel))
    skin_labels = [1 for _ in range(len(oversampled_skin_pixels))]
    noskin_labels = [0 for _ in range(len(undersample_noskin_pixel))]
    labels = np.concatenate((skin_labels, noskin_labels))
    return pixels_features, labels


def get_features_and_labels(use_cache=True):
    """Return a list of features vectors and a list of matching labels."""
    cache_filename = 'vdm'
    if use_cache and cache.cache_exists(cache_filename):
        features_vectors, labels = cache.load_features_and_labels(cache_filename)
    else:
        all_features = []
        all_labels = []
        for train_subset in (dir for dir in train.iterdir() if dir.is_dir()):
            raw_img_gen = sorted((train_subset / Path('raw')).iterdir())
            ann_img_gen = sorted((train_subset / Path('ann')).iterdir())
            for raw_img_path, ann_img_path in zip(raw_img_gen, ann_img_gen):
                if raw_img_path.suffix == '.png' and ann_img_path.suffix == '.png':
                    i_features, i_labels = get_features_and_labels_for_image(raw_img_path, ann_img_path)
                    all_features.append(i_features)
                    all_labels.append(i_labels)
        labels = np.concatenate(all_labels)
        features = np.concatenate(all_features)
        features, labels = balance_dataset(features, labels, factor=20)
        features_no = features.shape[1]
        features_vectors = [features[:, i].reshape(-1, 1) for i in range(features_no)]
        cache.dump_features_and_labels(features_vectors, labels, cache_filename)
    return features_vectors, labels


def get_imgs_and_gts():
    imgs = []
    gts = []
    for test_subset in (dir for dir in test_dir.iterdir() if dir.is_dir()):
        raw_img_gen = sorted((test_subset / Path('raw')).iterdir())
        ann_img_gen = sorted((test_subset / Path('ann')).iterdir())
        for raw_img_path, ann_img_path in zip(raw_img_gen, ann_img_gen):
            if raw_img_path.suffix == '.png' and ann_img_path.suffix == '.png':
                raw_img = tools.imread_rgb(raw_img_path)
                ann_image = tools.imread_rgb(ann_img_path)
                gt_mask = np.alltrue(ann_image == [255, 0, 0], axis=2)
                imgs.append(raw_img)
                gts.append(np.uint8(gt_mask))
    return imgs, gts