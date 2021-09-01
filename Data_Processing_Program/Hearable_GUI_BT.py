# -----------------------------------------------------------------------------
# Hearables_GUI.py
# ----------------------------------------------------------------------------- 
"""
Author:     Ian 
Created:    2021 Jan 11
Modified:   2021 Jan 11
Description
-----------
Build a GUI to control the Hearables Device.
"""

        
import serial
import threading
import time
# import datetime
import math
import array
import os
import csv

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets, uic
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import *
from pyqtgraph.graphicsItems.GradientEditorItem import Gradients

import numpy as np
from numpy_ringbuffer import RingBuffer

# from ctypes import *

import sys

import argparse
from Hearable_API import Hearable

from scipy import signal
from statistics import mean

import configPopup as cp

# from MainWindow import *

timestr = time.strftime("%Y%m%d_%H%M%S")
print(timestr)

data_str = 'data_' + timestr + '.bin'


parser = argparse.ArgumentParser(description='captures data from port 8 (default)')
parser.add_argument("--port",default='COM4',help="--port=COM3")
parser.add_argument("--file",default=data_str,help="--file=data.bin")
args = parser.parse_args()


###########################
#Configurable parameters
###########################

PPG_BUFF_SIZE = 500
EEG_BUFF_SIZE = 4096
EEG_FFT_SIZE = 4096
EEG_SPECTRO_LENGTH = 200
EEG_OVERLAP = int(EEG_FFT_SIZE/2)
UPDATE_DELAY = 5  #update period in seconds
DISP_LENGTH = 100
SPO2_AVERAGING = 5

BTN_START_STRING_START = "Start"
BTN_START_STRING_STOP = "Stop"

OP_FILE = args.file
PORT = args.port

SPECTRO_MIN = -140
SPECTRO_MAX = -90
SPECTRO_MAX_FREQ = 60


# N = 250 # number of PPG points
# M = 10000 # number of EEG points

fs = 1000.0  # Sample frequency (Hz)
f0 = 50.0  # Frequency to be removed from signal (Hz)
Q = 30.0  # Quality factor
fs_ppg = 1000/32;
# Design notch filter
b, a = signal.iirnotch(f0, Q, fs)


#scipy.signal.butter(N, Wn, btype='low', analog=False, output='ba', fs=None)
bHigh, aHigh = signal.butter(5, 1,'hp', fs=1000) #5th order high pass at 1hz
bLow, aLow = signal.butter(5, 30,'lp', fs=1000 ) #5th order high pass at 1hz


sosHpPPG = signal.butter(5, 0.8,'hp', fs=fs_ppg,output='sos') #5th order high pass at 1hz
sosLpPPG = signal.butter(5, 15,'lp', fs=fs_ppg,output='sos') #5th order low pass at 10hz
# bLowPPG, aLowPPG = signal.butter(5, 30,'lp', fs=32 ) #5th order high pass at 1hz



###########################
# Initialise variables
###########################

spo2_store = np.zeros(DISP_LENGTH,dtype=float)
spo2_smooth_store = np.zeros(DISP_LENGTH,dtype=float)
increment = 2.6e05

ptr = -DISP_LENGTH                      # set first x position
readPos = 0
eegTs_wpr = 0
eegSample_wpr = 0

spectroData = SPECTRO_MIN * np.ones((SPECTRO_MAX_FREQ,EEG_SPECTRO_LENGTH),dtype=float) 
totalSampleCount = 0

#############################
# QT Window
#############################


