import sys
import numpy as np
import time
import array
import os
import glob
import datetime
import argparse
import csv

parser = argparse.ArgumentParser(description='process a hearables.bin file (default)')
parser.add_argument("--file",default='data_20210828_chest.bin',help="--file=data.bin")
args = parser.parse_args()


#DECLARE FIXED VALUES
USB_PACKET_SIZE=2048
PPG_KEYWORD = b'PPG_'
PPG1_KEYWORD = b'PPG1'
PPG2_KEYWORD = b'PPG2'
EEG_KEYWORD = b'EEG_'
ACC_KEYWORD = b'ACC_'
KEYWORD_SIZE=4
TIME_SIZE = 8


TIME_KEYWORD = b'Time'

TS_CLOCK_FREQ = 32768

TIMESTAMP_SIZE = 8
USB_PACKET_SIZE = 2048
EEG_BLE_SAMPLES = 8
EEG_BLE_PACKET_SIZE = EEG_BLE_SAMPLES * 9 * 3
EEG_CHUNK_SIZE = EEG_BLE_PACKET_SIZE + 8


#zero global
readPos = 0



def processFile(ipFilename='capture.bin', ppgFilename='ppgData.bin', eegFilename='eegData.bin', ppg1Filename='ppg1Data.bin', ppg2Filename='ppg2Data.bin', accFilename='accData.bin'):
    global readPos
    
    ppgList= []
    ppg1List= []
    ppg2List= []
    eegList=[]
    accList =[]
    
    with open(ipFilename, 'rb') as f:
        fLength = os.stat(ipFilename).st_size
        fLength = fLength - (fLength % USB_PACKET_SIZE) #trim any incomplete packets 
        newPacketNum = int((fLength -readPos) / USB_PACKET_SIZE)
        # print (newPacketNum)
        for i in range(0,newPacketNum) :
            f.seek (i*USB_PACKET_SIZE + readPos,0)
            keyword = f.read(4)
            #print(keyword)
            if keyword == PPG_KEYWORD:
                ppgList.append( np.fromfile(f,dtype=np.uint8,count = USB_PACKET_SIZE-KEYWORD_SIZE) )
            elif keyword == PPG1_KEYWORD:
                ppg1List.append( np.fromfile(f,dtype=np.uint8,count = USB_PACKET_SIZE-KEYWORD_SIZE) )
            elif keyword == PPG2_KEYWORD:
                ppg2List.append( np.fromfile(f,dtype=np.uint8,count = USB_PACKET_SIZE-KEYWORD_SIZE) )
            elif keyword == EEG_KEYWORD:
                eegList.append( np.fromfile(f,dtype=np.uint8,count = USB_PACKET_SIZE-KEYWORD_SIZE) )
            elif keyword == ACC_KEYWORD:
                accList.append( np.fromfile(f,dtype=np.uint8,count = USB_PACKET_SIZE-KEYWORD_SIZE) )
            else:
                print ('error - keyword not found')
                exit()
        f.close()
        readPos = fLength 

    
    with open( eegFilename, 'a+b') as f:
        for x in eegList :
            f.write(x)
        f.close()
            
    with open( ppgFilename, 'a+b') as f:
        for x in ppgList :
            f.write(x)
        f.close()
    
    with open( ppg1Filename, 'a+b') as f:
        for x in ppg1List :
            f.write(x)
        f.close()
        
    with open( ppg1Filename, 'a+b') as f:
        for x in ppg2List :
            f.write(x)
        f.close()
        
    with open( accFilename, 'a+b') as f:
        for x in accList :
            f.write(x)
        f.close()


def processEegData(eegFilename):
    
    eegData =[]
    
    with open( eegFilename, 'rb') as f:
        a = f.read()
    
    validLength = a.__len__() - a.__len__() % (EEG_BLE_PACKET_SIZE + TIMESTAMP_SIZE + 8)
    a = a[:validLength]
    n_buffers = int (a.__len__()/(EEG_BLE_PACKET_SIZE + TIMESTAMP_SIZE + 8))
    
    for i in range(n_buffers):
        eegBuffer = bytearray()
        for j in range(EEG_BLE_PACKET_SIZE + TIMESTAMP_SIZE):
            eegBuffer.append(a[i*(EEG_BLE_PACKET_SIZE + TIMESTAMP_SIZE + 8)+j] )
        offset = eegBuffer.find(TIME_KEYWORD)
        assert offset==0
        raw = np.frombuffer(eegBuffer[8:], dtype='uint8')
        raw = raw.astype('uint32')
        eegWords = np.squeeze(pow(2,8)*raw[2::3] + pow(2,16)*raw[1::3] + pow(2,24)*raw[0::3])
        eegWords = eegWords.astype('int32')
        eegWords = eegWords.astype('float32') *(2.4/(12*pow(2,24))) / pow(2,8)
        eegData.extend(eegWords)
    
    eegCsvFile = 'eeg.csv'
    #output dump file
    if os.path.exists(eegCsvFile):
        os.remove(eegCsvFile)
    csvfile = open(eegCsvFile, 'a',newline='')
    csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(int(len(eegData)/9)) :
        csvwriter.writerow(eegData[i*9:i*9+9])
    


if __name__ == '__main__' and sys.flags.interactive == 0:
    ipFilename = args.file
    ppgFilename='ppgData.bin'
    eegFilename='eegData.bin'
    ppg1Filename='ppg1Data.bin'
    ppg2Filename='ppg2Data.bin'
    accFilename='accData.bin'
    if os.path.isfile(ppgFilename): os.remove(ppgFilename)
    if os.path.isfile(eegFilename): os.remove(eegFilename)
    if os.path.isfile(ppg1Filename): os.remove(ppg1Filename)
    if os.path.isfile(ppg2Filename): os.remove(ppg2Filename)
    if os.path.isfile(accFilename): os.remove(accFilename)
    processFile(ipFilename,ppgFilename,eegFilename,ppg1Filename,ppg2Filename,accFilename )
    processEegData(eegFilename)
