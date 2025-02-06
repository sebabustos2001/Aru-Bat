import smbus2
import os

from datetime import datetime, timedelta

class SHT3x:
	# RasPi5 only have one I2C bus to free use (bus = 1)

	def __init__(self, Bus=1, address=0x44):  # I2C SHT3x 0x44 default address
		self.bus = smbus2.SMBus(Bus)	# (0x45 second address)
		self.address = address
		self.mode_sht3x = 0x10  	# Default Mode: Low Precision

		self.log_file = f"BS03_TEMP_{hex(self.address)}.txt".replace("0x", "")

		# If .txt file doesn't exist, generate .txt and write headers
		if not os.path.exists(self.log_file):
			with open(self.log_file, 'w') as f:
				f.write("Year-Month-Day\t"
						"Time\t"
						"Temperature[C°]\t"
						"Humidity[%]\n")

	def read(self):
		self.bus.write_i2c_block_data(self.address, 0x2C, [self.mode_sht3x])	# Measure command
		data = self.bus.read_i2c_block_data(self.address, 0x00, 6)	# 6 data bytes read for sensor
		temperature_raw = data[0] << 8 | data[1]
		humidity_raw = data[3] << 8 | data[4]

		# Data Transform -> byte to physics units [°C] [%]
		temperature = -45 + (175 * temperature_raw / 65535.0)
		humidity = 100 * (humidity_raw / 65535.0)

		return temperature, humidity

	def write(self, temperature, humidity):
		# Write sensor data and Datetime on the log.txt file
		current_time = datetime.now()
		with open(self.log_file, 'a') as f:
			f.write(f"{current_time.year}-"
					f"{current_time.month}-"
					f"{current_time.day}\t"
					f"{current_time.strftime('%H:%M:%S')}\t"
					f"{temperature:.2f}\t{humidity:.2f}\n")

	def print(self):
		# Print sensor data
		temperature, humidity = self.read()
		current_time = datetime.now()
		print(f"Year-Month-Day\tTime\tTemperature\tHumidity[%]\tBS01_{hex(self.address)}\n"
			f"{current_time.year}-"
			f"{current_time.month}-"
			f"{current_time.day}\t"
			f"{current_time.strftime('%H:%M:%S')}\t"
			f"{temperature:.2f}\t{humidity:.2f}\n")

	def data(self):
		"""
		Call `read` to read data from sensor and then, 
		write the data on the .txt file and print it to terminal using `write`.
		"""
		try:
			temperature, humidity = self.read()
			self.write(temperature, humidity)
		except Exception as e:
			print(f"ERROR: READ/WRITE DATA SENSOR SHT3x {hex(self.address)}: {e}")

	def precision(self, mode='low'):
		if mode == 'low':
			self.mode_sht3x = 0x10
		elif mode == 'medium':
			self.mode_sht3x = 0x0D
		elif mode == 'high':
			self.mode_sht3x = 0x06
