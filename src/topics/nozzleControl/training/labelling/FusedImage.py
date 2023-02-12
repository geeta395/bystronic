# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:31:38 2022

@author: chggo
"""

import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from zipfile import ZipFile
import json


result=r'C:\Users\chggo\REG_analysis\data\nozzle_MP2'
path=r'N:\00_Dev_General\30_CC_übergreifend\LipVision\20221114_APxx_ICP_Nozzle\20230131_MP2'



class FusedImages():
    def __init__(self,path,result,string=False):
        # Note: if string is false, no metainfo will be print on image, at training time string==false should be used
        self.path=path
        self.result=result
        self.dumpList=[]
        self.string=string
     
    def imgFromZip(self):
        
        count=0
        for item in os.listdir(self.path):     
            if item.endswith('.zip'):
                print('{} dump is processed'.format(count))
               
                Im=[]
                file_name=os.path.join(self.path,item)
                zip_ref = ZipFile(file_name)
                listOfFiles = zip_ref.namelist()
               
                for f in listOfFiles:
                    if f.endswith('.png'):
                        zip_ref.open(f)
                        img=zip_ref.read(f)
                        buff=np.frombuffer(img,np.uint8)
                        img = cv2.imdecode(buff,cv2.IMREAD_ANYDEPTH)
                        Im.append(img)
                
                       
                m=os.path.join(self.result,'fused_'+str(count)+'.png') 
                self.Fusion(Im,listOfFiles,zip_ref,m)
                count=count+1
                self.dumpList.append({'dump':file_name,'image':m})
                
        df={'zipAndimagePath':self.dumpList}
        self.saveJson(df)
        return
 
    def saveJson(self,df):
        
        json_object = json.dumps(df)
         
        # Writing to sample.json
        jssn=os.path.join(self.result,"forLabels.json")
        with open(jssn, "w") as outfile:
            outfile.write(json_object)
        return
    
    def meta(self,listOfFiles,zip_ref):
        
        nozzleType=None
        equipmentNr=0
        metaInfo='NoImgMeta'
        for f in listOfFiles:
            if f.endswith('/imgMeta.json'):
                zip_ref.open(f)
                imgMeta=zip_ref.read(f)
                imgMeta=json.loads(imgMeta.decode("utf-8"))
                nozzleType=imgMeta['data'][0]['meta']['param']['nozzleType']
                raster=imgMeta['data'][0]['meta']['cuttingHead']['raster']
                Type=imgMeta['type'][11:]
                metaInfo=nozzleType+','+'R'+str(raster)+','+Type
              
                
            if f.endswith('metaInfo.json'):
                zip_ref.open(f)
                metafile=zip_ref.read(f)
                metafile=json.loads(metafile.decode("utf-8"))
                equipmentNr=metafile['id']['value']
                metaInfo=metaInfo+','+'equ_'+equipmentNr
                
                
            
        if nozzleType==None:
            print('imgmeta.json is not available in the dump')
        
        return(metaInfo)
    
    def Fusion(self,Im,listOfFiles,zip_ref,m):
       
        #Merge
        mergeMertens = cv2.createMergeMertens()
        exp = mergeMertens.process(Im)
           
        #UnNormalize 
        alpha = 0xFFFF / (np.max(exp)-np.min(exp))  
        beta = -np.min(exp)* alpha
        expUnNorm=alpha*exp+beta
        expUnNorm = expUnNorm.astype(np.uint16)
       
        #Save
        if self.string :
            metaInfo=self.meta(listOfFiles,zip_ref)
            imgText=self.process(expUnNorm,metaInfo)
        else:
            imgText=expUnNorm
            
        plt.imsave(m,imgText,cmap='jet',vmin=0,vmax=65535)
       
      
        return
    
   
    def process(self,img1,string):
        img=img1.copy()
        cv2.putText(img=img, text=string, org=(15,30), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=0xFFFF,thickness=2)
        return(img)
    
  
EF=FusedImages(path,result)
EF.imgFromZip()


