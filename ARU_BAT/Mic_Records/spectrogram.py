import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

# Cargar archivo .wav
def plot_spectrogram(wav_file):
    sample_rate, data = wavfile.read(wav_file)

    # Si el archivo es estereo, usar solo un canal (el canal izquierdo, por ejemplo)
    if len(data.shape) == 2:
        data = data[:, 0]

    # Calcular el espectrograma
    frequencies, times, Sxx = spectrogram(data, sample_rate)

    # Graficar el espectrograma
    plt.figure(figsize=(10, 6))
    plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud')
    plt.ylabel('Frecuencia [Hz]')
    plt.xlabel('Tiempo [s]')
    plt.title('Espectrograma')
    plt.colorbar(label='Intensidad [dB]')
    plt.show()

# Reemplaza "tu_archivo.wav" por la ruta de tu archivo .wav
plot_spectrogram('2024-10-04-16:26:09')
