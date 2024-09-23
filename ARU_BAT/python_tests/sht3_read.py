import smbus2
import time

# Direccion I2C del sensor SHT3x
SHT3X_I2C_ADDRESS = 0x44

# Comando para iniciar la medicion de alta repetibilidad sin estiramiento de reloj
SHT3X_MEASURE_CMD = [0x2C, 0x06]

# Inicializar el bus I2C
bus = smbus2.SMBus(1)  # '1' se refiere al bus I2C en la Raspberry Pi

def read_sht3x():
    # Enviar el comando de medicion
    bus.write_i2c_block_data(SHT3X_I2C_ADDRESS, SHT3X_MEASURE_CMD[0], SHT3X_MEASURE_CMD[1:])

    # Esperar 0.5 segundos para que el sensor realice la medicion
    time.sleep(0.5)

    # Leer 6 bytes de datos del sensor
    data = bus.read_i2c_block_data(SHT3X_I2C_ADDRESS, 0x00, 6)

    # Extraer los valores de temperatura y humedad de los bytes leidos
    temperature_raw = data[0] << 8 | data[1]
    humidity_raw = data[3] << 8 | data[4]

    # Convertir los valores brutos a unidades fisicas
    temperature = -45 + (175 * temperature_raw / 65535.0)
    humidity = 100 * (humidity_raw / 65535.0)

    return temperature, humidity

try:
    temp, hum = read_sht3x()
    print(f"Temperatura: {temp:.2f} grados C")
    print(f"Humedad: {hum:.2f} %")
except Exception as e:
    print(f"Error al leer del sensor: {e}")
