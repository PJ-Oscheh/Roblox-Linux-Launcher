#!/usr/bin/env python

import sys;
import logging;
import os;

if sys.version_info.major < 3:
    print("Require python version 3")
    quit()

#Create a log file local to the module.
current_module = sys.modules[__name__]
moduledir=os.path.dirname(current_module.__file__)
logfile=os.path.join(moduledir, 'robloxLauncher.log')

logger = logging.getLogger(__name__)
logging.basicConfig(filename=logfile, filemode='w', level=logging.DEBUG)

#Log all unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

__import__("roblox-linux-launcher")
