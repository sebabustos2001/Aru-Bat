from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

# Inicializar la interfaz I2C
serial = i2c(port=1, address=0x3C)  # Asegurate de que la direccion coincida con la de tu display OLED

# Crear el dispositivo OLED
device = ssd1306(serial)

# Definir una fuente de texto (opcional, usa una fuente integrada si no se especifica)
# Puedes cambiar 'font_path' a la ruta de cualquier fuente TTF en tu sistema
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 14)  # Tamano de fuente ajustable

# Mostrar el texto "Hola Seba" en el display
with canvas(device) as draw:
    draw.text((0,30), "Calla MOCOSO", font=font, fill="white")

print("Texto 'Hola Seba' mostrado en el display OLED.")
input("Enter para salir")
