import argparse
import scrapers
import pathlib
import json
import logging
import re
import traceback
import os
from selenium import webdriver


def runScraper(module, keyPhrase, numLinks, patience, webdriverOptions, dir="data"):
    # Reformat keyphrase
    keyPhraseDir = re.sub(r"[^\w\s]", '', keyPhrase)
    keyPhraseDir = re.sub(r"\s+", '_', keyPhraseDir)
    keyPhraseDir = keyPhraseDir.lower()
    try:
        scraper = module.Scraper(patience, webdriverOptions)
        jsonList = scraper.getJSON(keyPhrase, numLinks)
        filename = f"{dir}/{keyPhraseDir}/{module.__name__}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w+") as f:
            json.dump(jsonList, f)
    except Exception as err:
        logging.root.warning(f"{type(err)}: {err} {traceback.format_exc()}")
        logging.root.warning(f"Error from {module.__name__}, skipping...")


def mainRun(args):
    # Set logging level
    if args.silent == 0:
        logging.root.setLevel('INFO')
    elif args.silent == 1:
        logging.root.setLevel('WARNING')
    elif args.silent == 2:
        logging.root.setLevel('CRITICAL')

    logging.root.info("Run:" + str(args))

    # Get defaults from json file
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        config = json.load(f)

    # Set defaults for any missing args
    if not args.keyphrase and ('keyphrase' not in config or not config['keyphrase']): ## Need a keyphrase to search for
        print('No saved default keyphrase. Run requires a keyphrase to start searching for.')
        parser_run.print_usage()
        return
    config['keyphrase'] = args.keyphrase if args.keyphrase else config['keyphrase']
    config['numlinks'] = args.numlinks if args.numlinks else config['numlinks'] if 'numlinks' in config else 20
    config['patience'] = args.patience if args.patience else config['patience'] if 'patience' in config else 10
    config['outdir'] = str(args.outdir) if args.outdir else config['outdir'] if 'outdir' in config else 'data'

    # Write current configuration back to defaults json file
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as f:
        json.dump(config, f)
        
    # Other configuration stuff
    webdriverOptions = webdriver.ChromeOptions()
    webdriverOptions.add_experimental_option('excludeSwitches', ['enable-logging']) # Ignore non-breaking selenium output
    webdriverOptions.page_load_strategy = 'eager'

    # Run
    if args.module == 'all': 
        for module in scrapers.Scrapers:
            runScraper(module, config['keyphrase'], config['numlinks'], config['patience'], webdriverOptions, config['outdir'])
    else:
        module = moduleNames[args.module]
        runScraper(module, config['keyphrase'], config['numlinks'], config['patience'], webdriverOptions, config['outdir'])


def mainSet(args):
    logging.root.info("Set:" + str(args))

    # Get defaults from json file
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        config = json.load(f)

    # Set defaults
    config['keyphrase'] = args.keyphrase if args.keyphrase else config['keyphrase'] if 'keyphrase' in config else None
    config['numlinks'] = args.numlinks if args.numlinks else config['numlinks'] if 'numlinks' in config else 20
    config['patience'] = args.patience if args.patience else config['patience'] if 'patience' in config else 10
    config['outdir'] = str(args.outdir) if args.outdir else config['outdir'] if 'outdir' in config else 'data'
    if args.reset:
        config['keyphrase'] = None
        config['numlinks'] = 20
        config['patience'] = 10
        config['outdir'] = 'data'

    # Write current configuration back to defaults json file
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'w') as f:
        json.dump(config, f)


def mainRead(args):
    moduleNames = {module.__name__.removeprefix('scrapers.'):module for module in scrapers.Scrapers}
    print(list(moduleNames.keys()))
    # Get defaults from json file
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        print(json.load(f))


def mainParser(args):
    parser.print_help()

############## SETUP STUFF ################
moduleNames = {module.__name__.removeprefix('scrapers.'):module for module in scrapers.Scrapers}
# print(moduleNames)
logging.basicConfig()
logging.root.setLevel('INFO')


############## PARSER #################
parser = argparse.ArgumentParser(description='Web scraper designed around news sites.')
parser.set_defaults(func=mainParser)
subparsers = parser.add_subparsers(title='commands')

###### RUN #####
parser_run = subparsers.add_parser('run', 
                                   help="'run -h' for run help",
                                   description='Run specified scraper to find articles based on a keyphrase.')
parser_run.add_argument('module', 
                        metavar='name',
                        choices=['all'] + list(moduleNames.keys()), 
                        help='scraper to run: ' + str(['all'] + list(moduleNames.keys())))
parser_run.add_argument('-s', '--silent',
                        nargs='?',
                        type=int,
                        const=1,
                        default=0,
                        choices=range(3),
                        help='silences logging output, defaults to 1 when set. {0: show info, 1: show warnings, 2: silence all}')
parser_run.add_argument('keyphrase',
                        nargs='?',
                        help='string to search. put in "" quotes if more than one word')
parser_run.add_argument('numlinks',
                        type=int,
                        nargs='?',
                        help='minimum number of articles to attempt to retrieve')
parser_run.add_argument('outdir',
                        nargs='?',
                        type=pathlib.Path,
                        help='output directory path')
parser_run.add_argument('patience',
                        type=int,
                        nargs='?',
                        help='number of seconds to wait for a page to load (among other things)')
parser_run.set_defaults(func=mainRun)

##### SET #####
parser_set = subparsers.add_parser('set', 
                                   help="'set -h' for set help",
                                   description='Manually set default options. Defaults are typically set to whatever configuration was last ran.')
parser_set.add_argument('-k', '--keyphrase',
                        nargs=1,
                        help='set string to search. put in "" quotes if more than one word')
parser_set.add_argument('-n', '--numlinks',
                        nargs=1,
                        type=int,
                        help='set minimum number of articles to attempt to retrieve')
parser_set.add_argument('-p', '--patience',
                        nargs=1,
                        type=int,
                        help='set number of seconds to wait for a page to load (among other things)')
parser_set.add_argument('-o', '--outdir',
                        nargs=1,
                        type=pathlib.Path,
                        help='set output directory path')
parser_set.add_argument('-r', '--reset',
                        action='store_true',
                        help='reset all default options to original configuration')
parser_set.set_defaults(func=mainSet)

##### READ #####
parser_read = subparsers.add_parser('read', 
                                   help='prints info and current defaults configuration',
                                   description='Prints info and current defaults configuration.')
parser_read.set_defaults(func=mainRead)


args = parser.parse_args()
args.func(args)
# print(args)

