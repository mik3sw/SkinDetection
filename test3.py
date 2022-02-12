import cv2
from cv2 import cvtColor
from src.tools import lbp, agc
#import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import imutils
from src.skin_classifier import SkinClassifier
from src.core import frame_processor



img = cv2.imread('docs/start.png')
bg = cv2.imread('docs/bg.png')
#cv2.imshow("start", img)
#cv2.waitKey(0)
'''
fig = plt.figure()
ax = fig.add_subplot(1, 2, 1)
imgplot = plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
ax.set_title('Frame')
#plt.colorbar(ticks=[0.1, 0.3, 0.5, 0.7], orientation='horizontal')

ax = fig.add_subplot(1, 2, 2)
imgplot = plt.imshow(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))
ax.set_title('Background')
#plt.colorbar(ticks=[0.1, 0.3, 0.5, 0.7], orientation='horizontal')

plt.show()
'''


#features = ('Cr', 'H', 'CIEA')      # max accuracy adv
#skin_clf = SkinClassifier(features, ds='adv')

#p1 = agc.adaptive_gamma_correction(img)
#p2 = lbp.white_balance(p1)
#p3 = lbp.erase_colors(p2, red=True, yellow=True, white=True, orange=True)
#p4 = frame_processor.process_frame(skin_clf, img, cv2.cvtColor(bg, cv2.COLOR_BGR2RGB))

bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

diff = bg.copy()
cv2.absdiff(bg, img, diff)
#converting the difference into grayscale images
mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
#otsu thresholding
(T, thresh) = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
thresh = cv2.dilate(thresh, kernel, iterations=10)
thresh = cv2.erode(thresh, kernel, iterations=5)
thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

th = 1
imask =  thresh>th
canvas = np.zeros_like(img, np.uint8)
canvas[imask] = img[imask]

cv2.imshow("Differences", cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
cv2.waitKey(0)


#mask = skin_clf.extract_mask(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
#mask_3d = np.dstack((mask, mask, mask))
#is_skin = mask_3d == np.array([1, 1, 1])
#skin_replaced = np.where(is_skin, is_skin, cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).astype(np.uint8)
#skin_replaced1 = np.where(is_skin, cv2.cvtColor(bg, cv2.COLOR_BGR2RGB), cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).astype(np.uint8)
#skin_replaced2 = np.where(is_skin, is_skin, is_skin).astype(np.uint8)
#cv2.imwrite("extract_mask_post.png", cv2.cvtColor(skin_replaced, cv2.COLOR_BGR2RGB))



'''
fig = plt.figure()
ax = fig.add_subplot(3, 3, 1)
imgplot = plt.imshow(cv2.cvtColor(p1, cv2.COLOR_BGR2RGB))
ax.set_title('Gamma correction')
#plt.colorbar(ticks=[0.1, 0.3, 0.5, 0.7], orientation='horizontal')

ax = fig.add_subplot(3, 3, 2)
imgplot = plt.imshow(cv2.cvtColor(p2, cv2.COLOR_BGR2RGB))
ax.set_title('White Balance')
#plt.colorbar(ticks=[0.1, 0.3, 0.5, 0.7], orientation='horizontal')

ax = fig.add_subplot(3, 3, 3)
imgplot = plt.imshow(cv2.cvtColor(p3, cv2.COLOR_BGR2RGB))
ax.set_title('Erase colors')

ax = fig.add_subplot(2, 3, 4)
imgplot = plt.imshow(canvas)
ax.set_title('Differences')

ax = fig.add_subplot(3, 3, 5)
m = plt.imread("extract_mask_post.png")
imgplot = plt.imshow(m)
ax.set_title('Mask')

ax = fig.add_subplot(3, 3, 6)
#m = plt.imread("extract_mask.png")
imgplot = plt.imshow(skin_replaced)
ax.set_title('Postprocess')


ax = fig.add_subplot(2, 3, 8)
imgplot = plt.imshow(skin_replaced1)
ax.set_title('Background Replaced')



plt.show()
'''

