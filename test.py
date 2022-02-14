from src import skin_classifier
from src.tools import lbp, agc
#skin_classifier.main()
import cv2

img = cv2.imread("docs/imgs/img15.jpg")

gamma = agc.adaptive_gamma_correction(img)
wb = lbp.white_balance(gamma)
cv2.imshow("original", img)
cv2.imshow("wb", wb)
cv2.imshow("gamma", gamma)
cv2.waitKey(0)