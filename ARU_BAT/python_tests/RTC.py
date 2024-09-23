import os

# Sincroniza la hora del RTC con la hora del sistema
os.system("sudo hwclock -r")

# Lee la hora actual desde el RTC
rtc_time = os.popen("sudo hwclock -r").read()
print(f"La hora actual del RTC es: {rtc_time.strip()}")
