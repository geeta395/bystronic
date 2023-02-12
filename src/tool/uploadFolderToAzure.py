# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 12:15:57 2022

@author: chggo
"""

import time
import os
from os.path import exists
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from modules.pathHelper import path_srcRoot, path_resources, path_log, path_work
from modules.logger import logger
from modules.dataTransfer.azure_uploader import AzureUploader
import sys

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def run():
    sas_url=( "https://datapltestexchange.blob.core.windows.net/upload?sp=c&st=2022-09-05T13:03:12Z&se=2032-09-05T21:03:12Z&spr=https&sv=2021-06-08&sr=c&sig=byH0i89HMBDotD%2Bwc9%2F2bilnJ5wCKgPYYl8YnX9bdqw%3D" )

    print ("hello from icpdataprocessor\n---\n")
    print ("path_srcRoot  : ", path_srcRoot)
    print ("path_resources: ", path_resources) # models, config
    print ("path_log      : ", path_log)       # log data
    print ("path_work     : ", path_work)      # working data (can be deleted)
    
    uploader=AzureUploader(sas_url)
    #worker=Dump(path_work, uploader)
    
    # enter upload folder here
    arr = listdir_fullpath('N:\\00_Dev_General\\30_CC_übergreifend\\LipVision\\20221101_LoC_Prev_Traj\\MCxxyy\\validDumps')
    
    for filePath in arr:
        if filePath.endswith(".zip"):
                r,f=uploader.upload_using_sas(filePath)
                if r == 201:
                    print ("Upload ok: " + filePath)
                else:
                    print ("Upload:" + str(r) + ", " + filePath)
    
    print ("Done")
            

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logger.warning('keyboard Interrupted')
        sys.exit(0)        #run()