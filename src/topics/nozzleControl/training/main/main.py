# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 16:19:33 2022

@author: chggo
"""

import os
import json
from modules.pathHelper import path_work,path_resources
from topics.nozzleControl.training.main.mainHelper import Helper


def main():
    
    # Read parameters
    config_path=os.path.join(path_work,'topics','nozzleControl','common','resources','parameters.json')
    file = open(config_path)
    parameters=json.load(file)

    
    H=Helper(parameters)
    
    # GPU settings: 
    H.checkForGPU()

    # Read Data
    List=H.readData()    
   
    # Validate
    # Note: "validate_test" can only be true if inference has been made already. It checks training and inference distribution difference
    V=H.validateInput(List)
    
    # Preprocess data
    mean_1,mean_2,mean_3,std_1,std_2,std_3,normOut,Img,PP=H.preProcess(List)
    
    # Model Training
    imageList,predRadius,predX,predY,testRadius,testX,testY,dataTest,T=H.modelTraining(mean_1,mean_2,mean_3,std_1,std_2,std_3,normOut,Img,PP)

    # Visualize
    H.visualize(List,PP,T,V,imageList,predRadius,predX,predY,testRadius,testX,testY)
    
    # Ensemble
    if parameters['ensembleResult']:
        H.ensemble(PP,Img,V,T,normOut,imageList,dataTest)
    return

main()