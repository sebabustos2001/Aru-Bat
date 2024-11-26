import time
import json

from datetime import datetime
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

class Display:
	def __init__(self):
	# Initializing OLED Display (I2C default address = 0x3C)
		self.serial = i2c(port=1, address=0x3C)
		self.device = ssd1306(self.serial)
		self.width = self.device.width
		self.height = self.device.height

		with open("config.json", "r") as json_file:
			self.configs = json.load(json_file)
		self.start_time = self.configs["start_time"]
		self.end_time = self.configs["end_time"]
		self.constant_rec = self.configs["constant_record"]
		self.state_rec = self.configs["state_record"]

	def motd(self, message, duration=2):
		font = ImageFont.truetype("DejaVuSans.ttf", 15)
		with canvas(self.device) as draw:
			# Write text on the center of display
			text_size = draw.textsize(message, font = font)
			x_pos = (self.width - text_size[0]) // 2
			y_pos = (self.height - text_size[1]) // 2
			draw.text((x_pos, y_pos), message, font = font, fill="white")
		time.sleep(duration)
		self.device.clear()

	def time(self, duration=5):
		font = ImageFont.truetype("DejaVuSans.ttf", 12)
		current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		with canvas(self.device) as draw:
			text_size = draw.textsize(current_time, font=font)
			x_pos = (self.width - text_size[0]) // 2
			y_pos = (self.height - text_size[1]) // 2
			draw.text((x_pos, y_pos), current_time, font=font, fill="white")
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