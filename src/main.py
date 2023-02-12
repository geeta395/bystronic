# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 12:15:57 2022

@author: chggo
"""

import time
import os
from os.path import exists
import json
from modules.pathHelper import path_srcRoot, path_resources, path_log, path_work
from modules.logger import logger
from modules.dataTransfer.mqtt_client import MqttClient
from modules.dataTransfer.azure_uploader import AzureUploader
#from topics.loc.machine.dataPreparation.dumpProcess import Dump
from modules.topicWorker import TopicWorker
import sys


def writeConfig(file):
    logger.info('Config file is created')
    config={'mqtt':{'username':'manager', 'password':"byadmin",
                    'broker':'localhost','topic':'icp/dumps/#','port':1883}}

    # Write the new structure to the new file
    with open(file, 'w') as configfile:
        configfile.write(json.dumps(config))
        print ("config saved   : ", file)
    return

def readConfig(path_configFile):
    f = open(path_configFile)
    data=json.load(f)
    topic=data['mqtt']['topic']
    username=data['mqtt']['username']
    password=data['mqtt']['password']
    broker=data['mqtt']['broker']
    port=data['mqtt']['port']
    return(topic,username,password,broker,port)
    


def run():
    sas_url=( "https://datapltestexchange.blob.core.windows.net/upload?sp=c&st=2022-09-05T13:03:12Z&se=2032-09-05T21:03:12Z&spr=https&sv=2021-06-08&sr=c&sig=byH0i89HMBDotD%2Bwc9%2F2bilnJ5wCKgPYYl8YnX9bdqw%3D" )


   
    print ("hello from icpdataprocessor\n---\n")
    print ("path_srcRoot  : ", path_srcRoot)
    print ("path_resources: ", path_resources) # models, config
    print ("path_log      : ", path_log)       # log data
    print ("path_work     : ", path_work)      # working data (can be deleted)
    
    # write config file
    path_configFile=os.path.join(path_resources,'config.json')
   

    if not exists(path_configFile):
        writeConfig(path_configFile)
        
    
    
    #read data from config file
    topic,username,password,broker,port=readConfig(path_configFile)

  

    uploader=AzureUploader(sas_url)
    worker=TopicWorker(uploader)
    
    # parameter 'charts' is 'True' if Image is required 
    client = MqttClient(worker,logger,'icpDataProcess', username=username, password=password, brokerUrl=broker, port = port,charts=True)
    client.connect()
    client.subscribe(topic=topic)  
    while True:
        time.sleep(3)
    
    


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logger.warning('keyboard Interrupted')
        sys.exit(0)        #run()