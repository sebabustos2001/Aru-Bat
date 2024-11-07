import smbus2
import time
import os
import pyaudio
import wave
import json
import curses
import numpy as np

from datetime import datetime, timedelta
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
from scipy.fft import rfft, rfftfreq

class SensorSHT3x:
	# RasPi5 only have 1 I2C bus to free use (bus = 1)
	def __init__(self, Bus=1, address=0x44):  	# I2C SHT3x 0x44 default address
		self.bus = smbus2.SMBus(Bus)			# (0x45 second address)
		self.address = address
		self.mode_sht3x = 0x10  	# Default Mode: Low Precision

		self.log_file = f"TemperatureLog_{hex(self.address)}.txt".replace("0x", "")

		# Si el archivo no existe, crear y escribir los encabezados
		if not os.path.exists(self.log_file):
			with open(self.log_file, 'w') as f:
				f.write("Year-Month-Day\t"
						"Time\t"
						"Temperature[C°]\t"
						"Humidity[%]\n")

	def read_temp_humid(self):
		self.bus.write_i2c_block_data(self.address, 0x2C, [self.mode_sht3x])	# Measure command
		data = self.bus.read_i2c_block_data(self.address, 0x00, 6)	# 6 data bytes read for sensor
		temperature_raw = data[0] << 8 | data[1]
		humidity_raw = data[3] << 8 | data[4]

		# Transform of data byte to physics units
		temperature = -45 + (175 * temperature_raw / 65535.0)
		humidity = 100 * (humidity_raw / 65535.0)

		return temperature, humidity

	def write_data(self, temperature, humidity):
		"""Write sensor data and Datetime on the log.txt file"""
		current_time = datetime.now()
		with open(self.log_file, 'a') as f:
			f.write(f"{current_time.year}-"
					f"{current_time.month}-"
					f"{current_time.day}\t"
					f"{current_time.strftime('%H:%M:%S')}\t"
					f"{temperature:.2f}\t{humidity:.2f}\n")

	def set_precision(self, mode='low'):
		if mode == 'low':
			self.mode_sht3x = 0x10
		elif mode == 'medium':
			self.mode_sht3x = 0x0D
		elif mode == 'high':
			self.mode_sht3x = 0x06

class Microphone_Record():
	def __init__(self,
				channels=1,
				sampling_frec=250000,
				chunk=16384,
				record_seconds=60,
				output_file="output.wav"):

		# Micrphone settings
		self.channels = channels
		self.sampling_frec = sampling_frec
		self.chunk = chunk
		self.record_seconds = record_seconds

		self.record_dir = "Mic_Records"
		if not os.path.exists(self.record_dir):
			os.makedirs(self.record_dir)
		self.audio = pyaudio.PyAudio()

	def start_recording(self):
		current_time = datetime.now()
		timestamp = current_time.strftime("%Y-%m-%d-%H:%M:%S")
		output_file = os.path.join(self.record_dir, f"{timestamp}.wav")

		# Start record
		print("Initializing record...")
		stream = self.audio.open(format = pyaudio.paInt16, 
								channels = self.channels,
								rate = self.sampling_frec, 
								input = True, 
								frames_per_buffer = self.chunk)

		print("Recording...")
		frames = []

		for i in range(0, int(self.sampling_frec / self.chunk * self.record_seconds)):
			data = stream.read(self.chunk)
			frames.append(data)

		print("Record ending...")

		# Stop recording
		stream.stop_stream()
		stream.close()

		# Save WAV file
		wf = wave.open(output_file, 'wb')
		wf.setnchannels(self.channels)
		wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
		wf.setframerate(self.sampling_frec)
		wf.writeframes(b''.join(frames))
		wf.close()

		print(f"File save as {output_file}")

	def close(self):
		# Closing PyAudio
		self.audio.terminate()

class RTC:
	def __init__(self):
		self.rtc_path = '/dev/rtc'

	def get_rtc_time(self):
		"""Obtains RTC time from Raspberry Pi 5."""
		try:
			# Leer la hora directamente del RTC usando hwclock
			rtc_time = os.popen("sudo hwclock -r").read().strip()
			return datetime.strptime(rtc_time, "%Y-%m-%d %H:%M:%S.%f %z")

		except Exception as e:
			print("Error al obtener la hora del RTC:", e)
			return None

	def set_system_time_from_rtc(self):
		"""Refresh OS time using the RTC time."""
		try:
			os.system("sudo hwclock -s")
		except Exception as e:
			print("Error al actualizar la hora del sistema desde el RTC:", e)

	def set_wake_alarm(self, wake_time_str):
		"""Sets the wake-up alarm for the Raspberry Pi."""
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
		"""Sets the shutdown alarm for the Raspberry Pi."""
		current_time = datetime.now()
		shutdown_time = datetime.strptime(shutdown_time_str, "%H:%M").replace(
			year=current_time.year, month=current_time.month, day=current_time.day
		)
		if shutdown_time <= current_time:
			shutdown_time += timedelta(days=1)
		seconds_until_shutdown = int((shutdown_time - current_time).total_seconds())
		print(f"Shutdown alarm set for {shutdown_time}.")
		os.system(f'sudo shutdown -h +{seconds_until_shutdown // 60}')

