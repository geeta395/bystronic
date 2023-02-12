# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:52:10 2023

@author: chggo
"""

import h5py
import pandas as pd

class H5Reader:
    
    def __init__(self, fileName):
        self.fileName = fileName
        self.log = []
        
    def readString(self, ds):
        return [x.decode() for x in ds][0]
    
    def readStrings(self, ds):
        return [x.decode() for x in ds]
    
    def readNumberAtPosition(self, ds, idx):
        return ds[:,idx]

    
    def readH5(self):
        hfStreams = self.get_streams()
        if '.GHMI.SET.PARAM.CONFIG' in hfStreams.keys():
            dsetParamConfig = hfStreams.get('.GHMI.SET.PARAM.CONFIG')[()] # TwinCat 2
        elif '.gHMI.Set.Param.Config' in hfStreams.keys():
             dsetParamConfig = hfStreams.get('.gHMI.Set.Param.Config')[()] # TwinCat 3
        else:
             print('---> missing stream .GHMI.SET.PARAM.CONFIG or .gHMI.Set.Param.Config')
             return None
        if '.GHMI.SET.PARAM.CUT' in hfStreams.keys():
            dsetParamCut = hfStreams.get('.GHMI.SET.PARAM.CUT')[()]
        elif '.gHMI.Set.Param.Cut' in hfStreams.keys():
            dsetParamCut = hfStreams.get('.gHMI.Set.Param.Cut')[()]
        else:
              print('---> missing stream .GHMI.SET.PARAM.CUT or .gHMI.Set.Param.Cut')
              return None
        paramConfig = {}
        paramConfig['equipmentNummer'] = self.readString(dsetParamConfig['EQUIPMENTNUMBER'])   
        
        param = {}
        param['nozzleType'] = self.readString(dsetParamCut['NOZZLETYPE'])
        param['nozzleDiameter'] = dsetParamCut['NOZZLEDIAMETER']
        param['nozzleDistance_0'] = self.readNumberAtPosition(dsetParamCut['NOZZLEDISTANCECUT'], 0)     # NozzelDistance[0]
        param['nozzleDistance_4'] = self.readNumberAtPosition(dsetParamCut['NOZZLEDISTANCECUT'], 4)     # NozzelDistance[4]
        param['gasType'] = self.readString(dsetParamCut['GASTEXT'])
        if param['gasType'] == 'O2':
            param['gasPressure_0'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH1'], 0) # O2
            param['gasPressure_4'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH1'], 4) # O2
        elif param['gasType'] == 'N2':
            param['gasPressure_0'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH2'], 0) # N2
            param['gasPressure_4'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH2'], 4) # N2
        else:
            param['gasPressure_0'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH3'], 0) # Other gas
            param['gasPressure_4'] = self.readNumberAtPosition(dsetParamCut['GASPRESSURECUTCH3'], 4) # Other gas
        param['raster'] = dsetParamCut['RASTER']
        param['laserPower_0'] = self.readNumberAtPosition(dsetParamCut['CUTPOWER'], 0)          # cutPower[0]
        param['laserPower_4'] = self.readNumberAtPosition(dsetParamCut['CUTPOWER'], 4)          # cutpower[4]
        param['thickness'] = dsetParamCut['THICKNESS']
        param['paramGroup'] = self.readString(dsetParamCut['PARAMGROUP'])
        param['materialNumber'] = self.readString(dsetParamCut['MATERIALNUMBER'])           
        param['nominalSpeed_0'] = self.readNumberAtPosition(dsetParamCut['SPEED'], 0)
        param['nominalSpeed_4'] = self.readNumberAtPosition(dsetParamCut['SPEED'], 4)
        param['focalPosition_0'] = self.readNumberAtPosition(dsetParamCut['FOCALPOSITION'], 0)
        param['focalPosition_4'] = self.readNumberAtPosition(dsetParamCut['FOCALPOSITION'], 4)
        
        # VisionResult
        dsetVR = hfStreams.get('VisionResultCutting')[()]
        vr = {}
        vr['tsBeckhoff'] = dsetVR['beckhofftime']
        for feature in ['frame', 'exposure', 'gain','maxIntensityAvrg', 'maxIntensity', 'rotation', 'luaResult', 'velo_mm_min', 'scale_ppmm', 'trajectory','imageClass']: # 'distBack50', 'distBack80', 'distFront50', 'distLeft10', 'distRight10'
            try:   # I added maxIntensityAvrg
                vr[feature] = dsetVR[feature]
            except:
                self.log.append(f'could not read {feature} in h5 VisionResultCutting')    
        
       
        result = {}
        result['param'] = pd.DataFrame(param)
        result['paramConfig'] = pd.DataFrame(paramConfig, index=[0])
        result['vr'] = pd.DataFrame(vr)
        
        return result
    
    def get_streams(self):
        """
        Read top level streams of h5 file structure
        Returns
        -------
        list of string
            Stream names.
        """
        
        hf = h5py.File(self.fileName, 'r')
        return hf.get('Streams')
        
    def read_video_streams(self):
        hfStreams = self.get_streams()
        
        # Video Streams
        if 'VideoStreams' in hfStreams.keys():
            dsetVideoStreams = hfStreams.get('VideoStreams')[()]
        else:
             print('---> missing stream VideoStreams')
             return None
        
        vs = {}
        vs['name'] = self.readStrings(dsetVideoStreams['name'])
        vs['ch'] = dsetVideoStreams['ch']
        vs['part'] = dsetVideoStreams['part']
        vs['frame'] = dsetVideoStreams['frame']
        
        vs = pd.DataFrame(vs)
        
        return vs
    