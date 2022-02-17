from pathlib import Path
import pickle
from rich.console import Console


console = Console()


def cache_exists(filename):
    features_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_features.pickle')
    labels_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_labels.pickle')
    return features_path.exists() and labels_path.exists()


def dump_features_and_labels(features, labels, filename):
    features_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_features.pickle')
    with open(features_path, 'wb') as f:
        console.log('Writing features to cache..')
        pickle.dump(features, f, pickle.HIGHEST_PROTOCOL)
    labels_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_labels.pickle')
    with open(labels_path, 'wb') as f:
        console.log('Writing labels to cache..')
        pickle.dump(labels, f, pickle.HIGHEST_PROTOCOL)


def load_features_and_labels(filename):
    console.log('Loading features and labels from cache..')
    features_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_features.pickle')
    with open(features_path, 'rb') as f:
        features = pickle.load(f)
    labels_path = Path(__file__).parent.parent.parent / Path(f'.cache/{filename}_labels.pickle')
    with open(labels_path, 'rb') as f:
        labels = pickle.load(f)
    return features, labels
