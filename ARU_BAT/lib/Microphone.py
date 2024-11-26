import os
import pyaudio
import wave
import time

from datetime import datetime, timedelta

class Microphone():
	def __init__(self,
				channels=1,
				sample_frec=250000,
				chunk=16384,
				record_seconds=59,
				output_file="output.wav"):

		# Micrphone settings
		self.channels = channels
		self.sample_frec = sample_frec
		self.chunk = chunk
		self.record_seconds = record_seconds

		self.record_dir = "BS01_Records"
		if not os.path.exists(self.record_dir):
			os.makedirs(self.record_dir)
		self.audio = pyaudio.PyAudio()

	def start_recording(self):
		current_time = datetime.now()
		new_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
		wait_time = (new_minute - current_time).total_seconds()
		time.sleep(wait_time)
		
		timestamp = current_time.strftime("%Y-%m-%d-%H:%M:%S")
		output_file = os.path.join(self.record_dir, f"BS01-{timestamp}.wav")	# Set audio file name

		# Start record
		print("Initializing record...")
		stream = self.audio.open(format = pyaudio.paInt16,
								channels = self.channels,
								rate = self.sample_frec,
								input = True,
								frames_per_buffer = self.chunk)

		print("Recording...")
		frames = []

		for i in range(0, int(self.sample_frec / self.chunk * self.record_seconds)):
			data = stream.read(self.chunk)
			frames.append(data)

		print("Record ending")

		# Stop recording
		stream.stop_stream()
		stream.close()

		# Save WAV file
		wf = wave.open(output_file, 'wb')
		wf.setnchannels(self.channels)
		wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
		wf.setframerate(self.sample_frec)
		wf.writeframes(b''.join(frames))
		wf.close()

		print(f"Record File save as {output_file}")
		time.sleep(0.1)

	def close(self):
		# Closing PyAudio
		self.audio.terminate()
