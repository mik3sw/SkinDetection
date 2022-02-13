from collections import namedtuple, defaultdict
from contextlib import contextmanager
from statistics import mean
import time

from sklearn.metrics import confusion_matrix
from rich.console import Console


console = Console()


@contextmanager
def timer(description):
    start = time.time()
    yield
    delta = time.time() - start
    console.log(f'{description} took {delta:.4f} s')


def conf_matrix(predicted, gt):
    r, c = predicted.shape
    predicted_labels = predicted.reshape((r*c))
    gt_labels = gt.reshape((r*c))
    conf_mtx = confusion_matrix(gt_labels, predicted_labels, normalize='all')
    return conf_mtx


def get_statistics(confusion_matrix):
    tn, fp, fn, tp = confusion_matrix.ravel()
    if tn == 0 or tp == 0:
        raise ValueError('Something went really wrong')
    accuracy = (tp + tn) / (tn + fp + fn + tp)      # how many were right
    sensitivity = tp / (tp + fn)                    # true positives over expected real positives
    specifity = tn / (tn + fp)                      # true negtive over expected real negatives
    precision = tp / (tp + fp)                      # true positives over found positives
    miss_rate = fn / (fn + tp)                      # false negative over real positives
    stats = {
        'accuracy': accuracy,
        'sensitivity': sensitivity,
        'specifity': specifity,
        'precision': precision,
        'miss rate': miss_rate,
    }
    return stats


def get_overall_statistics(confusion_matrixes):
    Stat = namedtuple('Stat', ['name', 'mean', 'min', 'max'])
    aggregated_stats = defaultdict(list)
    for cm in confusion_matrixes:
        for stat, value in get_statistics(cm).items():
            aggregated_stats[stat].append(value)
    overall_stats = [Stat(stat, mean(v), min(v), max(v)) 
                        for stat, v in aggregated_stats.items()]
    return overall_stats
