# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:57:45 2022

@author: chggo
"""

from math import sqrt
 
# Function to find the circle on
# which the given three points lie
def findCircle(Dict,w,h):
    
    x1=(w*float(Dict['x1']))/100
    x2=(w*float(Dict['x2']))/100
    x3=(w*float(Dict['x3']))/100
    y1=(h*float(Dict['y1']))/100
    y2=(h*float(Dict['y2']))/100
    y3=(h*float(Dict['y3']))/100
    
    point={'x1':x1,'y1':y1,'x2':x2,'y2':y2,'x3':x3,'y3':y3}
    
    x12 = x1 - x2;
    x13 = x1 - x3;
 
    y12 = y1 - y2;
    y13 = y1 - y3;
 
    y31 = y3 - y1;
    y21 = y2 - y1;
 
    x31 = x3 - x1;
    x21 = x2 - x1;
 
    # x1^2 - x3^2
    sx13 = pow(x1, 2) - pow(x3, 2);
 
    # y1^2 - y3^2
    sy13 = pow(y1, 2) - pow(y3, 2);
 
    sx21 = pow(x2, 2) - pow(x1, 2);
    sy21 = pow(y2, 2) - pow(y1, 2);
 
    f = (((sx13) * (x12) + (sy13) *
          (x12) + (sx21) * (x13) +
          (sy21) * (x13)) // (2 *
          ((y31) * (x12) - (y21) * (x13))));
             
    g = (((sx13) * (y12) + (sy13) * (y12) +
          (sx21) * (y13) + (sy21) * (y13)) //
          (2 * ((x31) * (y12) - (x21) * (y13))));
 
    c = (-pow(x1, 2) - pow(y1, 2) -
         2 * g * x1 - 2 * f * y1);
 
    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
    # where centre is (h = -g, k = -f) and
    # radius r as r^2 = h^2 + k^2 - c
    h = -g;
    k = -f;
    sqr_of_r = h * h + k * k - c;
 
    # r is the radius
    r = round(sqrt(sqr_of_r), 5);
    circle={'r':r,'x':h,'y':k}
    return(circle,point)