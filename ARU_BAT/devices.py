import smbus2
import time

class SensorSHT3x:
	# RasPi5 only have 1 I2C bus to free use (bus = 1)
	def __init__(self, Bus=1, address=0x44):  # I2C SHT3x address
		self.bus = smbus2.SMBus(Bus)
		self.address = address
		self.mode_sht3x = 0x10  # Default Mode: Low Precision
		
	def read_temp_humid(self):
		self.bus.write_i2c_block_data(self.address, 0x2C, [self.mode_sht3x])	# Measure command
		data = self.bus.read_i2c_block_data(self.address, 0x00, 6)	# 6 data bytes read for sensor
		temperature_raw = data[0] << 8 | data[1]
		humidity_raw = data[3] << 8 | data[4]
		
		# Transform of data byte to physics units
		temperature = -45 + (175 * temperature_raw / 65535.0)	
		humidity = 100 * (humidity_raw / 65535.0)
		
		return temperature, humidity
	
	def set_precision(self, mode='low'):
		if mode == 'low':
			self.mode_sht3x = 0x10
		elif mode == 'medium':
			self.mode_sht3x = 0x0D
		elif mode == 'high':
			self.mode_sht3x = 0x06

