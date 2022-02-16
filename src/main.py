import argparse
from pathlib import Path

from rich.markdown import Markdown
from rich.table import Table
from rich.console import Console

from video import cam, single, multithread
from skin_classifier import SkinClassifier


console = Console()


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
main.py -f filename --multi     | process given file using multithreading
'''


parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="== PROGETTO ELABORAZIONE DELLE IMMAGINI ==",
        epilog=sample_usages,
    )
parser.add_argument('-f', '--file', help='video file to process')
parser.add_argument('-m', '--multi', action='store_true', help='use multithreading')
parser.add_argument('-i', '--info', action='store_true', help='show info')


def info_f():
    table = Table(title="Comandi disponibili", show_lines=True)
    table.add_column("Comando", justify="center", style="cyan", no_wrap=True)
    table.add_column("Argomenti", style="magenta")
    table.add_column("Spiegazione", justify="left", style="green")
    table.add_row("HELP", "-h --help", "Mostra i comandi disponibili e come si usano")
    table.add_row("INFO", "-i --info", "Mostra questa schermata")
    table.add_row("FILE", "-f filename", "Processa iterativamente ogni frame del file passato e restituisce un video output")
    table.add_row("MULTITHREADS", "-f filename --multi", "Processa il video con un numero di threads uguali al numero di core (virtuali/fisici) di cui si dispone e restituisce un video output")
    table.add_row("CAMERA", "None", "Usa, se disponibile, la webcam del pc e processa frame per frame live")
    md = Markdown(project_description)
    console.print(md)
    console.print(table)


def main():
    args = parser.parse_args()
    filename = args.file
    multi = args.multi
    info = args.info

    if info:
        info_f()
        return

    # dataset = 'adv'     # 'vdm' or 'adv'
    dataset = 'vdm'
    if dataset == 'vdm':
        features = ('G', 'Cr', 'CIEA', 'CIEB')
    else:
        features = ('G', 'H', 'CIEA')
    skin_clf = SkinClassifier(features, ds=dataset, rebuild=False)
    
    console.log(f'Using {dataset} dataset')

    if filename is None:
        console.log("Using camera as video source")
        try:
            cam.run(skin_clf)
        except Exception as e:
            console.log(f'Error, got: {e}')
    else:
        if Path(filename).exists():
            if multi:
                console.log("[bold green]Starting using threads[/]")
                multithread.init(filename, skin_clf)
            else:
                console.log(f'Using {filename} as video source')
                single.run(filename, skin_clf)
        else:
            console.log('File not found!')


if __name__ == '__main__':
    main()