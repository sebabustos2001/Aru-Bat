import smbus2
import time

# Direccion I2C del display OLED SSD1306
OLED_I2C_ADDRESS = 0x3C

# Inicializar el bus I2C
bus = smbus2.SMBus(1)

# Fuente de 5x8 para caracteres ASCII
font = {
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
    'o': [0x3E, 0x51, 0x49, 0x49, 0x3E],
    'l': [0x00, 0x41, 0x7F, 0x40, 0x00],
    'a': [0x38, 0x54, 0x54, 0x54, 0x18],
    'S': [0x46, 0x49, 0x49, 0x49, 0x31],
    'e': [0x38, 0x54, 0x54, 0x54, 0x08],
    'b': [0x7F, 0x48, 0x44, 0x44, 0x38],
}

def oled_command(cmd):
    bus.write_byte_data(OLED_I2C_ADDRESS, 0x00, cmd)

def initialize_oled():
    oled_command(0xAE)
    oled_command(0xA8)
    oled_command(0x3F)
    oled_command(0xD3)
    oled_command(0x00)
    oled_command(0x40)
    oled_command(0xA1)
    oled_command(0xC8)
    oled_command(0xDA)
    oled_command(0x12)
    oled_command(0x81)
    oled_command(0x7F)
    oled_command(0xA4)
    oled_command(0xA6)
    oled_command(0xD5)
    oled_command(0x80)
    oled_command(0x8D)
    oled_command(0x14)
    oled_command(0xAF)

def clear_display():
    for i in range(8):
        oled_command(0xB0 + i)
        oled_command(0x00)
        oled_command(0x10)
        for j in range(128):
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, 0x00)

def write_char(c):
    if c in font:
        for byte in font[c]:
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, byte)
        bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, 0x00)  # Espacio entre caracteres

def write_text(text):
    oled_command(0xB0)  # Establecer direccion de pagina a 0 (primera linea)
    oled_command(0x00)  # Establecer direccion de columna baja a 0
    oled_command(0x10)  # Establecer direccion de columna alta a 0

    for char in text:
        write_char(char)

def main():
    initialize_oled()
    clear_display()
    write_text("Hola Seba")  # Escribir "Hola Seba" en el display
    print("Texto 'Hola Seba' escrito en el display.")

if __name__ == "__main__":
    main()
