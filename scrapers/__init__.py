import os
import importlib
import re

'''
Expect no scraper to be named "all.py"

Creates a set of modules "Scrapers" and imports them
'''


__globals = globals()
Scrapers = set()

files = (file for file in os.listdir(os.path.dirname(__file__)) 
         if os.path.isfile(os.path.join(os.path.dirname(__file__), file)))
for file in files:
    if not re.match(r'^__', file):
        modName = file[:-3]
        moduleObj = importlib.import_module('.'+modName, package=__name__)
        Scrapers.add(moduleObj)
        __globals[modName] = moduleObj
del modName, moduleObj, files