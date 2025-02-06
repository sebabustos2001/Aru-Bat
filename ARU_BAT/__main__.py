import time
import json
import os

from datetime import datetime, timedelta
from multiprocessing import Process

from lib.SHT3x import SHT3x
from lib.RTC import RTC
from lib.Microphone import Microphone
from lib.Display import Display
from lib.GPS import GPS

class BatSens:
	def __init__(self):
		self.temperature_process = None
		self.mic_process = None
		self.gps_process = None
		self.audio_process = None
		self.configs = {}
		self.display = Display()	# Instance for Display class
		self.rtc = RTC()	        # Instance for RTC class

	def load_json_configs(self):
		with open("config.json", "r") as json_file:
			self.configs = json.load(json_file)	# upload variables from JSON file

	def starting(self):
		self.rtc.set_time()
		# Message of the Day
		self.display.motd("BatSens")
		self.display.time()
		self.batsens_set()

	def batsens_set(self):
		self.rtc.rtc_time()
		current_time = datetime.now().time()
		self.load_json_configs()

		if self.configs["program"] is False:
			batsens.config_device()
			self.display.actual_config()
			self.load_json_configs()

		if self.configs["program"]is True:
			self.display.actual_config()
			self.start_time = datetime.strptime(self.configs["start_time"], "%H:%M").time()
			self.end_time = datetime.strptime(self.configs["end_time"], "%H:%M").time()

			if self.start_time <= self.end_time:
				if self.start_time <= current_time < self.end_time:
					batsens.wake_alarm(self.start_time)
					batsens.sleep_alarm(self.end_time)
					batsens.processes()
				else:
					batsens.wake_alarm(self.start_time)
					os.system(f'sudo halt')

			else:
				if current_time >= self.start_time or current_time < self.end_time:
					batsens.wake_alarm(self.start_time)
					batsens.sleep_alarm(self.end_time)
					batsens.processes()
				else:
					batsens.wake_alarm(self.start_time)
					os.system(f'sudo halt')

	def sensors(self):
		# Instance for SHT3x sensors
		SHT3xSensor_1 = SHT3x(address=0x44)
		SHT3xSensor_1.precision(mode='low')

		#SHT3xSensor_2 = SHT3x(address=0x45)
		#SHT3xSensor_2.sht3x_precision(mode='low')

		current_time = datetime.now()
		new_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
		wait_time = (new_minute - current_time).total_seconds()
		time.sleep(wait_time)

		while True:
			SHT3xSensor_1.data()
			SHT3xSensor_1.print()
			time.sleep(60)


	def recording(self):
		# Instance for Microphone
		mic = Microphone()

		if self.configs["constant_record"] is True:
			while True:
				mic.start_recording()
		mic.close()

	def config_device(self):
		self.display.setup_config()
		self.display.actual_config()

	def wake_alarm(self, start_time):
		start_time_str = start_time.strftime("%H:%M")
		self.rtc.wake_alarm(start_time_str)

	def sleep_alarm(self, end_time):
		end_time_str = end_time.strftime("%H:%M")
		self.rtc.halt_alarm(end_time_str)

	def gps(self):
		gps = GPS()
		while True:
			gps.get_location()
			print("GPS lecture done. Waiting 30 minutes")
			time.sleep(1800)

	def processes(self):
		self.temp_process = Process(target = self.sensors)
		self.mic_process = Process(target = self.recording)
		self.gps_process = Process(target=self.gps)

		self.temp_process.start()
		self.mic_process.start()
		self.gps_process.start()

if __name__ == "__main__":
	batsens = BatSens()
	batsens.starting()
