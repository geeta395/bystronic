# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 09:06:56 2022

@author: chggo
"""

import os
import pandas as pd
from topics.loc.common.modules.dump_helper import DumpHelper
from topics.loc.common.visualization.mergeCV import mergePlot
pjoin=os.path.join


path= r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData\test1'
result_path=pjoin(path,'result')
imageNam="Preview_"
os.chdir(path)

# create a folder in the given directory

if path:
    try: 
        result_path=os.path.join(path,'result')
        os.mkdir(result_path) 
    except OSError as error: 
        print(error) 
        
        
H55=DumpHelper(path,result_path)
folder,zipName=H55.checkEmpty()

image=mergePlot(path,result_path)


length=len(folder)
for i in range(0,length,2):
    image.saveImg(i,folder,zipName)
    print('Dump {} has been executed'.format(i))
    print('---------------------------------------------------------------------------')

# save name of selected(non empty) zip files
Z=pd.DataFrame({'filename':zipName})
Z.to_excel(os.path.join(path,'uploded.xlsx'))