class Display:
	def __init__(self):
	# Inicializar la pantalla OLED (I2C con direccion por defecto 0x3C)
		self.serial = i2c(port=1, address=0x3C)
		self.device = ssd1306(self.serial)
		self.width = self.device.width
		self.height = self.device.height
		self.display_controller = DisplayController(self)

		with open("config.json", "r") as json_file:
			self.configs = json.load(json_file)
		self.start_time = self.configs["start_time"]
		self.end_time = self.configs["end_time"]
		self.constant_rec = self.configs["constant_record"]
		self.state_rec = self.configs["state_record"]

	def MOTD(self, message, duration=1):
		font = ImageFont.truetype("DejaVuSans.ttf", 15)
		with canvas(self.device) as draw:

			# Dibujar texto en el centro de la pantalla
			text_size = draw.textsize(message, font = font)
			x_pos = (self.width - text_size[0]) // 2
			y_pos = (self.height - text_size[1]) // 2
			draw.text((x_pos, y_pos), message, font = font, fill="white")

		time.sleep(duration)
		self.device.clear()

	def setup_config(self):
		if self.start_time is None:
			font = ImageFont.truetype("DejaVuSans.ttf", 15)
			with canvas(self.device) as draw:
				text_size = draw.textsize("START TIME\nNO SET", font = font)
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "START TIME\nNO SET", font = font, fill="white")
			time.sleep(3)
			self.device.clear()
			editable_time = "00:00"


		self.edit_start_time = False

		if self.end_time is None:
			font = ImageFont.truetype("DejaVuSans.ttf", 15)
			with canvas(self.device) as draw:
				text_size = draw.textsize("END TIME\nNOT SET", font = font)
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "END TIME\nNOT SET", font = font, fill="white")
			time.sleep(3)
			self.device.clear()
			editable_time = "00:00"

		self.edit_end_time = False

		if self.constant_rec is False and self.state_rec is False:
			font = ImageFont.truetype("DejaVuSans.ttf", 15)
			with canvas(self.device) as draw:
				text_size = draw.textsize("RECORD MODE\nNOT SET", font = font)
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "RECORD MODE\nNOT SET", font = font, fill="white")
			time.sleep(3)
			self.device.clear()

		elif self.constant_rec is True and self.state_rec is True:
			font = ImageFont.truetype("DejaVuSans.ttf", 15)
			with canvas(self.device) as draw:
				text_size = draw.textsize("RECORD MODE\nNOT SET", font = font)
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "RECORD MODE\nNOT SET", font = font, fill="white")

			time.sleep(3)
			self.device.clear()
			self.configs["constant_record"] = False
			self.configs["state_record"] = False
			with open("config.json", "w") as json_file:
				json.dump(self.configs, json_file, indent=4)

	def actual_config(self, duration = 5):
		font = ImageFont.truetype("DejaVuSans.ttf", 9)
		if self.constant_rec is True:
			with canvas(self.device) as draw:
				conf_message = f"START TIME:{self.start_time}\nEND TIME:{self.end_time}\nRECORD MODE: Constant"
				text_size = draw.textsize(conf_message, font = font)
				draw.text((10, 20), conf_message, font = font, fill="white")
			time.sleep(duration)
			self.device.clear()

		elif self.state_rec is True:
			with canvas(self.device) as draw:
				conf_message = f"START TIME:{self.start_time}\nEND TIME:{self.end_time}\nRECORD MODE: State"
				text_size = draw.textsize(conf_message, font = font)
				draw.text((10, 20), conf_message, font = font, fill="white")
			time.sleep(duration)
			self.device.clear()

class AudioProcessor:
	def __init__(self, directory="Mic_Records",
			threshold_frequency_min=18000,
			threshold_frequency_max=100000,
			threshold_amplitude=500,
			burst_duration=1,
			peak_duration=0.3):
		self.directory = directory
		self.threshold_frequency_min = threshold_frequency_min
		self.threshold_frequency_max = threshold_frequency_max
		self.threshold_amplitude = threshold_amplitude
		self.burst_duration = burst_duration
		self.peak_duration = peak_duration
		self.processed_files = set()

	def process_audio_files(self):
		for filename in os.listdir(self.directory):
			if filename.endswith(".wav") and filename not in self.processed_files:
				file_path = os.path.join(self.directory, filename)
				if not self.contains_high_frequency(file_path):
					os.remove(file_path)
					print(f"Archivo {filename} eliminado")
				else:
					print(f"Vocalizacion detectada en {filename}")
				self.processed_files.add(filename)

	def contains_high_frequency(self, filepath):
		with wave.open(filepath, 'rb') as wav:
			framerate = wav.getframerate()
			n_frames = wav.getnframes()
			audio_data = np.frombuffer(wav.readframes(n_frames), dtype=np.int16)
		duration = n_frames / framerate

		N = len(audio_data)
		yf = rfft(audio_data)
		xf = rfftfreq(N, 1/framerate)

		passband_freq = (xf > self.threshold_frequency_min) & (xf < self.threshold_frequency_max)
		xf_filtered = xf[passband_freq]
		yf_filtered = np.abs(yf[passband_freq])

		peak_count = 0
		for i in range(len(xf_filtered)):
			if self.threshold_frequency_min <= xf_filtered[i] <= self.threshold_frequency_max and yf_filtered[i] > self.threshold_amplitude:
				peak_count += 1

		if peak_count > 0 and (peak_count/duration) >= (1/self.burst_duration):
			for i in range(len(xf_filtered)):
				if self.threshold_frequency_min <= xf_filtered[i] <= self.threshold_frequency_max and yf_filtered[i] > self.threshold_amplitude:
					if (peak_count / duration) >= (1/self.peak_duration):
						return True
		return False

		#return any(xf[i] > self.threshold_frequency and abs(yf[i]) > self.threshold_amplitude for i in range(len(yf)))


class DisplayController:
	def __init__(self, Display):
		self.display = Display

	def update_config(self, key, value):
		with open("config.json", "r") as json_file:
			configs = json.load(json_file)
		configs[key] = value
		with open("config.json", "w") as json_file:
			json.dump(configs, json_file, indent=4)
