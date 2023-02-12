# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 09:21:32 2022

@author: chggo
"""

import json
import os



def input2json(path,List,Test=False,onnx=False,onnx_path=None):
    for k in range(len(List)):
        json_data = List[k]
        
        c2={'focalPosition_0':json_data[2]['focalPosition_0'][0],'gasPressure_0':json_data[2]['gasPressure_0'][0],'laserPower_0':json_data[2]['laserPower_0'][0],'nominalSpeed_0':json_data[2]['nominalSpeed_0'][0]
            ,'nozzleDiameter':json_data[2]['nozzleDiameter'][0],'nozzleDistance_0':json_data[2]['nozzleDistance_0'][0],'raster':json_data[2]['raster'][0],'thickness':json_data[2]['thickness'][0]}
        c0={'cutControl':list(json_data[0]['cutControl']),'sinC':list(json_data[0]['sinC']),'cosC':list(json_data[0]['cosC'])}
        c1={'locCut':list(json_data[1]['locCut']),'reCut':list(json_data[1]['reCut']),'sinB':list(json_data[1]['sinB']),'cosB':list(json_data[1]['cosB'])}
        ddct={'dataC':c0,'dataB':c1,'dataP':c2,'label':json_data[3],'zipName':json_data[4]}
        if Test==False:
          n=os.path.join(path,'json_files','data','Zip'+str(k)+'.json')
        else:
            if onnx==True:
                n=os.path.join(onnx_path,'inputData.json')
            else:
                n=os.path.join(path,'json_files','pred','Zip'+str(k)+'.json')
        with open(n, 'w') as outfile:
            outfile.write(json.dumps(ddct))
        return
                