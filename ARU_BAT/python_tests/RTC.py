import os
import time

# Sincroniza la hora del RTC con la hora del sistema
os.system("sudo hwclock -r")

# Lee la hora actual desde el RTC
rtc_time = os.popen("sudo hwclock -r").read()
print(f"La hora actual del RTC es: {rtc_time.strip()}")


# Establece la alarma de despertado a 60 segundos
os.system('echo +60 | sudo tee /sys/class/rtc/rtc0/wakealarm')

# Espera unos segundos para asegurar que la alarma se haya configurado correctamente
time.sleep(5)

# Apaga la Raspberry Pi
os.system('sudo halt')

