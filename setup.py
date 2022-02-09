import zipfile
import signal
from threading import Event
import requests
import logging
from rich.logging import RichHandler


from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

progress = Progress(
    TextColumn("[bold blue]Dataset.zip", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


done_event = Event()

def handle_sigint(signum, frame):
    done_event.set()

signal.signal(signal.SIGINT, handle_sigint)



def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with progress:
        task_id = progress.add_task("download", filename="Dataset.zip", start=False, total=551670285)
        with open(destination, "wb") as f:
            progress.start_task(task_id)
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    progress.update(task_id, advance=len(chunk))
                    f.write(chunk)
        progress.console.log(f"Downloaded {destination}")


def download(id: str, dest_dir: str):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, "Dataset.zip")  


if __name__ == "__main__":
    log = logging.getLogger("rich")
    file_id = '1Np7tn4Rn4IiaIBgn37PsjUrsQdfO7e35'
    destination = 'Dataset.zip'
    
    try:
        log.info("Download dataset")
        download(file_id, "./")
        log.info("Unzipping dataset")
        with zipfile.ZipFile("Dataset.zip", 'r') as zip_ref:
            zip_ref.extractall()
        log.info("Done")
    except:
        log.critical("ERRORE durante il download")
    