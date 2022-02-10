import argparse
import configparser
import logging
from pathlib import Path
#from src import core, data, tools, video
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
import logging
from rich.logging import RichHandler
from rich.console import Console

from rich.logging import RichHandler

from src.video import cam, single, ffmpeg_processing
from src.skin_classifier import SkinClassifier


FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


project_description = '''
# Progetto Elaborazione delle Immagini: The Invisible Man
__Partecipanti__
1. Mattia Napoli       [852239]
2. Eleonora Cicalla    [851649]
3. Michele Marcucci    [851905]
'''

sample_usages='''
Sample usage:
main.py                         | launch interactive cam session
main.py -f filename             | process given file
main.py -f filename --ffmpeg    | process given file using ffmpeg
'''

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="== PROGETTO ELABORAZIONE DELLE IMMAGINI ==",
        epilog=sample_usages,
    )
parser.add_argument('-f', '--file', help='video file to process')
parser.add_argument('--ffmpeg', action='store_true', help='use ffmpeg library to speed up the processing')
parser.add_argument('-i', '--info', action='store_true', help='show info')

def info_f():
    table = Table(title="Comandi disponibili", show_lines=True)
    table.add_column("Comando", justify="center", style="cyan", no_wrap=True)
    table.add_column("Argomenti", style="magenta")
    table.add_column("Spiegazione", justify="left", style="green")
    table.add_row("HELP", "-h --help", "Mostra i comandi disponibili e come si usano")
    table.add_row("INFO", "-i --info", "Mostra questa schermata")
    table.add_row("FFMPEG", "-f filename --ffmpeg", "Per ora funzionante solo su linux, permette di usare il multiprocessing per dividere il video in più parti e processarle singolarmente e contemporaneamente (fast processing)")
    table.add_row("CAMERA", "None", "Usa, se disponibile, la webcam del pc e processa frame per frame live")
    table.add_row("FILE", "-f filename", "Processa iterativamente ogni frame del file passato e restituisce un video final.mp4")
    console = Console()
    md = Markdown(project_description)
    console.print(md)
    console.print(table)


def main():
    args = parser.parse_args()
    filename = args.file
    use_ffmpeg = args.ffmpeg
    info = args.info
    if info:
        info_f()
        return

    #features = ('G', 'CIEL', 'CIEA')      # vdm set
    #skin_clf = SkinClassifier(features, ds='vdm')
    config = configparser.ConfigParser()
    config.read('config.ini')

    features = ('Cr', 'H', 'CIEA')      # max accuracy adv
    skin_clf = SkinClassifier(features, ds=config["classifier"]["dataset"])

    
    

    log = logging.getLogger('rich')
    log.info('Got logger')
    log.info("Using {} database".format(config["classifier"]["dataset"]))

    if filename is None:
        log.info("Using camera as video source")
        cam.run(skin_clf)
    else:
        if use_ffmpeg:
            log.info("[yellow]Starting using multiprocessing[/] [bold red blink]Only Linux[/]", extra={"markup": True})
            log.info("File is: {}".format(filename))
            ffmpeg_processing.init(filename, skin_clf, ffmpeg_processing.get_rgb_background(filename))
        else:
            if Path(filename).exists():
                log.info(f'Using {filename} as video source')
                single.run(filename, skin_clf)
            else:
                log.critical('File not found!')


if __name__ == '__main__':
    main()