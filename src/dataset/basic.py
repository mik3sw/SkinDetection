from pathlib import Path

import numpy as np

import dataset.cache as cache
import utils.imgtools as tools


dataset_dir = Path(__file__).parent.parent.parent / Path('Datasets/Basic_Skin_Dataset')
skin_path = dataset_dir / Path('skin.png')
noskin_path = dataset_dir / Path('noskin.png')


def get_test_imgs():
    test1 = tools.imread_rgb(dataset_dir / Path('test1.jpg'))
    test2 = tools.imread_rgb(dataset_dir / Path('test2.jpg'))
    test3 = tools.imread_rgb(dataset_dir / Path('test3.jpg'))
    test4 = tools.imread_rgb(dataset_dir / Path('test4.jpg'))
    return [test1, test2, test3, test4]


def get_test_gts():
    """Return a list of ground truth masks."""
    test1_gt = tools.imread_gray(dataset_dir / Path('test1-gt.png'))
    test2_gt = tools.imread_gray(dataset_dir / Path('test2-gt.png'))
    test3_gt = tools.imread_gray(dataset_dir / Path('test3-gt.png'))
    test4_gt = tools.imread_gray(dataset_dir / Path('test4-gt.png'))
    gts = [test1_gt, test2_gt, test3_gt, test4_gt]
    gts = [(gt >= 255) for gt in gts]
    return gts


def get_labels(skin, noskin):
    skin_r, skin_c, _ = skin.shape
    noskin_r, noskin_c, _ = noskin.shape
    skin_labels = [1 for _ in range(skin_r * skin_c)]
    noskin_labels = [0 for _ in range(noskin_r * noskin_c)]
    return np.concatenate((skin_labels, noskin_labels))


def get_features_and_labels(use_cache=True):
    """Return a list of features vectors and a list of matching labels."""
    cache_filename = 'basic'
    if use_cache and cache.cache_exists(cache_filename):
        features_vectors, labels = cache.load_features_and_labels(cache_filename)
    else:
        skin = tools.imread_rgb(skin_path)
        noskin = tools.imread_rgb(noskin_path)

        r, g, b = tools.get_color_features(skin, noskin, tools.get_rgb_values)
        y, cr, cb = tools.get_color_features(skin, noskin, tools.get_ycrcb_values)
        h, s, v = tools.get_color_features(skin, noskin, tools.get_hsv_values)
        ciel, ciea, cieb = tools.get_color_features(skin, noskin, tools.get_lab_values)
        lbp_skin = tools.get_lbp_values(skin)
        lbp_noskin = tools.get_lbp_values(noskin)
        lbp = np.concatenate((lbp_skin, lbp_noskin)).reshape(-1, 1)
        lbpror_skin = tools.get_lbp_ror_values(skin)
        lbpror_noskin = tools.get_lbp_ror_values(noskin)
        lbpror = np.concatenate((lbpror_skin, lbpror_noskin)).reshape(-1, 1)
        
        features = np.hstack((r, g, b, y, cr, cb, h, s, v, ciel, ciea, cieb, lbp, lbpror))
        features_no = features.shape[1]
        features_vectors = [features[:, i].reshape(-1, 1) for i in range(features_no)]
        labels = get_labels(skin, noskin)
        cache.dump_features_and_labels(features_vectors, labels, cache_filename)
    return features_vectors, labels
