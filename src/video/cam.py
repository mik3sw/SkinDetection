import cv2
import frame_processor



def run(skin_clf):
    """Dato in input lo stream video preso dalla webcam del pc"""
    bg = get_rgb_background()
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cam.set(cv2.CAP_PROP_AUTO_WB, 0)
    while True:
        ret_val, img = cam.read()
        img = cv2.flip(img, 1)
        bgr_skin_replaced = frame_processor.process_frame(skin_clf, img, bg)
        #bgr_skin_replaced = src.tools.lbp.diff_mask(img, bg)
        cv2.imshow('ESC to quit', bgr_skin_replaced)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()


def get_rgb_background():
    """Funzione che cattura un frame e lo considera come background statico della scena"""
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_AUTO_WB, 0)
    while True:
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow('Background: press \'q\' when ready', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            wallpaper = frame
            break
    cam.release()
    cv2.destroyAllWindows()
    rgb_wallpaper = cv2.cvtColor(wallpaper, cv2.COLOR_RGB2BGR)
    return rgb_wallpaper