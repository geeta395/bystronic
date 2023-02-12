#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:39:11 2022

@author: chggo
"""

from tensorflow import keras
from tensorflow.keras import layers,regularizers
from keras.layers import BatchNormalization,LeakyReLU,Add,concatenate


class Model():
    def __init__(self):
        pass
       
    def imgReg(self,x):
       
       initializer = keras.initializers.HeNormal()
       
       
       x = layers.Conv2D(16, 3, padding="same",kernel_initializer=initializer)(x)
       x = BatchNormalization(epsilon=0.1)(x)
       x = LeakyReLU(alpha=0.1)(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       res=x
       
       
       x = layers.Conv2D(32, 3, padding="same",kernel_initializer=initializer)(x)  
       x = BatchNormalization(epsilon=0.1)(x)
       x = LeakyReLU(alpha=0.1)(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
     
       res = layers.Conv2D(32, 1, padding="same",strides=2)(res)
       x=Add()([x,res])
       res=x
       
     
       x = layers.Conv2D(64, 3, padding="same",kernel_initializer=initializer)(x)  
       x = BatchNormalization(epsilon=0.1)(x)
       x = LeakyReLU(alpha=0.1)(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       res = layers.Conv2D(64, 1, padding="same",strides=2)(res)
       x = Add()([x, res])
       res=x
       
       x = layers.Conv2D(128, 3, padding="same",kernel_initializer=initializer)(x)  
       x = BatchNormalization(epsilon=0.1)(x)
       x = LeakyReLU(alpha=0.1)(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       res = layers.Conv2D(128, 1, padding="same",strides=2)(res)
       x = Add()([x, res])
       res=x
       
       x = layers.Conv2D(256, 3, padding="same",kernel_initializer=initializer)(x)  
       x = BatchNormalization(epsilon=0.1)(x)
       x = LeakyReLU(alpha=0.1)(x)
       x= layers.MaxPooling2D(2, padding="same")(x)
       
       
       # Dense Block
       x=layers.Flatten()(x)
       x = layers.Dropout(0.2)(x)
       x=layers.Dense(128,activation='relu', kernel_regularizer=regularizers.L2(.01))(x)
       x = layers.Dropout(0.1)(x)
       x=layers.Dense(64,activation='relu', kernel_regularizer=regularizers.L2(.01))(x)
       x=layers.Dense(16, activation='relu',kernel_regularizer=regularizers.L2(.01))(x)
       output=layers.Dense(3,activation='linear')(x)    # Linear activation is Identity
       
       
       return output

   
    