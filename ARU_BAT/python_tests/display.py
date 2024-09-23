import smbus2
import time

# Direccion I2C del display OLED SSD1306
OLED_I2C_ADDRESS = 0x3C

# Inicializar el bus I2C
bus = smbus2.SMBus(1)  # '1' se refiere al bus I2C en la Raspberry Pi

def oled_command(cmd):
    """Enviar comando al display OLED."""
    bus.write_byte_data(OLED_I2C_ADDRESS, 0x00, cmd)

def initialize_oled():
    """Inicializar el display OLED con una secuencia basica de comandos."""
    oled_command(0xAE)  # Apagar el display
    oled_command(0xA8)  # Multiplex ratio
    oled_command(0x3F)  # Duty = 1/64
    oled_command(0xD3)  # Desplazamiento de pantalla
    oled_command(0x00)  # Sin desplazamiento
    oled_command(0x40)  # Start line address = 0
    oled_command(0xA1)  # Modo de direccionamiento normal
    oled_command(0xC8)  # Modo de escaneo normal
    oled_command(0xDA)  # Configuracion de hardware
    oled_command(0x12)  # Com configuration
    oled_command(0x81)  # Configuracion del contraste
    oled_command(0x7F)  # Contraste medio
    oled_command(0xA4)  # Salvar RAM
    oled_command(0xA6)  # Modo normal de display
    oled_command(0xD5)  # Configuracion del oscilador
    oled_command(0x80)  # Dividir reloj
    oled_command(0x8D)  # Configuracion de la carga del display
    oled_command(0x14)  # Habilitar la carga
    oled_command(0xAF)  # Encender el display

def clear_display():
    """Limpiar el contenido del display OLED."""
    for i in range(8):
        oled_command(0xB0 + i)  # Seleccionar pagina
        oled_command(0x00)      # Direccion de columna baja
        oled_command(0x10)      # Direccion de columna alta
        for j in range(128):
            bus.write_byte_data(OLED_I2C_ADDRESS, 0x40, 0x00)  # Llenar con ceros (blanco)

def main():
    initialize_oled()
    clear_display()
    # Puedes agregar mas comandos aqui para escribir texto o graficos en el display
    print("OLED inicializado y limpiado.")

if __name__ == "__main__":
    main()
