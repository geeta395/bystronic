# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 11:51:20 2022

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
  

directory=r'C:\Users\chggo\REG_analysis\MlOpsIcpLocDetection\data\data_preparation\data_selection\20221118_20221128_down\10101642\test'
dst_dir=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\data\newData\azure18_28Nov\down\test'
#folder='checkNozzleFlying'
folder='checkNozzleCalibrationDown'
#folder='checkNozzleSheet'
#folder='checkNozzleCalibrationTop'
label=True

class getImgesForLabelling():
    def __init__(self,directory,dst_dir,folder,label):
        self.directory=directory
        self.dst_dir=dst_dir
        self.dump_list=[]
        self.nozzle=[]
        self.folder=folder
        self.label=label
        
    def getImages(self):
        i=0
        for item in os.listdir(self.directory):                
      
            print('{}th folder is being processed'.format(i))
            self.jet_list=[]
            file_name=os.path.join(self.directory,item)
            metaInfo= self.meta(file_name)
        
            jetname,exp=self.Image(file_name,metaInfo,i)
            dictt={'dump':file_name,'images':jetname}
            self.dump_list.append(dictt)
            i=i+1
        
        uniqueMeta=list({(dictionary['nozzleType'],dictionary['raster']): dictionary for dictionary in self.nozzle}.values())
        data={'zipAndimagePath':self.dump_list,'nozzle and raster':uniqueMeta}
        self.saveJson(data)
        return(data,exp)
    
    def saveJson(self,data):
        
        json_object = json.dumps(data)
         
        # Writing to sample.json
        jssn=os.path.join(self.dst_dir,"forLabels.json")
        with open(jssn, "w") as outfile:
            outfile.write(json_object)
        return
    
    def meta(self,file_name):
        jsn=os.path.join(file_name,'data','imgMeta.json')
        nozzleType=None
        imgMeta=open(jsn)
        imgMeta=json.load(imgMeta)
        nozzleType=imgMeta['data'][0]['meta']['param']['nozzleType']
        raster=imgMeta['data'][0]['meta']['cuttingHead']['raster']
        self.nozzle.append({"nozzleType":nozzleType,'raster':raster})
            
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
    
    
    def Image(self,file_name,metaInfo,count):
        nozzleType=metaInfo['nozzleType']
        raster=metaInfo['raster']
        string=nozzleType + '_R'+ str(raster)
        Im=[]
        Impath=os.path.join(file_name,'img',self.folder)
        for f in os.listdir(Impath):   
            if f.endswith('.png'):
                imgPath=os.path.join(Impath,f)
                img=cv2.imread(imgPath,cv2.IMREAD_ANYDEPTH)
                Im.append(img)
        exp=self.fusion(Im)
        
        if self.label==True:
            cv2.putText(img=exp, text=string, org=(15,30), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color= 0xFFFF,thickness=2)
        
        jetname=os.path.join(self.dst_dir,'fused_'+ str(count)+'.png')
        plt.imsave(jetname,exp,cmap='jet',vmin=0,vmax=65535)
        return(jetname,exp)
    
GM=getImgesForLabelling(directory, dst_dir,folder,label)
data,exp=GM.getImages()

