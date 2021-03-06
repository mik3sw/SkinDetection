import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from rich.console import Console

import classifier as classifier
import dataset.basic as basic_dataset
import dataset.vdm as vdm_dataset
import utils.imgtools as tools
from preprocessing import preprocess
from postprocessing import postprocess
import utils.stats as stats


console = Console()


def plot_imgs_and_masks(imgs, masks, preprocessed, postprocessed, figure):
    cols = len(imgs)
    rows = 4
    plt.figure(figure)
    for idx, img in enumerate(imgs):
        plt.subplot2grid((rows, cols), (0, idx))
        plt.imshow(img)
    for idx, img in enumerate(preprocessed):
        plt.subplot2grid((rows, cols), (1, idx))
        plt.imshow(img)
    for idx, mask in enumerate(masks):
        plt.subplot2grid((rows, cols), (2, idx))
        plt.imshow(mask, 'gray')
    for idx, mask in enumerate(postprocessed):
        plt.subplot2grid((rows, cols), (3, idx))
        plt.imshow(mask, 'gray')


class SkinClassifier:
    def __init__(self, features, clf=None, ds='adv', rebuild=True):
        self.features = features    # ('G', 'H', 'A*') for example
        if clf is None:
            self.clf = classifier.get_instance(features, rebuild=rebuild, ds=ds)
        else:
            self.clf = clf
    
    def _extract_all_features(self, img):
        R, G, B = tools.unpack_channels(tools.get_rgb_values(img))
        Y, Cr, Cb = tools.unpack_channels(tools.get_ycrcb_values(img))
        H, S, V = tools.unpack_channels(tools.get_hsv_values(img))
        CIEL, CIEA, CIEB = tools.unpack_channels(tools.get_lab_values(img))
        LBP = tools.get_lbp_values(img).reshape(-1, 1)
        LBP_ROR = tools.get_lbp_ror_values(img).reshape(-1, 1)
        all_features = {
            'R': R, 'G': G, 'B': B, 'Y': Y, 'Cr': Cr, 'Cb': Cb,
            'H': H, 'S': S, 'V': V, 'CIEL': CIEL, 'CIEA': CIEA, 'CIEB': CIEB,
            'LBP': LBP, 'LBP_ROR':LBP_ROR
        }
        return all_features

    def _predict_mask(self, img):
        rows, cols, _ = img.shape
        all_features = self._extract_all_features(img)
        chosen_features = [all_features[label] for label in self.features]
        features = np.hstack(chosen_features)
        labels = self.clf.predict(features)
        mask = labels.reshape((rows, cols))
        uint8_mask = np.uint8(mask)
        return uint8_mask
    
    def extract_mask(self, rgb_image):
        pre = preprocess(rgb_image)
        predicted = self._predict_mask(pre)
        post = postprocess(predicted)
        uint8_mask = np.uint8(post)
        return uint8_mask


def demo(skin_clf):
    basic_imgs = basic_dataset.get_test_imgs()
    basic_gts = basic_dataset.get_test_gts()

    vdm_imgs, vdm_gts = vdm_dataset.get_imgs_and_gts()
    reduced_data = list(zip(vdm_imgs, vdm_gts))[::30]
    vdm_imgs, vdm_gts = zip(*reduced_data)

    test_imgs = list(basic_imgs) + list(vdm_imgs)
    test_gts = list(basic_gts) + list(vdm_gts)

    preprocessed_imgs = [preprocess(img) for img in test_imgs]
    masks = [skin_clf._predict_mask(img) for img in preprocessed_imgs]
    postprocessed_masks = [postprocess(mask) for mask in masks]

    cms = [stats.conf_matrix(mask, gt) for mask, gt in zip(postprocessed_masks, test_gts)]
    overall_stats = stats.get_overall_statistics(cms)

    console.log(f'Statistic   =>  avg    | min    | max')
    for stat in overall_stats:
        stats_name = f'{stat.name:<11} =>  '
        stats_values = f'{stat.mean:.4f} | {stat.min:.4f} | {stat.max:.4f}'
        console.log(stats_name + stats_values)

    plot_imgs_and_masks(test_imgs, masks, 
        preprocessed_imgs, postprocessed_masks, figure=1)
    plt.show()


def main():
    with stats.timer('Classifier build'):
        dataset = 'adv'
        # dataset = 'vdm'
        if dataset == 'adv':
            features = ('G', 'H', 'CIEA')
        else:
            features = ('G', 'CIEL', 'CIEA')

        console.log(f'Skin Classifier based on <{dataset}> dataset')
        skin_clf = SkinClassifier(features, ds=dataset, rebuild=True)

        demo(skin_clf)


if __name__ == '__main__':
    main()
