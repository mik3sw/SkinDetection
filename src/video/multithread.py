import logging
import time
import cv2
from src.core.frame_processor import process_frame
from rich.progress import Progress
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

import threading
import time
import queue
import multiprocessing as mp



def get_video_details(filename):
    cap = cv2.VideoCapture(filename)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return int(width), int(height), int(fps), int(count)


def get_rgb_background(filename):
    bg_data = []
    cap = cv2.VideoCapture(filename)
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bg_data.append(rgb_frame)
    cap.release()
    
    bg = bg_data[0]
    for i in range(1, len(bg_data)):
        alpha = 1.0/(i + 1)
        beta = 1.0 - alpha
        bg = cv2.addWeighted(bg_data[i], alpha, bg, beta, 0.0)
    
    return bg

# Global variables
q = queue.Queue()
final = queue.Queue()
skin_clf = None
bg = None

def worker():
    global skin_clf, bg
    while True:
        frame = q.get()
        if frame is None:
            break
        # Funzione da lanciare
        do_sth(skin_clf, frame, bg)
        q.task_done()


def do_sth(skin_clf, frame, bg):
    log = logging.getLogger('rich')
    log.debug("Frame: {}".format(frame[1]))
    new_frame = process_frame(skin_clf, frame[0], bg)
    final.put((new_frame, frame[1]))
    time.sleep(0.1)

def get_ordered_frame(j):
    for item in final.queue:
        if item[1] == j:

            return item[0]

def init(filename, clf):
    global skin_clf, bg
    t1 = time.perf_counter()
    log = logging.getLogger('rich')
    skin_clf = clf
    threads = []
    thread_count = mp.cpu_count()
    
    no_suffix = filename.split(".m4v")[0]
    out_filename = f'{no_suffix}_processed.m4v'
    width, height, fps, count = get_video_details(filename)
    cap = cv2.VideoCapture(filename)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(out_filename, fourcc, fps, (width, height))

    log.info("Video da processare: {}".format(filename))
    log.info("Frame da processare: {}".format(count))
    #
    # time.sleep(3)

    # == Acquisizione Backgroung ==
    log.debug("Acquisisco background...")
    bg = get_rgb_background(filename)
    log.debug("Background acquisito!")

    # == Creazione Threads ==
    log.debug("Creo {} Threads...".format(thread_count))
    for x in range(0, thread_count):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        log.info('Started: %s' % t)
    log.debug("Threads creati!")

    # == Riempio la Queue ==
    log.debug("Metto ogni frame nella Queue (frame, index)")
    cap = cv2.VideoCapture(filename)
    i = 0
    while True:
        ret, frame = cap.read()
        if ret:
            q.put((frame, i))
            i+=1
        else:
            break

    
    
    
    # block until all tasks are done
    q.join()

    # stop workers
    for _ in threads:
        q.put(None)

    for t in threads:
        t.join()
    
    
    j = 0
    log.debug("Scrivo i frame in {}".format(out_filename))
    while j!= count:
        fr = get_ordered_frame(j)
        out.write(fr)
        j+=1

    t2 = time.perf_counter()
    log.info(f'Finished in {t2-t1} seconds')

        

