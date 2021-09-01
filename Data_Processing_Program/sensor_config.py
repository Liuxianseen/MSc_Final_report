class eeg_config:
    d_enable = {'Disable':0, 'Enable':1}
    d_test = {'Disable':0, 'Enable':1}
    d_speed = {'32000':128,'16000':129,'8000':130,'4000':131,'2000':132,'1000':133,'500':134}
    d_channel = {'Not Connected':0,'Physiological input':1,'External sensor':2,'RES (dont use)':3}

    inv_d_channel = {0:'Not Connected', 1:'Physiological input',2:'External sensor',3:'RES (dont use)'}


    
    
    def __init__(self):
        self.enable = 1		#(0-1)	#Enable/disable this sensor
        self.test = 0		#(0-1)	#Enable/disable built in test
        self.speed = '1000'		#(128-134)	#Sampling rate: 128=32ks/s, 129=16ks/s, 130=8ks/s, 131=4ks/s, 132=2ks/s, 133=1ks/s, 134=500s/s 

        #Channel Config, for each channel choose from 1 of the following 4 options
        #0 = NC  Not Connected, 
        #1 = PHY (Physiological input used for RLD), 
        #2 = SEN (External sensor e.g. Breathing belt not used for RLD), 
        #3 = RES (Impedance pneumography with R series device)  (DO NOT USE)
        self.channel0 = 'Physiological input'	#(0-3)	
        self.channel1 = 'Physiological input'	#(0-3)	
        self.channel2 = 'Physiological input'	#(0-3)	
        self.channel3 = 'Physiological input'	#(0-3)	
        self.channel4 = 'Physiological input'	#(0-3)	
        self.channel5 = 'Physiological input'	#(0-3)	
        self.channel6 = 'Physiological input'	#(0-3)	
        self.channel7 = 'Physiological input'	#(0-3)	
        
        
class acc_config:

    d_enable = {'Disable':0, 'Enable':1}
    d_sample_rate_divider = {'1000':0,'500':1,'330':2,'250':3,'200':4,'167':5,'143':6,'125':7,'110':8,'100':9,'90':10}
    d_data_op_rate = {'100':1,'67':2,'50':3,'40':4,'33':5,'29':6,'25':7,'22':8,'20':9}
    d_low_pass_filter = {'188':1,'98':2,'42':3,'20':4,'10':5,'5':6}
    d_gyro_sensitivity = {'250':0,'500':1,'1000':2,'2000':3}


    
	
    def __init__(self):
        self.enable = 1					#(0-1)	#Enable/disable this sensor
        self.sample_rate_divider = '200' 	#(0-10)	#Sampling rate calculated as 1000/(value+1) so setting to 4 gives 1000/5 = 200Hz
        self.data_op_rate = '20'			#(1-9)	#Rate at which the motion processor outputs data (doesn't change sampling rate): calculated as 200/(value+1) i.e. 1=100Hz, 9=20Hz
        self.low_pass_filter = '42'			#(1-6)	#Cutoff for digital low pass filter (accel & gyro). 1=188Hz, 2=98Hz, 3=42Hz, 4=20Hz, 5=10Hz, 6=5Hz
        self.gyro_sensitivity =  '2000'		#(0-3)	#Range of gyroscope ADC: 0=250, 1=500, 2=1000, 3=2000 degrees/s
        self.motion_detect_thresh = 2 	#(0-255	#Threshold for classifying as motion 
        self.zero_motion_thresh = 156	#(0-255	#Threshold for classifying as no motion 0-255
        self.motion_detect_duration = 80 #(0-255	#Duration for classifying as motion 
        self.zero_motion_duration = 0
        
        
        
        
        
class ppg_config:


    d_enable = {'Disable':0, 'Enable':1}
    d_mode = {'Heart Rate Mode':2,'SpO2 Mode':3,'Multi Led Mode':7}
    d_LED_num = {'Heart Rate Mode':1,'SpO2 Mode':2,'Multi Led Mode':3}
    d_adc_range = {'8pA':0,'16pA':1,'31pA':2,'63pA':3}
    d_averaging = {'1':0,'2':1,'4':2,'8':3,'16':4,'32':5}
    d_sample_rate = {'50':0,'100':1,'200':2,'400':3,'800':4,'1000':5,'1600':6,'3200':7}
    d_pulse_width = {'69us':0,'118us':1,'215us':2,'411us':3}
    



     
    
    def __init__(self):
        self.enable = 1					#(0-1)		#Enable/disable this sensor
        self.mode = 'SpO2 Mode'  					#(2,3,7)	#Sensor mode (enables different combinations of LEDs):  2 = HeartRateMode, 3 = SpO2Mode, 7 = MultiLedMode.  
        self.adc_range = '16pA' 				#(0-3)		#Controls ADC LSB (and hence range): 0 = 8pA, 1 = 16pA, 2 = 31pA, 3 = 63pA
        self.averaging = '32'				#(0-5)		#Averages data samples before transmission: 0= no averaging, 1 = 2 samples, 2 = 4, 3 = 8, 4 = 16, 5 = 32 samples

        # GENERAL NOTE - Do not set both sample rate and pulse width to max. 
        #Rough guideline is that sample_rate*pulse_width should be less than 0.21 in SpO2 mode and less than 0.3 in Heartrate mode. 
        #More info in Tables 11 and 12 in Max30101 data sheet   
        self.sample_rate = '1000'				#(0-7)		#Sample rate: 0 = 50Hz, 1 = 100Hz, 2 = 200Hz, 3 = 400Hz, 4 = 800Hz, 5 = 1kHz, 6 = 1.6kHz, 7 = 3.2kHz
        self.pulse_width = '69us'				#(0-3)		#LED pulse width: 0 = 69us,	1 = 118us, 2 = 215us, 3 = 411us

        self.red_amplitude = 31			#(0-255)	#red LED amplitude: value*0.2mA  so 1 = 0.2mA, 12 = 2.4mA ... up to max of 255
        self.ir_amplitude = 31			#(0-255)	#IR LED amplitude: value*0.2mA  so 1 = 0.2mA, 12 = 2.4mA ... up to max of 255
        self.green_amplitude = 31		#(0-255)	#Green LED amplitude: value*0.2mA  so 1 = 0.2mA, 12 = 2.4mA ... up to max of 255
        self.proximity_amplitude = 15 	#(0-255)	#IR LED amplitude for detecting skin contact: value*0.2mA  so 1 = 0.2mA, 12 = 2.4mA ... up to max of 255
        self.proximity_threshold = 15	#(0-255)	#Threshold for detecting skin contact 1:255, 0 is most sensitive, 255 will probably never trigger.
