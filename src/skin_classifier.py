import configparser
import numpy as np
import matplotlib.pyplot as plt

import src.classifier as classifier
import src.data.basic as basic_dataset
import src.tools.imgtools as tools
from src.core.preprocessing import preprocess
from src.core.postprocessing import postprocess
import src.stats as stats


def plot_imgs_and_masks(imgs, masks, preprocessed, figure):
    assert len(imgs) == len(masks), 'Each image must have a corresponding mask'
    cols = len(imgs)
    rows = 3
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


class SkinClassifier:
    def __init__(self, features, clf=None, ds='adv'):
        self.features = features    # ('G', 'H', 'A*') for example
        if clf is None:
            config = configparser.ConfigParser()
            config.read('config.ini')
            if config['classifier']['rebuild'] == 'True':
                reb = True
            else:
                reb = False
            self.clf = classifier.get_instance(features, rebuild=reb, ds=ds)
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
        return mask
    
    def extract_mask(self, rgb_image):
        pre = preprocess(rgb_image)
        predicted = self._predict_mask(pre)
        post = postprocess(predicted)
        uint8_mask = np.uint8(post)
        return uint8_mask


def main():
    with stats.timer('Classifier build'):
        # features = ('G', 'H', 'CIEA')
        features = ('Cr', 'H', 'CIEA')      # max accuracy
        # features = ('G', 'Cr', 'CIEA')      # max precision
        # features = ('H', 'CIEL')      # max accuracy DT
        features = ('G', 'CIEL', 'CIEA')      # vdm set
        print(f'Skin Classifier based on <vdm> dataset')
        skin_clf = SkinClassifier(features, ds='vdm')

    test_imgs = basic_dataset.get_test_imgs()
    preprocessed_imgs = [preprocess(img) for img in test_imgs]
    masks = [skin_clf.extract_mask(img) for img in test_imgs]

    test_gts = basic_dataset.get_test_gts()
    cms = [stats.conf_matrix(mask, gt) for mask, gt in zip(masks, test_gts)]
    overall_stats = stats.get_overall_statistics(cms)

    print(f'Statistic   =>  mean   | min    | max')
    for stat in overall_stats:
        print(f'{stat.name:<11} =>  ', end='')
        print(f'{stat.mean:.4f} | {stat.min:.4f} | {stat.max:.4f}')

    plot_imgs_and_masks(test_imgs, masks, preprocessed_imgs, figure=1)
    plt.show()


if __name__ == '__main__':
    main()
