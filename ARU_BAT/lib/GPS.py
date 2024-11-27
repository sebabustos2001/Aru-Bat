import gps
import os
import time

class GPS:
    def __init__(self, log_file="gps_full_data.txt"):
        # Conecta a gpsd
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        # Archivo de log
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as file:
                # Encabezado con columnas para GPGGA, GPGSV y GPGSA
                file.write("GPGGA,GPGSV,GPGSA\n")

    def parse_sentence(self, report):
        """
        Convierte los datos del reporte del GPS en una estructura para almacenar en columnas.
        """
        if report.get('class') == 'TPV':
            # GPGGA datos principales
            gpgga = {
                "latitude": getattr(report, "lat", None),
                "longitude": getattr(report, "lon", None),
                "altitude": getattr(report, "alt", None),
                "time": getattr(report, "time", None),
                "fix_quality": getattr(report, "mode", None),
            }
            return "GPGGA", gpgga

        elif report.get('class') == 'SKY':
            # GPGSV datos satélites visibles
            gpgsv = {
                "satellites_visible": getattr(report, "satellites", None),
            }
            return "GPGSV", gpgsv

        elif report.get('class') == 'GST':
            # GPGSA datos de precisión y satélites usados
            gpgsa = {
                "pdop": getattr(report, "pdop", None),
                "hdop": getattr(report, "hdop", None),
                "vdop": getattr(report, "vdop", None),
                "satellites_used": getattr(report, "used", None),
            }
            return "GPGSA", gpgsa

        return None, None

    def get_location(self):
        # Lee datos del GPS y guarda en columnas para GPGGA, GPGSV y GPGSA
        try:
            for _ in range(5):  # Repetir 5 lecturas
                report = self.session.next()
                gpgga_data = ""
                gpgsv_data = ""
                gpgsa_data = ""

                # Procesar datos
                sentence_type, data = self.parse_sentence(report)
                if sentence_type == "GPGGA":
                    gpgga_data = str(data)
                elif sentence_type == "GPGSV":
                    gpgsv_data = str(data)
                elif sentence_type == "GPGSA":
                    gpgsa_data = str(data)

                # Guardar en el archivo
                with open(self.log_file, 'a') as file:
                    file.write(f"{gpgga_data},{gpgsv_data},{gpgsa_data}\n")

                print(f"GPGGA: {gpgga_data} | GPGSV: {gpgsv_data} | GPGSA: {gpgsa_data}")
                time.sleep(2)  # Espera 2 segundos entre lecturas

        except KeyError:
            print("Error al leer los datos del GPS (clave faltante)")
        except StopIteration:
            print("GPSD ha terminado")
        except Exception as e:
            print(f"Error al obtener la ubicación: {e}")

# Ejemplo de uso
#if __name__ == "__main__":
#    gps_module = GPS()
#    gps_module.get_location()

