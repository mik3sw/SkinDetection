import itertools

#from sklearn.ensemble import RandomForestClassifier
#from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.naive_bayes import GaussianNB
#from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
#from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier
from rich.console import Console

import classifier
import dataset.advanced as adv_dataset
import dataset.vdm as vdm_dataset
from skin_classifier import SkinClassifier
import stats


console = Console()


def get_features_combinations(features):
    combos = []
    for lenght in range(1, len(features)+1):
        for combo in itertools.combinations(features, lenght):
            combos.append(combo)
    console.log(f'Got {len(features)} features and {len(combos)} combinations')
    return combos


def fetch_sfa_test_data(scaledown_factor):
    test_imgs = list(adv_dataset.get_original_imgs())
    test_gts = list(adv_dataset.get_gt_imgs())
    assert len(test_gts) == len(test_gts)
    reduced_data = list(zip(test_imgs, test_gts))[::scaledown_factor]
    test_imgs, test_gts = zip(*reduced_data)
    console.log(f'Fetched {len(test_imgs)} test and gt images from SFA')
    return test_imgs, test_gts


def fetch_vdm_test_data(scaledown_factor=1):
    imgs, gts = vdm_dataset.get_imgs_and_gts()
    assert len(imgs) == len(gts)
    reduced_data = list(zip(imgs, gts))[::scaledown_factor]
    imgs, gts = zip(*reduced_data)
    console.log(f'Fetched {len(imgs)} test and gt images from VDM')
    return imgs, gts


def get_metrics(skin_clf, test_imgs, test_gts):
    predicted_masks = (skin_clf.extract_mask(img) for img in test_imgs)
    cms = (stats.conf_matrix(mask, gt) for mask, gt in zip(predicted_masks, test_gts))
    metrics = stats.get_overall_statistics(cms)
    return metrics


def print_combo_item(item):
    features, score, metrics = item
    print(f'Accuracy: {score:.5f}. Features: {features}')
    for stat in metrics:
        if stat.name in ('sensitivity', 'specifity'):
            continue
        print(f'    {stat.name:<11} =>  ', end='')
        print(f'{stat.mean:.4f} | {stat.min:.4f} | {stat.max:.4f}')


def print_test_statistics(combos_metrics, to_exclude, top_n=5):
    console.rule(f'Top-{top_n} other features and scores:')
    combos_sorted_desc = sorted(combos_metrics, key=lambda triple: triple[1], reverse=True)
    for item in combos_sorted_desc[:top_n]:
        if item[0] not in to_exclude:
            print_combo_item(item)


def print_min_miss_rate(combos_metrics):
    max_miss_rate = 1
    for item in combos_metrics:
        _, _, metrics = item
        mean_miss_rate = metrics[4].mean
        if mean_miss_rate < max_miss_rate:
            max_miss_rate = mean_miss_rate
            min_item = item
    console.rule('Minimal mean miss rate found with:')
    print_combo_item(min_item)
    return min_item[0]


def print_max_accuracy(combos_metrics):
    min_accuracy = 0
    for item in combos_metrics:
        _, _, metrics = item
        mean_accuracy = metrics[0].mean
        if mean_accuracy > min_accuracy:
            min_accuracy = mean_accuracy
            max_item = item
    console.rule('Max mean accuracy found with:')
    print_combo_item(max_item)
    return max_item[0]


def print_max_precision(combos_metrics):
    min_precision = 0
    for item in combos_metrics:
        _, _, metrics = item
        mean_precision = metrics[3].mean
        if mean_precision > min_precision:
            min_precision = mean_precision
            max_item = item
    console.rule('Max mean precision found with')
    print_combo_item(max_item)
    return max_item[0]


def print_progress(mark='.'):
    print(mark, end='', flush=True)


def main():
    clf = make_pipeline(StandardScaler(), GaussianNB())
    # clf = make_pipeline(StandardScaler(), DecisionTreeClassifier())
    # clf = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3))
    # clf = RandomForestClassifier(max_depth=2, random_state=0)
    # clf = GaussianProcessClassifier(random_state=0)
    # clf = SVC(kernel='poly', random_state=0)

    # Choose here the features you want to test
    features = (
        # 'R', 
        'G', 
        # 'B', 
        # 'Y', 
        'Cr', 
        # 'Cb', 
        'H', 
        # 'S', 
        # 'V', 
        # 'CIEL', 
        'CIEA', 
        'CIEB', 
        # 'LBP', 
        # 'LBP_ROR'
    )

    dataset = 'vdm'
    threshold = .85

    all_features, labels = classifier.fetch_dataset(ds=dataset)
    if dataset == 'adv':
        all_features, labels = classifier.scale_down_dataset(all_features, labels, 32)

    pixels_no = len(labels)
    skin_pixels_no = len(['a' for i in labels if i == 1])
    sample_no = len(all_features['R'])

    console.rule('TESTER')
    console.log(f'Testing feature combinations on {clf}')
    console.log(f'Using <{dataset}> dataset..')
    console.log(f'Total number of pixels: {pixels_no}')
    console.log(f'skin/total ratio: {skin_pixels_no/pixels_no:0.2f}')
    console.log(f'Dataset made of {sample_no} samples')
    console.log(f'Threshold for analysis set at: {threshold*100} %')

    combinations = get_features_combinations(features)
    test_imgs, test_gts = fetch_sfa_test_data(scaledown_factor=64)
    vdm_imgs, vdm_gts = fetch_vdm_test_data(scaledown_factor=5)

    console.rule('Pre/Post Processing Setup')
    console.log('No Preprocessing at all')
    console.rule()

    combos_metrics_sfa = []
    combos_metrics_vdm = []
    for features in combinations:
        test_clf, score = classifier.get_test_instance(clf, all_features, labels, features)
        if score > threshold:
            skin_clf = SkinClassifier(features, clf=test_clf, ds=dataset)
            metrics_sfa = get_metrics(skin_clf, test_imgs, test_gts)
            combos_metrics_sfa.append((features, score, metrics_sfa))
            metrics_vdm = get_metrics(skin_clf, vdm_imgs, vdm_gts)
            combos_metrics_vdm.append((features, score, metrics_vdm))
            print_progress()
            
        else:
            print_progress(mark='_')
    print()

    console.rule('SFA GTs Report')
    miss_rate_feature_sfa = print_min_miss_rate(combos_metrics_sfa)
    accuracy_feature_sfa = print_max_accuracy(combos_metrics_sfa)
    precision_feature_sfa = print_max_precision(combos_metrics_sfa)
    to_exclude_sfa = set([miss_rate_feature_sfa, accuracy_feature_sfa, precision_feature_sfa])
    print_test_statistics(combos_metrics_sfa, to_exclude_sfa)

    console.rule('VDM GTs Report')
    miss_rate_feature_vdm = print_min_miss_rate(combos_metrics_vdm)
    accuracy_feature_vdm = print_max_accuracy(combos_metrics_vdm)
    precision_feature_vdm = print_max_precision(combos_metrics_vdm)
    to_exclude_vdm = set([miss_rate_feature_vdm, accuracy_feature_vdm, precision_feature_vdm])
    print_test_statistics(combos_metrics_vdm, to_exclude_vdm)


if __name__ == '__main__':
    main()