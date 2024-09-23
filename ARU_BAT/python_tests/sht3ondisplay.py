import smbus2
import time

# Direcciones I2C del sensor SHT3x y del display OLED SSD1306
SHT3X_I2C_ADDRESS = 0x44
OLED_I2C_ADDRESS = 0x3C

# Inicializar el bus I2C
bus = smbus2.SMBus(1)

# Fuente de 5x8 para caracteres ASCII
font = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
    '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
    '2': [0x42, 0x61, 0x51, 0x49, 0x46],
    '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
    '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
    '5': [0x27, 0x45, 0x45, 0x45, 0x39],
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03],
    '8': [0x36, 0x49, 0x49, 0x49, 0x36],
    '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    '.': [0x00, 0x40, 0x60, 0x00, 0x00],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01]
}

def oled_command(cmd):
    bus.write_byte_data(OLED_I2C_ADDRESS, 0x00, cmd)

def initialize_oled():
    oled_command(0xAE)  # Apagar el display
    oled_command(0xA8)  # Configuracion de multiplexacion
    oled_command(0x3F)  # Ratio de multiplexacion (1/64)
    oled_command(0xD3)  # Desplazamiento de pantalla
    oled_command(0x00)  # Sin desplazamiento
    oled_command(0x40)  # Direccion de inicio de linea a 0
    oled_command(0xA1)  # Modo de direccionamiento
    oled_command(0xC8)  # Modo de escaneo
    oled_command(0xDA)  # Configuracion de hardware
    oled_command(0x12)  # Configuracion de COM
    oled_command(0x81)  # Contraste
    oled_command(0x7F)  # Contraste medio
    oled_command(0xA4)  # Mostrar en RAM
    oled_command(0xA6)  # Modo normal de display
    oled_command(0xD5)  # Configuracion del oscilador
    oled_command(0x80)  # Dividir reloj
    oled_command(0x8D)  # Cargar
    oled_command(0x14)  # Habilitar la carga
    oled_command(0xAF)  # Encender el display

def clear_display():
    for i in range(8):
        oled_command(0xB0 + i)  # Establecer direccion de pagina
        oled_command(0x00)      # Direccion de columna baja
        oled_command(0x10)      # Direccion de columna alta
        for j in range(128):
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, 0x00)

def scale_font(char_data):
    """Escala una fuente de 5x8 a 10x16 pixeles."""
    scaled_data = []
    for byte in char_data:
        # Escalar cada byte de 5x8 a 10x16 duplicando bits horizontalmente
        new_byte = ((byte & 0x01) * 3) | ((byte & 0x02) * 6) | ((byte & 0x04) * 12) | ((byte & 0x08) * 24) | ((byte & 0x10) * 48)
        scaled_data.append(new_byte)
        scaled_data.append(new_byte)  # Duplicar la fila para escalar verticalmente
    return scaled_data

def write_char_large(c):
    if c in font:
        # Escalar la fuente de 5x8 a 10x16
        char_data = scale_font(font[c])
        for byte in char_data:
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, byte)
        # Anadir espacio entre caracteres grandes
        for _ in range(2):
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, 0x00)

def write_text_large(text):
    # Configurar para empezar desde la parte superior del display
    oled_command(0xB0)  # Pagina 0 (linea superior)
    oled_command(0x00)  # Columna baja
    oled_command(0x10)  # Columna alta
    for char in text:
        write_char_large(char)

    # Cambiar a la segunda pagina para continuar escribiendo caracteres grandes
    oled_command(0xB1)  # Pagina 1 (segunda parte de caracteres grandes)
    oled_command(0x00)  # Columna baja
    oled_command(0x10)  # Columna alta
    for char in text:
        write_char_large(char)

def read_sht3x():
    # Enviar el comando de medicion
    bus.write_i2c_block_data(SHT3X_I2C_ADDRESS, 0x2C, [0x06])

    # Esperar 0.5 segundos para que el sensor realice la medicion
    time.sleep(0.5)

    # Leer 6 bytes de datos del sensor
    data = bus.read_i2c_block_data(SHT3X_I2C_ADDRESS, 0x00, 6)

    # Extraer los valores de temperatura de los bytes leidos
    temperature_raw = data[0] << 8 | data[1]

    # Convertir los valores brutos a unidades fisicas
    temperature = -45 + (175 * temperature_raw / 65535.0)

    return temperature

def main():
    initialize_oled()
    clear_display()

    while True:
        # Leer la temperatura del sensor SHT3x
        temperature = read_sht3x()

        # Formatear la temperatura para mostrarla
        temp_str = f"T: {temperature:.2f}C"
        print(temp_str)

        # Limpiar la pantalla y mostrar la temperatura en caracteres grandes
        clear_display()
        write_text_large(temp_str)

        # Esperar 1 segundo antes de actualizar de nuevo
        time.sleep(1)

if __name__ == "__main__":
    main()
