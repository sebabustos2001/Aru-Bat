import smbus2
import time
import os
import pyaudio
import wave
import json
import curses
import RPi.GPIO as GPIO

from datetime import datetime
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# Configuracion de pines para los botones
BUTTON_LEFT = 5   # Aumenta el numero
BUTTON_MIDDLE = 6 # Retrocede una accion
BUTTON_RIGHT = 13 # Confirma la accion

# Configuracion de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_MIDDLE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
				sampling_frec=48000, 
				chunk=1024, 
				record_seconds=5, 
				output_file="output.wav"):
		
		# Micrphone settings
		self.channels = channels
		self.sampling_frec = sampling_frec
		self.chunk = chunk
		self.record_seconds = record_seconds

		self.record_dir = "Mic_Records"
		if not os.path.exists(self.record_dir):
			os.makedirs(self.record_dir)
		
		#self.output_file = os.path.join(self.record_dir, 
		#								output_file)

		# Initialize PyAudio
		self.audio = pyaudio.PyAudio()

	def start_recording(self):
		current_time = datetime.now()
		timestamp = current_time.strftime("%Y-%m-%d-%H:%M:%S")
		output_file = os.path.join(self.record_dir, f"{timestamp}")
		
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
		# Variable which save the actual RTC time
		self.current_time = self.get_rtc_time()
	
	def get_rtc_time(self):
		# Obtains actual RTC time
		rtc_time = datetime.now()
		return rtc_time
	
	def set_wake_alarm(self, wake_time=None):
		"""
		Configura la alarma para despertar.
		- Si 'wake_time' es un numero, se utiliza como el numero de segundos para la alarma.
		- Si 'wake_time' es un string en formato 'HH:MM', la Raspberry Pi despertara a esa hora.
		"""
		if wake_time is None:
			print("Debe proporcionar un tiempo para la alarma.")
			return
			
		# Si es un string (formato DD:HH:MM)
		if isinstance(wake_time, str):
			try:
				current_time = datetime.now()
				target_time = datetime.strptime(wake_time, "%H:%M").replace(
					year=current_time.year, month=current_time.month, day=current_time.day
				)
				
				# Si la hora objetivo ya paso hoy, ajusta para el dia siguiente
				if target_time < current_time:
					target_time += timedelta(days=1)
				
				seconds_until_wake = int((target_time - current_time).total_seconds())
				os.system(f'sudo sh -c "echo +{seconds_until_wake} > /sys/class/rtc/rtc0/wakealarm"')
				print(f"Alarma configurada para despertar a las {wake_time}.")
				
			except ValueError:
				print("Error: El formato de la hora debe ser 'HH:MM'.")
		else:
			print("Error: El argumento debe ser un numero (segundos) o un string en formato 'HH:MM'.")
	
	def refresh_time(self):
		# Actualiza la hora actual del RTC
		self.current_time = self.get_rtc_time()

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
		with canvas(self.device) as draw:
			
			# Dibujar texto en el centro de la pantalla
			text_size = draw.textsize(message)
			x_pos = (self.width - text_size[0]) // 2
			y_pos = (self.height - text_size[1]) // 2
			draw.text((x_pos, y_pos), message, fill="white")

		time.sleep(duration)
		self.device.clear()
	
	def check_settings(self):
		if self.start_time is None:
			with canvas(self.device) as draw:
				text_size = draw.textsize("START TIME IS NO SET")
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "START TIME IS NO SET", fill="white")	
			time.sleep(3)
			self.device.clear()
			
			editable_time = "0000-00-00 00:00"
			self.display_controller.choose_time(editable_time, edit_start_time = True)
			
		self.edit_start_time = False
				
		if self.end_time is None:
			with canvas(self.device) as draw:
				text_size = draw.textsize("END TIME NOT SET")
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "END TIME NOT SET", fill="white")
				
			time.sleep(3)
			self.device.clear()
			
			editable_time = "0000-00-00 00:00"
			self.display_controller.choose_time(editable_time, edit_end_time = True)
			
		self.edit_end_time = False
		
		if self.constant_rec is False and self.state_rec is False:
			with canvas(self.device) as draw:
				text_size = draw.textsize("RECORD MODE NOT SET")
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "RECORD MODE NOT SET", fill="white")
				
			time.sleep(3)
			self.device.clear()
			self.display_controller.choose_record_mode()
			
		elif self.constant_rec is True and self.state_rec is True:
			with canvas(self.device) as draw:
				text_size = draw.textsize("RECORD MODE NOT SET")
				x_pos = (self.width - text_size[0]) // 2
				y_pos = (self.height - text_size[1]) // 2
				draw.text((x_pos, y_pos), "RECORD MODE NOT SET", fill="white")
				
			time.sleep(3)
			self.device.clear()
			self.configs["constant_record"] = False
			self.configs["state_record"] = False
			with open("config.json", "w") as json_file:
				json.dump(self.configs, json_file, indent=4)
			self.display_controller.choose_record_mode()

	def actual_config(self, duration = 5):
		font = ImageFont.truetype("DejaVuSans.ttf", 8)
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
			
		else:
			with canvas(self.device) as draw:
				conf_message = f"START TIME:{self.start_time}\nEND TIME:{self.end_time}\nRECORD MODE: {None}"
				text_size = draw.textsize(conf_message, font = font)
				draw.text((10, 20), conf_message, font = font, fill="white")	
			time.sleep(duration)
			self.device.clear()

