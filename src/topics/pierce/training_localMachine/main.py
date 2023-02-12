# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:19:48 2023

@author: chggo
"""

from topics.pierce.common.visualization.readData import ReadData


# parameters
dataPath=r"C:\Users\chggo\REG_analysis\resources\resultPiercing\test"
resultPath=r'C:\Users\chggo\REG_analysis\resources\resultPiercing\re'
gamma=2.5
   
# Proces dumps
RD=ReadData(dataPath,resultPath,gamma)
Data=RD.getGrphsForAll()



    
 
    
    
    
    
    
    
    
    
    
    
    
    
