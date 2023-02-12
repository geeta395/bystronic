# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 11:07:48 2022

@author: chggo
"""



import os
from typing import List
import shutil
import cv2
import matplotlib.pyplot as plt
import numpy as np
from zipfile import ZipFile
import json
  

directory=r'N:\00_Dev_General\30_CC_übergreifend\LipVision\20221114_APxx_ICP_Nozzle\20221116_MP2\1000mA'
#directory=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\data\newData\test'
dst_dir=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\data\newData\test'
label=True

class getImgesForLabelling():
    def __init__(self,directory,dst_dir,label):
        self.directory=directory
        self.dst_dir=dst_dir
        self.dump_list=[]
        self.nozzle=[]
        self.label=label
        
    def getImages(self):
        i=0
        for item in os.listdir(self.directory):                
            if item.endswith('.zip'):
                print('{}th dump is being processed'.format(i))
                
                file_name=os.path.join(self.directory,item)
                zip_ref = ZipFile(file_name)
                listOfFiles = zip_ref.namelist()
                metaInfo= self.meta(listOfFiles,zip_ref,file_name)
            
                jetname=self.Image(listOfFiles,zip_ref,metaInfo,i)
                dictt={'dump':file_name,'images':jetname}
                self.dump_list.append(dictt)
                i=i+1
        uniqueMeta=list({(dictionary['nozzleType'],dictionary['raster']): dictionary for dictionary in self.nozzle}.values())
        data={'zipAndimagePath':self.dump_list,'nozzle used':uniqueMeta}
        self.saveJson(data)
        return(data)
    
    def saveJson(self,data):
        
        json_object = json.dumps(data)
         
        # Writing to sample.json
        jssn=os.path.join(self.dst_dir,"forLabels.json")
        with open(jssn, "w") as outfile:
            outfile.write(json_object)
        return
    
    def meta(self,listOfFiles,zip_ref,file_name):
        
        nozzleType=None
        for f in listOfFiles:
            if f.endswith('/imgMeta.json'):
                zip_ref.open(f)
                imgMeta=zip_ref.read(f)
                imgMeta=json.loads(imgMeta.decode("utf-8"))
                nozzleType=imgMeta['data'][0]['meta']['param']['nozzleType']
                raster=imgMeta['data'][0]['meta']['cuttingHead']['raster']
                self.nozzle.append({"nozzleType":nozzleType,'raster':raster})
              
                break
            
        if nozzleType==None:
            print('imgmeta.json is not available in the dump:{}'.format(file_name))
            
        return({"nozzleType":nozzleType,'raster':raster})
    
    def fusion(self,Im):
       
        #Merge
        mergeMertens = cv2.createMergeMertens()
        exp = mergeMertens.process(Im)
           
        #UnNormalize 
        alpha = 0xFFFF / (np.max(exp)-np.min(exp))
        beta = -np.min(exp)* alpha
        exp=alpha*exp+beta
        exp = exp.astype(np.uint16)
        return(exp)
    
    def Image(self,listOfFiles,zip_ref,metaInfo,count):
        nozzleType=metaInfo['nozzleType']
        raster=metaInfo['raster']
        string=nozzleType + '_R'+ str(raster)
        Im=[]
        for f in listOfFiles:
            if f.endswith('.png'):
                zip_ref.open(f)
                img=zip_ref.read(f)
                img = cv2.imdecode(np.frombuffer(img, np.uint8),cv2.IMREAD_ANYDEPTH)
                Im.append(img)
        exp=self.fusion(Im)
        if self.label==True:
            cv2.putText(img=exp, text=string, org=(15,30), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=0xFFFF,thickness=2)
        jetname=os.path.join(self.dst_dir,'fused-'+str(count)+'.png')
        plt.imsave(jetname,exp)
    
        return(jetname)
    
GM=getImgesForLabelling(directory, dst_dir,label)
data=GM.getImages()

