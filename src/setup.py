import zipfile
import signal
from threading import Event
import requests
import logging
from rich.logging import RichHandler
from os import remove
import shutil
from pathlib import Path


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
    TextColumn("[bold blue]Datasets.zip", justify="right"),
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
        task_id = progress.add_task("download", filename="Datasets.zip", start=False, total=551670285)
        with open(destination, "wb") as f:
            progress.start_task(task_id)
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    progress.update(task_id, advance=len(chunk))
                    f.write(chunk)
        progress.console.log(f"Downloaded {destination}")


def download(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    save_response_content(response, destination)  


if __name__ == "__main__":
    log = logging.getLogger("rich")
    file_id = '1Np7tn4Rn4IiaIBgn37PsjUrsQdfO7e35'
    zip_path = Path(__file__).parent.parent / Path('Datasets.zip')
    unzipped_path = Path(__file__).parent.parent / Path('Dataset')
    cache_path = Path(__file__).parent.parent / Path('.cache')
    
    try:
        log.debug("Downloading Datasets.zip")
        download(file_id, zip_path)
        log.debug("Download complete!")
        try:
            log.debug("Unzipping dataset (this might take a while")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall()
            unzipped_path.rename(Path(__file__).parent.parent / Path('Datasets'))
            log.debug("Unzipping complete!")
            log.debug("Removing temporary files and folders (this may take a while)")
            remove(zip_path)
            try:
                shutil.rmtree("__MACOSX")
            except:
                log.error("Not macOS, skipping")
        except Exception as e:
            log.critical(f'Errore durante unzipping: {e}')
    except Exception as e:
        log.critical(f"ERRORE durante il download: {e}")

    log.debug('Creating ".cache" folder..')
    cache_path.mkdir(parents=True, exist_ok=True)
    log.info("Done")