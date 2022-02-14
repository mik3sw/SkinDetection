import logging
import time
import cv2
import frame_processor as process_frame
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


# == Global variables ==
q = queue.Queue()
final = queue.Queue()
skin_clf = None
bg = None
codenames = ["Michi", "Tia", "Ele",
            "Wall-Maria", "Wall-Rose", "Wall-Sina", 
            "Thor", "Loki", "Odin",
            "BMO", "Jake", "Finn",
            "Alien", "Kayo", 
            "Meta"
            ]

bar = Progress(
        SpinnerColumn("dots"),
        #TextColumn("[bold green]Processing: "),
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    )

task = None

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
    #if (frame[1]+1)%10 == 0:
    #    log.debug("Frame: {}".format(frame[1]+1))
    new_frame = process_frame(skin_clf, frame[0], bg)
    final.put((new_frame, frame[1]))
    bar.update(task, advance=1)
    time.sleep(0.1)


def get_ordered_frame(j):
    for item in final.queue:
        if item[1] == j:
            return item[0]


def init(filename, clf):
    # == Istanzio le variabili necessarie == 
    global skin_clf, bg, task
    t1 = time.perf_counter()
    skin_clf = clf
    threads = []
    thread_count = mp.cpu_count()
    
    # Nome/path del file
    no_suffix = filename.split(".m4v")[0]
    out_filename = f'{no_suffix}_processed.m4v'

    # Video source, video out, video info
    width, height, fps, count = get_video_details(filename)
    cap = cv2.VideoCapture(filename)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(out_filename, fourcc, fps, (width, height))

    # == Stampo informazioni task ==
    log = logging.getLogger('rich')
    log.info("Video da processare: {}\n"
             "Frame da processare: {}".format(filename, count))
    #log.info("Frame da processare: {}".format(count))

    # == Acquisizione Backgroung ==
    #log.debug("Acquisisco background...")
    bg = get_rgb_background(filename)
    #log.debug("Background acquisito!")

    # == Creazione Threads ==
    # nota: si possono aggiungere i nomi ai Threads (name = ...)
    log.debug("Creo {} Threads".format(thread_count))
    for x in range(0, thread_count):
        try:
            t = threading.Thread(target=worker, name = codenames[x])
        except:
            t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        #log.debug('Started: %s' % t)
    #log.debug("Threads creati!")

    # == Riempio la Queue ==
    with bar as progress:
        #log.debug("Metto ogni frame nella Queue (frame, index)")
        task2 = progress.add_task("[bold blue]Getting frames", total=count)
        task = progress.add_task("[bold green]Processing...", total=count)
        cap = cv2.VideoCapture(filename)
        i = 0
        while True:
            ret, frame = cap.read()
            if ret:
                q.put((frame, i))
                i+=1 
                progress.update(task2, advance=1)
            else:
             break
        # block until all tasks are done
        q.join()

    # stop workers
    for _ in threads:
        q.put(None)

    for t in threads:
        t.join()
    

    # == Scrittura video output ==
    j = 0
    log.debug("Scrivo i frame in {}".format(out_filename))
    while j!= count:
        fr = get_ordered_frame(j)
        out.write(fr)
        j+=1

    # == Processo finito ==
    t2 = time.perf_counter()
    log.info(f'Finished in {t2-t1} seconds')

        

