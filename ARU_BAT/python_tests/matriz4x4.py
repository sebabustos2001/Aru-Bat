import RPi.GPIO as GPIO
import time

# Pines GPIO para columnas y filas
COLUMNS = [5, 6, 13, 19]  # C4, C3, C2, C1
ROWS = [26, 16, 20, 21]   # R1, R2, R3, R4

# Mapa de botones (segun la matriz)
button_map = {
    (0, 3): "0",       # S15
    (1, 2): "1",       # S9
    (1, 1): "2",       # S10
    (1, 0): "3",       # S11
    (2, 3): "4",       # S5
    (2, 2): "5",       # S6
    (2, 1): "6",       # S7
    (2, 0): "7",       # S1
    (3, 3): "8",       # S2
    (3, 2): "9",       # S3
    (0, 2): "Enter",   # S14
    (0, 3): "IZQ",     # S15
    (0, 0): "DER",     # S16
    (1, 3): "DOWN",    # S12
    (3, 0): "UP",      # S8
    (3, 1): "ESC"      # S4
}

# Tiempo de debounce en segundos
DEBOUNCE_TIME = 0.05

# Inicializacion de GPIO
GPIO.setmode(GPIO.BCM)

# Configura las columnas como salidas
for col in COLUMNS:
    GPIO.setup(col, GPIO.OUT)
    GPIO.output(col, GPIO.HIGH)  # Desactiva la columna inicialmente

# Configura las filas como entradas con pull-up
for row in ROWS:
    GPIO.setup(row, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def scan_matrix():
    # Recorre cada columna y activa una a la vez
    for col_num, col in enumerate(COLUMNS):
        GPIO.output(col, GPIO.LOW)  # Activa la columna
        
        for row_num, row in enumerate(ROWS):
            if GPIO.input(row) == GPIO.LOW:  # Si la fila esta baja, boton presionado
                if (row_num, col_num) in button_map:
                    print(f"Boton presionado: {button_map[(row_num, col_num)]}")
                time.sleep(DEBOUNCE_TIME)  # Pausa para evitar rebotes
        
        GPIO.output(col, GPIO.HIGH)  # Desactiva la columna

try:
    print("Presiona Ctrl+C para salir")
    while True:
        scan_matrix()
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Saliendo del programa...")
finally:
    GPIO.cleanup()  # Limpia los pines GPIO
