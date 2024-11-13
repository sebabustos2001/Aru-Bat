import time
import os

from multiprocessing import Process
from datetime import datetime, timedelta

class RTC:
	def __init__(self):
		self.rtc_path = '/dev/rtc'

	def get_rtc_time(self):
		# Obtains RTC time from Raspberry Pi 5
		try:
			# Read RTC time using hwclock
			rtc_time = os.popen("sudo hwclock -r").read().strip()
			return datetime.strptime(rtc_time, "%Y-%m-%d %H:%M:%S.%f %z")

		except Exception as e:
			print("RTC ERROR - Can't obtain time:", e)
			return None

	def set_system_time_from_rtc(self):
		# Refresh OS time using the RTC time
		try:
			os.system("sudo hwclock -s")
		except Exception as e:
			print("RTC ERROR - Can't set OS time using RTC:", e)

	def set_wake_alarm(self, wake_time_str):
		# Sets the wake-up alarm for the Raspberry Pi
		current_time = datetime.now()
		wake_time = datetime.strptime(wake_time_str, "%H:%M").replace(
			year=current_time.year, month=current_time.month, day=current_time.day
		)
		if wake_time <= current_time:
			wake_time += timedelta(days=1)
		seconds_until_wake = int((wake_time - current_time).total_seconds())
		os.system('sudo echo 0 | sudo tee /sys/class/rtc/rtc0/wakealarm')

		os.system(f'sudo echo +{seconds_until_wake} | sudo tee /sys/class/rtc/rtc0/wakealarm')
		print(f"Wake alarm set for {wake_time}.")

	def set_shutdown_alarm(self, shutdown_time_str):
		# Sets the shutdown alarm for the Raspberry Pi
		current_time = datetime.now()
		shutdown_time = datetime.strptime(shutdown_time_str, "%H:%M").replace(
			year=current_time.year, month=current_time.month, day=current_time.day
		)
		if shutdown_time <= current_time:
			shutdown_time += timedelta(days=1)
		seconds_until_shutdown = int((shutdown_time - current_time).total_seconds())
		print(f"Shutdown alarm set for {shutdown_time}.")
		def halt_after_delay():
			time.sleep(seconds_until_shutdown)
			os.system('sudo halt')
		shutdown_process = Process(target=halt_after_delay)
		shutdown_process.start()
		#os.system(f'sudo shutdown -h +{seconds_until_shutdown // 60}')