class MainWindow(QtWidgets.QMainWindow):
    
    myHearable = None
    opFile = None
    buff_red = np.zeros(PPG_BUFF_SIZE,dtype='uint32')
    buff_ir = np.zeros(PPG_BUFF_SIZE,dtype='uint32')
    buff_green = np.zeros(PPG_BUFF_SIZE,dtype='uint32')
    ppg_time = np.zeros(PPG_BUFF_SIZE,dtype='uint32')
    
    buff_EEG = np.zeros(EEG_BUFF_SIZE,dtype='float32')
    eeg_time = np.zeros(EEG_BUFF_SIZE,dtype='uint32')
    
    configPage = None
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
     
        
        self.opFile = OP_FILE
        
        
        #output dump file
        if os.path.exists(self.opFile):
            os.remove(self.opFile)
        self.initSerial(PORT)
        self.myHearable = Hearable(self.ser)
        
        #Load the UI Page
        # uic.loadUi('mainWindow.ui', self)
        
        self.createPPG()
        self.createEEG()
        self.createCtrl()
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.eegBox,stretch=55) #stretch controls the size ratio 
        mainLayout.addWidget(self.ppgBox,stretch=35)
        mainLayout.addWidget(self.ctrlBox,stretch=10)
        
        wid = QtGui.QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(mainLayout)
        # self.showMaximized()
        
    def createPPG(self):
        self.ppgBox = QGroupBox("PPG")
        
        self.gwPPG = PlotWidget()
        self.gwPPGraw = PlotWidget()
        self.lblSpo2 = QLabel ("--")
        
        layout = QGridLayout()
        layout.addWidget(self.gwPPG,0,0)
        layout.addWidget(self.gwPPGraw,0,1)
        
        self.ppgBox.setLayout(layout)
        
    def createEEG(self):
        self.eegBox = QGroupBox("EEG")
        
        self.gwEEG = PlotWidget()
        
        win = pg.GraphicsLayoutWidget()
        
        self.vbSpectro = win.addViewBox()
        self.spectroImg = pg.ImageItem(border='w')
        self.spectroImg.setOpts(axisOrder='row-major')
        
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(self.spectroImg)
        # If you don't add the histogram to the window, it stays invisible, but I find it useful.
        win.addItem(hist)
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(SPECTRO_MIN,SPECTRO_MAX)
        
        gradient = Gradients['magma'] #thermal’, ‘flame’, ‘yellowy’, ‘bipolar’, ‘spectrum’, ‘cyclic’, ‘greyclip’, ‘grey’, ‘viridis’, ‘inferno’, ‘plasma’, ‘magma’
        self.cmap = pg.ColorMap(
            pos=[c[0] for c in gradient['ticks']],
            color=[c[1] for c in gradient['ticks']],
            mode=gradient['mode'])
        hist.gradient.setColorMap(self.cmap)
        
        self.vbSpectro.addItem(self.spectroImg)
        
        layout =  QVBoxLayout()
        layout.addWidget(self.gwEEG)
        layout.addWidget(win)
        
        self.eegBox.setLayout(layout)
        
    def createCtrl(self):
        self.ctrlBox = QGroupBox("Control")
        
        self.lblInfo = QLabel ("Push Start to begin")
        self.btnConfigPpg = QPushButton("Configure Device")
        self.btnStart = QPushButton("Start")
        self.btnStop = QPushButton("Stop")
        
        self.btnStart.clicked.connect(self.startAq)
        self.btnStop.clicked.connect(self.stopAq)
        self.btnConfigPpg.clicked.connect(self.configHearable)
        
        layout =  QGridLayout()
        layout.addWidget(self.lblInfo,0,0,1,3)
        layout.addWidget(self.btnConfigPpg,1,0)
        layout.addWidget(self.btnStart,1,1)
        layout.addWidget(self.btnStop,1,2)
        
        self.ctrlBox.setLayout(layout)
    
    def exitGUI(self):
        self.myHearable.stopAq()
        self.threadClose=True
        time.sleep(0.5)
        self.ser.close()
    
    def serMonitor(self):
        while True:
            bytesToRead = self.ser.inWaiting()
            if(bytesToRead > 20000):
                print('Backlog of data risk of loss')
            val = self.ser.read(bytesToRead)
            
            if len(val) > 0:
                
                with open(self.opFile,'ab') as f:
                    f.write(val)
                self.myHearable.processData(val)
            
            
                
            if self.threadClose:
                break
            time.sleep(0.01)
    
    
    
    
    def initSerial(self,port):
        self.ser = serial.Serial(port, baudrate=1000000, bytesize=8, parity='N', stopbits=1,timeout=None)
        self.ser.set_buffer_size(rx_size = 32768, tx_size = 32768)
        
        #flag to close thread
        self.threadClose=False
        #thread to monitor the serial port and dump to a file
        t = threading.Thread(name='serMonitor', target=self.serMonitor)
        t.daemon = True
        t.start()
        
    
    def configHearable(self):
        self.configPage = cp.configPopup(self.myHearable)
        # self.configPage.setGeometry(QRect(100, 100, 400, 200))
        self.configPage.show()

    
    def startAq(self):
        self.initialiseRecording()
        self.myHearable.startAq()
    
    def stopAq(self):
        self.myHearable.stopAq()

    def initialiseRecording(self):
        #TODO Reset variables
        #TODO open new recording file
        #TODO save configuration information somewhere
        pass
        
            
            
            
            
