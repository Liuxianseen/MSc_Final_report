#############################
# QT Window
#############################

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

import numpy as np
from numpy_ringbuffer import RingBuffer

# from ctypes import *

import sys

import argparse
from Hearable_API import Hearable

from scipy import signal
from statistics import mean

import configPopup as cp


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
        # colormap = cm.get_cmap("magma")
        # colormap._init()
        # lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt
        # self.spectroImg.setLookupTable(lut)
        
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(self.spectroImg)
        # If you don't add the histogram to the window, it stays invisible, but I find it useful.
        win.addItem(hist)
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(SPECTRO_MIN,SPECTRO_MAX)
        
        
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
        # print('0' + chConfig + intTest + fs)
        # self.myHearable.ppg.mode = 'Multi Led Mode'
        # self.myHearable.ppgWriteConfig(self.ser)
        self.configPage = cp.configPopup(self.myHearable)
        # self.configPage.setGeometry(QRect(100, 100, 400, 200))
        self.configPage.show()

    
    def startAq(self):
        self.myHearable.startAq()
    
    def stopAq(self):
        self.myHearable.stopAq()
 