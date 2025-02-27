import speech_recognition as sr
import pyaudio
import wave
import os
from datetime import datetime

def record_audio(filename, duration=5, sample_rate=44100, chunk=1024):
    """
    Record audio from microphone for specified duration
    
    Args:
        filename: Output audio filename
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz
        chunk: Audio chunk size
    """
    print(f"Recording for {duration} seconds...")
    
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Open audio stream
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk
    )
    
    frames = []
    
    # Record audio in chunks
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("Recording finished!")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save the audio file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

def transcribe_audio(audio_file, language="en-US"):
    """
    Transcribe audio file using Google Speech Recognition
    
    Args:
        audio_file: Path to audio file
        language: Language code (default: en-US)
        
    Returns:
        Transcribed text
    """
    recognizer = sr.Recognizer()
    
    # Load audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    
    try:
        # Use Google Speech Recognition
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def main():
    # Create output directory if it doesn't exist
    output_dir = "speech_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_file = f"{output_dir}/recording_{timestamp}.wav"
    
    # Record audio (5 seconds by default)
    record_duration = int(input("Enter recording duration in seconds: ") or "5")
    record_audio(audio_file, duration=record_duration)
    
    # Transcribe audio
    print("Transcribing audio...")
    language = input("Enter language code (default: en-US): ") or "en-US"
    transcription = transcribe_audio(audio_file, language)
    
    # Display and save transcription
    print("\nTranscription:")
    print(transcription)
    
    # Save transcription to text file
    text_file = f"{output_dir}/transcription_{timestamp}.txt"
    with open(text_file, 'w') as f:
        f.write(transcription)
    
    print(f"\nTranscription saved to {text_file}")

if __name__ == "__main__":
    main()