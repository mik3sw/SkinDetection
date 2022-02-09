import itertools

#from sklearn.ensemble import RandomForestClassifier
#from sklearn.gaussian_process import GaussianProcessClassifier
#from sklearn.naive_bayes import GaussianNB
#from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
#from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier

import classifier
import src.data.advanced as adv_dataset
from src.skin_classifier import SkinClassifier
import stats as stats


def get_features_combinations(features):
    combos = []
    for lenght in range(1, len(features)+1):
        for combo in itertools.combinations(features, lenght):
            combos.append(combo)
    print(f'[*] Got {len(combos)} different combinations of features')
    return combos


def fetch_test_data(scaledown_factor):
    test_imgs = list(adv_dataset.get_original_imgs())
    test_gts = list(adv_dataset.get_gt_imgs())
    assert len(test_gts) == len(test_gts)
    reduced_data = list(zip(test_imgs, test_gts))[::scaledown_factor]
    test_imgs, test_gts = zip(*reduced_data)
    print(f'[*] Fetched {len(test_imgs)} test and gt images')
    return test_imgs, test_gts


def get_metrics(skin_clf, test_imgs, test_gts):
    predicted_masks = (skin_clf.extract_mask(img) for img in test_imgs)
    cms = (stats.conf_matrix(mask, gt) for mask, gt in zip(predicted_masks, test_gts))
    metrics = stats.get_overall_statistics(cms)
    return metrics


def print_combo_item(item):
    features, score, metrics = item
    print(f'Accuracy: {score:.5f}. Features: {features}')
    for stat in metrics:
        print(f'    {stat.name:<11} =>  ', end='')
        print(f'{stat.mean:.4f} | {stat.min:.4f} | {stat.max:.4f}')


def print_test_statistics(combos_metrics, to_exclude, top_n=10):
    print(f'[+] Top-{top_n} other features and scores:')
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
    print('[+] Minimal mean miss rate found with:')
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
    print('[+] Max mean accuracy found with:')
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
    print('[+] Max mean precision found with:')
    print_combo_item(max_item)
    return max_item[0]


def print_progress(mark='.'):
    print(mark, end='', flush=True)



def main():
    # clf = make_pipeline(StandardScaler(), GaussianNB())
    clf = make_pipeline(StandardScaler(), DecisionTreeClassifier())
    # clf = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3))
    # clf = RandomForestClassifier(max_depth=2, random_state=0)
    # clf = GaussianProcessClassifier(random_state=0)
    # clf = SVC(kernel='poly', random_state=0)

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
        'CIEL', 
        'CIEA', 
        # 'CIEB', 
        # 'LBP', 
        # 'LBP_ROR'
    )

    print('[+] Testing feature combinations on Scaled Gaussian Classifier..')
    dataset = 'vdm'
    print(f'[+] Using <{dataset}> datatset..')
    all_features, labels = classifier.fetch_dataset(ds=dataset)
    pixels_no = len(labels)
    print(pixels_no)
    skin_pixels_no = len(['a' for i in labels if i == 1])
    print(skin_pixels_no)
    print(f'ratio: {skin_pixels_no/pixels_no:0.2f}')
    # all_features, labels = classifier.scale_down_dataset(all_features, labels, 32)
    sample_no = len(all_features['R'])
    print(f'[+] Dataset made of {sample_no} samples')
    combinations = get_features_combinations(features)
    test_imgs, test_gts = fetch_test_data(scaledown_factor=64)


    combos_metrics = []
    for features in combinations:
        test_clf, score = classifier.get_test_instance(clf, all_features, labels, features)
        if score > .90:
            # we're only interested in classifiers with an accuracy > 90 %
            # print_progress(mark='P')
            skin_clf = SkinClassifier(features, clf=test_clf)
            try:
                metrics = get_metrics(skin_clf, test_imgs, test_gts)
                combos_metrics.append((features, score, metrics))
                print_progress()
            except ValueError:
                print_progress(mark='x')
        else:
            print_progress(mark='_')
    print()

    miss_rate_feature = print_min_miss_rate(combos_metrics)
    accuracy_feature = print_max_accuracy(combos_metrics)
    precision_feature = print_max_precision(combos_metrics)
    to_exclude = set([miss_rate_feature, accuracy_feature, precision_feature])
    print_test_statistics(combos_metrics, to_exclude)

if __name__ == '__main__':
    main()
