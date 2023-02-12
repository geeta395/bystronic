#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:08:37 2020

@author: lcfa
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
        
        # Ecat Sniffer
        if 'EcatSniffer_Variables' in hfStreams.keys():
            dsetEcat = hfStreams.get('EcatSniffer_Variables')[()]
        else:
             print('---> missing stream EcatSniffer_Variables')
             return None
        
        ecat = {}
        ecat['tsBeckhoff'] = dsetEcat['beckhofftime']
        ecat['cutcontrol'] = dsetEcat['Cuttinghead_Tx_SiCoax']
        ecat['nozzleDist'] = dsetEcat['RtExt_Rx_CurrentNozzleDistance']
        
        #ecat['visionStatus'] = dsetEcat['Cuttinghead_Tx_VisionStatus']
        ecat['veloX'] = dsetEcat['DriveX1_Tx_VeloFeedback1'] * (24.0 * 60 * 1000 / 1073741824)
        ecat['veloY'] = dsetEcat['DriveY_Tx_VeloFeedback1'] * (24.0 * 60 * 1000 / 1073741824)
        ecat['posX'] = dsetEcat['DriveX1_Tx_PositionFeedback1'] * (24.0 / 1048576)
        ecat['posY'] = dsetEcat['DriveY_Tx_PositionFeedback1'] * (24.0 / 1048576)
        ecat['actPart'] = dsetEcat['RtExt_Rx_ActualPart']
        ecat['sscCw'] = dsetEcat['Cuttinghead_Rx_Controlword']
        ecat['sscFr'] = dsetEcat['Cuttinghead_Tx_FocusReal']
        ecat['sscVf'] = dsetEcat['Cuttinghead_Rx_VisionFocus']
        
        ecat['LensPosFLO'] = dsetEcat['Cuttinghead_Rx_FocalLengthOffset'] / 100
        ecat['DA'] = dsetEcat['Cuttinghead_Rx_NozzleDistance'] / 100
        ecat['FL'] = dsetEcat['Cuttinghead_Rx_Focus'] / 100
        ecat['DV'] = 0.0       # Düsenverlängerung (=0)
        ecat['overRideFeed'] = dsetEcat['RtExt_Tx_Override_Feed']
        
        result = {}
        result['param'] = pd.DataFrame(param)
        result['paramConfig'] = pd.DataFrame(paramConfig, index=[0])
        result['vr'] = pd.DataFrame(vr)
        result['ecat'] = pd.DataFrame(ecat)
        
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
    
    
#H5File=H5Reader(r"C:\Users\chggo\data\Recut\LoC_detection (need to process)\dump_20220106-151609.848_L10_ItearOffDetected_B694793548726273264_c62\data\tearOffDetected\20220106-151609.848.h5")  
#h5=H5File.readH5()