import time
from devices import SensorSHT3x

def main():
	# Instancia de sensor SHT3x
	TEMPSensor_1 = SensorSHT3x(address=0x44)
	
	# Set precision of TEMPSensor read
	# -> low 
	# -> medium
	# -> high
	TEMPSensor_1.set_precision(mode='low')
	
	try:
		while True:
			temperature, humidity = TEMPSensor_1.read_temp_humid()
			print(f"Temperatura: {temperature:.2f} Grados C, Humedad: {humidity:.2f} %")
			time.sleep(1)
	except KeyboardInterrupt:
		print("Programa detenido por el usuario.")

if __name__ == "__main__":
	main()
