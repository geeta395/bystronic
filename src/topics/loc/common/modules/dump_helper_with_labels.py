# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:50:25 2022S

@author: chggo
"""

# Get .h5 files from all the zip files given in the "path"


import os
from zipfile import ZipFile
from modules.logger import logger
from .H5Reader import H5Reader



class dump_helper_with_labels():
    def __init__(self,path):
    
       self.path=path
      
    def getlabels(self):
        
        F=[]
    
        for item in os.listdir(self.path): 
            if item=='DumpFP':
                dd=self.unZip(os.path.join(self.path,'DumpFP'),l=1)
                if dd is not None:
                    F.append(dd)
               
                
            elif item=='DumpTP':
                dd=self.unZip(os.path.join(self.path,'DumpTP'),l=0)
                if dd is not None:
                    F.append(dd)
              
        
            elif item=='DumpUnsure':
                dd=self.unZip(os.path.join(self.path,'DumpUnsure'),l=None)
                if dd is not None:
                    F.append(dd)
        return(F)
                
            
        
    def unZip(self,p,l=None):
        
        fold=[]     
        j=0
        label=[]
        ZipName=[]
        dictn=None
        dup_loc=[]
        dup_recut=[]
    
        for item in os.listdir(p):                # loop through items in dir
            if item.endswith('.zip'):                # check for ".zip" extension
                file_name=os.path.join(p,item)
                zip_ref = ZipFile(file_name)         # create zipfile object
                listOfFiles = zip_ref.namelist()
                count=0
                opd=os.path.dirname
                logger.info('{} zipfile is opened'.format(j))
                for f in listOfFiles :
                    
                    if f.endswith('.h5') and opd(f)=='data/lossOfCutDetected':
                         
                         f2=zip_ref.open(f) 
                         dup_loc.append(f2)
                         count=count+1
                    elif f.endswith('.h5') and opd(f)=='data/lossOfCutRecut':
                         
                         f2=zip_ref.open(f) 
                         dup_recut.append(f2)
                         count=count+1
                if count !=2 :                            #(more than 2 .h5 files in any folder)
                    
                    logger.info('-------------------------------------------------------------------')
                    logger.info('Number of .h5 file in dump {} is {}'.format(j,count))
                 
                emp=self.empty(dup_loc[-1],j)
                emp1=self.empty(dup_recut[-1],j)
                if emp==False and emp1 ==False:
                         
                    # append only last two elements to fix more than 2 .h5 files error
                    fold.append(dup_loc[-1]) 
                    fold.append(dup_recut[-1]) 
                  
                    label.append(l)
                    ZipName.append(item)
                        
                    
               
                j=j+1
                zip_ref.close() 
        dictn={'fold':fold,'label':label,'ZipName':ZipName}
                
                
        return(dictn)
    
    def createFolder(self):
       
        foldTest=0
        F=self.getlabels()
        logger.info('total zip files read from FP:{}'.format(len(F[0]['fold'])/2))
        logger.info('total zip files read from TP : {}'.format(len(F[1]['fold'])/2))
        logger.info('total zip files read from UnSure:{}'.format(len(F[2]['fold'])/2))
        
        if len(F)==1:
            fold=(F[0]['fold'])
            labels=(F[0]['label'])
            ZipName=(F[0]['ZipName'])
        elif len(F)==2:
            fold=F[0]['fold']+F[1]['fold']
            labels=F[0]['label']+F[1]['label']
            ZipName=F[0]['ZipName']+F[1]['ZipName']
        elif len(F)==3:
            fold=F[0]['fold']+F[1]['fold']
            labels=F[0]['label']+F[1]['label']
            ZipName=F[0]['ZipName']+F[1]['ZipName']
            foldTest=F[2]['fold']
            zipTest=F[2]['ZipName']
    
        return(fold,labels,foldTest,ZipName,zipTest) 


    def empty(self,fold1,dumpNum,setLimit=90):
        
        emp=False
        H5File=H5Reader(fold1)
        h5=H5File.readH5()
       
        ecat=h5['ecat']
        
        if ecat.shape[0]<setLimit:
            emp=True
            logger.info('discard dump {}'.format(dumpNum))
        
            
        return(emp)
