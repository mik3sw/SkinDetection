from pathlib import Path
import time

from joblib import dump, load
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
#from sklearn.tree import DecisionTreeClassifier
import numpy as np

import src.data.advanced as adv_dataset
import src.data.basic as basic_dataset
import src.data.vdm as vdm_dataset
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


# Features:
# * color RGB
# * color YCbCr
# * color HSV
# * LBP pattern

# X = n sample x m features (pixel_no x [R, G, B])
# X = [[R, G, B], ...]
# y = [0, 1]


def fetch_dataset(ds):
    if ds == 'adv':
        features, labels = adv_dataset.get_features_and_labels()
    elif ds == 'basic':
        features, labels = basic_dataset.get_features_and_labels()
    elif ds == 'vdm':
        features, labels = vdm_dataset.get_features_and_labels()
    else:
        raise ValueError()
    R, G, B, Y, Cr, Cb, H, S, V, CIEL, CIEA, CIEB, LBP, LBP_ROR = features
    all_features = {
        'R': R, 'G': G, 'B': B, 'Y': Y, 'Cr': Cr, 'Cb': Cb,
        'H': H, 'S': S, 'V': V, 'CIEL': CIEL, 'CIEA': CIEA, 'CIEB': CIEB,
        'LBP': LBP, 'LBP_ROR':LBP_ROR
    }
    return all_features, labels


def choose_features(all_features, feature_labels):
    #log = logging.getLogger('rich')
    #log.debug("Scelgo le features...")
    chosen_features = [all_features[f] for f in feature_labels]
    X = np.hstack(chosen_features)
    return X


def scale_down_dataset(all_features, labels, factor):
    # scaled_features = [feat[::factor] for feat in features]
    #log = logging.getLogger('rich')
    #log.debug("Scalo il dataset")
    scaled_all_features = {k: feature[::factor] for k, feature in all_features.items()}
    scaled_labels = labels[::factor]
    return scaled_all_features, scaled_labels


def train(clf, X, y, dbg=False):
    log = logging.getLogger('rich')
    start = time.time()
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    if dbg: 
        log.info(f'Training with {len(X_train)} samples and {len(X_train[0])} features...')
    clf.fit(X_train, y_train)
    if dbg: 
        log.info(f'Training took {time.time()-start:.2f} s')
    score = accuracy_score(clf.predict(X_test), y_test)
    if dbg: 
        log.info(f'Score: {score}')
    return score


def get_test_instance(clf, all_features, labels, feature_labels):
    #log = logging.getLogger('rich')
    #log.debug("Test istance")
    X = choose_features(all_features, feature_labels)
    y = labels
    score = train(clf, X, y)
    return clf, score


def get_instance(feature_labels, rebuild=False, ds='basic'):
    clf_path = Path('classifier.joblib')
    if rebuild or not clf_path.exists():
        log = logging.getLogger('rich')
        log.debug("Building dataset...")
        # X, y = fetch_adv_dataset() if adv else fetch_basic_dataset()
        all_features, labels = fetch_dataset(ds)
        # Scale down was used only for DecisionTree
        # all_features, labels = scale_down_dataset(all_features, labels, 10)
        X = choose_features(all_features, feature_labels)
        y = labels
        # X, y = fetch_dataset(adv, feature_labels)
        clf = make_pipeline(StandardScaler(), GaussianNB())
        train(clf, X, y, dbg=True)
        dump(clf, clf_path)
    else:
        clf = load(clf_path)
    return clf


if __name__ == '__main__':
    features = ('G', 'H', 'CIEL', 'CIEA')
    clf = get_instance(features, rebuild=True, ds='adv')
    log = logging.getLogger('rich')
    log.info(f'Classifier retrieved.')
