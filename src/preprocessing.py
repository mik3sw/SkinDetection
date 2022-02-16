from utils.agc import adaptive_gamma_correction
from utils.lbp import erase_colors, white_balance
import utils.imgtools as imgtools
from pathlib import Path
import matplotlib.pyplot as plt


def preprocess(image):
    try:
        image = adaptive_gamma_correction(image)
    except Exception as e:
        pass
    image = white_balance(image)
    
    r = True
    y = True
    w = True
    o = True
    
    image = erase_colors(image, red=r, yellow=y, white=w, orange=o)
    return image


def plot_imgs_and_preprocessed(img_preprocessed_pairs):
    cols = 2
    rows = len(img_preprocessed_pairs)
    plt.figure(1)
    for idx, (img, preproccesed) in enumerate(img_preprocessed_pairs):
        plt.subplot2grid((rows, cols), (idx, 0))
        plt.imshow(img)
        plt.subplot2grid((rows, cols), (idx, 1))
        plt.imshow(preproccesed)


if __name__ == '__main__':
    proj_dir = Path(__file__).parent.parent
    yellowish_light = imgtools.imread_rgb(proj_dir / Path('test_data/YellowishLightTest.jpg'))
    over_exposed = imgtools.imread_rgb(proj_dir / Path('test_data/OverExposedTest.jpg'))
    ele_skin = imgtools.imread_rgb(proj_dir / Path('test_data/EleSkin.png'))
    test_imgs = [yellowish_light,
                 over_exposed,
                 ele_skin,]
    preprocessed = [preprocess(img) for img in test_imgs]
    img_preprocessed_pairs = list(zip(test_imgs, preprocessed))
    plot_imgs_and_preprocessed(img_preprocessed_pairs)
    plt.show()
    