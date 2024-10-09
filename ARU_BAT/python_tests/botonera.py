import RPi.GPIO as GPIO
import time

# Configuracion de los pines de los botones
BUTTON_LEFT = 5
BUTTON_RIGHT = 6
BUTTON_START = 13

# Tiempo de debounce en segundos
DEBOUNCE_TIME = 0.01

# Configuracion de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_START, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_callback(channel):
    if channel == BUTTON_LEFT:
        print("1 - IZQ")
    elif channel == BUTTON_RIGHT:
        print("1 - DER")
    elif channel == BUTTON_START:
        print("1 - START")
    time.sleep(DEBOUNCE_TIME)

# Configuracion de interrupciones
GPIO.add_event_detect(BUTTON_LEFT, GPIO.FALLING, callback=button_callback, bouncetime=int(DEBOUNCE_TIME * 1000))
GPIO.add_event_detect(BUTTON_RIGHT, GPIO.FALLING, callback=button_callback, bouncetime=int(DEBOUNCE_TIME * 1000))
GPIO.add_event_detect(BUTTON_START, GPIO.FALLING, callback=button_callback, bouncetime=int(DEBOUNCE_TIME * 1000))

try:
    print("Presiona Ctrl+C para salir")
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Saliendo del programa...")
finally:
    GPIO.cleanup()
