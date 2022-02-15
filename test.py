from src import skin_classifier
from src.tools import lbp, agc
#skin_classifier.main()
import cv2
import numpy as np

img = cv2.imread("docs/start1.png")
bg = cv2.imread("docs/bg1.png")
diff = bg.copy()

cv2.absdiff(bg, img, diff)
mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
(T, thresh) = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
thresh = cv2.dilate(thresh, kernel, iterations=10)
#thresh = cv2.erode(thresh, kernel, iterations=1)
#thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

th = 1
imask =  thresh>th
canvas = np.zeros_like(img, np.uint8)
canvas[imask] = img[imask]
canvas = lbp.erase_colors(canvas, white=True)


#gamma = agc.adaptive_gamma_correction(img)
#wb = lbp.white_balance(gamma)
#cv2.imshow("original", img)
#cv2.imshow("wb", wb)
#cv2.imshow("gamma", gamma)
#cv2.imshow("diff", diff)
#cv2.imshow("mask", mask)
cv2.imshow("thresh", canvas)
cv2.waitKey(0)