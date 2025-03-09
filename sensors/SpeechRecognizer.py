import shutil
import subprocess
import whisper
import pyaudio
import wave
import time
import os

class SpeechRecognizer:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.audio = pyaudio.PyAudio()

    def recognize_from_file(self, audio_file):
        """Transcribe speech from a WAV file."""
        audio_file = os.path.abspath(audio_file)  # Ensure absolute path
        print(f"🔍 Checking file: {audio_file}")

        # ✅ Ensure file exists before proceeding
        if not os.path.exists(audio_file):
            print(f"❌ Error: Audio file not found at {audio_file}")
            return ""

        # ✅ Ensure Python can open the file
        try:
            with open(audio_file, "rb") as f:
                print("✅ File can be opened successfully!")
        except Exception as e:
            print(f"❌ Error: Unable to open file {audio_file} - {e}")
            return ""

        # ✅ Delay to avoid access issues
        time.sleep(1)

        try:
            result = self.model.transcribe(audio_file)
            return result['text']
        except Exception as e:
            print(f"❌ Error transcribing file: {e}")
            return ""


    def recognize_from_microphone(self, duration=5, output_filename="Documents/git_repo/EdgeSense/sensors/audio_data/sample_recording.wav"):
        """Record from microphone and transcribe in real-time."""
        print(f"🎙️ Recording for {duration} seconds...")

        # ✅ Ensure the directory exists
        output_filename = os.path.abspath(output_filename)
        output_directory = os.path.dirname(output_filename)
        if output_directory and not os.path.exists(output_directory):
            os.makedirs(output_directory)

        try:
            stream = self.audio.open(format=self.format, channels=self.channels,
                                     rate=self.rate, input=True,
                                     frames_per_buffer=self.chunk)
            frames = []

            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"❌ Error recording audio: {e}")
            return ""

        # ✅ Save the recorded WAV file properly
        try:
            with wave.open(output_filename, "wb") as wave_file:
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.audio.get_sample_size(self.format))
                wave_file.setframerate(self.rate)
                wave_file.writeframes(b"".join(frames))
        except Exception as e:
            print(f"❌ Error saving recorded audio: {e}")
            return ""

        if not os.path.exists(output_filename):
            print(f"❌ Error: The recorded file {output_filename} was not created.")
            return ""
        else:
            print(f"✅ File recorded successfully: {output_filename}")

        print("Transcribing...")
        return self.recognize_from_file(output_filename)

if __name__ == "__main__":
    recognizer = SpeechRecognizer()
    print("Recognized from file: ", recognizer.recognize_from_file("Documents/git_repo/EdgeSense/sensors/audio_data/sample_stop.wav"))
    print("Recognized from mic: ", recognizer.recognize_from_microphone(5))
