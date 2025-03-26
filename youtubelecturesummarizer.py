import argparse
import os
from pytube import YouTube
import whisper
from transformers import pipeline

def download_youtube_audio(url, output_path='./'):
    """Download audio from YouTube video and return file path"""
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        output_file = audio_stream.download(output_path=output_path)
        return output_file
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")

def transcribe_audio(audio_path, model_size="base"):
    """Transcribe audio to text using Whisper"""
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")

def summarize_text(text, model_name="sshleifer/distilbart-cnn-12-6", max_length=300):
    """Summarize text using Hugging Face pipeline"""
    try:
        # Split text into manageable chunks
        chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
        
        summarizer = pipeline("summarization", model=model_name)
        summaries = []
        
        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=max_length,
                min_length=50,
                do_sample=False
            )
            summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)
    except Exception as e:
        raise Exception(f"Error summarizing text: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='YouTube Lecture Summarizer')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--output', default='summary.txt', 
                       help='Output file name')
    parser.add_argument('--model-size', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size for transcription')
    args = parser.parse_args()

    try:
        print("⏬ Downloading audio...")
        audio_file = download_youtube_audio(args.url)
        
        print("🔉 Transcribing audio...")
        transcription = transcribe_audio(audio_file, args.model_size)
        
        print("📝 Summarizing text...")
        summary = summarize_text(transcription)
        
        with open(args.output, 'w') as f:
            f.write(summary)
        
        print(f"✅ Summary saved to {args.output}")
        print("\nSummary Preview:")
        print(summary[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    main()
