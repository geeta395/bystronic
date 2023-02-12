# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 13:43:18 2022

@author: chggo
"""
import os
import logging
import warnings
from logging.handlers import RotatingFileHandler
from modules.pathHelper import path_log
warnings.filterwarnings("ignore")


def Logger(path):
    
    # It limits log file size
    # Create and configure logger
   
    logger=logging.getLogger('matplotlib.font_manager')
    logger.setLevel(level=logging.INFO)  #.INFO
    
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s (%(lineno)d) %(message)s')
   
    # set the handler
    fileHandler = logging.handlers.RotatingFileHandler(
      filename=path, mode='a',encoding=None, delay=False,
      maxBytes=1024*1024*2,  
      backupCount=2
    )
    
    fileHandler.setFormatter(log_formatter)
    fileHandler.setLevel(level=logging.INFO)  # INFO
    if not logger.hasHandlers():
        logger.addHandler(fileHandler)
   
    return(logger)

# Get the current working directory
path= os.path.join(path_log, 'icpdataprocessor.log')

print("Init logger   :", path)

logger=Logger(path)
