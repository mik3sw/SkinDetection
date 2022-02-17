import os.path
import sys
from concurrent.futures import as_completed, ThreadPoolExecutor
import signal
from functools import partial
from threading import Event
from typing import Iterable
from urllib.request import urlopen
from pathlib import Path
import zipfile

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
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


done_event = Event()


def handle_sigint(signum, frame):
    done_event.set()


signal.signal(signal.SIGINT, handle_sigint)


def copy_url(task_id: TaskID, url: str, path: str) -> None:
    """Copy data from a url to a local file."""
    progress.console.log(f"Requesting {url}")
    response = urlopen(url)
    # This will break if the response doesn't contain content length
    progress.update(task_id, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        progress.start_task(task_id)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            progress.update(task_id, advance=len(data))
            if done_event.is_set():
                return
    progress.console.log(f"Downloaded {path}")


def download(urls: Iterable[str], dest_dir: str):
    """Download multuple files to the given directory."""

    with progress:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for url in urls:
                filename = url.split("/")[-1]
                dest_path = os.path.join(dest_dir, filename)
                task_id = progress.add_task("download", filename=filename, start=False)
                pool.submit(copy_url, task_id, url, dest_path)

if __name__ == "__main__":
    proj_dir = Path(__file__).parent.parent
    download(['http://www.sel.eesc.usp.br/sfa/sfa.zip',
            'http://www-vpu.eps.uam.es/publications/SkinDetDM/data/train.zip',
            'http://www-vpu.eps.uam.es/publications/SkinDetDM/data/test.zip'], proj_dir)

    dataset_dir = Path(__file__).parent.parent / Path('Datasets')
    sfa_dataset_dir = dataset_dir / Path('Advanced_Skin_Dataset')
    vdm_train_dataset_dir = dataset_dir / Path('VDM_Dataset/train')
    vdm_test_dataset_dir = dataset_dir / Path('VDM_Dataset/test')

    sfa_dataset_dir.mkdir(parents=True, exist_ok=True)
    vdm_train_dataset_dir.mkdir(parents=True, exist_ok=True)
    vdm_test_dataset_dir.mkdir(parents=True, exist_ok=True)

    sfa_zip = proj_dir / Path('sfa.zip')
    vdm_train_zip = proj_dir / Path('train.zip')
    vdm_test_zip = proj_dir / Path('test.zip')

    with zipfile.ZipFile(sfa_zip, 'r') as zip_ref:
        zip_ref.extractall(sfa_dataset_dir)
    with zipfile.ZipFile(vdm_train_zip, 'r') as zip_ref:
        zip_ref.extractall(vdm_train_dataset_dir)
    with zipfile.ZipFile(vdm_test_zip, 'r') as zip_ref:
        zip_ref.extractall(vdm_test_dataset_dir)

    sfa_zip.unlink()
    vdm_train_zip.unlink()
    vdm_test_zip.unlink()

    cache_path = proj_dir / Path('.cache')
    cache_path.mkdir(parents=True, exist_ok=True)