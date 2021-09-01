# -----------------------------------------------------------------------------
# sbGUI.py
# ----------------------------------------------------------------------------- 
"""
Author:     Ian 
Created:    2016 Apr 15
Modified:   2016 Apr 15
Description
-----------
Build a GUI to control recording settings.
"""

        
        
import serial
import threading
import time
import datetime
import math
import array
import os
import numpy as np
from ctypes import *
import sys
from numpy_ringbuffer import RingBuffer

from sensor_config import *





class Hearable:
    
   
    mySerial = None
    def __init__(self,ser):
        
        
        self.ipBuffer = RingBuffer(capacity=50000, dtype=np.uint8)
        
        bufferSize = 50000 #Number of samples to buffer

        self.EEGBytes = RingBuffer(capacity=bufferSize, dtype=np.uint8)
        self.PPGBytes = RingBuffer(capacity=bufferSize, dtype=np.uint8)
        self.ACCBytes = RingBuffer(capacity=bufferSize, dtype=np.uint8)
        
        
        self.EEGData =[RingBuffer(capacity=bufferSize, dtype=np.uint32)]
        self.PPGData=[RingBuffer(capacity=bufferSize, dtype=np.uint32)]
        self.ACCData=[RingBuffer(capacity=bufferSize, dtype=np.uint32)]
        
                
        for i in range(8):
            self.EEGData.append(RingBuffer(capacity=bufferSize, dtype=np.float32))
        for i in range(6):
            self.PPGData.append(RingBuffer(capacity=bufferSize, dtype=np.uint16))
        for i in range(6):
            self.ACCData.append(RingBuffer(capacity=bufferSize, dtype=np.float16))
        
        self.acc = acc_config()
        self.ppg = ppg_config()
        self.eeg = eeg_config()
        
        self.USB_PPG_KEYWORD = 'PPG_'
        self.USB_EEG_KEYWORD = 'EEG_'
        self.USB_ACC_KEYWORD = 'ACC_'
        self.PPG1_KEYWORD = b'PPG1'
        self.PPG2_KEYWORD = b'PPG2'
        self.TIME_KEYWORD = b'Time'

        self.TS_CLOCK_FREQ = 32768

        self.TIMESTAMP_SIZE = 8
        self.USB_PACKET_SIZE = 2048
        self.EEG_BLE_SAMPLES = 8
        self.EEG_BLE_PACKET_SIZE = self.EEG_BLE_SAMPLES * 9 * 3
        self.EEG_CHUNK_SIZE = self.EEG_BLE_PACKET_SIZE + 8

        

        self.ACC_BLE_PACKET_SIZE = 236 #contains lots of zeros and will change as i've added acceleration
        
        
        self.EEG_FREQ = int(self.eeg.speed)
        self.PPG_FREQ = int(self.ppg.sample_rate)/int(self.ppg.averaging)
        self.PPG_NUM_LEDS = int(self.ppg.d_LED_num[self.ppg.mode])
        
        self.PPG_BLE_PACKET_SIZE = 102 #Varies, might be better to test whether correct
        self.PPG_BLE_TEMP_SIZE = 2
        self.PPG_CHUNK_SIZE = self.PPG_BLE_PACKET_SIZE + self.PPG_BLE_TEMP_SIZE
        
        self.mySerial = ser
            
    
    def processData(self,ipData):
        
        for i in range (len(ipData)):
            self.ipBuffer.append(ipData[i])
        
        while self.ipBuffer.__len__() > self.USB_PACKET_SIZE:
            # print(self.ipBuffer.__len__())
            preamble=[]
            for i in range(4):
                preamble.append(self.ipBuffer.popleft())
            header = "".join(map(chr, preamble))
            # print (header)
            
            #trim off the keyword header and write to a file
            if header == self.USB_EEG_KEYWORD:
                for i in range(self.USB_PACKET_SIZE-4):
                    self.EEGBytes.append(self.ipBuffer.popleft())
            elif header == self.USB_PPG_KEYWORD:
                for i in range(self.USB_PACKET_SIZE-4):
                    self.PPGBytes.append(self.ipBuffer.popleft())
            elif header == self.USB_ACC_KEYWORD:
                for i in range(self.USB_PACKET_SIZE-4):
                    self.ACCBytes.append(self.ipBuffer.popleft())
            else:
                print("unrecognised keyword at start of USB packet")
                pass
            
        self.processArrays()
    
    def processArrays(self):
        ###################
        #Process EEG data
        ###################
        while self.EEGBytes.__len__() > (self.EEG_CHUNK_SIZE +self.TIMESTAMP_SIZE):  
            
            eegBuffer = bytearray()
            for i in range(self.EEG_BLE_PACKET_SIZE + self.TIMESTAMP_SIZE):
                eegBuffer.append(self.EEGBytes.popleft())
            offset = eegBuffer.find(self.TIME_KEYWORD)
            if offset >0:
                # print('EEG data gap of at least ', offset)
                eegBuffer = eegBuffer[offset:]
                for i in range(offset):
                    eegBuffer.append(self.EEGBytes.popleft())
            elif offset == -1:
                print('EEG time keyword not found')
            # if len(eegBuffer) != self.EEG_BLE_PACKET_SIZE + self.TIMESTAMP_SIZE:
                # print('EEG buffer length is ', len(eegBuffer))
                
            
            ts = np.frombuffer(eegBuffer[4:8],dtype='uint32')
            raw = np.frombuffer(eegBuffer[8:], dtype='uint8')
            raw = raw.astype('uint32')
            eegWords = np.squeeze(pow(2,8)*raw[2::3] + pow(2,16)*raw[1::3] + pow(2,24)*raw[0::3])
            eegWords = eegWords.astype('int32')
            eegWords = eegWords.astype('float32') *(2.4/(12*pow(2,24))) / pow(2,8)
            
            for i in range(int(len(eegWords)/9)) :
                self.EEGData[0].append(ts+i* int(self.TS_CLOCK_FREQ/self.EEG_FREQ)) #timestamp fudge - assumes 1khz sample need to check fs
                for j in range(8):
                    self.EEGData[j+1].append(eegWords[i*9+j+1])#appending to a ring buffer not the list...
            
            

        ###################
        #Process PPG data
        ###################     
        while self.PPGBytes.__len__() > (self.PPG_CHUNK_SIZE +self.TIMESTAMP_SIZE +len(self.PPG1_KEYWORD)): 
        
            ppgBuffer = bytearray()
            for i in range(self.PPG_CHUNK_SIZE + self.TIMESTAMP_SIZE +len(self.PPG1_KEYWORD)):
                ppgBuffer.append(self.PPGBytes.popleft())
            offset = ppgBuffer.find(b'PPG')
            if offset >0:
                # print('PPG data gap of at least ', offset)
                ppgBuffer = ppgBuffer[offset:]
                for i in range(offset):
                    ppgBuffer.append(self.PPGBytes.popleft())
            elif offset == -1:
                print('PPG time keyword not found')
            ppgSource=0 #default
            if ppgBuffer.find(self.PPG1_KEYWORD) == -1 : ppgSource=1
            
            ts = np.frombuffer(ppgBuffer[8:12],dtype='uint32')
            raw = np.frombuffer(ppgBuffer[12:-2],dtype='uint8')
            raw = raw.astype('uint32')
            vals = np.squeeze(pow(2,16)*raw[0::3] + pow(2,8)*raw[1::3] + raw[2::3])
            #print (vals)
            for i in range(int(len(vals)/self.PPG_NUM_LEDS)): #assumes 2 LED
                self.PPGData[0].append(ts+i*int(self.TS_CLOCK_FREQ/self.PPG_FREQ)) #timestamp fudge - assumes 1khz sample need to check fs
                for j in range(self.PPG_NUM_LEDS):
                    self.PPGData[ppgSource*3+j+1].append(vals[i*self.PPG_NUM_LEDS+j])
        
        # print('There are now ' + str(len(self.EEGData[0])) + ' EEG samples and ' + str(len(self.PPGData[0])) + ' PPG samples')
            
    def startAq(self):
        self.mySerial.write(str.encode('start\r\n'))
        print('attempting to start...')
    
    def stopAq(self):
        self.mySerial.write(str.encode('stop\r\n'))
        print('attempting to stop...')
        
    def eegWriteConfig(self):
        configCmd = str.encode('configeeg') + \
            self.eeg.enable.to_bytes(1, byteorder='big') + \
            self.eeg.test.to_bytes(1, byteorder='big') + \
            self.eeg.d_speed[self.eeg.speed].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel0].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel1].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel2].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel3].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel4].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel5].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel6].to_bytes(1, byteorder='big') + \
            self.eeg.d_channel[self.eeg.channel7].to_bytes(1, byteorder='big') + \
            str.encode('\r\n')

        
        #Debug print out 
        print (configCmd)
        self.mySerial.write(configCmd)
        
        self.EEG_FREQ = int(self.eeg.speed)
        

        
    def eegReadConfig(self):
        pass

    def ppgWriteConfig(self):
        configCmd = str.encode('configppg') + \
            self.ppg.enable.to_bytes(1, byteorder='big') + \
            self.ppg.d_mode[self.ppg.mode].to_bytes(1, byteorder='big') + \
            self.ppg.d_adc_range[self.ppg.adc_range].to_bytes(1, byteorder='big') + \
            self.ppg.d_averaging[self.ppg.averaging].to_bytes(1, byteorder='big') + \
            self.ppg.d_sample_rate[self.ppg.sample_rate].to_bytes(1, byteorder='big') + \
            self.ppg.d_pulse_width[self.ppg.pulse_width].to_bytes(1, byteorder='big') + \
            self.ppg.red_amplitude.to_bytes(1, byteorder='big') + \
            self.ppg.ir_amplitude.to_bytes(1, byteorder='big') + \
            self.ppg.green_amplitude.to_bytes(1, byteorder='big') + \
            self.ppg.proximity_amplitude.to_bytes(1, byteorder='big') + \
            self.ppg.proximity_threshold.to_bytes(1, byteorder='big') + \
            str.encode('\r\n')

        
        #Debug print out 
        print (configCmd)
        self.mySerial.write(configCmd)
        
        
        self.PPG_FREQ = int(self.ppg.sample_rate)/int(self.ppg.averaging)
        self.PPG_NUM_LEDS = int(self.ppg.d_LED_num[self.ppg.mode])
        self.PPG_BLE_PACKET_SIZE = 102 #Varies, might be better to test whether correct
        self.PPG_BLE_TEMP_SIZE = 2
        self.PPG_CHUNK_SIZE = self.PPG_BLE_PACKET_SIZE + self.PPG_BLE_TEMP_SIZE
        
    def ppgReadConfig(self):
        pass
        
    def accWriteConfig(self):
        configCmd = str.encode('configacc') + \
            self.acc.enable.to_bytes(1, byteorder='big') + \
            self.acc.d_sample_rate_divider[self.acc.sample_rate_divider].to_bytes(1, byteorder='big') + \
            self.acc.d_data_op_rate[self.acc.data_op_rate].to_bytes(1, byteorder='big') + \
            self.acc.d_low_pass_filter[self.acc.low_pass_filter].to_bytes(1, byteorder='big') + \
            self.acc.d_gyro_sensitivity[self.acc.gyro_sensitivity].to_bytes(1, byteorder='big') + \
            self.acc.motion_detect_thresh.to_bytes(1, byteorder='big') + \
            self.acc.zero_motion_thresh.to_bytes(1, byteorder='big') + \
            self.acc.motion_detect_duration.to_bytes(1, byteorder='big') + \
            self.acc.zero_motion_duration.to_bytes(1, byteorder='big') + \
            str.encode('\r\n')

        
        #Debug print out 
        print (configCmd)
        self.mySerial.write(configCmd)
        
    def accReadConfig(self):
        pass
