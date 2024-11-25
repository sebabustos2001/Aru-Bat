import time
import json
import os

from datetime import datetime
from multiprocessing import Process

from lib.SHT3x import SHT3x
from lib.RTC import RTC
from lib.Microphone import Microphone
from lib.Display import Display
from lib.AudioProcessor import AudioProcessor


class BatSense:
	def __init__(self, display, rtc):
		self.display = display
		self.rtc = rtc
		self.temperature_process = None
		self.mic_process = None
		self.audio_process = None
		self.configs = {}

	def load_json_configs(self):
		with open("config.json", "r") as json_file:
			self.configs = json.load(json_file)	#upload variables from JSON file

	def device_starting(self):
		# Message of the Day
		self.display.MOTD("BatSense", duration = 3)
		self.display.device_time()
		self.load_json_configs()
		current_time = datetime.now().time()

		if self.configs["program"] is False:
			batsense.config_device()
			self.display.actual_config()
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

	def Sensors(self):
		# Instance for SHT3x sensor
		SHT3xSensor_1 = SHT3x(address=0x44)
		SHT3xSensor_1.set_precision(mode='low')

		#SHT3xSensor_2 = SHT3x(address=0x45)
		#SHT3xSensor_2.set_precision(mode='low')

		while True:
			temp_in, humidity_in = SHT3xSensor_1.read_sht3x()
			#temp_out, humidity_out = SHT3xSensor_2.read_sht3x()

			SHT3xSensor_1.write_sht3x(temp_in, humidity_in)
			#SHT3xSensor_2.write_sht3x(temp_out, humidity_out)

			SHT3xSensor_1.print_sht3x(temp_in, humidity_in)
			#SHT3xSensor_2.print_sht3x(temp_out, humidity_out)
			time.sleep(30)


	def recording(self):
		mic = Microphone()
		if self.configs["constant_record"] is True:
			while True:
				mic.start_recording()
				time.sleep(0.1)

		elif self.configs["state_record"] is True:
			return 0	# On develop
		mic.close()

	def audio_processing(self):
		audio_process = AudioProcessor()
		while True:
			audio_process.process_audio_files()
			time.sleep(2)

	def processes(self):
		self.temp_process = Process(target = self.Sensors)
		self.mic_process = Process(target = self.recording)
		#self.audio_process = Process(target = self.audio_processing)

		self.temp_process.start()
		self.mic_process.start()
		#self.audio_process.start()

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
