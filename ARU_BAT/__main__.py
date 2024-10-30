import time
import json
import os
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
from multiprocessing import Process
from devicesv2 import SensorSHT3x, RTC, Microphone_Record, Display
				
class BatSense:
	def __init__(self, display, rtc):
		self.display = display
		self.rtc = rtc
		self.temperature_process = None
		self.mic_process = None
		self.configs = {}
		self.BUTTON_RIGHT = 13
		
	def load_json_configs(self):
		with open("config.json", "r") as json_file:
			self.configs = json.load(json_file)

	def device_starting(self):
		""" Message of the Day """	
		self.display.MOTD("BatSense", duration = 3)
		self.load_json_configs()
		current_time = datetime.now().time()
		if self.configs["program"] is False:
			batsense.config_device()
			self.display.start_program()
			self.load_json_configs()
	
		if self.configs["program"]is True:
			self.display.actual_config()
			self.start_time = datetime.strptime(self.configs["start_time"], "%H:%M").time()
			self.end_time = datetime.strptime(self.configs["end_time"], "%H:%M").time()
			
			if self.start_time <= self.end_time:
				if self.start_time <= current_time < self.end_time:
					batsense.wake_alarm(self.start_time)
					batsense.sleep_alarm(self.end_time)
					batsense.processes()
				else:
					batsense.wake_alarm(self.start_time)
					os.system(f'sudo halt')
			
			else:
				if current_time >= self.start_time or current_time < self.end_time:
					batsense.wake_alarm(self.start_time)
					batsense.sleep_alarm(self.end_time)
					batsense.processes()
				else:
					batsense.wake_alarm(self.start_time)
					os.system(f'sudo halt')
    
			# Configurar la hora de encendido y apagado usando el RTC
			#batsense.wake_alarm(self.start_time)
			#batsense.sleep_alarm(self.end_time)
			#batsense.processes()
	
	def hot_changes(self):
		while True:
			if GPIO.input(self.BUTTON_RIGHT) == GPIO.LOW:
				self.display.MOTD("BatSense", duration=3)
				if self.configs["program"] is True:
					self.display.stop_program()
					time.sleep(0.2)
					self.display.device.clear()
					self.load_json_configs()
					if self.configs["program"] is False:
						self.temp_process.terminate()
						self.mic_process.terminate()
					
				elif self.configs["program"] is False:
					self.display.start_program()
					time.sleep(0.2)
					self.display.device.clear()
					self.load_json_configs()
					batsense.device_starting()
					
	def TempSensors(self):
		# Instance for SHT3x sensor
		TEMPSensor_1 = SensorSHT3x(address=0x44)
		TEMPSensor_2 = SensorSHT3x(address=0x45)
		
		# Set read precission for TEMPSensor
		# -> low 
		# -> medium
		# -> high
		TEMPSensor_1.set_precision(mode='low')
		TEMPSensor_2.set_precision(mode='low')
	
		while True:
			temp_in, humidity_in = TEMPSensor_1.read_temp_humid()
			temp_out, humidity_out = TEMPSensor_2.read_temp_humid()
			current_time = datetime.now()
			print(f"Year-Month-Day\tTime\tTemperature\tHumidity[%]\n"
				f"{current_time.year}-"
				f"{current_time.month}-"
				f"{current_time.day}\t"
				f"{current_time.strftime('%H:%M:%S')}\t"
				f"{temp_in:.2f}\t{humidity_in:.2f}\n")
			print(f"Year-Month-Day\tTime\tTemperature\tHumidity[%]\n"
				f"{current_time.year}-"
				f"{current_time.month}-"
				f"{current_time.day}\t"
				f"{current_time.strftime('%H:%M:%S')}\t"
				f"{temp_out:.2f}\t{humidity_out:.2f}\n")
			
			TEMPSensor_1.write_data(temp_in, humidity_in)
			TEMPSensor_2.write_data(temp_out, humidity_out)
			time.sleep(60)

	def recording(self):
		mic = Microphone_Record()
		if self.configs["constant_record"] is True:
			while True:
				mic.start_recording()
				time.sleep(0.1)
	
		elif configs["state_record"] is True:
			return 0	# On develop	 
		mic.close()
	
	def processes(self):
		self.temp_process = Process(target = self.TempSensors)
		self.mic_process = Process(target = self.recording)
		#self.hot_changes = Process(target = self.hot_changes)
		self.temp_process.start()
		self.mic_process.start()
	
	def config_device(self):
		self.display.setup_config()
		self.display.actual_config()
		self.display.device.clear()
		
	def starting(self):
		self.start_program()
		self.display.device.clear()
	
	def wake_alarm(self, start_time):
		start_time_str = start_time.strftime("%H:%M")
		self.rtc.set_wake_alarm(start_time_str)

	def sleep_alarm(self, end_time):
		end_time_str = end_time.strftime("%H:%M")
		self.rtc.set_shutdown_alarm(end_time_str)

if __name__ == "__main__":
	display = Display()
	rtc = RTC()
	rtc.set_system_time_from_rtc()
	batsense = BatSense(display, rtc)
	batsense.device_starting()
