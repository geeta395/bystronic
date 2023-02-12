# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 12:55:41 2022

@author: chggo
"""

import json

# write json file for scaled parameters

SCALED_PARAMS = {
    'laser_power':[2000,20000],
    'thickness':[0,25],
    'raster':[0,6],
    'nozzle_diameter':[0,6],
    'nozzle_distance':[0.2,2.0],
    'speed':[630, 85800],
    'focal_position': [-2.5,13.5],
    'gas_pressure':[3,18],
     'cut_control': [0,65535],
            }


# Serializing json
json_object = json.dumps(SCALED_PARAMS, indent=9)
 
# Writing to sample.json
# with open("scaledPara.json", "w") as outfile:
#     outfile.write(json_object)