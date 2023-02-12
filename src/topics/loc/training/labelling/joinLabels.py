# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 09:05:17 2022

@author: chggo
"""

import pandas as pd
import numpy as np
import re

# Read Data from label studio
labelFromLS=r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData\unlabeled_20220109\labeled(20220109).csv'
labelFromLS=pd.read_csv(labelFromLS)

# Read Zip file name
UploadedList=r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData\unlabeled_20220109\uploded.xlsx'
UploadedList=pd.read_excel(UploadedList)
UploadedList=list(UploadedList.iloc[:,-1])


def checkRepetition(UploadedList):
    B=[]
    for i in range(len(UploadedList)):
        B.append(UploadedList[i].split("_")[1])
        
    repeatedIndex=[]
    for j in range(len(repeatedIndex)-1):
        for i in range(len(repeatedIndex)-1):
            if j>i and repeatedIndex[j]==repeatedIndex[i]:
                repeatedIndex.append(i)
    if len(repeatedIndex)==0:
        print('No Repeatition')
    else:
        print('{} Repeated Values are found'.format(len(repeatedIndex)))
    return(repeatedIndex)

repeatedIndex=checkRepetition(UploadedList)
    

Images=labelFromLS['image']
labels=labelFromLS['choice']

# Category to Numeric
#labels.replace(['TP-LOC', 'FP-No LOC','Not Sure'], [0, 1,2], inplace=True)
labels.replace(['TP-(real LOC)', 'FP-(No LOC)','Not Sure'], [0, 1,2], inplace=True)
                       
# Get image name form Images

def getName(Images,labels):
    Img=[]
    Num=[]
    for img in Images:
        txt=img.split("/")
        a=(txt[-1])
        Img.append(a)
        txt1=a.split("__")
        num=re.split(r'\W+', txt1[-1])[0]
        Num.append(num)
    imageNameList=pd.DataFrame({'imgage':Img,'num':(Num),'labels':labels})
    return(imageNameList)

def deleteRepeated(Images,labels,UploadedList):
    imageNameList=getName(Images,labels)
    res = [eval(i) for i in imageNameList['num']]
    imageNameList['num']=res
    imageNameList=imageNameList.sort_values(by=['num'])
    imageNameList=imageNameList.reset_index(drop=True)
    length=imageNameList.shape[0]
    S=[]
    for i in range(0,length-1): #
        if (int(imageNameList['num'][i]) != int(imageNameList['num'][i+1])):
            S.append(list(imageNameList.iloc[i,:]))
        else:
            print('Image number {} is repeated at {}th position'.format(imageNameList['num'][i],i))
    if (int(imageNameList['num'][length-2]) != int(imageNameList['num'][length-1])):
            S.append(list(imageNameList.iloc[length-1,:]))
       
    S=np.stack(S)
    imageNameList=pd.DataFrame(S,columns=['imgage','num','label'])
   
    if len(UploadedList)==(imageNameList.shape[0]):
        imageNameList['zipName']=UploadedList
    else: 
        print('Repeated values check zipfiles')
    imageNameList=imageNameList.drop(['num'],axis=1)
    return(imageNameList)


imageNameList=deleteRepeated(Images, labels, UploadedList)
imageNameList.to_excel(r'C:\Users\chggo\data\Recut\icpLocDetection\labeledData\unlabeled_20220109\joined.xlsx',index=False)
