import gps

class GPS:
    def __init__(self):
        # Conecta a gpsd
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def get_location(self):
        # Obtiene una lectura del GPS
        try:
            report = self.session.next()
            # Solo procesa reportes de tipo TPV (Time-Position-Velocity)
            if report['class'] == 'TPV':
                latitude = getattr(report, 'lat', None)
                longitude = getattr(report, 'lon', None)
                altitude = getattr(report, 'alt', None)
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'altitude': altitude
                }
        except KeyError:
            return None
        except StopIteration:
            print("GPSD ha terminado")
        except Exception as e:
            print(f"Error al obtener la ubicación: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    gps_module = GPS()
    location = gps_module.get_location()
    if location:
        print("Latitud:", location['latitude'])
        print("Longitud:", location['longitude'])
        print("Altitud:", location['altitude'])
    else:
        print("No se pudo obtener la ubicación")