##############################
### QtApp Initialisation #####
##############################

app = QtWidgets.QApplication(sys.argv)
main = MainWindow()

#PPG SPO2
rawPen = pg.mkPen(color=(0, 120, 0))   #set up the line colour
raw_curve = main.gwPPG.plot(pen=rawPen)           # create an empty "plot" (a curve to plot)

smoothPen = pg.mkPen(color=(255, 255, 0), width=2)
smooth_curve = main.gwPPG.plot(pen=smoothPen)        

main.gwPPG.setYRange(50, 100, padding=0)
main.gwPPG.showGrid(x=False, y=True, alpha=0.5)



#EEG
eegCurve = main.gwEEG.plot(pen=rawPen)        
main.gwEEG.setYRange(-0.1, 0.1, padding=0)
main.gwEEG.showGrid(x=False, y=True, alpha=0.5)




#PPG raw
redPen = pg.mkPen(color=(255, 0, 0), width=2)
irPen = pg.mkPen(color=(0, 0, 255), width=2)
greenPen =pg.mkPen(color=(0, 255, 0), width=2)

redCurve = main.gwPPGraw.plot(pen=redPen)
irCurve = main.gwPPGraw.plot(pen=irPen)
greenCurve = main.gwPPGraw.plot(pen=greenPen)

# main.gwPPG.setYRange(50, 100, padding=0)
main.gwPPGraw.showGrid(x=False, y=True, alpha=0.5)



main.show()



##############################
### QtApp functions      #####
##############################