class DisplayController:
	
	def __init__(self, Display):
		self.display = Display

	def choose_time(self, editable_time, edit_start_time=False, edit_end_time=False):
		cursor_pos = 0
		if edit_start_time:
			message = "SET START TIME"
		elif edit_end_time:
			message = "SET END TIME"
		
		def refresh_display(editable_time):
			with canvas(self.display.device) as draw:
				current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
				draw.text((10, 10), message, fill="white")
				draw.text((10, 30), current_time, fill="white")
				draw.text((10, 50), editable_time, fill="white")

		while True:
			refresh_display(editable_time)
            
			# Espera hasta que se presione un boton
			if GPIO.input(BUTTON_LEFT) == GPIO.LOW:
				editable_time = self.increment_digit(editable_time, cursor_pos)
				time.sleep(0.2)  # Debounce
			elif GPIO.input(BUTTON_MIDDLE) == GPIO.LOW:
				cursor_pos = max(cursor_pos - 1, 0)
				time.sleep(0.2)
			elif GPIO.input(BUTTON_RIGHT) == GPIO.LOW:
				cursor_pos += 1
				if cursor_pos >= len(editable_time):
					# Confirmacion final
					refresh_display(editable_time)
					confirmed = self.confirm_time(editable_time)
					if confirmed:
						if edit_start_time:
							self.display.start_time = editable_time
							self.update_config("start_time", editable_time)
						if edit_end_time:
							self.display.end_time = editable_time
							self.update_config("end_time", editable_time)
						break
					else:
						cursor_pos = 0
				time.sleep(0.2)

	def increment_digit(self, editable_time, pos):
		if editable_time[pos].isdigit():
			new_digit = (int(editable_time[pos]) + 1) % 10
			editable_time = editable_time[:pos] + str(new_digit) + editable_time[pos + 1:]
		return editable_time

	def confirm_time(self, editable_time):
		options = ["SI", "NO"]
		selected_option = 0

		while True:
			with canvas(self.display.device) as draw:
				# Muestra el mensaje de confirmacion y la fecha
				draw.text((10, 10), "Confirmar?", fill="white")
				draw.text((10, 30), editable_time, fill="white")
            
				# Resalta la opcion seleccionada invirtiendo colores
				for i, option in enumerate(options):
					x_pos = 10 + i * 50
					y_pos = 50
					if i == selected_option:
						draw.rectangle((x_pos, y_pos, x_pos + 40, y_pos + 20), outline="white", fill="white")
						draw.text((x_pos + 10, y_pos), option, fill="black")
					else:
						draw.text((x_pos + 10, y_pos), option, fill="white")

			# Verifica que boton se presiona
			if GPIO.input(BUTTON_LEFT) == GPIO.LOW:
				selected_option = (selected_option + 1) % 2  # Cambia entre 0 y 1
				time.sleep(0.2)  # Debounce
			elif GPIO.input(BUTTON_RIGHT) == GPIO.LOW:
				return options[selected_option] == "SI"

	def update_config(self, key, value):
		with open("config.json", "r") as json_file:
			configs = json.load(json_file)
		configs[key] = value
		with open("config.json", "w") as json_file:
			json.dump(configs, json_file, indent=4)
		

	# Funcion para elegir el modo de grabacion
	def choose_record_mode(self):
		options = ["CONSTANT", "STATE"]
		selected_option = 0

		while True:
			with canvas(self.display.device) as draw:
				# Muestra el mensaje para elegir el modo de grabacion
				draw.text((10, 10), "CHOOSE RECORD MODE:", fill="white")
            
				# Resalta la opcion seleccionada invirtiendo colores
				for i, option in enumerate(options):
					x_pos = 10
					y_pos = 30 + i * 20
					if i == selected_option:
						draw.rectangle((x_pos, y_pos, x_pos + 80, y_pos + 15), outline="white", fill="white")
						draw.text((x_pos + 10, y_pos), option, fill="black")
					else:
						draw.text((x_pos + 10, y_pos), option, fill="white")

			# Verifica que boton se presiona
			if GPIO.input(BUTTON_LEFT) == GPIO.LOW:
				selected_option = (selected_option + 1) % len(options)  # Alterna entre 0 y 1
				time.sleep(0.2)  # Debounce
			elif GPIO.input(BUTTON_RIGHT) == GPIO.LOW:
				# Actualiza la configuracion segun la seleccion y guarda en config.json
				if selected_option == 0:  # CONSTANT
					self.display.constant_rec = True
					self.display.state_rec = False
				else:  # STATE
					self.display.constant_rec = False
					self.display.state_rec = True

				with open("config.json", "r") as json_file:
					configs = json.load(json_file)
				configs["constant_record"] = self.display.constant_rec
				configs["state_record"] = self.display.state_rec
				with open("config.json", "w") as json_file:
					json.dump(configs, json_file, indent=4)
            
				break
