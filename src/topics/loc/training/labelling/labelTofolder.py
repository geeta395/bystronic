# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 12:01:51 2022

@author: chggo
"""

import pandas as pd
import shutil
import os
pjoin=os.path.join

# move dumps to folders according to labels

# Read excel
path=r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData'

imageNameList=pd.read_excel(pjoin(path,'unlabeled-20221808\joined.xlsx'))

TruePos=pjoin(path,'DumpTp\\')
FalsePos=pjoin(path,'DumpFp\\')
Unsure=pjoin(path,'DumpUnsure\\')
SourceFolder=pjoin(path,'unlabeled-20221808\\')

def sendToFloder(imageNameList):
    for i in range(imageNameList.shape[0]):
        if imageNameList['label'][i]==0:
            image2move=imageNameList['zipName'][i]
            source=pjoin(SourceFolder,image2move)
            destination=pjoin(TruePos,image2move)
            shutil.move(source,destination)
            
        
        if imageNameList['label'][i]==1:
            image2move=imageNameList['zipName'][i]
            source=pjoin(SourceFolder,image2move)
            destination=pjoin(FalsePos,image2move)
            shutil.move(source,destination)
            
        if imageNameList['label'][i]==2:
            image2move=imageNameList['zipName'][i]
            source=pjoin(SourceFolder,image2move)
            destination=pjoin(Unsure,image2move)
            shutil.move(source,destination)
    return

sendToFloder(imageNameList)
        