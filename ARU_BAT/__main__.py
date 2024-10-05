import time
import json
import os
from datetime import datetime, timedelta
from multiprocessing import Process
from devicesv2 import SensorSHT3x, RTC, Microphone_Record, Display

def TempSensors():
	# Instance for SHT3x sensor
	TEMPSensor_1 = SensorSHT3x(address=0x44)
	TEMPSensor_2 = SensorSHT3x(address=0x45)
	
	# Set read precission for TEMPSensor
	# -> low 
	# -> medium
	# -> high
	TEMPSensor_1.set_precision(mode='low')
	TEMPSensor_2.set_precision(mode='low')
	
	rtc = RTC()
	current_time = rtc.get_rtc_time()
	temperature, humidity = TEMPSensor_1.read_temp_humid()
	temperature2, humidity2 = TEMPSensor_2.read_temp_humid()
	
	while True:
		
		print(f"Year-Month-Day\tTime\tTemperature\tHumidity[%]\n"
			f"{current_time.year}-"
			f"{current_time.month}-"
			f"{current_time.day}\t"
			f"{current_time.strftime('%H:%M:%S')}\t"
			f"{temperature:.2f}\t{humidity:.2f}\n")
		print(f"Year-Month-Day\tTime\tTemperature\tHumidity[%]\n"
			f"{current_time.year}-"
			f"{current_time.month}-"
			f"{current_time.day}\t"
			f"{current_time.strftime('%H:%M:%S')}\t"
			f"{temperature2:.2f}\t{humidity2:.2f}\n")
		
		TEMPSensor_1.write_data(temperature, humidity)
		TEMPSensor_2.write_data(temperature2, humidity2)
		time.sleep(5.1)

def BatSense(sampling_frec = 48000):
	if configs["constant_record"] is True:
		while True:
			mic = Microphone_Record(record_seconds = 5)
			mic.start_recording()
			time.sleep(0.1)
	
	elif configs["state_record"] is True:
		return 0	# On develop	 
	mic.close()
	

def RTC_Alarm(start_time, end_time):
	# Convert the entries on datetime objects
	rtc = RTC()
	current_year = datetime.now().year
	start_time = datetime.strptime(f"{current_year}-"
									f"{start_time_str}", 
									"%Y-%m-%d-%H-%M")
	end_time = datetime.strptime(f"{current_year}-"
									f"{end_time_str}", 
									"%Y-%m-%d-%H-%M")
    
	if end_time < start_time:
		end_time += timedelta(days=1)

	while True:
		if start_time <= datetime.now() < end_time:
			return 0
		elif datetime.now() >= end_time:
			rtc.set_wake_alarm(wake_time = start_time.strftime("%H:%M"))
			os.system("sudo shutdown now")
		break

if __name__ == "__main__":
	with open("config.json", "r") as json_file:
		configs = json.load(json_file)
	display = Display()
	
	""" Message of the Day """	
	display.MOTD("BatSense", duration = 3)
	
	display.check_settings()	# Check Settings on Display
	display.actual_config()		# Print actual Settings
	
	if configs["start_time"] is not None and configs["end_time"] is not None and (configs["constant_record"] is True or configs["state_record"] is True) and configs["program"] is True:
		
		temp_process = Process(target = TempSensors)
		mic_process = Process(target = BatSense)
		#rtc_process = Process(target = RTC_Alarm)
	
		temp_process.start()
		mic_process.start()
		#rtc_process.start()
	
		temp_process.join()
		mic_process.join()
		#rtc_process.join()
