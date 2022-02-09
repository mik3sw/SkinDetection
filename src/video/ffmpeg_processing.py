from multiprocessing import Pool
import time
from os import remove
import time

import cv2
import subprocess as sp
import multiprocessing as mp

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from src import *
from src.skin_classifier import SkinClassifier
import numpy as np
from rich.progress import Progress
import logging
from rich.logging import RichHandler
from rich.spinner import Spinner
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

#from main import skin_clf
skin_clf = None
task = None
frame_count_total = 0
num_processes = 0

progress = Progress(
    TimeElapsedColumn(),
    SpinnerColumn("dots"),
    TextColumn("[bold green]Processing with {} Threads".format(num_processes)),
    SpinnerColumn("dots"),
)

#features = ('G', 'H', 'CIEA')
#skin_clf = SkinClassifier(features)



def find_wallpaper(file_name):
    wallpaper_data = []

    try:
        cap = cv2.VideoCapture(file_name)
        j = 0
        while True and j < 10:
            ret, frame = cap.read()
            j += 1
            if ret == True:
                wallpaper_data.append(frame)
    except:
        print("errore durante la ricerca dello sfondo")

    avg_image = wallpaper_data[0]
    for i in range(len(wallpaper_data)):
        if i == 0:
            pass
        else:
            alpha = 1.0/(i + 1)
            beta = 1.0 - alpha
            avg_image = cv2.addWeighted(wallpaper_data[i], alpha, avg_image, beta, 0.0)
    cv2.imwrite('wallpaper.jpg', avg_image)


def get_video_frame_details(file_name):
    vidcap = cv2.VideoCapture(file_name)
    success,image = vidcap.read()
    height, width = image.shape[:2]
    count = 0
    while success:     
        success,image = vidcap.read()
        count += 1
    return width, height, count

def get_length(filename):
    result = sp.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=sp.PIPE,
        stderr=sp.STDOUT)
    return float(result.stdout)


def process_video(video_name):
    global task, progress
    #carico lo sfondo
    wallpaper = cv2.imread("wallpaper.jpg")
    wallpaper = cv2.cvtColor(wallpaper, cv2.COLOR_BGR2RGB)
    wallpaper = cv2.resize(wallpaper,(480,360),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

    cap = cv2.VideoCapture(video_name)
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    width, height, frame_count = get_video_frame_details(video_name)
    
    out = cv2.VideoWriter('{}_processed.mp4'.format(video_name.replace(".mp4", "")),fourcc, 30, (480,360))


    while True:
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame,(480,360),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cloak_mask = skin_clf.extract_mask(frame)
            cloak_mask_3d = np.dstack((cloak_mask, cloak_mask, cloak_mask))
            cloak_removed = np.multiply(frame, 1 - cloak_mask_3d).astype(np.uint8)
            cloak_removed = np.where(cloak_removed == 0, wallpaper, cloak_removed)
            cloak_removed = cv2.cvtColor(cloak_removed, cv2.COLOR_BGR2RGB)
            out.write(cloak_removed)
            update_t()
        else:
            break
    
    cap.release()
    out.release()

def combine_output_files(num_processes):
    # Create a list of output files and store the file names in a txt file
    list_of_output_files = ["tmp_{}_processed.mp4".format(i) for i in range(num_processes)]
    list_old = ["tmp_{}.mp4".format(i) for i in range(num_processes)]
    #print("Lista dei file parziali da realizzare: {}".format(list_of_output_files))

    # questo ha senso?
    with open("list_of_output_files.txt", "w") as f:
        for t in list_of_output_files:
            f.write("file {} \n".format(t))
    
    with open("list_old.txt", "w") as f:
        for t in list_old:
            f.write("file {} \n".format(t))


    # use ffmpeg to combine the video output files
    ffmpeg_cmd = "ffmpeg -y -loglevel error -f concat -safe 0 -i list_of_output_files.txt -vcodec copy final.mp4"
    sp.Popen(ffmpeg_cmd, shell=True).wait()

    # Remove the temperory output files
    for f in list_of_output_files:
        remove(f)
    
    for f in list_old:
        remove(f)
    #remove("list_of_output_files.txt")


def update_t():
    global task, progress
    progress.update(task, advance = 1)



def init(file_name, clf):
    global skin_clf, frame_count_total, task, num_processes
    skin_clf = clf
    

    #print("starting with {}".format(file_name))
    t1 = time.perf_counter()
    #file_name = "input2.mp4"
    output_file_name = "output.mp4"
    width, height, frame_count_total = get_video_frame_details(file_name)
    duration = get_length(file_name)
    num_processes = mp.cpu_count()
    time_jump_unit =  duration / num_processes

    # Creo dei video da mandare in pasto ai processi
    videos = []
    i = 0
    for x in range(num_processes):
        ffmpeg_extract_subclip(file_name, i, i+time_jump_unit, targetname="tmp_{}.mp4".format(x))
        #clip = VideoFileClip(file_name).subclip(i, i+time_jump_unit).write_videofile("tmp_{}.mp4".format(x))
        videos.append("tmp_{}.mp4".format(x))
        #videos.append(clip)
        i += time_jump_unit
    
    
    with progress as progress1:
        task = progress1.add_task("", total = frame_count_total)
        with Pool(processes=num_processes) as pool:
            pool.map(process_video, videos)
    
    combine_output_files(num_processes)

    t2 = time.perf_counter()
    log = logging.getLogger("rich")
    log.info(f'Finished in {t2-t1} seconds')