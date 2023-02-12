# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 10:22:11 2022

@author: chggo
"""


import os
import json
import onnxruntime
from modules.logger import logger
from modules.pathHelper import path_resources
from topics.loc.machine.onnx.preprocessing import Preprocessing

class Predict():
    def __init__(self,file_path):
        self.file_path=file_path
        path_current = os.path.dirname(os.path.abspath(__file__))
        self.path_model =  os.path.join(os.path.abspath(os.path.join(path_current, os.pardir, os.pardir)) ,'common', 'resources', 'loc.onnx')
        self.path_json =  os.path.join(os.path.abspath(os.path.join(path_current, os.pardir, os.pardir)) ,'common', 'resources', 'InputShape.json')

    def onnxPred(self):
        
        # get preprocessed data
        P=Preprocessing(self.file_path, self.path_json)
        List,data=P.jsonSaved()
        
        if len(List) !=0:
            inf=True
            label,prob=self.prediction(List)
            if int(label[0])==0:
                l='TP(Real LOC)'
            else:
                l='FP(No LOC)'
            c=data['C_inShape']
            b=data['B_inShape']
            data1={'C_inShape':c,'B_inShape':b,'label':l,'probability':prob}
        
            # save 
            n1=os.path.join(self.file_path,'label&Description.json')
            
            with open(n1, 'w') as outfile1:
                outfile1.write(json.dumps(data1))
                
            logger.info('save labels and description')
            logger.info('Inference status:{}'.format(inf))
            
        else:
            inf=False
            logger.info('Inference status:{}'.format(inf))
        
        return(inf)
    
    def prediction(self,List):
                   
        CC,BB,PP,ZZ=[List[0][0].to_numpy()],[List[0][1].to_numpy()],[List[0][2].to_numpy()],['None']
    
        session = onnxruntime.InferenceSession(self.path_model, None)
        
        input_name = session.get_inputs() 
        output_name = session.get_outputs()[0].name
        
        result=session.run([output_name],{input_name[0].name:CC,input_name[1].name:BB,input_name[2].name:PP})  
        P1=list(((result[0]>0.5).astype(int)).flatten())
        prob=str(result[0].flatten())
        logger.info('prediction score:{}'.format(prob))
        return(P1,prob)