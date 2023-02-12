# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 16:44:45 2022

@author: chggo
"""

from topics.loc.machine.dataPreparation.dumpProcess import DoWorkLOC
from topics.nozzleControl.machine.dataPreparation.dumpProcess import DoWorkNozzleControl
from topics.pierce.machine.doWorkPiercing import DoWorkPiercing
from modules.doWork_helper import DoWorkHelper
from modules.logger import logger

class TopicWorker:
    def __init__(self,uploader):
        self.uploader=uploader
        self.DW=DoWorkHelper(self.uploader)
        
    def doWork(self,oMsg,charts):
        topic=oMsg['topic']
        stream=oMsg["payload"]
    
        if topic.endswith('lossOfCutDetected'):
            print('doWork in the topic {}'.format(topic))
            logger.info('stream is sent to doWorkLocOfCut')
            D=DoWorkLOC(self.DW)
            try:
                D.doWorkLocOfCut(stream,charts)
            except Exception:
                logger.exception('doWorkLocOfCut is failed')
           
        elif topic.startswith("icp/dumps/checkNozzle"):
            print('doWork in the topic {}'.format(topic))
            #logger.info('Subscribed Topic is {}'.format(topic))
            N=DoWorkNozzleControl(self.DW)
            try:
                N.doWorkNozzle(stream,topic)
            except Exception:
                logger.exception('doWorkNozzle is failed')

        elif topic.startswith("icp/dumps/pierce"):
            print('doWork in the topic {}'.format(topic))
            P=DoWorkPiercing(self.DW)
            try:
                P.saveFinalImg(stream)
            except Exception:
                logger.exception('doWorkPiercing is failed')
           
            
        else:
            tfile,tzip=self.DW.checkIf_file()
            self.DW.saveStream(stream,tzip)
            self.DW.checkUpload(tzip,inf=True,topic=topic)
        return