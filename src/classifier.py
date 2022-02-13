from pathlib import Path
import time

from joblib import dump, load
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
import numpy as np
from rich.console import Console

import dataset.advanced as adv_dataset
import dataset.basic as basic_dataset
import dataset.vdm as vdm_dataset


console = Console()


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
    chosen_features = [all_features[f] for f in feature_labels]
    X = np.hstack(chosen_features)
    return X


def scale_down_dataset(all_features, labels, factor):
    scaled_all_features = {k: feature[::factor] for k, feature in all_features.items()}
    scaled_labels = labels[::factor]
    return scaled_all_features, scaled_labels


def train(clf, X, y, dbg=False):
    start = time.time()
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    if dbg: 
        console.log(f'Training with {len(X_train)} samples and {len(X_train[0])} features...')
    clf.fit(X_train, y_train)
    if dbg: 
        console.log(f'Training took {time.time()-start:.2f} s')
    score = accuracy_score(clf.predict(X_test), y_test)
    if dbg: 
        console.log(f'Score: {score}')
    return score


def get_test_instance(clf, all_features, labels, feature_labels):
    X = choose_features(all_features, feature_labels)
    y = labels
    score = train(clf, X, y)
    return clf, score


def get_instance(feature_labels, rebuild=False, ds='basic'):
    clf_path = Path(f'.cache/{ds}_classifier.joblib')
    if rebuild or not clf_path.exists():
        console.log("Fetching dataset...")
        all_features, labels = fetch_dataset(ds)
        X = choose_features(all_features, feature_labels)
        y = labels
        clf = make_pipeline(StandardScaler(), GaussianNB())
        train(clf, X, y, dbg=True)
        dump(clf, clf_path)
    else:
        clf = load(clf_path)
    return clf


if __name__ == '__main__':
    features = ('G', 'H', 'CIEL', 'CIEA')
    clf = get_instance(features, rebuild=True, ds='adv')
    console.log(f'Classifier retrieved.')
