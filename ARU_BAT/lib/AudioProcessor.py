import time
import os
import wave
import numpy as np

from scipy.fft import rfft, rfftfreq

class AudioProcessor:
	def __init__(self, directory="Microphone_Records",
			threshold_frequency_min=18000,
			threshold_frequency_max=100000,
			threshold_amplitude=500,
			burst_duration=1,
			peak_duration=0.3):
		self.directory = directory
		self.threshold_frequency_min = threshold_frequency_min
		self.threshold_frequency_max = threshold_frequency_max
		self.threshold_amplitude = threshold_amplitude
		self.burst_duration = burst_duration
		self.peak_duration = peak_duration
		self.processed_files = set()

	def process_audio_files(self):
		for filename in os.listdir(self.directory):
			if filename.endswith(".wav") and filename not in self.processed_files:
				file_path = os.path.join(self.directory, filename)
				if not self.contains_high_frequency(file_path):
					os.remove(file_path)
					print(f"Archivo {filename} eliminado")
				else:
					print(f"Vocalizacion detectada en {filename}")
				self.processed_files.add(filename)

	def contains_high_frequency(self, filepath):
		with wave.open(filepath, 'rb') as wav:
			framerate = wav.getframerate()
			n_frames = wav.getnframes()
			audio_data = np.frombuffer(wav.readframes(n_frames), dtype=np.int16)
		duration = n_frames / framerate

		N = len(audio_data)
		yf = rfft(audio_data)
		xf = rfftfreq(N, 1/framerate)

		passband_freq = (xf > self.threshold_frequency_min) & (xf < self.threshold_frequency_max)
		xf_filtered = xf[passband_freq]
		yf_filtered = np.abs(yf[passband_freq])

		peak_count = 0
		for i in range(len(xf_filtered)):
			if self.threshold_frequency_min <= xf_filtered[i] <= self.threshold_frequency_max and yf_filtered[i] > self.threshold_amplitude:
				peak_count += 1

		if peak_count > 0 and (peak_count/duration) >= (1/self.burst_duration):
			for i in range(len(xf_filtered)):
				if self.threshold_frequency_min <= xf_filtered[i] <= self.threshold_frequency_max and yf_filtered[i] > self.threshold_amplitude:
					if (peak_count / duration) >= (1/self.peak_duration):
						return True
		return False

		#return any(xf[i] > self.threshold_frequency and abs(yf[i]) > self.threshold_amplitude for i in range(len(yf)))
