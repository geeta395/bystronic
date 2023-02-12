# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 14:17:55 2022

@author: chggo
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as st
import statistics as S

path=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\result\resultNoisy\result\allPredictions.xlsx'
en=r'C:\Users\chggo\REG_analysis\icpNozzleCentering\result\resultNoisy\result\ensembleResult.xlsx'
df=pd.read_excel(path,index_col=0)
ensemble=pd.read_excel(en,index_col=0)
heads=10

def forAllHeads(start):
    R=[]
    i=start
    while i < df.shape[1]:
        
        R.append(df.iloc[:,i])
        i=i+4
    return(R)
    
def getAttributes(heads,start,pred,true=[],allowedPixels=5):
   
    rad=pd.DataFrame(forAllHeads(start))
    var=np.sqrt(rad.var(axis=0))
    n=len(var)
    rad=rad.append(var,ignore_index=True)
    rad=rad.append(pred)
    if len(true) !=0 :
        rad=rad.append(true)
        P=[]
        for i in range(n):
            P.append(np.abs(pred[i]-true[i]))
        P=pd.Series(P)
        rad=rad.append(P,ignore_index=True)
    ind=IndX(heads,true)

    rad=rad.set_axis(ind) #,inplace=True)
    if start==0:
        bad=rad[rad.columns[rad.iloc[-1]>allowedPixels]]
        bad=bad.columns
    else:
        bad=0
        
    a=rad.iloc[:heads,:]
    mode=st.mode(a)
    rad=rad.append(list(mode.mode))
    M=a.describe()
    rad=rad.append(M.iloc[5,:])
    idd=rad.index.tolist()
    idx = idd.index(0)
    idd[idx] = 'Mode'
    rad.index = idd
    
    return(rad,bad)

def IndX(heads,true):
    ind=[]
    for i in range(heads):
        ind.append('H_'+ str(i))
    ind.append('SE')
    ind.append('pred')
    if  len(true) !=0 :
        ind.append('true')
   
        ind.append('pixelDiff')
    return(ind)

def combineBad(X,Y,rad,allowedPixels=5):
    pixel=np.sqrt(np.square(X.iloc[-3])+np.square(Y.iloc[-3]))
    P1=pixel>allowedPixels
    bad=P1[P1].index
    Bad=pd.DataFrame()
    Bad= Bad.append(list(bad))
    Bad['predX']=list(X.loc['pred',bad])
    Bad['modeX']=list(X.loc['Mode',bad])
    Bad['medianX']=list(X.loc['50%',bad])
    
    Bad['predY']=list(Y.loc['pred',bad])
    Bad['modeY']=list(Y.loc['Mode',bad])
    Bad['medianY']=list(Y.loc['50%',bad])
    
    Bad['predR']=list(rad.loc['pred',bad])
    Bad['modeR']=list(rad.loc['Mode',bad])
    Bad['medianR']=list(rad.loc['50%',bad])
    return(Bad)
    

rad,badR=getAttributes(10,0,ensemble['r'],ensemble['rTest'])
X,_=getAttributes(10,1,ensemble['X'],ensemble['xTest'])
Y,_=getAttributes(10,2,ensemble['Y'],ensemble['yTest'])
bad=combineBad(X, Y,rad)

