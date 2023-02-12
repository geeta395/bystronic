# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 10:01:17 2023

@author: chggo
"""

import numpy as np
import matplotlib.pyplot as plt
# customize colormap for 16 bit images

class ColorMap():
    def __init__(self):
        pass
    
    def main(self,img):
        
        # Color map 
        custom_colormap = [
          (0.0000, 0.00, 0.00, 0.25),
          (0.0200, 0.00, 0.40, 0.70),
          (0.0800, 0.10, 0.60, 1.00),
          (0.2500, 0.20, 0.86, 0.86),
          (0.5000, 0.93, 1.00, 0.05),
          (0.9500, 1.00, 0.25, 0.10),
          (1.0000, 1.00, 0.75, 0.75)]
        
       
        imgC=self.applyMap(img,custom_colormap)
        
        return(imgC)
        
    
    def getChannels(self,custom_colormap):
        rangeMax = 65535 #(for 16 bit)
        
        m_lut_Red = []
        m_lut_Green = []
        m_lut_Blue = []
        
        mapIdx = 0
        for i in range(rangeMax):
            if (mapIdx < len(custom_colormap) - 1 and custom_colormap[mapIdx + 1][0] * rangeMax < i):
              mapIdx += 1
              
            d = custom_colormap[mapIdx + 1][0] - custom_colormap[mapIdx][0]
            w1 = 1 / d * (i / rangeMax - custom_colormap[mapIdx][0])
            w0 = 1 - w1
            
            m_lut_Red.append((255 * (w0 * custom_colormap[mapIdx][1] + w1 * custom_colormap[mapIdx + 1][1]) + 0.5))
            m_lut_Green.append((255 * (w0 * custom_colormap[mapIdx][2] + w1 * custom_colormap[mapIdx + 1][2]) + 0.5))
            m_lut_Blue.append((255 * (w0 * custom_colormap[mapIdx][3] + w1 * custom_colormap[mapIdx + 1][3]) + 0.5))
       
        return(m_lut_Red,m_lut_Green,m_lut_Blue)
    
    def applyMap(self,img):
        m_lut_Red,m_lut_Green,m_lut_Blue=self.getChannels(custom_colormap)
        total_pixels=np.prod(img.shape)
        w,h=img.shape
        img8=((img/256).astype('uint8')).reshape(w,h,1)
        imgC=np.zeros(shape=(w,h)).astype('uint8')
        while 0<idx<total_pixels:
            grey = (img8[idx * 2 + 1] << 4) + (img8[idx * 2] >> 4)
    		imgC[idx * 3] = m_lut_Blue[grey]
    		imgC[idx * 3 + 1] = m_lut_Green[grey]
    		imgC[idx * 3 + 2] = m_lut_Red[grey]
            idx -= 1

        return(imgC)
        
CM=ColorMap()
imgC=CM.main(img)