import logging
import time

import cv2
from rich.progress import Progress
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from src.core.frame_processor import process_frame



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


def run(filename, skin_clf):
    t1 = time.perf_counter()

    no_suffix = filename.split(".m4v")[0]
    out_filename = f'{no_suffix}_processed.m4v'
    width, height, fps, count = get_video_details(filename)

    bg = get_rgb_background(filename)

    cap = cv2.VideoCapture(filename)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(out_filename, fourcc, fps, (width, height))

    bar = Progress(
        SpinnerColumn("dots"),
        TextColumn("[bold green]Processing: "),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
    )

    with bar as progress:
        task = progress.add_task("[bold green]Processing...", total=count)
        while True:
            ret, frame = cap.read()
            if ret:
                bgr_skin_replaced = process_frame(skin_clf, frame, bg)
                out.write(bgr_skin_replaced)
                progress.update(task, advance=1)
            else:
                break

    cap.release()
    out.release()
    t2 = time.perf_counter()
    log = logging.getLogger('rich')
    log.info(f'Finished in {t2-t1} seconds')