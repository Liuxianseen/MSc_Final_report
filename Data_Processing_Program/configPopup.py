import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets, uic
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import *

from Hearable_API import Hearable

class configPopup(QWidget):

    currHearable = None
    def __init__(self,Hearable):
        QWidget.__init__(self)
        
        
        self.currHearable = Hearable
        self.createPPG(Hearable)
        self.createEEG(Hearable)
        self.createACC(Hearable)

        self.btnUpload = QPushButton("Send configuration")
        self.btnCancel = QPushButton("Cancel")
        
        self.btnUpload.clicked.connect(self.processConfig)
        self.btnCancel.clicked.connect(self.cancel)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.ppgBox)
        mainLayout.addWidget(self.eegBox)
        mainLayout.addWidget(self.accBox)
        mainLayout.addWidget(self.btnUpload)
        mainLayout.addWidget(self.btnCancel)
        
        self.setLayout(mainLayout)
        
    def createPPG(self,Hearable):
        self.ppgBox = QGroupBox("PPG")
        self.ppgEnableCheckBox = QCheckBox("Enable")
        self.ppgEnableCheckBox.setChecked(Hearable.ppg.enable)
        
        self.ppgModeLBL = QLabel("PPG mode")
        self.ppgModeComboBox = QComboBox()
        for option in Hearable.ppg.d_mode:
            self.ppgModeComboBox.addItem(option)
        self.ppgModeComboBox.setCurrentIndex(self.ppgModeComboBox.findText(Hearable.ppg.mode))
        self.ppgModeLBL.setBuddy(self.ppgModeComboBox)
        
        
        self.ppgADCLBL = QLabel("ADC range")
        self.ppgADCComboBox = QComboBox()
        for option in Hearable.ppg.d_adc_range:
            self.ppgADCComboBox.addItem(option)
        self.ppgADCComboBox.setCurrentIndex(self.ppgADCComboBox.findText(Hearable.ppg.adc_range))
        self.ppgADCLBL.setBuddy(self.ppgADCComboBox)
        
        
        self.ppgAverageLBL = QLabel("Sample averaging")
        self.ppgAverageComboBox = QComboBox()
        for option in Hearable.ppg.d_averaging:
            self.ppgAverageComboBox.addItem(option)
        self.ppgAverageComboBox.setCurrentIndex(self.ppgAverageComboBox.findText(Hearable.ppg.averaging))
        self.ppgAverageLBL.setBuddy(self.ppgAverageComboBox)       

        self.ppgRateLBL = QLabel("Sampling rate")
        self.ppgRateComboBox = QComboBox()
        for option in Hearable.ppg.d_sample_rate:
            self.ppgRateComboBox.addItem(option)
        self.ppgRateComboBox.setCurrentIndex(self.ppgRateComboBox.findText(Hearable.ppg.sample_rate))
        self.ppgRateLBL.setBuddy(self.ppgRateComboBox)   
        
        
        self.ppgPWLBL = QLabel("Pulse width")
        self.ppgPWComboBox = QComboBox()
        for option in Hearable.ppg.d_pulse_width:
            self.ppgPWComboBox.addItem(option)
        self.ppgPWComboBox.setCurrentIndex(self.ppgPWComboBox.findText(Hearable.ppg.pulse_width))
        self.ppgPWLBL.setBuddy(self.ppgPWComboBox)   
        
        
        
        self.ppgRedLBL = QLabel("Red amplitude (0-255)")
        self.ppgIRLBL = QLabel("IR amplitude (0-255)")
        self.ppgGreenLBL = QLabel("Green amplitude (0-255)")
        self.ppgProxLBL = QLabel("Proximity amplitude (0-255)")
        self.ppgProxThreshLBL = QLabel("Proximity threshold (0-255)")
        
        self.ppgRedSpinBox = QSpinBox()
        self.ppgIRSpinBox = QSpinBox()
        self.ppgGreenSpinBox = QSpinBox()
        self.ppgProxSpinBox = QSpinBox()
        self.ppgProxThreshSpinBox = QSpinBox()
        
        self.ppgRedSpinBox.setMaximum(255)
        self.ppgIRSpinBox.setMaximum(255)
        self.ppgGreenSpinBox.setMaximum(255)
        self.ppgProxSpinBox.setMaximum(255)
        self.ppgProxThreshSpinBox.setMaximum(255)
        
        self.ppgRedSpinBox.setMinimum(0)
        self.ppgIRSpinBox.setMinimum(0)
        self.ppgGreenSpinBox.setMinimum(0)
        self.ppgProxSpinBox.setMinimum(0)
        self.ppgProxThreshSpinBox.setMinimum(0)
        
        self.ppgRedSpinBox.setValue((Hearable.ppg.red_amplitude))
        self.ppgIRSpinBox.setValue((Hearable.ppg.ir_amplitude))
        self.ppgGreenSpinBox.setValue((Hearable.ppg.green_amplitude))
        self.ppgProxSpinBox.setValue((Hearable.ppg.proximity_amplitude))
        self.ppgProxThreshSpinBox.setValue((Hearable.ppg.proximity_threshold))
        
        
        
        layout =  QGridLayout()
        layout.addWidget(self.ppgEnableCheckBox,0,0)
        layout.addWidget(self.ppgModeLBL,1,0)
        layout.addWidget(self.ppgModeComboBox,1,1)
        layout.addWidget(self.ppgADCLBL,2,0)
        layout.addWidget(self.ppgADCComboBox,2,1)
        layout.addWidget(self.ppgAverageLBL,3,0)
        layout.addWidget(self.ppgAverageComboBox,3,1)
        layout.addWidget(self.ppgRateLBL,4,0)
        layout.addWidget(self.ppgRateComboBox,4,1)
        layout.addWidget(self.ppgPWLBL,5,0)
        layout.addWidget(self.ppgPWComboBox,5,1)
        
        layout.addWidget(self.ppgRedLBL,0, 2)
        layout.addWidget(self.ppgRedSpinBox,0, 3)
        layout.addWidget(self.ppgIRLBL,1, 2)
        layout.addWidget(self.ppgIRSpinBox,1, 3)
        layout.addWidget(self.ppgGreenLBL,2, 2)
        layout.addWidget(self.ppgGreenSpinBox,2, 3)
        layout.addWidget(self.ppgProxLBL,3, 2)
        layout.addWidget(self.ppgProxSpinBox,3, 3)
        layout.addWidget(self.ppgProxThreshLBL,4, 2)
        layout.addWidget(self.ppgProxThreshSpinBox,4, 3)
        
        
        

        self.ppgBox.setLayout(layout)
        
        
        
    def createEEG(self,Hearable):
        self.eegBox = QGroupBox("EEG")
        self.eegEnableCheckBox = QCheckBox("Enable")
        self.eegEnableCheckBox.setChecked(Hearable.eeg.enable)
        
        self.eegTestCheckBox = QCheckBox("Test")
        self.eegTestCheckBox.setChecked(Hearable.eeg.test)
        
        self.eegSpeedLBL = QLabel("Sampling rate")
        self.eegSpeedComboBox = QComboBox()
        for option in Hearable.eeg.d_speed:
            self.eegSpeedComboBox.addItem(option)
        self.eegSpeedComboBox.setCurrentIndex(self.eegSpeedComboBox.findText(Hearable.eeg.speed))
        self.eegSpeedLBL.setBuddy(self.eegSpeedComboBox)
        
        
        self.eegC0CheckBox = QCheckBox("Channel 0")
        self.eegC0CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel0])
        self.eegC1CheckBox = QCheckBox("Channel 1")
        self.eegC1CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel1])
        self.eegC2CheckBox = QCheckBox("Channel 2")
        self.eegC2CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel2])
        self.eegC3CheckBox = QCheckBox("Channel 3")
        self.eegC3CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel3])
        self.eegC4CheckBox = QCheckBox("Channel 4")
        self.eegC4CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel4])
        self.eegC5CheckBox = QCheckBox("Channel 5")
        self.eegC5CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel5])
        self.eegC6CheckBox = QCheckBox("Channel 6")
        self.eegC6CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel6])
        self.eegC7CheckBox = QCheckBox("Channel 7")
        self.eegC7CheckBox.setChecked(Hearable.eeg.d_channel[Hearable.eeg.channel7])
        
        
        
        
        layout =  QGridLayout()
        layout.addWidget(self.eegEnableCheckBox,0,0)
        layout.addWidget(self.eegTestCheckBox,1,0)
        layout.addWidget(self.eegSpeedLBL,2,0)
        layout.addWidget(self.eegSpeedComboBox,2,1)
        layout.addWidget(self.eegC0CheckBox,3,0)
        layout.addWidget(self.eegC1CheckBox,4,0)
        layout.addWidget(self.eegC2CheckBox,5,0)
        layout.addWidget(self.eegC3CheckBox,6,0)
        layout.addWidget(self.eegC4CheckBox,3,2)
        layout.addWidget(self.eegC5CheckBox,4,2)
        layout.addWidget(self.eegC6CheckBox,5,2)
        layout.addWidget(self.eegC7CheckBox,6,2)
        
        
        

        self.eegBox.setLayout(layout)
        
        
    def createACC(self,Hearable):
        self.accBox = QGroupBox("Accelerometer")
        self.accEnableCheckBox = QCheckBox("Enable")
        self.accEnableCheckBox.setChecked(Hearable.acc.enable)
        
        self.accRateLBL = QLabel("Sample rate")
        self.accRateComboBox = QComboBox()
        for option in Hearable.acc.d_sample_rate_divider:
            self.accRateComboBox.addItem(option)
        self.accRateComboBox.setCurrentIndex(self.accRateComboBox.findText(Hearable.acc.sample_rate_divider))
        self.accRateLBL.setBuddy(self.accRateComboBox)
        
        self.accDataLBL = QLabel("Data op update rate")
        self.accDataComboBox = QComboBox()
        for option in Hearable.acc.d_data_op_rate:
            self.accDataComboBox.addItem(option)
        self.accDataComboBox.setCurrentIndex(self.accDataComboBox.findText(Hearable.acc.data_op_rate))
        self.accDataLBL.setBuddy(self.accDataComboBox)
        
        
        self.accLpfLBL = QLabel("Low Pass Filter")
        self.accLpfComboBox = QComboBox()
        for option in Hearable.acc.d_low_pass_filter:
            self.accLpfComboBox.addItem(option)
        self.accLpfComboBox.setCurrentIndex(self.accLpfComboBox.findText(Hearable.acc.low_pass_filter))
        self.accLpfLBL.setBuddy(self.accLpfComboBox)        
        
        
        self.accGyroLBL = QLabel("Gyro sensitivity")
        self.accGyroComboBox = QComboBox()
        for option in Hearable.acc.d_gyro_sensitivity:
            self.accGyroComboBox.addItem(option)
        self.accGyroComboBox.setCurrentIndex(self.accGyroComboBox.findText(Hearable.acc.gyro_sensitivity))
        self.accGyroLBL.setBuddy(self.accGyroComboBox)    
        
        
        self.accMotionDetectLBL = QLabel("Motion detection threshold (0-255)")
        self.accZeroMotionLBL = QLabel("Zero motion detection threshold  (0-255)")
        self.accMotionDurationLBL = QLabel("Motion detection duration  (0-255)")
        self.accZeroMotionDurationLBL = QLabel("Zero motion detection duration (0-255)")
        
        self.accMotionDetectSpinBox = QSpinBox()
        self.accZeroMotionSpinBox = QSpinBox()
        self.accMotionDurationSpinBox = QSpinBox()
        self.accZeroMotionDurationSpinBox = QSpinBox()
        
        self.accMotionDetectSpinBox.setMaximum(255)
        self.accZeroMotionSpinBox.setMaximum(255)
        self.accMotionDurationSpinBox.setMaximum(255)
        self.accZeroMotionDurationSpinBox.setMaximum(255)
        
        self.accMotionDetectSpinBox.setMinimum(0)
        self.accZeroMotionSpinBox.setMinimum(0)
        self.accMotionDurationSpinBox.setMinimum(0)
        self.accZeroMotionDurationSpinBox.setMinimum(0)
        
        self.accMotionDetectSpinBox.setValue(int(Hearable.acc.motion_detect_thresh))
        self.accZeroMotionSpinBox.setValue(int(Hearable.acc.zero_motion_thresh))
        self.accMotionDurationSpinBox.setValue(int(Hearable.acc.motion_detect_duration))
        self.accZeroMotionDurationSpinBox.setValue(int(Hearable.acc.zero_motion_duration))
        
        
        
        layout =  QGridLayout()
        layout.addWidget(self.accEnableCheckBox,0,0)
        layout.addWidget(self.accRateLBL,1,0)
        layout.addWidget(self.accRateComboBox,1,1)
        layout.addWidget(self.accDataLBL,2,0)
        layout.addWidget(self.accDataComboBox,2,1)
        layout.addWidget(self.accLpfLBL,3,0)
        layout.addWidget(self.accLpfComboBox,3,1)
        layout.addWidget(self.accGyroLBL,4,0)
        layout.addWidget(self.accGyroComboBox,4,1)
        
        layout.addWidget(self.accMotionDetectLBL,1, 2)
        layout.addWidget(self.accMotionDetectSpinBox,1, 3)
        layout.addWidget(self.accZeroMotionLBL,2, 2)
        layout.addWidget(self.accZeroMotionSpinBox,2, 3)
        layout.addWidget(self.accMotionDurationLBL,3, 2)
        layout.addWidget(self.accMotionDurationSpinBox,3, 3)
        layout.addWidget(self.accZeroMotionDurationLBL,4, 2)
        layout.addWidget(self.accZeroMotionDurationSpinBox,4, 3)
        

        self.accBox.setLayout(layout)

    def processConfig(self):
        
        self.currHearable.ppg.enable = int(self.ppgEnableCheckBox.isChecked())
        self.currHearable.ppg.mode =  self.ppgModeComboBox.currentText()	
        self.currHearable.ppg.adc_range = 	self.ppgADCComboBox.currentText()
        self.currHearable.ppg.averaging = self.ppgAverageComboBox.currentText()	
        self.currHearable.ppg.sample_rate = self.ppgRateComboBox.currentText()
        self.currHearable.ppg.pulse_width = self.ppgPWComboBox.currentText()
        self.currHearable.ppg.red_amplitude = self.ppgRedSpinBox.value()
        self.currHearable.ppg.ir_amplitude = self.ppgIRSpinBox.value()
        self.currHearable.ppg.green_amplitude = self.ppgGreenSpinBox.value()	
        self.currHearable.ppg.proximity_amplitude = self.ppgProxSpinBox.value()
        self.currHearable.ppg.proximity_threshold = self.ppgProxThreshSpinBox.value()
        
        
        self.currHearable.eeg.enable = int(self.eegEnableCheckBox.isChecked())
        self.currHearable.eeg.test = int(self.eegTestCheckBox.isChecked())
        self.currHearable.eeg.speed = self.eegSpeedComboBox.currentText()	
        self.currHearable.eeg.channel0 = self.currHearable.eeg.inv_d_channel[int(self.eegC0CheckBox.isChecked())]
        self.currHearable.eeg.channel1 = self.currHearable.eeg.inv_d_channel[int(self.eegC1CheckBox.isChecked())]
        self.currHearable.eeg.channel2 = self.currHearable.eeg.inv_d_channel[int(self.eegC2CheckBox.isChecked())]
        self.currHearable.eeg.channel3 = self.currHearable.eeg.inv_d_channel[int(self.eegC3CheckBox.isChecked())]
        self.currHearable.eeg.channel4 = self.currHearable.eeg.inv_d_channel[int(self.eegC4CheckBox.isChecked())]
        self.currHearable.eeg.channel5 = self.currHearable.eeg.inv_d_channel[int(self.eegC5CheckBox.isChecked())]
        self.currHearable.eeg.channel6 = self.currHearable.eeg.inv_d_channel[int(self.eegC6CheckBox.isChecked())]
        self.currHearable.eeg.channel7 = self.currHearable.eeg.inv_d_channel[int(self.eegC7CheckBox.isChecked())]
        
        

        self.currHearable.acc.enable = int(self.accEnableCheckBox.isChecked())
        self.currHearable.acc.sample_rate_divider = self.accRateComboBox.currentText()
        self.currHearable.acc.data_op_rate = self.accDataComboBox.currentText()
        self.currHearable.acc.low_pass_filter = self.accLpfComboBox.currentText()
        self.currHearable.acc.gyro_sensitivity =  self.accGyroComboBox.currentText()
        self.currHearable.acc.motion_detect_thresh = self.accMotionDetectSpinBox.value()
        self.currHearable.acc.zero_motion_thresh = self.accZeroMotionSpinBox.value()
        self.currHearable.acc.motion_detect_duration = self.accMotionDurationSpinBox.value()
        self.currHearable.acc.zero_motion_duration = self.accZeroMotionDurationSpinBox.value()
        
        
        self.currHearable.ppgWriteConfig()
        self.currHearable.eegWriteConfig()
        self.currHearable.accWriteConfig()
        
        self.close()
        
        
        
    def cancel(self):
        self.close()
    
    