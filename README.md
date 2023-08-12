## Web scraper designed around news sites.

### Summary

Uses selenium to scrape a specified number of news articles related to a key phrase from a couple news websites. The data is stored as JSON files in a specified directory or in a directory called 'data'.

### Usage

Use as a command-line package

Install required packages via

    {pip} install -r requirements.txt

Run via command line

    {python} ICB_Scraper [-h] {run,set,read}

- Run
    
    ```
    usage: {python} ICB_Scraper run [-h] [-s [{0,1,2}]] name [keyphrase] [numlinks] [outdir] [patience]

    Run specified scraper to find articles based on a keyphrase.

    positional arguments:
    name                  scraper to run
    keyphrase             string to search. put in "" quotes if more than one word
    numlinks              minimum number of articles to attempt to retrieve
    outdir                output directory path
    patience              number of seconds to wait for a page to load (among other things)

    options:
    -h, --help            show this help message and exit
    -s [{0,1,2}], --silent [{0,1,2}]
                            silences logging output, defaults to 1 when set. {0: show info, 1: show warnings, 2: silence all}
    ```

- Set

    ```
    usage: {python} ICB_Scraper set [-h] [-k KEYPHRASE] [-n NUMLINKS] [-p PATIENCE] [-o OUTDIR] [-r]

    Manually set default options. Defaults are typically set to whatever configuration was last ran.

    options:
    -h, --help            show this help message and exit
    -k KEYPHRASE, --keyphrase KEYPHRASE
                            set string to search. put in "" quotes if more than one word
    -n NUMLINKS, --numlinks NUMLINKS
                            set minimum number of articles to attempt to retrieve
    -p PATIENCE, --patience PATIENCE
                            set number of seconds to wait for a page to load (among other things)
    -o OUTDIR, --outdir OUTDIR
                            set output directory path
    -r, --reset           reset all default options to original configuration
    ```

- Read

    ```
    usage: {python} ICB_Scraper read [-h]

    Prints info and current defaults configuration.
    ```

### Structure

Relevant folders and directories

    ICB_Scraper/
    ├─ scrapers/
    │  ├─ common/
    │  │  ├─ helpers.py: helper functions and mixin classes
    │  │  ├─ scraper.py: abstract classes
    │  ├─ concrete scrapers
    ├─ __main__.py: user interface
    ├─ requirements.txt: required packages

### Notes

Work in progress. Connections may break but not in a fatal way.

The NYTimes scraper uses the NYTimes API, and thus requires and API key. If you have an API key, the scraper expects it as an environmental variable. The other scrapers work just fine without this.

New concrete scraper classes can be made pretty easily, but must be customized to each specific website.