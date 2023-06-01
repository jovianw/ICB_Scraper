import os
import importlib
import re

__globals = globals()
Scrapers = set()

for file in os.listdir(os.path.dirname(__file__)):
    if not re.match(r'^__', file):
        modName = file[:-3]
        moduleObj = importlib.import_module('.'+modName, package=__name__)
        Scrapers.add(moduleObj)
        __globals[modName] = moduleObj
del modName, moduleObj