import argparse
import os
from PyPDF2 import PdfReader
from gtts import gTTS
import pydub
from pydub import AudioSegment
import tempfile
import shutil

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    
    print(f"Extracting text from PDF with {len(reader.pages)} pages...")
    for i, page in enumerate(reader.pages):
        print(f"Processing page {i+1}/{len(reader.pages)}")
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    return text

def split_text_into_chunks(text, max_chars=3000):
    """Split text into smaller chunks to avoid gTTS limitations."""
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = text.split('\n')
    
    for paragraph in paragraphs:
        # If paragraph is too long, split it further by sentences
        if len(paragraph) > max_chars:
            sentences = paragraph.replace('. ', '.\n').split('\n')
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= max_chars:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
        else:
            if len(current_chunk) + len(paragraph) <= max_chars:
                current_chunk += paragraph + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def text_to_speech(text_chunks, output_path, language='en', slow=False):
    """Convert text chunks to speech and save as an audio file."""
    temp_dir = tempfile.mkdtemp()
    temp_files = []
    
    try:
        combined_audio = None
        
        for i, chunk in enumerate(text_chunks):
            if not chunk.strip():
                continue
                
            print(f"Converting chunk {i+1}/{len(text_chunks)} to speech...")
            
            # Create temporary file for this chunk
            temp_file = os.path.join(temp_dir, f"chunk_{i}.mp3")
            temp_files.append(temp_file)
            
            # Convert text to speech
            tts = gTTS(text=chunk, lang=language, slow=slow)
            tts.save(temp_file)
            
            # Add to combined audio
            if combined_audio is None:
                combined_audio = AudioSegment.from_mp3(temp_file)
            else:
                chunk_audio = AudioSegment.from_mp3(temp_file)
                combined_audio += chunk_audio
        
        # Export final audio file
        print(f"Saving audiobook to {output_path}...")
        combined_audio.export(output_path, format="mp3")
        print("Conversion completed successfully!")
        
    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir)

def pdf_to_audiobook(pdf_path, output_path, language='en'):
    """Convert PDF to audiobook."""
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Split text into manageable chunks
    text_chunks = split_text_into_chunks(text)
    print(f"Split text into {len(text_chunks)} chunks")
    
    # Convert text to speech
    text_to_speech(text_chunks, output_path, language)

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Audiobook')
    parser.add_argument('pdf_file', help='Path to the PDF file')
    parser.add_argument('--output', '-o', default='audiobook.mp3', help='Output audio file (default: audiobook.mp3)')
    parser.add_argument('--language', '-l', default='en', help='Language for text-to-speech (default: en)')
    
    args = parser.parse_args()
    
    # Check if the PDF file exists
    if not os.path.isfile(args.pdf_file):
        print(f"Error: PDF file '{args.pdf_file}' not found.")
        return
    
    # Convert PDF to audiobook
    pdf_to_audiobook(args.pdf_file, args.output, args.language)

if __name__ == "__main__":
    main()