def updatePlt():
    global spo2_store, ptr, raw_curve, spo2_smooth_store, smooth_curve, main, eegTs_wpr, eegSample_wpr, spectroData, EEG_SPECTRO_LENGTH, EEG_OVERLAP, EEG_FFT_SIZE,totalSampleCount
    
    ########################
    #   PPG
    ########################
    
    spo2 = 0
    loopsize=32
    while main.myHearable.PPGData[0].__len__() > loopsize:
        #print('.')
        for i in range(loopsize):
            main.ppg_time = np.roll(main.ppg_time,-1)
            main.ppg_time[-1] = (main.myHearable.PPGData[0].popleft())
            
            if main.myHearable.PPGData[1].__len__() >0:
                main.buff_red = np.roll(main.buff_red,-1)
                main.buff_red[-1] = (main.myHearable.PPGData[1].popleft())
                # print(main.buff_red[-1])
                
            if main.myHearable.PPGData[2].__len__() >0:
                main.buff_ir = np.roll(main.buff_ir,-1)
                main.buff_ir[-1] = (main.myHearable.PPGData[2].popleft())
                
            if main.myHearable.PPGData[3].__len__() >0:
                main.buff_green = np.roll(main.buff_green,-1)
                main.buff_green[-1] = (main.myHearable.PPGData[3].popleft())
            
        dc_red = np.mean(main.buff_red)
        dc_ir = np.mean(main.buff_ir)
        ac_red = np.max(main.buff_red) - np.min(main.buff_red)
        ac_ir = np.max(main.buff_ir) - np.min(main.buff_ir)
        if not (ac_red ==0 or dc_red ==0 or ac_ir ==0 or dc_ir ==0) and np.mean(main.buff_red[-10:]) > 10000:
            spo2 = 104 - 17.0*((ac_red/dc_red)/(ac_ir/dc_ir))
        # print(dc_red,dc_ir,ac_red,ac_ir,spo2)
        
        # main.lblInfoUpdate(spo2) #bit hacky, but just want to provide some feedback when sensor comes off
            
        spo2_store = np.roll(spo2_store,-1)
        spo2_store[-1] =  spo2
        spo2_smooth = np.mean(spo2_store[-SPO2_AVERAGING:-1])
        spo2_smooth_store = np.roll(spo2_smooth_store,-1)
        spo2_smooth_store[-1] = spo2_smooth
        
        
        ptr += 1                              # update x position for displaying the curve
        raw_curve.setData(spo2_store)                     # set the curve with this data
        smooth_curve.setData(spo2_smooth_store)                     
        raw_curve.setPos(ptr,0)                   # set x position in the graph to 0
        smooth_curve.setPos(ptr,0)      
        if spo2 ==0:
            main.lblSpo2.setText ('--')
        else:
            main.lblSpo2.setText (str(int(round(spo2)))  + "%" )
        
        redFiltHp = signal.sosfiltfilt(sosHpPPG,main.buff_red)
        redFilt = signal.sosfiltfilt(sosLpPPG,redFiltHp)
        redCurve.setData(redFilt)
        irFiltHp = signal.sosfiltfilt(sosHpPPG,main.buff_ir)
        irFilt = signal.sosfiltfilt(sosLpPPG,irFiltHp)
        irCurve.setData(irFilt)
        greenFiltHp = signal.sosfiltfilt(sosHpPPG,main.buff_green)
        greenFilt = signal.sosfiltfilt(sosLpPPG,greenFiltHp)
        greenCurve.setData(greenFilt)

        
    ########################
    #   EEG
    ########################
    
    
    # eegTs = np.zeros(main.myHearable.EEData[0].__len__() ,'uint32')
    # eegSamples = np.zeros(main.myHearable.EEData[1].__len__() ,float)
    
    for i in range( main.myHearable.EEGData[0].__len__() ):
        main.eeg_time[eegTs_wpr] = main.myHearable.EEGData[0].popleft()
        eegTs_wpr = (eegTs_wpr + 1) % EEG_BUFF_SIZE
        
            
            
    for i in range( main.myHearable.EEGData[2].__len__() ):
        main.buff_EEG[eegSample_wpr] = main.myHearable.EEGData[2].popleft()
        if (eegSample_wpr +1) % (EEG_OVERLAP)==0 and (totalSampleCount +1) >= EEG_BUFF_SIZE:
            if eegSample_wpr +1 == EEG_BUFF_SIZE: 
                buff = main.buff_EEG
            else: 
                buff = np.concatenate((main.buff_EEG[eegSample_wpr:],main.buff_EEG[:eegSample_wpr]))
            #f,t,Sxx = signal.spectrogram(buff,fs=int(main.myHearable.eeg.speed), nperseg=EEG_FFT_SIZE, noverlap=EEG_OVERLAP,mode='psd') 
            # print(Sxx[0:SPECTRO_MAX_FREQ,:])
            #spectroData = np.hstack((spectroData,Sxx[0:SPECTRO_MAX_FREQ,:]))
            #spectroData = np.delete(spectroData, np.s_[:-EEG_SPECTRO_LENGTH],1)
            # print(np.log(np.min(spectroData[0:SPECTRO_MAX_FREQ,:])), np.log(np.max(spectroData[0:SPECTRO_MAX_FREQ,:])))
            #print(spectroData)
            # print(np.min(spectroData[0:55,:]), np.max(spectroData[0:SPECTRO_MAX_FREQ,:]))
            #main.spectroImg.setImage(np.log(spectroData[0:55,:]))
        eegSample_wpr = (eegSample_wpr + 1) % EEG_BUFF_SIZE
        totalSampleCount += 1
        
        
        
    
    
    
    # yRange = max(main.buff_EEG) - min(main.buff_EEG)
    lpVals = signal.filtfilt(bLow,aLow,main.buff_EEG,method='gust')
    hpVals = signal.filtfilt(bHigh, aHigh,lpVals,method='gust')
    filtVals = signal.filtfilt(b,a,hpVals,method='gust')
    # print(len(filtVals))
    # print(yRange)
    
    blanking = 200
    
    if (eegSample_wpr < blanking):
        filtVals[0:eegSample_wpr+blanking] = 0
        filtVals[eegSample_wpr-blanking:] = 0
    elif (eegSample_wpr > EEG_BUFF_SIZE - blanking):
        filtVals[eegSample_wpr-blanking:] = 0
        filtVals[:blanking-eegSample_wpr+EEG_BUFF_SIZE] = 0
    else:
        filtVals[eegSample_wpr - blanking : eegSample_wpr + blanking] = 0
    
    main.gwEEG.setYRange(min(filtVals), max(filtVals), padding=0)
    eegCurve.setData(filtVals[10:-10])
    
    

    
    
    
        
            
    QtGui.QApplication.processEvents()    # you MUST process the plot now






timer  = pg.QtCore.QTimer()
timer.timeout.connect(updatePlt)
timer.start(UPDATE_DELAY*1000)





##################
### END QtApp ####
##################
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

main.exitGUI()

# if __name__ == '__main__':

    # import sys

    # app = QApplication(sys.argv)
    # gallery = WidgetGallery()
    # gallery.show()
    
    # sys.exit(app.exec_()) 
