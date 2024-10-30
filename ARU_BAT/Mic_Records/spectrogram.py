import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# Cargar archivo .wav
def plot_spectrogram(wav_file):
    sample_rate, data = wavfile.read(wav_file)

    # Si el archivo es estreo, usar solo un canal (el canal izquierdo, por ejemplo)
    if len(data.shape) == 2:
        data = data[:, 0]

    # Calcular el espectrograma
    frequencies, times, Sxx = spectrogram(data, sample_rate)

    # Ajustar la precisin de los tiempos (en segundos, con milisegundos)
    times = np.round(times, 3)  # Redondear los tiempos a milisegundos

    # Graficar el espectrograma
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud')
    plt.ylabel('Frecuencia [Hz]')
    plt.xlabel('Tiempo [s]')
    plt.title('Espectrograma')
    plt.colorbar(label='Intensidad [dB]')

    # Mostrar ejes en formato de milisegundos
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.3f}'))
    
    plt.show()

# Reemplaza "tu_archivo.wav" por la ruta de tu archivo .wav
plot_spectrogram('2024-10-30-00:53:48')
